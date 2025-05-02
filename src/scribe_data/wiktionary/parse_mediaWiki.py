# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to parse the translations of a word from MediaWiki API.
"""

import json
import re
from pathlib import Path

from scribe_data.utils import DEFAULT_MEDIAWIKI_EXPORT_DIR, get_language_from_iso
from scribe_data.wikidata.wikidata_utils import mediawiki_query


def fetch_translation_page(word: str):
    """
    Fetch the translation for a given word via the Wiktionary MediaWiki API.

    Parameters
    ----------
    word : str
        The word that a translation page should be retrieved for.

    Returns
    -------
    str
        The wikitext with the translations of the given word.
    """
    data = mediawiki_query(word=word)

    pages = data.get("query", {}).get("pages", {})
    # Extract page object from dictionary.
    page = next(iter(pages.values())) if pages else {}

    # Get the wikitext from the 'revisions' key.
    return page.get("revisions", [{}])[0].get("*", "")


def parse_wikitext_for_translations(wikitext: str):
    """
    Parse the wikitext line by line to extract translations, language codes, part of speech and context.

    Parameters
    ----------
    wikitext : str
        A string that contains translations.

    Returns
    -------
    dict
        A dictionary of translations from the wikitext page assigned as values to language keys.
    """
    translations_by_lang = {}
    current_part_of_speech = None  # track whether we are in Noun or Verb
    current_context = None  # track the current trans-top context

    # Split the wikitext into individual lines
    for line in wikitext.splitlines():
        # Detect part of speech/data-types: Noun or Verb.
        if line.startswith("===Noun==="):
            current_part_of_speech = "Noun"

        elif line.startswith("===Verb==="):
            current_part_of_speech = "Verb"

        if trans_top_match := re.match(r"\{\{trans-top\|(.+?)\}\}", line):
            current_context = trans_top_match[1].strip()

        if template_match := re.match(
            r"^\*\s([A-Za-z\s]+):\s\{\{t\+?\|([a-zA-Z\-]+)\|([^|]+)\}\}",
            line.strip(),
        ):
            lang_code = template_match[2].strip()
            translation_text = template_match[3].strip()

            # Ensure there's a list to hold translations for this language.
            if lang_code not in translations_by_lang:
                translations_by_lang[lang_code] = []

            translations_by_lang[lang_code].append(
                {
                    "translation": translation_text,
                    "part_of_speech": current_part_of_speech,
                    "context": current_context,
                }
            )

    return translations_by_lang


def build_json_format(word: str, translations_by_lang: dict):
    """
    Build the final JSON format for the translations of a word.

    Parameters
    ----------
    word : str
        The word to translate.

    translations_by_lang : dict
        Translations with languages as their keys.

    Returns
    -------
    dict
        Formatted translations.
    """
    book_translations = {word: {}}
    # Keep counters to number the translations for each (lang, part_of_speech).
    language_counters = {}

    for lang_code, entries in translations_by_lang.items():
        try:
            lang_name = get_language_from_iso(lang_code)

        except ValueError:
            # Skip this language if it's not supported.
            continue

        # Make sure this language is in the dictionary.
        if lang_name not in book_translations[word]:
            book_translations[word][lang_name] = {}

        for item in entries:
            pos = item["part_of_speech"] or "Unknown"
            desc = item["context"]
            trans = item["translation"]

            if pos not in book_translations[word][lang_name]:
                book_translations[word][lang_name][pos] = {}
                language_counters[(lang_code, pos)] = 1

            idx = str(language_counters[(lang_code, pos)])

            # Insert the item at the next available index.
            book_translations[word][lang_name][pos][idx] = {
                "description": desc,
                "translations": trans,
            }
            language_counters[(lang_code, pos)] += 1

    return book_translations


def parse_wiktionary_translations(word, output_dir=DEFAULT_MEDIAWIKI_EXPORT_DIR):
    """
    Parse translations from Wiktionary and save them to a JSON file.

    Fetches the Wiktionary page for the given word, extracts translations
    across different languages, and saves them in a structured JSON format.

    Parameters
    ----------
    word : str
        The word to fetch translations for.

    output_dir : str or Path, optional
        Directory to save JSON output (default is DEFAULT_MEDIAWIKI_EXPORT_DIR).
        Will be created if it doesn't exist.

    Notes
    -----
    The output JSON structure follows the format:
    {
        "word": {
            "language": {
                "part_of_speech": {
                    "1": {
                        "description": "context",
                        "translations": "translated_text"
                    }
                }
            }
        }
    }
    """
    output_dir = output_dir or DEFAULT_MEDIAWIKI_EXPORT_DIR
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    translations_by_lang = parse_wikitext_for_translations(fetch_translation_page(word))
    if not translations_by_lang:
        print("No translations found")
        return

    json_path = output_path / f"{word}.json"
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(
            build_json_format(word, translations_by_lang),
            file,
            indent=4,
            ensure_ascii=False,
        )

    print(f"JSON file saved to {json_path}")
