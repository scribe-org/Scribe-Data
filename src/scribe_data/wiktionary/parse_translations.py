# SPDX-License-Identifier: GPL-3.0-or-later
"""
Parse translations for a target language from a Wiktionary pages-articles dump.
"""

import bz2
import os
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import mwparserfromhell
from tqdm import tqdm

from scribe_data.wiktionary.parse_constants import get_wiktionary_config

# A single translation entry (e.g., {"description": "...", "translation": "..."}).
TranslationEntry = Dict[str, str]

# Maps a sense index (e.g., "1") to its translation entry.
SensesToTranslations = Dict[str, TranslationEntry]

# Maps a Part of Speech (e.g., "noun") to its senses.
PosToSenses = Dict[str, SensesToTranslations]

# Maps a source word to its parts of speech.
WordToPos = Dict[str, PosToSenses]

# Maps a target language ISO to the translated words.
LanguageToWords = Dict[str, WordToPos]


# MARK: Shared Helpers


def _merge_parsed_into_output(
    output: LanguageToWords,
    word: str,
    parsed: Dict[str, PosToSenses],
) -> None:
    """
    Merge a single page's parsed translations into the cumulative output dict.

    Parameters
    ----------
    output : LanguageToWords
        The running accumulator.

    word : str
        The source word whose translations are being merged.

    parsed : Dict[str, PosToSenses]
        Translations returned by one of the ``_parse_page_translations_*`` functions.
    """
    for code, pos_senses in parsed.items():
        word_map = output.setdefault(code, {})
        pos_map = word_map.setdefault(word, {})
        for pos, senses in pos_senses.items():
            if sense_map := pos_map.setdefault(pos, {}):
                for src_idx, src_data in senses.items():
                    target_idx = src_idx
                    while target_idx in sense_map:
                        target_idx = str(int(target_idx) + 1)
                    sense_map[target_idx] = src_data

            else:
                sense_map.update(senses)


def _build_sense_entry(description: str, translation: str) -> Dict[str, str]:
    """
    Build a sense entry dict with stable keys for JSON consumers.

    Parameters
    ----------
    description : str
        Gloss or meaning for the sense (e.g. ``trans-top`` / ``trad-arriba`` first
        argument). Empty when the source template has no gloss, which is common on
        eswiktionary (bare ``{{trad-arriba}}``).

    translation : str
        Comma-joined translation word(s).

    Returns
    -------
    Dict[str, str]
        ``{"description": str, "translation": str}``.
    """
    return {
        "description": description.strip() if description else "",
        # Remove latinized versions of words that are commonly found in parentheses.
        "translation": re.sub(r"\(.*\)", "", translation).strip().replace(" ,", ","),
    }


def _extract_translation_word(
    node,
    code: str,
    raw_word: str,
    config: dict,
    target_langs: Optional[frozenset],
    tag_index: Optional[int] = None,
) -> Optional[str]:
    """
    Return a cleaned translation string with grammatical tags appended, or None to skip the word.

    Parameters
    ----------
    node : mwparserfromhell.nodes.Template
        The parsed template node for the translation entry.

    code : str
        ISO language code from the template's first parameter.

    raw_word : str
        The raw translation word extracted from the template.

    config : dict
        Wiktionary config for the source language edition.

    target_langs : Optional[frozenset]
        ISO codes of languages to keep, or None to keep all.

    tag_index : Optional[int]
        When set (e.g. eswiktionary ``t1`` / ``t2`` rows), only ``g{tag_index}`` is used
        for grammar tags instead of every ``g*`` on the template.

    Returns
    -------
    Optional[str]
        The cleaned word (with tags) or None if it should be skipped.
    """
    if not raw_word:
        return None

    if target_langs and code not in target_langs:
        return None

    ignored_strings = config["ignored_strings"]
    word_lower = raw_word.lower()
    if word_lower in ignored_strings or any(
        word_lower.startswith(prefix) for prefix in config["ignored_prefixes"]
    ):
        return None

    valid_tags = []
    if tag_index is not None:
        g_key = f"g{tag_index}"
        if node.has(g_key):
            if pval := str(node.get(g_key).value.strip_code()).strip():
                valid_tags.append(pval)

    else:
        for param in node.params:
            pname = str(param.name).strip()
            if pname in {"1", "2"}:
                continue

            pval = str(param.value.strip_code()).strip()
            if not pval:
                continue

            if pname.startswith("g"):
                valid_tags.append(pval)

            elif pname.isdigit() and pval.lower() not in ignored_strings:
                valid_tags.append(pval)

    if valid_tags:
        valid_tags = list(dict.fromkeys(valid_tags))
        raw_word = f"{raw_word} ({', '.join(valid_tags)})"

    return raw_word if len(raw_word) < 200 else None


def _add_translations_to_result(
    result: Dict[str, PosToSenses],
    current_pos: str,
    pos_sense_tracker: Dict[str, int],
    words_by_lang: Dict[str, List[str]],
    description: str,
):
    """
    Write words_by_lang into result under the next sense index for current_pos.

    Parameters
    ----------
    result : Dict[str, PosToSenses]
        The per-language output dict being built up.

    current_pos : str
        The current part-of-speech label.

    pos_sense_tracker : Dict[str, int]
        Tracks the sense count per POS so each block gets a unique index.

    words_by_lang : Dict[str, List[str]]
        Collected translations grouped by ISO code.

    description : str
        The sense description / gloss for the current translation block.
    """
    if not any(words_by_lang.values()):
        return

    pos_sense_tracker.setdefault(current_pos, 0)
    pos_sense_tracker[current_pos] += 1
    sense_idx_str = str(pos_sense_tracker[current_pos])

    for code, words in words_by_lang.items():
        if not words:
            continue

        result.setdefault(code, {}).setdefault(current_pos, {})[sense_idx_str] = (
            _build_sense_entry(
                description=description,
                translation=", ".join(words),
            )
        )


# MARK: Parse Page


def _extract_source_lang_section(wikitext: str, config: dict) -> Optional[str]:
    """
    Return the wikitext content of the source-language section.

    Uses ``lang_header_pattern`` and ``lang_header_level`` (default 2 for ``== … ==``).
    For level-1 ``= … =`` (e.g., ptwiktionary / ruwiktionary), set ``lang_header_level: 1``.

    Parameters
    ----------
    wikitext : str
        Full wikitext of the Wiktionary page.

    config : dict
        Wiktionary config for the source language edition.

    Returns
    -------
    Optional[str]
        The section wikitext, or None if the source-language section is not found.
    """
    if config.get("lang_header_pattern"):
        pattern = config["lang_header_pattern"]
        level = config.get("lang_header_level", 2)
        eqs = "=" * level

        # Match lines like exactly `level` '=' signs, text, and `level` '=' signs.
        heading_regex = re.compile(rf"^{eqs}([^=\n]+){eqs}\s*$", re.MULTILINE)
        next_heading_regex = re.compile(rf"^{eqs}[^=]", re.MULTILINE)

        for line_match in heading_regex.finditer(wikitext):
            if pattern.search(line_match.group(1)):
                start = line_match.end()
                next_h = next_heading_regex.search(wikitext, start)
                end = next_h.start() if next_h else len(wikitext)
                return wikitext[start:end].strip()

    return None


# MARK: Engine: ast_u_tabelle


def _parse_ast_u_tabelle(
    config: dict,
    target_langs: Optional[frozenset],
    wikitext: str,
    _word: str,
) -> Dict[str, PosToSenses]:
    """
    Parse translations from a single page using the ``Ü-Tabelle`` format (e.g. German Wiktionary).

    Parameters
    ----------
    config : dict
        Wiktionary config for the source language edition.

    target_langs : Optional[frozenset]
        ISO codes of languages to extract, or None for all.

    wikitext : str
        Raw wikitext of the Wiktionary page.

    _word : str
        The source word on the page (unused, kept for a uniform signature).

    Returns
    -------
    Dict[str, PosToSenses]
        ``{target_lang_iso: {pos: {sense_idx: {description?, translation}}}}``.
    """
    result: Dict[str, PosToSenses] = {}

    lang_section = _extract_source_lang_section(wikitext=wikitext, config=config)
    if not lang_section:
        return result

    pos_map: dict = config.get("pos_map", {})

    wikicode = mwparserfromhell.parse(lang_section)

    current_pos = "other"
    pos_sense_tracker: Dict[str, int] = {}

    template_pos: str = config.get("template_pos", "wortart")
    template_table: str = config.get("template_table", "ü-tabelle")
    template_list: str = config.get("template_list", "ü-liste")
    template_t_list = frozenset(
        config.get("template_translation", ["ü", "üt", "üxx", "üt+"])
    )

    for node in wikicode.nodes:
        # Update the current POS whenever we hit a heading with a word type template.
        if isinstance(node, mwparserfromhell.nodes.Heading):
            for t in node.title.filter_templates():
                if t.name.strip().lower() == template_pos:
                    pos_raw = str(t.get(1).value).strip().lower() if t.has(1) else ""
                    current_pos = (
                        pos_map.get(pos_raw, pos_raw.replace(" ", "_"))
                        if pos_map
                        else pos_raw
                    )

        elif isinstance(node, mwparserfromhell.nodes.Template):
            if node.name.strip().lower() != template_table:
                continue

            # Find the named param that holds the translation list.
            list_param = next(
                (
                    p.name.strip()
                    for p in node.params
                    if p.name.strip().lower() == template_list
                ),
                None,
            )

            if not list_param:
                continue

            description = str(node.get("G").value).strip() if node.has("G") else ""

            liste_ast = node.get(list_param).value
            words_by_lang: Dict[str, List[str]] = {}

            for t in liste_ast.filter_templates():
                tname = t.name.strip().lower()
                if tname not in template_t_list:
                    continue

                if not t.has(1) or not t.has(2):
                    continue

                code = str(t.get(1).value).strip().lower()
                raw_word = str(t.get(2).value.strip_code()).strip()

                if extracted := _extract_translation_word(
                    t, code, raw_word, config, target_langs
                ):
                    words_by_lang.setdefault(code, []).append(extracted)

            _add_translations_to_result(
                result, current_pos, pos_sense_tracker, words_by_lang, description
            )

    return result


# POS values accepted after pos_map lookup.
_KNOWN_POS = frozenset(
    [
        "noun",
        "verb",
        "adjective",
        "adverb",
        "preposition",
        "conjunction",
        "interjection",
        "pronoun",
        "determiner",
        "numeral",
        "phrase",
        "symbol",
        "particle",
        "proper_noun",
    ]
)


# MARK: Shared Block-Parsing Core


def _parse_block_translations(
    config: dict,
    target_langs: Optional[frozenset],
    wikitext: str,
    collect_row,
) -> Dict[str, PosToSenses]:
    """
    Shared parsing core for all ``trans-top`` / ``Trad1``-style block engines.

    Handles everything that is common across block-based engines:

    * Extracting the source-language section of the page.
    * Detecting POS from headings and inline templates.
    * Opening / closing translation blocks (``template_top`` / ``template_bottom``).
    * Accumulating per-language words and flushing them into *result*.

    The **only** variation between engines is *how* a single translation row is
    turned into a list of words for a given language.  That logic is supplied by
    the caller as the ``collect_row`` callback.

    Parameters
    ----------
    config : dict
        Wiktionary config for the source language edition.

    target_langs : Optional[frozenset]
        ISO codes of languages to extract, or ``None`` for all.

    wikitext : str
        Raw wikitext of the Wiktionary page.

    collect_row : Callable[[node, node_idx, all_nodes, tname, target_langs, config,
                             current_words_by_lang], None]
        Called once per candidate template node that is *inside* an open
        translation block and is **not** a ``template_top`` / ``template_bottom``
        or POS marker.  The callback appends any harvested words directly into
        *current_words_by_lang*.

    Returns
    -------
    Dict[str, PosToSenses]
        ``{target_lang_iso: {pos: {sense_idx: {description?, translation}}}}``.
    """
    result: Dict[str, PosToSenses] = {}

    lang_section = _extract_source_lang_section(wikitext=wikitext, config=config)
    if not lang_section:
        return result

    pos_map: dict = config.get("pos_map", {})
    template_top = frozenset(config.get("template_top", ["trans-top"]))
    template_bottom: str = config.get("template_bottom", "trans-bottom")

    wikicode = mwparserfromhell.parse(lang_section)
    all_nodes = list(wikicode.nodes)

    current_pos = "other"
    pos_sense_tracker: Dict[str, int] = {}

    in_translation_block = False
    current_desc = ""
    current_words_by_lang: Dict[str, List[str]] = {}

    def _commit_block():
        """
        Flush the current translation block into result and reset state.
        """
        nonlocal current_words_by_lang, current_desc, in_translation_block
        if current_words_by_lang:
            _add_translations_to_result(
                result=result,
                current_pos=current_pos,
                pos_sense_tracker=pos_sense_tracker,
                words_by_lang=current_words_by_lang,
                description=current_desc,
            )
        current_words_by_lang = {}
        current_desc = ""
        in_translation_block = False

    for node_idx, node in enumerate(all_nodes):
        if isinstance(node, mwparserfromhell.nodes.Heading):
            if in_translation_block:
                _commit_block()

            header_text = str(node.title).strip().lower()

            # Some editions put a template in the heading (e.g. French `{{S|nom|fr}}`,
            # Spanish `{{sustantivo masculino|es}}`).
            for t in node.title.filter_templates():
                tname = t.name.strip().lower()
                if tname in pos_map:
                    header_text = tname
                    break

                if t.has(1):
                    tval = str(t.get(1).value).strip().lower()
                    if tval in pos_map:
                        header_text = tval

            mapped = pos_map.get(header_text, header_text.replace(" ", "_"))
            if mapped in _KNOWN_POS or mapped != header_text.replace(" ", "_"):
                current_pos = mapped

        elif isinstance(node, mwparserfromhell.nodes.Template):
            tname = node.name.strip().lower()

            # Inline POS marker (e.g. Indonesian ``{{-n-}}``).
            mapped_tname = pos_map.get(tname, tname.replace(" ", "_"))
            if mapped_tname in _KNOWN_POS or mapped_tname != tname.replace(" ", "_"):
                if in_translation_block:
                    _commit_block()
                current_pos = mapped_tname

            elif tname in template_top:
                if in_translation_block:
                    _commit_block()
                in_translation_block = True
                if node.has(1):
                    desc = str(node.get(1).value.strip_code()).strip()
                    current_desc = re.sub(r"^[\d.]+\s*", "", desc).strip()

            elif tname == template_bottom:
                _commit_block()

            elif in_translation_block:
                # Delegate row parsing to the engine-specific callback.
                collect_row(
                    node,
                    node_idx,
                    all_nodes,
                    tname,
                    target_langs,
                    config,
                    current_words_by_lang,
                )

    if in_translation_block:
        _commit_block()

    return result


# MARK: Engine: ast_trans_top


def _collect_row_template(
    node,
    _node_idx,
    _all_nodes,
    tname: str,
    target_langs: Optional[frozenset],
    config: dict,
    current_words_by_lang: Dict[str, List[str]],
) -> None:
    """
    Row collector for the ``ast_trans_top`` engine.

    Extracts translation words from ``{{t|lang|word}}``-style templates
    (including the ``t1=`` / ``t2=`` named-parameter variant used by eswiktionary).

    Parameters
    ----------
    node : mwparserfromhell.nodes.Template
        Current template node being evaluated inside an open translation block.

    _node_idx : int
        Unused index of *node* in the full node list (kept for callback signature
        compatibility).

    _all_nodes : list
        Unused full node list (kept for callback signature compatibility).

    tname : str
        Lowercased template name.

    target_langs : Optional[frozenset]
        ISO language whitelist, or ``None`` to accept all target languages.

    config : dict
        Source-edition extraction config.

    current_words_by_lang : Dict[str, List[str]]
        Mutable ``{lang_code: [word, ...]}`` accumulator for the current block.
    """
    template_t_list = frozenset(
        config.get("template_translation", ["t", "t+", "t-check", "tt", "tt+"])
    )
    if tname not in template_t_list:
        return
    if not node.has(1):
        return

    code = str(node.get(1).value).strip().lower()

    if node.has(2):
        raw_word = str(node.get(2).value.strip_code()).strip()
        if extracted := _extract_translation_word(
            node, code, raw_word, config, target_langs
        ):
            current_words_by_lang.setdefault(code, []).append(extracted)

    else:
        # eswiktionary: {{t|de|a1=1|t1=Buch|g1=n}} — lemma in t1, t2, …
        i = 1
        while node.has(f"t{i}"):
            raw_word = str(node.get(f"t{i}").value.strip_code()).strip()
            if extracted := _extract_translation_word(
                node, code, raw_word, config, target_langs, i
            ):
                current_words_by_lang.setdefault(code, []).append(extracted)
            i += 1


def _parse_ast_trans_top(
    config: dict,
    target_langs: Optional[frozenset],
    wikitext: str,
    _word: str,
) -> Dict[str, PosToSenses]:
    """
    Parse translations using the ``trans-top`` / ``trans-bottom`` block format.

    Used by: enwiktionary, frwiktionary, eswiktionary, svwiktionary, ptwiktionary, …

    Each translation row is a ``{{t|lang|word}}`` (or ``{{t+|…}}``) template.

    Parameters
    ----------
    config : dict
        Wiktionary config for the source language edition.

    target_langs : Optional[frozenset]
        ISO codes of languages to extract, or ``None`` for all.

    wikitext : str
        Raw wikitext of the Wiktionary page.

    _word : str
        Source page title (unused by this engine, retained for uniform signature).

    Returns
    -------
    Dict[str, PosToSenses]
        ``{target_lang_iso: {pos: {sense_idx: {description?, translation}}}}``.
    """
    return _parse_block_translations(
        config=config,
        target_langs=target_langs,
        wikitext=wikitext,
        collect_row=_collect_row_template,
    )


# MARK: Engine: ast_wikilink_list


def _collect_row_wikilink(
    node,
    node_idx: int,
    all_nodes: list,
    tname: str,
    target_langs: Optional[frozenset],
    config: dict,
    current_words_by_lang: Dict[str, List[str]],
) -> None:
    """
    Row collector for the ``ast_wikilink_list`` engine.

    In itwiktionary each row looks like ``:* {{en}}: [[word1]], [[word2]]``.
    The template name *is* the ISO code; words are bare ``[[wikilinks]]`` that
    follow on the same line.

    Parameters
    ----------
    node : mwparserfromhell.nodes.Template
        Current language-marker template (its name is the target language code).

    node_idx : int
        Index of *node* in *all_nodes*.

    all_nodes : list
        Full linear node sequence for the parsed source-language section.

    tname : str
        Lowercased template name, interpreted as a language code.

    target_langs : Optional[frozenset]
        ISO language whitelist, or ``None`` to accept all target languages.

    config : dict
        Source-edition extraction config.

    current_words_by_lang : Dict[str, List[str]]
        Mutable ``{lang_code: [word, ...]}`` accumulator for the current block.
    """
    lang_code = tname  # e.g. "en", "de"
    if target_langs and lang_code not in target_langs:
        return

    ignored_strings = config.get("ignored_strings", [])
    ignored_prefixes = config.get("ignored_prefixes", [])

    row_words: List[str] = []
    for following in all_nodes[node_idx + 1 :]:
        if isinstance(following, mwparserfromhell.nodes.Text):
            if "\n" in str(following):
                break  # end of this line

        elif isinstance(following, mwparserfromhell.nodes.Wikilink):
            raw_word = str(following.title).strip()
            # Piped links: [[word|display]] → use the display (right-hand) text.

            if "|" in raw_word:
                raw_word = raw_word.split("|", 1)[1].strip()
            word_lower = raw_word.lower()

            if not raw_word:
                continue

            if word_lower in ignored_strings or any(
                word_lower.startswith(p) for p in ignored_prefixes
            ):
                continue

            if len(raw_word) < 200:
                row_words.append(raw_word)

        elif isinstance(following, mwparserfromhell.nodes.Template):
            break  # next language flag or section boundary

    if row_words:
        current_words_by_lang.setdefault(lang_code, []).extend(row_words)


def _parse_ast_wikilink_list(
    config: dict,
    target_langs: Optional[frozenset],
    wikitext: str,
    _word: str,
) -> Dict[str, PosToSenses]:
    """
    Parse translations using the ``Trad1`` / ``Trad2`` block + wikilink format.

    Used by: itwiktionary.

    Each translation row is ``:* {{lang_code}}: [[word1]], [[word2]]`` — the
    template name is the ISO code and words are bare ``[[wikilinks]]``.

    Parameters
    ----------
    config : dict
        Wiktionary config for the source language edition.

    target_langs : Optional[frozenset]
        ISO codes of languages to extract, or ``None`` for all.

    wikitext : str
        Raw wikitext of the Wiktionary page.

    _word : str
        Source page title (unused by this engine, retained for uniform signature).

    Returns
    -------
    Dict[str, PosToSenses]
        ``{target_lang_iso: {pos: {sense_idx: {description?, translation}}}}``.
    """
    return _parse_block_translations(
        config=config,
        target_langs=target_langs,
        wikitext=wikitext,
        collect_row=_collect_row_wikilink,
    )


# MARK: Engine Dispatch

_ENGINES: Dict[str, callable] = {
    "ast_u_tabelle": _parse_ast_u_tabelle,
    "ast_trans_top": _parse_ast_trans_top,
    "ast_wikilink_list": _parse_ast_wikilink_list,
}


def _parse_page_translations(
    config: dict,
    target_langs: Optional[frozenset],
    wikitext: str,
    word: str,
) -> Dict[str, PosToSenses]:
    """
    Route to the right engine and parse a single Wiktionary page.

    Parameters
    ----------
    config : dict
        Wiktionary config for the source language edition.

    target_langs : Optional[frozenset]
        ISO codes of languages to extract translations for.

    wikitext : str
        Raw wikitext of the Wiktionary page.

    word : str
        The source word on the page.

    Returns
    -------
    Dict[str, PosToSenses]
        ``{target_lang_iso: {pos: {sense_idx: {description?, translation}}}}``.
    """
    engine = config.get("engine", "ast_trans_top")
    parser_fn = _ENGINES.get(engine, _parse_ast_trans_top)
    return parser_fn(
        config,
        target_langs,
        wikitext,
        word,
    )


# MARK: Parse Dump


def _parse_page_worker(
    args: Tuple[str, str, Optional[frozenset], dict],
) -> Optional[Tuple[str, Dict[str, PosToSenses]]]:
    """
    Parse a single Wiktionary page, designed to be called from a worker process.

    Parameters
    ----------
    args : Tuple[str, str, Optional[frozenset], dict]
        Packed tuple of (word, wikitext, target_langs, config).

    Returns
    -------
    Optional[Tuple[str, Dict[str, PosToSenses]]]
        ``(word, parsed)`` or ``None`` if the page has no translations.
    """
    word, wikitext, target_langs, config = args
    if not word or not wikitext:
        return None

    parsed = _parse_page_translations(
        config=config,
        target_langs=target_langs,
        wikitext=wikitext,
        word=word,
    )
    return (word, parsed) if parsed else None


def _iter_dump_pages(wiktionary_dump_path: Path, pbar=None):
    """
    Yield ``(title, text)`` for each page in the XML dump.

    Parameters
    ----------
    wiktionary_dump_path : Path
        Path to a ``*wiktionary-*-pages-articles.xml.bz2`` dump file.

    pbar : Optional[tqdm]
        Optional tqdm progress bar to continuously record bytes read.
    """
    import shutil
    import subprocess
    import threading

    # Simple wrapper to update pbar dynamically behind bz2.open.
    class ProgressFileWrapper:
        """
        File-like wrapper that updates a progress bar on read operations.

        Parameters
        ----------
        path : Path | str
            File path to open in binary mode.

        pbar_ref : Optional[tqdm]
            Progress bar to update with consumed byte counts.
        """

        def __init__(self, path, pbar_ref):
            """
            Open the wrapped file and store the progress-bar reference.

            Parameters
            ----------
            path : Path | str
                File path to open in binary mode.

            pbar_ref : Optional[tqdm]
                Progress bar to update with consumed byte counts.
            """
            self.f = open(path, "rb")
            self.pbar_ref = pbar_ref

        def read(self, size=-1):
            """
            Read bytes and update progress by the number of bytes returned.

            Parameters
            ----------
            size : int, default=-1
                Maximum number of bytes to read. ``-1`` means read until EOF.

            Returns
            -------
            bytes
                Bytes read from the wrapped file object.
            """
            data = self.f.read(size)
            if self.pbar_ref and data:
                self.pbar_ref.update(len(data))
            return data

        def readinto(self, b):
            """
            Read bytes into ``b`` and increment progress by bytes written.

            Parameters
            ----------
            b : writable buffer
                Destination buffer accepted by ``readinto``.

            Returns
            -------
            int
                Number of bytes read into ``b``.
            """
            n = self.f.readinto(b)
            if self.pbar_ref and n:
                self.pbar_ref.update(n)
            return n

        def close(self):
            """Close the wrapped binary file object."""
            self.f.close()

    proc = None
    if str(wiktionary_dump_path).endswith(".bz2") and shutil.which("bzcat"):
        raw_f = open(wiktionary_dump_path, "rb")
        proc = subprocess.Popen(["bzcat"], stdin=raw_f, stdout=subprocess.PIPE)

        def poll_progress(tracked_f, pbar_ref, process):
            import time

            while process.poll() is None:
                if pbar_ref:
                    try:
                        current = tracked_f.tell()
                        diff = current - pbar_ref.n
                        if diff > 0:
                            pbar_ref.update(diff)

                    except (OSError, ValueError):
                        pass

                time.sleep(0.5)

            if pbar_ref:
                try:
                    diff = tracked_f.tell() - pbar_ref.n
                    if diff > 0:
                        pbar_ref.update(diff)

                except (OSError, ValueError):
                    pass

            tracked_f.close()

        t = threading.Thread(
            target=poll_progress, args=(raw_f, pbar, proc), daemon=True
        )
        t.start()
        f = proc.stdout

    else:
        raw_f = ProgressFileWrapper(wiktionary_dump_path, pbar)
        if str(wiktionary_dump_path).endswith(".bz2"):
            f = bz2.open(raw_f, "rb")
        else:
            f = raw_f

    try:
        context = iter(ET.iterparse(f, events=("start", "end")))
        try:
            _, root = next(context)

        except StopIteration:
            return

        for event, elem in context:
            if event != "end":
                continue

            tag = elem.tag
            ns = tag[: tag.rfind("}") + 1] if "}" in tag else ""
            tag_name = tag[tag.rfind("}") + 1 :] if "}" in tag else tag

            if tag_name != "page":
                continue

            title = elem.findtext(f"{ns}title", default="")
            text = elem.findtext(f"{ns}revision/{ns}text", default="")

            yield title, text

            elem.clear()
            root.clear()

    finally:
        if proc:
            proc.terminate()
            proc.wait()

        else:
            f.close()


def parse_xml_dump(
    wiktionary_dump_path: Union[str, Path],
    target_lang_codes: Optional[List[str]],
    *,  # force keyword-only arguments
    source_iso: str = "en",
    progress: bool = True,
    num_workers: Optional[int] = None,
) -> LanguageToWords:
    """
    Parse a Wiktionary XML dump and return translations for the requested languages.

    Parameters
    ----------
    wiktionary_dump_path : str or Path
        Path to a ``*wiktionary-*-pages-articles.xml.bz2`` dump file.

    target_lang_codes : list of str or None
        ISO codes of languages to extract (e.g. ``["de", "fr"]``). ``None`` extracts all.

    source_iso : str, default ``"en"``
        ISO code of the source Wiktionary edition.

    progress : bool, default ``True``
        Whether to show a progress bar.

    num_workers : Optional[int]
        Number of worker processes. Defaults to cpu_count - 1.

    Returns
    -------
    LanguageToWords
        ``{target_lang_iso: {word: {pos: {sense_idx: {description?, translation}}}}}``.
    """
    path = Path(wiktionary_dump_path)
    if not path.exists():
        raise FileNotFoundError(f"Wiktionary dump not found: {path}")

    output: LanguageToWords = {}

    if num_workers is None:
        num_workers = max(1, (os.cpu_count() or 1) - 1)

    try:
        total_size = path.stat().st_size

    except (OSError, AttributeError):
        total_size = None

    pbar = None
    if progress:
        pbar = tqdm(
            total=total_size,
            desc="Parsing Wiktionary",
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        )

    target_langs_frozenset = (
        frozenset(c.lower() for c in target_lang_codes) if target_lang_codes else None
    )

    config = get_wiktionary_config(source_iso=source_iso)

    def _filtered_iterator():
        """
        Yield (word, text, target_langs, config) tuples, skipping pages that can't have translations.
        """
        count = 0
        for title, text in _iter_dump_pages(path, pbar):
            count += 1

            if not title or not text:
                continue

            # Allow translation subpages but skip all other namespaced titles.
            if ":" in title and not title.startswith("Appendix:"):
                continue

            word = title.strip()
            if not word or not word[0].isalnum():
                continue

            # Quick text scan — skip pages with no translation markers at all.
            prefilters = config.get("prefilters", [])
            if prefilters and all(f not in text for f in prefilters):
                continue

            # Normalize delegated subpages back to their base word.
            if word.endswith("/translations") or word.endswith("/übersetzungen"):
                word = word.split("/")[0]

            yield word, text, target_langs_frozenset, config

        if pbar:
            pbar.refresh()
            pbar.close()

    try:
        if num_workers == 1:
            # Single-process path — handy for debugging or low-memory environments.
            for result in map(_parse_page_worker, _filtered_iterator()):
                if result:
                    _merge_parsed_into_output(output, *result)

        else:
            # Use a process pool for speed on large dumps.
            # We maintain a bounded set of active futures to avoid OOM memory explosion
            # while keeping the workers busy and the progress bar updating smoothly.
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                for result in executor.map(
                    _parse_page_worker, _filtered_iterator(), chunksize=50
                ):
                    if result:
                        _merge_parsed_into_output(output, *result)

    except KeyboardInterrupt:
        print("\nParsing cleanly interrupted by user. Saving progress...")

    except Exception as e:
        print(f"\nParsing encountered an error: {e}. Saving progress...")

    return output


# MARK: Exports


def parse_wiktionary_translations(
    target_languages: Optional[Union[str, List[str]]] = None,
    wiktionary_dump_path: Optional[Union[str, Path]] = None,
    output_dir: Optional[str] = None,
    overwrite: bool = False,
) -> None:
    """
    Parse a Wiktionary XML dump and write per-language translation JSON files.

    Parameters
    ----------
    target_languages : str or list of str, optional
        Language(s) to extract (e.g. ``"de"``, ``"german"``).
        ``None`` or ``"all"`` extracts every known language.

    wiktionary_dump_path : str or Path, optional
        Path to a ``*wiktionary-*-pages-articles.xml.bz2`` dump file.

    output_dir : str, optional
        Directory where JSON files are saved.

    overwrite : bool, default ``False``
        Whether to overwrite existing output files.
    """
    import orjson

    from scribe_data.utils import (
        DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR,
        DEFAULT_WIKTIONARY_JSON_EXPORT_DIR,
        check_index_exists,
        get_language_from_iso,
        language_metadata,
        resolve_lang_iso,
    )

    output_dir = output_dir or DEFAULT_WIKTIONARY_JSON_EXPORT_DIR
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    target_isos: List[str] = []
    if not target_languages or target_languages == "all" or target_languages == ["all"]:
        # Collect ISO codes for every language and sub-language we know about.
        for lang_info in language_metadata.values():
            if iso := lang_info.get("iso"):
                target_isos.append(iso)
            for sub_info in lang_info.get("sub_languages", {}).values():
                if sub_iso := sub_info.get("iso"):
                    target_isos.append(sub_iso)

    else:
        specs = (
            [target_languages]
            if isinstance(target_languages, str)
            else target_languages
        )
        for lang_spec in specs:
            iso = resolve_lang_iso(language=lang_spec)
            if not iso:
                print(f"Warning: Unknown language '{lang_spec}', skipping.")
                continue
            target_isos.append(iso)

        if not target_isos:
            return

    dump_path, source_iso = _resolve_dump_path(
        wiktionary_dump_path=wiktionary_dump_path,
        output_dir=DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR,
    )
    if not dump_path:
        return

    source_lang_name = get_language_from_iso(source_iso)
    out_subdir = _get_output_subdir(source_lang_name, language_metadata)
    base_out_path = Path(output_dir) / out_subdir
    base_out_path.mkdir(parents=True, exist_ok=True)

    data_by_lang = parse_xml_dump(
        dump_path,
        target_isos,
        source_iso=source_iso,
    )

    for iso, data in data_by_lang.items():
        out_path = base_out_path / f"{iso}_translations_from_{source_iso}.json"

        if not overwrite and check_index_exists(out_path, overwrite_all=overwrite):
            print(f"Skipping {iso}: '{out_path}' already exists.")
            continue

        with open(out_path, "wb") as f:
            f.write(
                orjson.dumps(
                    data,
                    option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS,
                )
            )

        print(
            f"Exported '{iso}' translations from '{source_iso}' to the file {out_path}"
        )


# MARK: Output Resolution


def _resolve_dump_path(
    wiktionary_dump_path: Optional[Union[str, Path]], output_dir: str
) -> Tuple[Optional[Path], str]:
    """
    Resolve a Wiktionary dump path and return the dump path together with the source ISO.

    Parameters
    ----------
    wiktionary_dump_path : Optional[Union[str, Path]]
        Explicit dump path, or a language name / ISO used to search for one.

    output_dir : str
        Directory to search in when no explicit path is given.

    Returns
    -------
    Tuple[Optional[Path], str]
        ``(resolved_path, source_iso)`` where path is ``None`` if nothing was found.
    """
    from scribe_data.utils import resolve_lang_iso

    iso = "en"  # default

    if (
        isinstance(wiktionary_dump_path, str)
        and not Path(wiktionary_dump_path).exists()
    ):
        if resolved := resolve_lang_iso(wiktionary_dump_path):
            iso = resolved
        elif wiktionary_dump_path.endswith("wiktionary"):
            iso = wiktionary_dump_path.replace("wiktionary", "")

    wiktionary = f"{iso}wiktionary"

    if (
        wiktionary_dump_path is None
        or wiktionary_dump_path == ""
        or (
            isinstance(wiktionary_dump_path, str)
            and not Path(wiktionary_dump_path).exists()
        )
    ):
        dump_export_path = Path(output_dir)
        candidates = list(dump_export_path.glob(f"{wiktionary}*pages-articles.xml*"))
        candidates.extend(Path(".").glob(f"{wiktionary}*pages-articles.xml*"))
        if candidates:
            return max(candidates, key=lambda p: p.stat().st_mtime), iso

        import questionary

        from scribe_data.cli.download import download_wiktionary_dumps

        print(f"\nNo {wiktionary} dump found locally.")
        should_download = questionary.select(
            f"Would you like to download the latest {wiktionary} dump?",
            choices=["Yes", "No"],
            default="Yes",
        ).ask()

        if should_download == "Yes":
            downloaded_path = download_wiktionary_dumps(
                output_dir=output_dir,
                language_isos=[iso],
                dump_snapshot="latest",
            )

            if downloaded_path and Path(downloaded_path).exists():
                return Path(downloaded_path), iso

        print(
            f"Failed to automatically download {wiktionary}. You can manually download from "
            f"https://dumps.wikimedia.org/{wiktionary}/ and save to output "
            f"directory or pass path to the file via --wiktionary-dump-path."
        )
        return None, iso

    # Explicit path provided and exists.
    spec_path = Path(wiktionary_dump_path)
    if spec_path.exists():
        if match := re.search(r"^([a-z]{2,3})wiktionary-", spec_path.name):
            iso = match[1]
        return spec_path.resolve(), iso

    print(f"Wiktionary dump not found: {spec_path}")
    return None, iso


def _get_output_subdir(lang_name: str, language_metadata: dict) -> str:
    """
    Return the output subdirectory for a language (e.g. ``'german'`` or ``'chinese/mandarin'``).

    Parameters
    ----------
    lang_name : str
        The source language name.

    language_metadata : dict
        Language metadata dict containing main languages and their sub-languages.

    Returns
    -------
    str
        Subdirectory path where translation JSON files should be saved.
    """
    lang_lower = lang_name.lower()
    for main_lang, data in language_metadata.items():
        if main_lang.lower() == lang_lower:
            return lang_lower.replace(" ", "_")

        if "sub_languages" in data:
            for sub in data["sub_languages"]:
                if sub.lower() == lang_lower:
                    return f"{main_lang}/{sub}".replace(" ", "_")

    return lang_lower.replace(" ", "_")
