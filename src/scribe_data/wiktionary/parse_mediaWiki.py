"""
   Functions to parse the translations of a word from MediaWiki API.

.. raw:: html
    <!--
    * Copyright (C) 2024 Scribe
    *
    * This program is free software: you can redistribute it and/or modify
    * it under the terms of the GNU General Public License as published by
    * the Free Software Foundation, either version 3 of the License, or
    * (at your option) any later version.
    *
    * This program is distributed in the hope that it will be useful,
    * but WITHOUT ANY WARRANTY; without even the implied warranty of
    * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    * GNU General Public License for more details.
    *
    * You should have received a copy of the GNU General Public License
    * along with this program.  If not, see <https://www.gnu.org/licenses/>.
    -->
"""

import re
import json
from scribe_data.wikidata.wikidata_utils import mediaWiki_query
from scribe_data.utils import get_language_from_iso


def fetch_translation_page(word):
    data = mediaWiki_query(word)

    pages = data.get("query", {}).get("pages", {})
    # Extract page object from dictionary
    page = next(iter(pages.values())) if pages else {}
    # Get the wikitext from the 'revisions' key
    wikitext = page.get("revisions", [{}])[0].get("*", "")
    return wikitext


def parse_wikitext_for_translations(wikitext):
    """
    Parse the wikitext line by line to extract translations,
    language codes, part of speech, and context.
    """
    translations_by_lang = {}
    current_part_of_speech = None  # Track whether we are in Noun or Verb
    current_context = None  # Track the current trans-top context

    # Split the wikitext into individual lines
    for line in wikitext.splitlines():
        # Detect part of speech/data-types: Noun or Verb
        if line.startswith("===Noun==="):
            current_part_of_speech = "Noun"
        elif line.startswith("===Verb==="):
            current_part_of_speech = "Verb"
        trans_top_match = re.match(r"\{\{trans-top\|(.+?)\}\}", line)
        if trans_top_match:
            current_context = trans_top_match.group(1).strip()

        template_match = re.match(
            r"^\*\s([A-Za-z\s]+):\s\{\{t\+?\|([a-zA-Z\-]+)\|([^|]+)\}\}", line.strip()
        )
        if template_match:
            lang_code = template_match.group(2).strip()
            translation_text = template_match.group(3).strip()

            # Ensure there's a list to hold translations for this language
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


def build_json_format(word, translations_by_lang):
    """
    Build the final JSON format for the translations of a word.
    """
    book_translations = {word: {}}
    # Keep counters to number the translations for each (lang, part_of_speech)
    language_counters = {}

    for lang_code, entries in translations_by_lang.items():
        try:
            lang_name = get_language_from_iso(lang_code)
        except ValueError:
            # Skip this language if it's not supported
            continue

        # Make sure this language is in the dictionary
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

            # Insert the item at the next available index
            book_translations[word][lang_name][pos][idx] = {
                "description": desc,
                "translations": trans,
            }
            language_counters[(lang_code, pos)] += 1

    return book_translations


def parse_wiktionary_translations(word):
    """
    Parse the translations of a word from Wiktionary.
    """
    wikitext = fetch_translation_page(word)
    translations_by_lang = parse_wikitext_for_translations(wikitext)

    if not translations_by_lang:
        print("No translations found")
        return

    final_json = build_json_format(word, translations_by_lang)
    print(json.dumps(final_json, indent=4, ensure_ascii=False))
