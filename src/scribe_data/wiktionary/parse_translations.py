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

from tqdm import tqdm

from scribe_data.wiktionary.parse_constants import get_wiktionary_config

# A single translation entry (e.g., {"description": "...", "translation": "..."})
TranslationEntry = Dict[str, str]

# Maps a sense index (e.g., "1") to its translation entry
SensesToTranslations = Dict[str, TranslationEntry]

# Maps a Part of Speech (e.g., "noun") to its senses
PosToSenses = Dict[str, SensesToTranslations]

# Maps a source word to its parts of speech
WordToPos = Dict[str, PosToSenses]

# Maps a target language ISO to the translated words
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
    Build a sense entry dict, leaving out the description key if it's empty.

    Parameters
    ----------
    description : str
        Gloss or meaning for the sense.

    translation : str
        Comma-joined translation word(s).

    Returns
    -------
    Dict[str, str]
        ``{"translation": ...}`` or ``{"description": ..., "translation": ...}``.
    """
    entry: Dict[str, str] = {}
    if description:
        entry["description"] = description

    entry["translation"] = translation

    return entry


def _extract_translation_word(
    node,
    code: str,
    raw_word: str,
    config: dict,
    target_langs: Optional[frozenset],
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
    desc: str,
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

    desc : str
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
            _build_sense_entry(desc, ", ".join(words))
        )


# MARK: Parse Page


def _extract_source_lang_section(wikitext: str, config: dict) -> Optional[str]:
    """
    Return the wikitext content of the source-language section.

    Handles both English-style ``=={Language}==`` headers and German-style
    ``== Word ({{Sprache|Deutsch}}) ==`` headers.

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
    # German Wiktionary uses headers like "== Hallo ({{Sprache|Deutsch}}) ==".
    if config.get("lang_header_pattern"):
        pattern = config["lang_header_pattern"]
        for line_match in re.finditer(r"^==([^=\n]+)==\s*$", wikitext, re.MULTILINE):
            if pattern.search(line_match.group(1)):
                start = line_match.end()
                next_h2 = re.search(r"^==[^=]", wikitext[start:], re.MULTILINE)
                end = start + next_h2.start() if next_h2 else len(wikitext)
                return wikitext[start:end].strip()

        return None

    # English Wiktionary: exact header name.
    source_lang_name = config.get("lang_header")
    if not source_lang_name:
        return None

    header = f"=={source_lang_name}=="
    start = wikitext.find(header)
    if start == -1:
        # Also try the spaced variant "== {Language} ==".
        padded = f"== {source_lang_name} =="
        start = wikitext.find(padded)
        if start == -1:
            return None
        start += len(padded)

    else:
        start += len(header)

    next_header = wikitext.find("\n==", start)
    while next_header != -1:
        if next_header + 3 < len(wikitext) and wikitext[next_header + 3] != "=":
            return wikitext[start:next_header].strip()

        next_header = wikitext.find("\n==", next_header + 1)

    return wikitext[start:].strip()


# MARK: Engine: ast_u_tabelle


def _parse_ast_u_tabelle(
    config: dict,
    target_langs: Optional[frozenset],
    wikitext: str,
    word: str,  # noqa: ARG001  (kept for uniform signature)
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

    word : str
        The source word on the page (unused, kept for a uniform signature).

    Returns
    -------
    Dict[str, PosToSenses]
        ``{target_lang_iso: {pos: {sense_idx: {description?, translation}}}}``.
    """
    import mwparserfromhell

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
        # Update the current POS whenever we hit a heading with a Wortart template.
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

            desc = str(node.get("G").value).strip() if node.has("G") else ""

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
                result, current_pos, pos_sense_tracker, words_by_lang, desc
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


# MARK: Engine: ast_trans_top


def _parse_ast_trans_top(
    config: dict,
    target_langs: Optional[frozenset],
    wikitext: str,
    word: str,  # noqa: ARG001
) -> Dict[str, PosToSenses]:
    """
    Parse translations from a single page using the ``trans-top`` / ``trans-bottom`` format.

    Parameters
    ----------
    config : dict
        Wiktionary config for the source language edition.

    target_langs : Optional[frozenset]
        ISO codes of languages to extract, or None for all.

    wikitext : str
        Raw wikitext of the Wiktionary page.

    word : str
        The source word on the page (unused, kept for a uniform signature).

    Returns
    -------
    Dict[str, PosToSenses]
        ``{target_lang_iso: {pos: {sense_idx: {description?, translation}}}}``.
    """
    import mwparserfromhell

    result: Dict[str, PosToSenses] = {}

    lang_section = _extract_source_lang_section(wikitext=wikitext, config=config)
    if not lang_section:
        return result

    pos_map: dict = config.get("pos_map", {})

    template_top = frozenset(
        config.get("template_top", ["trans-top", "trans-top-also", "checktrans-top"])
    )
    template_bottom: str = config.get("template_bottom", "trans-bottom")
    template_t_list = frozenset(
        config.get("template_translation", ["t", "t+", "t-check", "tt", "tt+"])
    )

    wikicode = mwparserfromhell.parse(lang_section)

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
                result,
                current_pos,
                pos_sense_tracker,
                current_words_by_lang,
                current_desc,
            )
        current_words_by_lang = {}
        current_desc = ""
        in_translation_block = False

    for node in wikicode.nodes:
        if isinstance(node, mwparserfromhell.nodes.Heading):
            if in_translation_block:
                _commit_block()

            header_text = str(node.title).strip().lower()

            # Some editions (e.g. French) put a template in the heading: `=== {{S|nom|fr}} ===`.
            for t in node.title.filter_templates():
                if t.has(1):
                    tval = str(t.get(1).value).strip().lower()
                    if tval in pos_map:
                        header_text = tval

            mapped = pos_map.get(header_text, header_text.replace(" ", "_"))
            if mapped in _KNOWN_POS or mapped != header_text.replace(" ", "_"):
                current_pos = mapped

        elif isinstance(node, mwparserfromhell.nodes.Template):
            tname = node.name.strip().lower()

            # Support languages (like Indonesian) that set POS via short templates (e.g., {{-n-}}) instead of Headings.
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
                    # strip_code removes mediawiki italics/bold markup.
                    desc = str(node.get(1).value.strip_code()).strip()
                    desc = re.sub(r"^[\d.]+\s*", "", desc).strip()
                    current_desc = desc

            elif tname == template_bottom:
                _commit_block()

            elif in_translation_block and tname in template_t_list:
                if not (node.has(1) and node.has(2)):
                    continue

                code = str(node.get(1).value).strip().lower()

                # strip_code strips wikilinks like [[link]] while keeping the visible text.
                raw_word = str(node.get(2).value.strip_code()).strip()

                extracted = _extract_translation_word(
                    node, code, raw_word, config, target_langs
                )
                if extracted:
                    current_words_by_lang.setdefault(code, []).append(extracted)

    # Flush any block that wasn't closed by a trans-bottom.
    if in_translation_block:
        _commit_block()

    return result


# MARK: Engine Dispatch

_ENGINES: Dict[str, callable] = {
    "ast_u_tabelle": _parse_ast_u_tabelle,
    "ast_trans_top": _parse_ast_trans_top,
    "regex_trans_top": _parse_ast_trans_top,  # kept for backwards compatibility with old configs
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
        config=config,
        target_langs=target_langs,
        wikitext=wikitext,
        word=word,
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


def _iter_dump_pages(wiktionary_dump_path: Path):
    """
    Yield ``(title, text)`` for each page in the XML dump.

    Parameters
    ----------
    wiktionary_dump_path : Path
        Path to a ``*wiktionary-*-pages-articles.xml.bz2`` dump file.
    """
    import shutil
    import subprocess

    proc = None
    if str(wiktionary_dump_path).endswith(".bz2") and shutil.which("bzcat"):
        proc = subprocess.Popen(
            ["bzcat", str(wiktionary_dump_path)], stdout=subprocess.PIPE
        )
        f = proc.stdout
    else:
        open_fn = bz2.open if str(wiktionary_dump_path).endswith(".bz2") else open
        f = open_fn(wiktionary_dump_path, "rb")

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
    *,
    source_lang_name: str,
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

    source_lang_name : str
        The language being translated from.

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

    iterator = _iter_dump_pages(path)

    # Rough page count estimate for the progress bar (Wiktionary ~180 bytes/page compressed).
    try:
        total_entries = path.stat().st_size // 180

    except (OSError, AttributeError):
        total_entries = None

    if progress:
        iterator = tqdm(
            iterator, total=total_entries, desc="Parsing Wiktionary", unit="pages"
        )

    target_langs_frozenset = (
        frozenset(c.lower() for c in target_lang_codes) if target_lang_codes else None
    )

    config = get_wiktionary_config(source_iso=source_iso)

    def _filtered_iterator():
        """
        Yield (word, text, target_langs, config) tuples, skipping pages that can't have translations.
        """
        for title, text in iterator:
            if not title or not text:
                continue

            # Allow translation subpages but skip all other namespaced titles.
            if ":" in title and not title.startswith("Appendix:"):
                continue

            word = title.strip().lower()
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

    try:
        if num_workers == 1:
            # Single-process path — handy for debugging or low-memory environments.
            for result in map(_parse_page_worker, _filtered_iterator()):
                if result:
                    _merge_parsed_into_output(output, *result)

        else:
            # Use a process pool for speed on large dumps.
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                for result in executor.map(
                    _parse_page_worker, _filtered_iterator(), chunksize=500
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
        source_lang_name=source_lang_name,
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
