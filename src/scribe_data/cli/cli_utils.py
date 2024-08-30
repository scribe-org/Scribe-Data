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
from typing import Union

from scribe_data.utils import DEFAULT_JSON_EXPORT_DIR

LANGUAGE_METADATA_FILE = (
    Path(__file__).parent.parent / "resources" / "language_metadata.json"
)
DATA_TYPE_METADATA_FILE = (
    Path(__file__).parent.parent / "resources" / "data_type_metadata.json"
)
DATA_DIR = Path(DEFAULT_JSON_EXPORT_DIR)

with LANGUAGE_METADATA_FILE.open("r", encoding="utf-8") as file:
    language_metadata = json.load(file)

with DATA_TYPE_METADATA_FILE.open("r", encoding="utf-8") as file:
    data_type_metadata = json.load(file)

language_map = {
    lang["language"].lower(): lang for lang in language_metadata["languages"]
}

# Create language_to_qid dictionary
language_to_qid = {
    lang["language"].lower(): lang["qid"] for lang in language_metadata["languages"]
}


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


def print_formatted_data(data: Union[dict, list], data_type: str) -> None:
    """
    Prints a formatted output from the Scribe-Data CLI.
    """
    if not data:
        print(f"No data available for data type '{data_type}'.")
        return

    if isinstance(data, dict):
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

        else:
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
