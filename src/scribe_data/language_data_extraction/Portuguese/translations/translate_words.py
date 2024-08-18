"""
Translates the Portuguese words queried from Wikidata to all other Scribe languages.

Example
-------
    python3 src/scribe_data/language_data_extraction/Portuguese/translations/translate_words.py

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
from pathlib import Path

from scribe_data.translation.translation_utils import (
    translate_to_other_languages,
)
from scribe_data.utils import DEFAULT_JSON_EXPORT_DIR

SRC_LANG = "Portuguese"
translate_script_dir = Path(__file__).parent
words_to_translate_path = translate_script_dir / "words_to_translate.json"

with open(words_to_translate_path, "r", encoding="utf-8") as file:
    json_data = json.load(file)

word_list = [item["word"] for item in json_data]

translated_words_path = Path(DEFAULT_JSON_EXPORT_DIR) / SRC_LANG / "translations.json"

if translated_words_path.exists():
    with open(translated_words_path, "r", encoding="utf-8") as file:
        translations = json.load(file)

translate_to_other_languages(
    source_language=SRC_LANG,
    word_list=word_list,
    translations=translations,
    batch_size=100,
)
