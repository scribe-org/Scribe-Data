# SPDX-License-Identifier: GPL-3.0-or-later
"""
Parse translations for a target language from a Wiktionary pages-articles dump.
"""

import bz2
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from scribe_data.wiktionary.parse_constants import (
    HEADER_RE,
    IGNORED_TRANSLATION_PREFIXES,
    IGNORED_TRANSLATION_STRINGS,
    T_NAMED_RE,
    T_TEMPLATE_RE,
    TRANS_BOTTOM_RE,
    TRANS_TOP_RE,
    _normalize_pos,
)

# MARK: Parse Page


def _extract_source_lang_section(wikitext: str, source_lang_name: str) -> Optional[str]:
    """
    Extract the =={Language}== section content.

    Parameters
    ----------
    wikitext : str
        The wikitext for the given Wiktionary page.

    source_lang_name : str
        The language that is being translated from.

    Returns
    -------
    Optional[str]
        The =={Language}== section of the wikitext page if there is one.
    """
    header = f"=={source_lang_name}=="
    start = wikitext.find(header)
    if start == -1:
        # Fallback for spacing deviations "== {Language} ==".
        start = wikitext.find(f"== {source_lang_name} ==")
        if start == -1:
            return None

        start += len(source_lang_name) + 6

    else:
        start += len(header)

    next_header = wikitext.find("\n==", start)
    while next_header != -1:
        # Check if the next header is a root block like \n=={Language}== (using exactly 2 equals).
        if next_header + 3 < len(wikitext) and wikitext[next_header + 3] != "=":
            return wikitext[start:next_header].strip()

        next_header = wikitext.find("\n==", next_header + 1)

    return wikitext[start:].strip()


def _parse_translation_blocks(translation_text: str) -> List[Tuple[str, str]]:
    """
    Parse trans-top/trans-bottom blocks for descriptions and block content.

    Parameters
    ----------
    translation_text : str
        The translation section of a wikitext page within trans-top/trans-bottom blocks.

    Returns
    -------
    List[Tuple[str, str]]
        A list of (description, block_content) tuples for translations.
    """
    blocks: List[Tuple[str, str]] = []
    top_matches = list(TRANS_TOP_RE.finditer(translation_text))
    for i, top_m in enumerate(top_matches):
        desc = ""
        if "|" in top_m.group(0):
            pipe = top_m.group(0).find("|") + 1
            end_brace = top_m.group(0).rfind("}}")
            desc = top_m.group(0)[pipe:end_brace].strip()
            desc = re.sub(r"^['\d.]+\s*", "", desc)
            desc = re.sub(r"''+", "", desc).strip()

        content_start = top_m.end()

        # If a Wiktionary contributor forgot to close the first Translation block with
        # {{trans-bottom}}, the code will default to the end of the text. This wrongly
        # ingests all subsequent blocks, causing them to be parsed and duplicated again.
        bottom_m = TRANS_BOTTOM_RE.search(translation_text, content_start)
        next_top_start = (
            top_matches[i + 1].start()
            if i + 1 < len(top_matches)
            else len(translation_text)
        )
        if bottom_m and bottom_m.start() <= next_top_start:
            content_end = bottom_m.start()

        else:
            content_end = next_top_start

        block_content = translation_text[content_start:content_end]
        blocks.append((desc, block_content))

    return blocks


def _extract_templates_from_block(
    translation_block_content: str, target_langs: Optional[frozenset]
) -> Dict[str, List[str]]:
    """
    Extract translation words from wikitext templates.

    Parameters
    ----------
    translation_block_content : str
        The unparsed translation block of the wikitext page.

    target_langs : Optional[frozenset]
        The languages that translations should be returned for.

    Returns
    -------
    Dict[str, List[str]]
        A dictionary of translations for the Wiktionary word ({target_lang_code: [words]}).
    """
    words_by_lang: Dict[str, List[str]] = {}
    for regex in (T_TEMPLATE_RE, T_NAMED_RE):
        for m in regex.finditer(translation_block_content):
            code = m.group(1).lower()
            word = m.group(2).strip()
            tags_matched = m.group(3)

            if (not target_langs or code in target_langs) and word:
                word_lower = word.lower()
                if word_lower in IGNORED_TRANSLATION_STRINGS or word_lower.startswith(
                    IGNORED_TRANSLATION_PREFIXES
                ):
                    continue

                word = re.sub(r"\[\[[^|\]]+\|([^\]]+)\]\]", r"\1", word)
                word = re.sub(r"\[\[([^\]]+)\]\]", r"\1", word)
                word = re.sub(r"\{\{[^}]+\}\}", "", word).strip()

                # Trailing Grammatical Tag Extraction:
                # Wiktionary translation templates often contain crucial grammatical attributes
                # trailing the actual word (e.g., {{t|de|Mädchen|n}} where 'n' = Neuter).
                # Rather than throwing these tags away, we isolate all trailing variables captured by Group 3.
                # We strip out noise tags (scripts, transliterations like 'tr=') and dynamically
                # extract valid explicit flags like 'g=n' down to 'n'.
                # Finally, we append these explicitly mapped attributes uniquely to the extracted word string.
                if tags_matched:
                    valid_tags = []
                    for t in tags_matched.split("|"):
                        t = t.strip()
                        if not t:
                            continue

                        if t.startswith(("g=", "g2=", "g3=")):
                            valid_tags.append(t.split("=", 1)[1])

                        elif (
                            "=" not in t
                            and t.lower() not in IGNORED_TRANSLATION_STRINGS
                        ):
                            valid_tags.append(t)

                    if valid_tags:
                        valid_tags = list(dict.fromkeys(valid_tags))
                        word = f"{word} ({', '.join(valid_tags)})"

                if word and len(word) < 200:
                    if code not in words_by_lang:
                        words_by_lang[code] = []
                    words_by_lang[code].append(word)

    return words_by_lang


# MARK: Extract Translations


def _parse_page_translations(
    source_lang_name: str,
    target_langs: Optional[frozenset],
    wikitext: str,
    word: str,
) -> Dict[str, Dict[str, Dict[str, Dict[str, str]]]]:
    """
    Parse a single Wiktionary page's wikitext.

    Parameters
    ----------
    source_lang_name : str
        The language that is being translated from.

    target_langs : Optional[frozenset]
        The languages that translations should be returned for.

    wikitext : str
        The wikitext for the given Wiktionary page.

    word : str
        The word in Wiktionary that's being translated.

    Returns
    -------
    Dict[str, Dict[str, Dict[str, Dict[str, str]]]]
        A dictionary of translations for the given word {target_code: {pos: {sense_idx: {description, translation}}}}).
    """
    result: Dict[str, Dict[str, Dict[str, Dict[str, str]]]] = {}
    lang_section = _extract_source_lang_section(
        wikitext=wikitext, source_lang_name=source_lang_name
    )
    if not lang_section:
        return result

    current_pos = "other"
    pos_sense_tracker: Dict[str, int] = {}

    headers = list(HEADER_RE.finditer(lang_section))

    for i, match in enumerate(headers):
        # Wiktionary often shifts Part of Speech headers from Level-3 (===Noun===)
        # to Level-4 (====Noun====) if multiple Etymology sections exist.
        # The HEADER_RE regex isolates the header string regardless of the number of equals signs,
        # so this logic seamlessly handles arbitrary Part of Speech header depths.
        header_text = match.group(2).strip()
        header_lower = header_text.lower()

        start = match.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(lang_section)
        content = lang_section[start:end]

        if header_lower == "translations":
            blocks = _parse_translation_blocks(content)

            if current_pos not in pos_sense_tracker:
                pos_sense_tracker[current_pos] = 0

            for desc, block in blocks:
                words_by_lang = _extract_templates_from_block(block, target_langs)

                if any(words for words in words_by_lang.values() if words):
                    pos_sense_tracker[current_pos] += 1
                    sense_idx_str = str(pos_sense_tracker[current_pos])

                    for code, words in words_by_lang.items():
                        if words:
                            if code not in result:
                                result[code] = {}
                            if current_pos not in result[code]:
                                result[code][current_pos] = {}
                            result[code][current_pos][sense_idx_str] = {
                                "description": desc,
                                "translation": ", ".join(words),
                            }

        else:
            mapped = _normalize_pos(header_text)
            if mapped != header_lower.replace(" ", "_") or header_lower in [
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
                "proper noun",
                "proper name",
            ]:
                current_pos = mapped

    return result


# MARK: Parse Dump


def _parse_page_worker(
    args: Tuple[str, str, Optional[frozenset], str],
) -> Optional[Tuple[str, Dict[str, Dict[str, Dict[str, Dict[str, str]]]]]]:
    """
    Parse a single Wiktionary page via a worker that chunks the page.

    Applies the same filtering as the main loop and returns (word, parsed)
    or None if the page should be skipped or has no translations.

    Parameters
    ----------
    args : Tuple[str, str, Optional[frozenset], str]
        The word, wikitext, target languages and source languages for page parsing.

    Returns
    -------
    Optional[Tuple[str, Dict[str, Dict[str, Dict[str, Dict[str, str]]]]]]
        The parsed translations from the given Wiktionary page.
    """
    word, wikitext, target_langs, source_lang_name = args
    if not word or not wikitext:
        return None

    parsed = _parse_page_translations(
        source_lang_name=source_lang_name,
        target_langs=target_langs,
        wikitext=wikitext,
        word=word,
    )

    return (word, parsed) if parsed else None


def _iter_dump_pages(wiktionary_dump_path: Path):
    """
    Yield (title, text) for each page in the XML dump.

    Parameters
    ----------
    wiktionary_dump_path : Path
        Path to a *wiktionary-*-pages-articles.xml.bz2 dump file.
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
        context = ET.iterparse(f, events=("start", "end"))
        context = iter(context)
        try:
            _, root = next(context)

        except StopIteration:
            return

        for event, elem in context:
            if event == "end":
                tag = elem.tag
                ns = tag[: tag.rfind("}") + 1] if "}" in tag else ""
                tag_name = tag[tag.rfind("}") + 1 :] if "}" in tag else tag

                if tag_name == "page":
                    title_elem = elem.find(f"{ns}title")
                    rev = elem.find(f"{ns}revision")
                    text = ""
                    if rev is not None:
                        text_elem = rev.find(f"{ns}text")
                        if text_elem is not None and text_elem.text:
                            text = text_elem.text

                    title = title_elem.text if title_elem is not None else ""
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
    progress: bool = True,
    num_workers: Optional[int] = None,
) -> Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, str]]]]]:
    """
    Parse wiktionary XML dump and extract translations for target languages.

    Parameters
    ----------
    wiktionary_dump_path : str or Path
        Path to a *wiktionary-*-pages-articles.xml.bz2 dump file.

    target_lang_codes : list of str or None
        ISO codes of target languages (e.g. ["de", "fr"]). If None, extracts all.

    source_lang_name : str
        The language that is being translated from.

    progress : bool, default=True
        Whether to show a progress bar.

    num_workers : Optional[int]
        The number of workers to use for translation parsing.

    Returns
    -------
    dict
        Translations for the source language ({target_code: {word: {pos: {sense_idx: {description, translation}}}}}).
    """
    from tqdm import tqdm

    path = Path(wiktionary_dump_path)
    if not path.exists():
        raise FileNotFoundError(f"Wiktionary dump not found: {path}")

    output: Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, str]]]]] = {}

    # Determine worker count: allow override via env, otherwise use all but one core.
    if num_workers is None:
        import os

        cpu_count = os.cpu_count() or 1
        num_workers = max(1, cpu_count - 1)

    iterator = _iter_dump_pages(path)

    # Calculate estimated total entries (Wiktionary averages ~180 bytes/page compressed).
    try:
        total_entries = path.stat().st_size // 180

    except (OSError, AttributeError):
        total_entries = None

    if progress:
        from tqdm import tqdm

        iterator = tqdm(
            iterator, total=total_entries, desc="Parsing Wiktionary", unit="pages"
        )

    target_langs_frozenset = (
        frozenset(c.lower() for c in target_lang_codes) if target_lang_codes else None
    )

    def _filtered_iterator():
        """
        Iterate over a wikitext page.
        """
        for title, text in iterator:
            if not title or not text:
                continue

            # Allow translations for subpages safely through the namespace filter.
            if ":" in title and not title.startswith("Appendix:"):
                continue

            word = title.strip().lower()
            if not word or not word[0].isalnum():
                continue

            # Fast string pre-filter to drop the vast majority of pages avoiding costly Regex and IPC overhead
            if "translation" not in text and "Translation" not in text:
                continue

            # Skips pages that mention "translation" in prose but have no actual translation templates.
            if "{{t" not in text and "{{T" not in text:
                continue

            # Re-map delegated translation subpages back to their base words
            # (e.g., "book/translations" merges seamlessly into "book").
            if word.endswith("/translations"):
                word = word[:-13]

            yield word, text, target_langs_frozenset, source_lang_name

    # Single-process fallback (e.g. for debugging or constrained environments).
    if num_workers == 1:
        try:
            for word, text, tgt_langs, src_lang in _filtered_iterator():
                parsed = _parse_page_translations(
                    source_lang_name=src_lang,
                    target_langs=tgt_langs,
                    wikitext=text,
                    word=word,
                )
                if not parsed:
                    continue

                for code, pos_senses in parsed.items():
                    if code not in output:
                        output[code] = {}

                    if word not in output[code]:
                        output[code][word] = {}

                    for pos, senses in pos_senses.items():
                        if pos not in output[code][word]:
                            output[code][word][pos] = {}

                        for sense_idx, data in senses.items():
                            output[code][word][pos][sense_idx] = data

        except KeyboardInterrupt:
            print("\nParsing cleanly interrupted by user. Saving progress...")

        return output

    # Multi-process parsing of pages
    try:
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            for result in executor.map(
                _parse_page_worker, _filtered_iterator(), chunksize=500
            ):
                if not result:
                    continue

                word, parsed = result
                for code, pos_senses in parsed.items():
                    if code not in output:
                        output[code] = {}

                    if word not in output[code]:
                        output[code][word] = {}

                    for pos, senses in pos_senses.items():
                        if pos not in output[code][word]:
                            output[code][word][pos] = {}

                        for sense_idx, data in senses.items():
                            output[code][word][pos][sense_idx] = data

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
    Extract translations from a Wiktionary XML dump for target languages.

    Parameters
    ----------
    target_languages : str or list of str, optional
        Language(s) to extract (e.g. "de", "german"). If None or "all", extracts all languages.

    wiktionary_dump_path : str or Path, optional
        Path to a *wiktionary-*-pages-articles.xml.bz2 dump file.

    output_dir : str, optional
        The directory to save the extracted translations.

    overwrite : bool, default=False
        Overwrite existing files.
    """
    import orjson

    from scribe_data.utils import (
        DEFAULT_JSON_EXPORT_DIR,
        DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR,
        check_index_exists,
        get_language_from_iso,
        language_metadata,
        resolve_lang_iso,
    )

    output_dir = output_dir or DEFAULT_JSON_EXPORT_DIR
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    target_isos = []
    if not target_languages:
        for lang_info in language_metadata.values():
            if "iso" in lang_info:
                target_isos.append(lang_info["iso"])

            if "sub_languages" in lang_info:
                target_isos.extend(
                    sub_info["iso"]
                    for sub_info in lang_info["sub_languages"].values()
                    if "iso" in sub_info
                )

    else:
        if isinstance(target_languages, str):
            target_languages = [target_languages]

        for lang_spec in target_languages:
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
        dump_path, target_isos, source_lang_name=source_lang_name
    )

    for iso, data in data_by_lang.items():
        out_path = base_out_path / f"{iso}_translations_from_{source_iso}.json"

        if not overwrite and check_index_exists(out_path, overwrite_all=overwrite):
            print(f"Skipping {iso}: '{out_path}' already exists.")
            continue

        with open(out_path, "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

        print(f"Exported {iso} translations from {source_iso} to {out_path}")


# MARK: Output Resolution


def _resolve_dump_path(
    wiktionary_dump_path: Optional[Union[str, Path]], output_dir: str
) -> Tuple[Optional[Path], str]:
    """
    Resolve path to wiktionary XML dump and return its source ISO.

    Parameters
    ----------
    wiktionary_dump_path : Optional[Union[str, Path]]
        Path to a *wiktionary-*-pages-articles.xml.bz2 dump file.

    output_dir : str
        The directory to save the extracted translations.

    Returns
    -------
    Tuple[Optional[Path], str]
        The path to the dump to parse.
    """
    from scribe_data.utils import resolve_lang_iso

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
        # Note: The snapshot is not included in the filename so Scribe-Server always looks for one file.
        candidates = list(dump_export_path.glob(f"{wiktionary}-pages-articles.xml*"))
        candidates.extend(Path(".").glob(f"{wiktionary}-pages-articles.xml*"))
        if candidates:
            return max(candidates, key=lambda p: p.stat().st_mtime), iso

        print(
            f"No {wiktionary} dump found. Download from "
            f"https://dumps.wikimedia.org/{wiktionary}/ and save to output "
            f"directory or pass path to the file via --wiktionary-dump-path."
        )
        return None, iso

    # If explicit path matches exactly.
    spec_path = Path(wiktionary_dump_path)
    if spec_path.exists():
        if match := re.search(r"^([a-z]{2,3})wiktionary-", spec_path.name):
            iso = match[1]

        return spec_path.resolve(), iso

    print(f"Wiktionary dump not found: {spec_path}")
    return None, iso


def _get_output_subdir(lang_name: str, language_metadata: dict) -> str:
    """
    Get output subdir (e.g. 'german' or 'chinese/mandarin').

    Parameters
    ----------
    lang_name : str
        A target language that translations are being derived for.

    language_metadata : dict
        The metadata containing information about main languages and their sub-languages.

    Returns
    -------
    str
        The subdirectory where translations should be saved.
    """
    lang_lower = lang_name.lower()
    for main_lang, data in language_metadata.items():
        if main_lang.lower() == lang_lower:
            return lang_lower.replace(" ", "_")

        if "sub_languages" in data:
            for sub, _ in data["sub_languages"].items():
                if sub.lower() == lang_lower:
                    return f"{main_lang}/{sub}".replace(" ", "_")

    return lang_lower.replace(" ", "_")
