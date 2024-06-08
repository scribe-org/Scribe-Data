"""
Setup and commands for the Scribe-Data command line interface.

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

#!/usr/bin/env python3

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Dict, List, Union

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

DATA_DIR = Path('language_data_export')

# Mapping of possible inputs to standardized language names
LANGUAGE_MAP = {
    'en': 'English', 'english': 'English',
    'fr': 'French', 'french': 'French',
    'de': 'German', 'german': 'German',
    'it': 'Italian', 'italian': 'Italian',
    'pt': 'Portuguese', 'portuguese': 'Portuguese',
    'ru': 'Russian', 'russian': 'Russian',
    'es': 'Spanish', 'spanish': 'Spanish',
    'sv': 'Swedish', 'swedish': 'Swedish'
}

def list_languages() -> None:
    if not DATA_DIR.exists() or not DATA_DIR.is_dir():
        print(f"Directory '{DATA_DIR}' does not exist.")
        return

    languages = [lang.name for lang in DATA_DIR.iterdir() if lang.is_dir()]
    languages.sort()
    print("Available languages:")
    for lang in languages:
        print(f"- {lang}")

def list_word_types(language: str = None) -> None:
    if language:
        # Normalize the input language
        normalized_language = LANGUAGE_MAP.get(language.lower())
        if not normalized_language:
            print(f"Language '{language}' is not recognized.")
            return

        language_dir = DATA_DIR / normalized_language
        if not language_dir.exists() or not language_dir.is_dir():
            print(f"No data found for language '{normalized_language}'.")
            return

        word_types = [wt.stem for wt in language_dir.glob('*.json')]
        if not word_types:
            print(f"No word types available for language '{normalized_language}'.")
            return

        max_word_type_length = max(len(wt) for wt in word_types)
        print(f"Word types for language '{normalized_language}':")
        for wt in word_types:
            print(f"  - {wt:<{max_word_type_length}}")
    else:
        word_types = set()
        for lang_dir in DATA_DIR.iterdir():
            if lang_dir.is_dir():
                word_types.update(wt.stem for wt in lang_dir.glob('*.json'))

        if not word_types:
            print("No word types available.")
            return

        word_types = sorted(word_types)
        print("Available word types:")
        for wt in word_types:
            print(f"  - {wt}")

def print_formatted_data(data: Union[Dict, List], word_type: str) -> None:
    if word_type == 'autosuggestions':
        max_key_length = max(len(key) for key in data.keys())
        for key, value in data.items():
            print(f"{key:<{max_key_length}} : {', '.join(value)}")
    elif word_type == 'emoji_keywords':
        max_key_length = max(len(key) for key in data.keys())
        for key, value in data.items():
            emojis = [item['emoji'] for item in value]
            print(f"{key:<{max_key_length}} : {' '.join(emojis)}")
    elif word_type == 'prepositions' or word_type == 'translations':
        max_key_length = max(len(key) for key in data.keys())
        for key, value in data.items():
            print(f"{key:<{max_key_length}} : {value}")
    else:
        if isinstance(data, dict):
            max_key_length = max(len(key) for key in data.keys())
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"{key:<{max_key_length}} : ")
                    max_sub_key_length = max(len(sub_key) for sub_key in value.keys())
                    for sub_key, sub_value in value.items():
                        print(f"  {sub_key:<{max_sub_key_length}} : {sub_value}")
                elif isinstance(value, list):
                    print(f"{key:<{max_key_length}} : ")
                    for item in value:
                        if isinstance(item, dict):
                            for sub_key, sub_value in item.items():
                                print(f"  {sub_key:<{max_key_length}} : {sub_value}")
                        else:
                            print(f"  {item}")
                else:
                    print(f"{key:<{max_key_length}} : {value}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        print(f"{key} : {value}")
                else:
                    print(item)
        else:
            print(data)

def query_data(language: str, word_type: str) -> None:
    # Normalize the input language
    normalized_language = LANGUAGE_MAP.get(language.lower())
    if not normalized_language:
        print(f"Language '{language}' is not recognized.")
        return

    data_file = DATA_DIR / normalized_language / f"{word_type}.json"
    if not data_file.exists():
        print(f"No data found for language '{normalized_language}' and word type '{word_type}'.")
        return

    try:
        with data_file.open('r') as file:
            data = json.load(file)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading '{data_file}': {e}")
        return

    print(f"Data for language '{normalized_language}' and word type '{word_type}':")
    print_formatted_data(data, word_type)

    if word_type.lower() == 'nouns':
        print("\nLegend:")
        print("PL    : Plural")
        print("empty : Singular\n")

def main() -> None:
    parser = argparse.ArgumentParser(description='Scribe-Data CLI Tool')
    subparsers = parser.add_subparsers(dest='command', required=True)

    subparsers.add_parser('list-languages', aliases=['ll'], help='List available languages')

    list_word_types_parser = subparsers.add_parser('list-word-types', aliases=['lwt'], help='List available word types')
    list_word_types_parser.add_argument('-l', '--language', help='Language code')

    query_parser = subparsers.add_parser('query', help='Query data for a specific language and word type')
    query_parser.add_argument('-l', '--language', required=True, help='Language code')
    query_parser.add_argument('-wt', '--word-type', required=True, help='Word type')

    args = parser.parse_args()

    if args.command in ['list-languages', 'll']:
        list_languages()
    elif args.command in ['list-word-types', 'lwt']:
        if args.language:
            list_word_types(args.language)
        else:
            list_word_types()
    elif args.command == 'query':
        query_data(args.language, args.word_type)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
