"""
Translates the French words queried from Wikidata to all other Scribe languages.

Example
-------
    python3 src/scribe_data/wikidata/languages/French/translations/translate_words.py

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

import json
import os
import sys

from scribe_data.translation.translation_utils import (
    translate_to_other_languages,
)

SRC_LANG = "French"
translate_script_dir = os.path.dirname(os.path.abspath(__file__))
words_to_translate_path = os.path.join(translate_script_dir, "words_to_translate.json")

with open(words_to_translate_path, "r", encoding="utf-8") as file:
    json_data = json.load(file)

word_list = [item["word"] for item in json_data]

translations = {}
translated_words_path = os.path.join(
    translate_script_dir,
    f"{os.path.dirname(sys.path[0]).split('scribe_data')[0]}/../language_data_export/{SRC_LANG}/translated_words.json",
)
if os.path.exists(translated_words_path):
    with open(translated_words_path, "r", encoding="utf-8") as file:
        translations = json.load(file)

translate_to_other_languages(
    source_language=SRC_LANG,
    word_list=word_list,
    translations=translations,
    batch_size=100,
)
