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

import argparse
import json
from pathlib import Path
from typing import Dict, List, Union

DATA_DIR = Path('language_data_export')

def list_languages() -> None:
    if not DATA_DIR.exists() or not DATA_DIR.is_dir():
        print(f"Directory '{DATA_DIR}' does not exist.")
        return

    languages = [lang for lang in DATA_DIR.iterdir() if lang.is_dir()]
    print("Available languages:")
    for lang in languages:
        print(f"- {lang.name}")
        word_types = [wt.stem for wt in lang.glob('*.json')]
        max_word_type_length = max(len(wt) for wt in word_types)
        for wt in word_types:
            print(f"  - {wt:<{max_word_type_length}}")
        print("")

def print_formatted_data(data: Union[Dict, List]) -> None:
    if isinstance(data, dict):
        max_key_length = max(len(key) for key in data.keys())
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{key:<{max_key_length}} : ")
                max_sub_key_length = max(len(sub_key) for sub_key in value.keys())
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key:<{max_sub_key_length}} : {sub_value}")
            else:
                print(f"{key:<{max_key_length}} : {value}")
    elif isinstance(data, list):
        max_key_length = max(len(key) for item in data for key in item.keys())
        for item in data:
            if isinstance(item, dict):
                for key, value in item.items():
                    print(f"{key:<{max_key_length}} : ")
                    if isinstance(value, dict):
                        max_sub_key_length = max(len(sub_key) for sub_key in value.keys())
                        for sub_key, sub_value in value.items():
                            print(f"  {sub_key:<{max_sub_key_length}} : {sub_value}")
                    else:
                        print(f"  {value}")
            else:
                print(json.dumps(item, indent=2))
    else:
        print(data)

def query_data(language: str, word_type: str) -> None:
    data_file = DATA_DIR / language / f"{word_type}.json"
    if not data_file.exists():
        print(f"No data found for language '{language}' and word type '{word_type}'.")
        return

    try:
        with data_file.open('r') as file:
            data = json.load(file)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading '{data_file}': {e}")
        return

    print(f"Data for language '{language}' and word type '{word_type}':")
    print_formatted_data(data)

def main() -> None:
    parser = argparse.ArgumentParser(description='Scribe-Data CLI Tool')
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('list-languages', help='List available language codes and word types')

    query_parser = subparsers.add_parser('query', help='Query data for a specific language and word type')
    query_parser.add_argument('-l', '--language', required=True, help='Language code')
    query_parser.add_argument('-wt', '--word-type', required=True, help='Word type')

    args = parser.parse_args()

    if args.command == 'list-languages':
        list_languages()
    elif args.command == 'query':
        query_data(args.language, args.word_type)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
