"""
Utility functions for the Scribe-Data CLI.

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
from typing import Dict, List, Union,Any, Optional

LANGUAGE_METADATA_FILE = (
    Path(__file__).parent.parent / "resources" / "language_metadata.json"
)
DATA_TYPE_METADATA_FILE = (
    Path(__file__).parent.parent / "resources" / "data_type_metadata.json"
)
DATA_DIR = Path("scribe_data_json_export")

with LANGUAGE_METADATA_FILE.open("r", encoding="utf-8") as file:
    language_metadata = json.load(file)

with DATA_TYPE_METADATA_FILE.open("r", encoding="utf-8") as file:
    data_type_metadata = json.load(file)

language_map = {
    lang["language"].lower(): lang for lang in language_metadata["languages"]
        }

all_keys_to_info: Dict[str, Dict] = {}
for lang in language_metadata["languages"]:
    all_keys_to_info[lang["language"].lower()] = lang
    all_keys_to_info[lang["iso"].lower()] = lang
    all_keys_to_info[lang["qid"]] = lang

def get_language_data(data_type: str, attribute: Optional[str] = None) -> Optional[Any]:
    """
    Retrieve language information or a specific attribute for a given input string.

    Parameters
    ----------
    data_type : str
        The input string representing a language, ISO code, or QID.
    attribute : str, optional
        The specific attribute to retrieve (e.g., 'language', 'iso', 'qid', 'remove-words', 'ignore-words').
        If None, returns the full language information dictionary.

    Returns
    -------
    Any or None
        If attribute is None, returns the full language information dictionary.
        If attribute is specified, returns the value of that attribute.
        Returns None if the data_type is not found or the attribute doesn't exist.
    """
    info = all_keys_to_info.get(data_type) or all_keys_to_info.get(data_type.lower())
    
    if info is None:
        return None
    
    if attribute is None:
        return info
    elif attribute == 'language':
        return info.get(attribute).capitalize()
    elif attribute in info:
        return info.get(attribute)
    else:
        return None

def correct_data_type(data_type: str) -> str:
    """
    Corrects common versions of data type arguments so users can choose between them.

    Parameters
    ----------
        data_type : str
            The data type to potentially correct.

    Returns
    -------
        The data_type value or a corrected version of it.
    """
    all_data_types = data_type_metadata["data-types"]

    if data_type in all_data_types:
        return data_type

    for wt in all_data_types:
        if f"{data_type}s" == wt:
            return wt
    return None


def print_formatted_data(data: Union[Dict, List], data_type: str) -> None:
    """
    Prints a formatted output from the Scribe-Data CLI.
    """
    if not data:
        print(f"No data available for data type '{data_type}'.")
        return

    max_key_length = max((len(key) for key in data.keys()), default=0)

    if data_type == "autosuggestions":
        for key, value in data.items():
            print(f"{key:<{max_key_length}} : {', '.join(value)}")

    elif data_type == "emoji_keywords":
        for key, value in data.items():
            emojis = [item["emoji"] for item in value]
            print(f"{key:<{max_key_length}} : {' '.join(emojis)}")

    elif data_type in {"prepositions", "translations"}:
        for key, value in data.items():
            print(f"{key:<{max_key_length}} : {value}")

    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{key:<{max_key_length}} : ")
                max_sub_key_length = max(
                    (len(sub_key) for sub_key in value.keys()), default=0
                )
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
