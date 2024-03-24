"""
Translates the French words queried from Wikidata to all other Scribe languages.

Example
-------
    python3 src/scribe_data/extract_transform/languages/French/translations/translate_words.py
"""

import json
import os
import sys

PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

from scribe_data.extract_transform.translation.translation_utils import (  # noqa: E402
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
    translate_script_dir, "../formatted_data/translated_words.json"
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
