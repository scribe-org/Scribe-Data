"""
Centralized keyword-emoji generation file to generated emoji for a specified Language

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
from scribe_data.unicode.process_unicode import gen_emoji_lexicon
from scribe_data.utils import export_formatted_data
from pathlib import Path

DATA_TYPE = "emoji-keywords"
EMOJI_KEYWORDS_DICT = 3

SUPPORTED_LANGUAGE_FILE =  Path(__file__).parent/"supported_languages.json"

def generate_emoji(language, output_dir: str = None):
    print(f"Got the language {language} for emoji generation")
    
    # check if this language is supported
    with open(SUPPORTED_LANGUAGE_FILE, 'r', encoding='utf-8') as file:
        languages = json.load(file)
    
    # Check if the language code exists in the dictionary
    for code, name in languages.items():
        if name == language:
            print(f"Emoji Generation for language : {language} is supported")
            break
    else:
        print(f"Emoji Generation for language : {language} is not supported")
        return

    updated_path = output_dir[2:] if output_dir.startswith("./") else output_dir
    export_dir = Path(updated_path) / language.capitalize()
    export_dir.mkdir(parents=True, exist_ok=True)

    if emoji_keywords_dict := gen_emoji_lexicon(
    language=language,
    emojis_per_keyword=EMOJI_KEYWORDS_DICT,
    ): export_formatted_data(
        file_path=output_dir,
        formatted_data=emoji_keywords_dict,
        query_data_in_use=True,
        language=language,
        data_type=DATA_TYPE,
    )

    