# SPDX-License-Identifier: GPL-3.0-or-later
"""
Parse translations from raw English Wiktionary XML dump.

Extracts translations for a target language from enwiktionary pages-articles dump.
Pure Python with XML and regex/template parsing. No external linguistic tooling.
"""

import bz2
import os
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from scribe_data.wiktionary.parse_constants import (
    IGNORED_TRANSLATION_PREFIXES,
    IGNORED_TRANSLATION_STRINGS,
    POS_HEADER_RE,
    T_NAMED_RE,
    T_TEMPLATE_RE,
    TRANS_BOTTOM_RE,
    TRANS_TOP_RE,
    TRANSLATIONS_HEADER_RE,
    _normalize_pos,
)


def _extract_source_lang_section(wikitext: str, source_lang_name: str) -> Optional[str]:
    """Extract the ==Language== section content."""
    header = f"=={source_lang_name}=="
    start = wikitext.find(header)
    if start == -1:
        # Fallback for spacing deviations "== Language =="
        start = wikitext.find(f"== {source_lang_name} ==")
        if start == -1:
            return None
        start += len(source_lang_name) + 6
    else:
        start += len(header)

    next_header = wikitext.find("\n==", start)
    while next_header != -1:
        # Check if the next header is a root block like \n==Language== (using exactly 2 equals)
        if next_header + 3 < len(wikitext) and wikitext[next_header + 3] != "=":
            return wikitext[start:next_header].strip()
        next_header = wikitext.find("\n==", next_header + 1)

    return wikitext[start:].strip()


def _split_pos_sections(content: str) -> List[Tuple[str, str]]:
    """Split content into (pos_header, section_text) pairs."""
    sections: List[Tuple[str, str]] = []
    pos_matches = list(POS_HEADER_RE.finditer(content))
    for i, m in enumerate(pos_matches):
        pos_name = m.group(1).strip()
        start = m.end()
        end = pos_matches[i + 1].start() if i + 1 < len(pos_matches) else len(content)
        section_text = content[start:end].strip()
        sections.append((pos_name, section_text))
    return sections


def _extract_translations_subsection(section_text: str) -> Optional[str]:
    """Find ====Translations==== and return its content up to next ====."""
    match = TRANSLATIONS_HEADER_RE.search(section_text)
    if not match:
        return None
    start = match.end()
    next_eq = re.search(r"\n====+\s", section_text[start:])
    end = start + next_eq.start() if next_eq else len(section_text)
    return section_text[start:end].strip()


def _parse_trans_blocks(trans_text: str) -> List[Tuple[str, str]]:
    """
    Parse trans-top/trans-bottom blocks. Returns [(description, block_content)].
    """
    blocks: List[Tuple[str, str]] = []
    top_matches = list(TRANS_TOP_RE.finditer(trans_text))
    for i, top_m in enumerate(top_matches):
        desc = ""
        if "|" in top_m.group(0):
            pipe = top_m.group(0).find("|") + 1
            end_brace = top_m.group(0).rfind("}}")
            desc = top_m.group(0)[pipe:end_brace].strip()
            desc = re.sub(r"^['\d.]+\s*", "", desc)
            desc = re.sub(r"''+", "", desc).strip()
        content_start = top_m.end()
        content_end = (
            TRANS_BOTTOM_RE.search(trans_text[content_start:]).start() + content_start
            if TRANS_BOTTOM_RE.search(trans_text[content_start:])
            else len(trans_text)
        )
        block_content = trans_text[content_start:content_end]
        blocks.append((desc, block_content))
    return blocks


def _extract_templates_from_block(
    block_content: str, target_langs: Optional[frozenset]
) -> Dict[str, List[str]]:
    """Extract translation words from templates. Returns {target_code: [words]}."""
    words_by_lang: Dict[str, List[str]] = {}
    for regex in (T_TEMPLATE_RE, T_NAMED_RE):
        for m in regex.finditer(block_content):
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


# MARK: Core Extraction


def _parse_page_translations(
    wikitext: str,
    target_langs: Optional[frozenset],
    word: str,
    source_lang_name: str = "English",
) -> Dict[str, Dict[str, Dict[str, Dict[str, str]]]]:
    """
    Parse a single page's wikitext.
    Returns {target_code: {pos: {sense_idx: {description, translation}}}}.
    """
    result: Dict[str, Dict[str, Dict[str, Dict[str, str]]]] = {}
    lang_section = _extract_source_lang_section(wikitext, source_lang_name)
    if not lang_section:
        return result

    for pos_header, section_text in _split_pos_sections(lang_section):
        trans_section = _extract_translations_subsection(section_text)
        if not trans_section:
            continue

        pos = _normalize_pos(pos_header)
        blocks = _parse_trans_blocks(trans_section)
        for sense_idx, (desc, block) in enumerate(blocks, start=1):
            words_by_lang = _extract_templates_from_block(block, target_langs)
            for code, words in words_by_lang.items():
                if words:
                    if code not in result:
                        result[code] = {}
                    if pos not in result[code]:
                        result[code][pos] = {}
                    result[code][pos][str(sense_idx)] = {
                        "description": desc,
                        "translation": ", ".join(words),
                    }

    return result


def _parse_page_worker(
    args: Tuple[str, str, Optional[frozenset], str],
) -> Optional[Tuple[str, Dict[str, Dict[str, Dict[str, Dict[str, str]]]]]]:
    """
    Worker function for parsing a single Wiktionary page.

    Applies the same filtering as the main loop and returns (word, parsed)
    or None if the page should be skipped or has no translations.
    """
    word, text, target_langs, source_lang_name = args
    if not word or not text:
        return None

    parsed = _parse_page_translations(text, target_langs, word, source_lang_name)
    if not parsed:
        return None

    return word, parsed


def _iter_dump_pages(dump_path: Path):
    """Yield (title, text) for each page in the XML dump."""
    import shutil
    import subprocess

    proc = None
    if str(dump_path).endswith(".bz2") and shutil.which("bzcat"):
        proc = subprocess.Popen(["bzcat", str(dump_path)], stdout=subprocess.PIPE)
        f = proc.stdout
    else:
        open_fn = bz2.open if str(dump_path).endswith(".bz2") else open
        f = open_fn(dump_path, "rb")

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
    dump_path: Union[str, Path],
    target_lang_codes: Optional[List[str]],
    *,
    source_lang_name: str = "English",
    progress: bool = True,
    num_workers: Optional[int] = None,
) -> Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, str]]]]]:
    """
    Parse wiktionary XML dump and extract translations for target languages.

    Parameters
    ----------
    dump_path : str or Path
        Path to enwiktionary-*-pages-articles.xml.bz2
    target_lang_codes : list of str or None
        ISO codes of target languages (e.g. ["de", "fr"]). If None, extracts all.
    progress : bool, default=True
        Show progress bar

    Returns
    -------
    dict
        {target_code: {word: {pos: {sense_idx: {description, translation}}}}}
    """
    from tqdm import tqdm

    path = Path(dump_path)
    if not path.exists():
        raise FileNotFoundError(f"Wiktionary dump not found: {path}")

    output: Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, str]]]]] = {}

    # Determine worker count: allow override via env, otherwise use all but one core.
    if num_workers is None:
        import os

        env_workers = os.getenv("SCRIBE_WIKTIONARY_WORKERS")
        if env_workers:
            try:
                num_workers = max(1, int(env_workers))
            except ValueError:
                num_workers = None
        if num_workers is None:
            cpu_count = os.cpu_count() or 1
            num_workers = max(1, cpu_count - 1)

    iterator = _iter_dump_pages(path)

    # Calculate estimated total entries (Wiktionary averages ~180 bytes/page compressed)
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
        for title, text in iterator:
            if not title or not text:
                continue
            # Allow translations subpages safely through the namespace filter
            if ":" in title and not title.startswith("Appendix:"):
                continue

            word = title.strip().lower()
            if not word or not word[0].isalnum():
                continue

            # Fast string pre-filter to drop the vast majority of pages avoiding costly Regex and IPC overhead
            if "translation" not in text and "Translation" not in text:
                continue

            # Re-map delegated translation subpages back to their base words
            # (e.g., "book/translations" merges seamlessly into "book").
            if word.endswith("/translations"):
                word = word[:-13]

            yield word, text, target_langs_frozenset, source_lang_name

    # Single-process fallback (e.g. for debugging or constrained environments)
    if num_workers == 1:
        try:
            for word, text, tgt_langs, src_lang in _filtered_iterator():
                parsed = _parse_page_translations(text, tgt_langs, word, src_lang)
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
                _parse_page_worker, _filtered_iterator(), chunksize=100
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
    Extract translations from enwiktionary XML dump for target languages.

    Parameters
    ----------
    target_languages : str or list of str, optional
        Language(s) to extract (e.g. "de", "german"). If None or "all", extracts all languages.
    wiktionary_dump_path : str or Path, optional
        Path to enwiktionary-*-pages-articles.xml.bz2
    output_dir : str, optional
        Base output directory
    overwrite : bool, default=False
        Overwrite existing files
    """
    import orjson

    from scribe_data.utils import (
        DEFAULT_DUMP_EXPORT_DIR,
        DEFAULT_JSON_EXPORT_DIR,
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
                for sub_info in lang_info["sub_languages"].values():
                    if "iso" in sub_info:
                        target_isos.append(sub_info["iso"])
    else:
        if isinstance(target_languages, str):
            target_languages = [target_languages]

        for lang_spec in target_languages:
            iso = resolve_lang_iso(lang_spec)
            if not iso:
                print(f"Warning: Unknown language '{lang_spec}', skipping.")
                continue
            target_isos.append(iso)
        if not target_isos:
            return

    dump_path, source_iso = _resolve_dump_path(
        wiktionary_dump_path,
        DEFAULT_DUMP_EXPORT_DIR,
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


# MARK: Dump Resolution


def _resolve_dump_path(
    spec: Optional[Union[str, Path]], output_dir: str
) -> Tuple[Optional[Path], str]:
    """Resolve path to wiktionary XML dump and return its source ISO."""
    from scribe_data.utils import resolve_lang_iso

    iso = "en"
    if isinstance(spec, str) and not Path(spec).exists():
        if resolved := resolve_lang_iso(spec):
            iso = resolved
        elif spec.endswith("wiktionary"):
            iso = spec.replace("wiktionary", "")

    prefix = f"{iso}wiktionary"

    if (
        spec is None
        or spec == ""
        or (isinstance(spec, str) and not Path(spec).exists())
    ):
        base = Path(output_dir)
        candidates = list(base.glob(f"{prefix}-*-pages-articles.xml*"))
        candidates.extend(Path(".").glob(f"{prefix}-*-pages-articles.xml*"))
        if candidates:
            return max(candidates, key=lambda p: p.stat().st_mtime), iso
        print(
            f"No {prefix} dump found. Download from "
            f"https://dumps.wikimedia.org/{prefix}/ and save to output "
            f"directory or pass path via --wiktionary-dump-path."
        )
        return None, iso

    # If explicit path matches exactly
    spec_path = Path(spec)
    if spec_path.exists():
        match = re.search(r"^([a-z]{2,3})wiktionary-", spec_path.name)
        if match:
            iso = match.group(1)
        return spec_path.resolve(), iso

    print(f"Wiktionary dump not found: {spec_path}")
    return None, iso


def _get_output_subdir(lang_name: str, language_metadata: dict) -> str:
    """Get output subdir (e.g. 'german' or 'chinese/mandarin')."""
    lang_lower = lang_name.lower()
    for main_lang, data in language_metadata.items():
        if main_lang.lower() == lang_lower:
            return lang_lower.replace(" ", "_")
        if "sub_languages" in data:
            for sub, _ in data["sub_languages"].items():
                if sub.lower() == lang_lower:
                    return f"{main_lang}/{sub}".replace(" ", "_")
    return lang_lower.replace(" ", "_")
