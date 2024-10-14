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

import difflib
import json
from pathlib import Path
from typing import Union

from scribe_data.utils import DEFAULT_JSON_EXPORT_DIR

LANGUAGE_DATA_EXTRACTION_DIR = Path(__file__).parent.parent / "language_data_extraction"

LANGUAGE_METADATA_FILE = (
    Path(__file__).parent.parent / "resources" / "language_metadata.json"
)
DATA_TYPE_METADATA_FILE = (
    Path(__file__).parent.parent / "resources" / "data_type_metadata.json"
)
DATA_DIR = Path(DEFAULT_JSON_EXPORT_DIR)

try:
    with LANGUAGE_METADATA_FILE.open("r", encoding="utf-8") as file:
        language_metadata = json.load(file)

except (IOError, json.JSONDecodeError) as e:
    print(f"Error reading language metadata: {e}")


try:
    with DATA_TYPE_METADATA_FILE.open("r", encoding="utf-8") as file:
        data_type_metadata = json.load(file)

except (IOError, json.JSONDecodeError) as e:
    print(f"Error reading data type metadata: {e}")


language_map = {
    lang["language"].lower(): lang for lang in language_metadata["languages"]
}

# Create language_to_qid dictionary.
language_to_qid = {
    lang["language"].lower(): lang["qid"] for lang in language_metadata["languages"]
}


# MARK: Correct Inputs


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
    all_data_types = data_type_metadata.keys()

    if data_type in all_data_types:
        return data_type

    for wt in all_data_types:
        if f"{data_type}s" == wt:
            return wt


# MARK: Print Formatted


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

        elif data_type in {"prepositions"}:
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


# MARK: Validate


def validate_language_and_data_type(language: str, data_type: str):
    """
    Validates that the language and data type QIDs are not None.

    Parameters
    ----------
        language : str
            The language to validate.

        data_type : str
            The data type to validate.

    Raises
    ------
        ValueError
            If either the language or data type is invalid (None).
    """
    # Not functional for lists of arguments yet.
    if isinstance(language, list) or isinstance(data_type, list):
        return

    language_is_valid = True
    data_type_is_valid = True

    value_error = ""
    closest_language_match_string = ""
    closest_data_type_match_string = ""

    if (
        isinstance(language, str)
        and language.lower() not in language_to_qid.keys()
        and not language.startswith("Q")
        and not language[1:].isdigit()
    ):
        language_is_valid = False
        if closest_language_match := difflib.get_close_matches(
            language, language_map.keys(), n=1
        ):
            closest_language_match_cap = closest_language_match[0].capitalize()
            closest_language_match_string = (
                f" The closest matching language is {closest_language_match_cap}."
            )

    if (
        isinstance(data_type, str)
        and data_type not in data_type_metadata.keys()
        and not data_type.startswith("Q")
        and not data_type[1:].isdigit()
    ):
        data_type_is_valid = False

        if closest_data_type_match := difflib.get_close_matches(
            data_type, data_type_metadata.keys(), n=1
        ):
            closest_data_type_match_string = (
                f" The closest matching data-type is {closest_data_type_match[0]}."
            )

    if not language_is_valid and data_type_is_valid:
        value_error = (
            f"Invalid language {language} passed.{closest_language_match_string}"
        )

        raise ValueError(value_error)

    elif language_is_valid and not data_type_is_valid:
        value_error = (
            f"Invalid data-type {data_type} passed.{closest_data_type_match_string}"
        )

        raise ValueError(value_error)

    elif not language_is_valid and not data_type_is_valid:
        value_error = f"Invalid language {language} and data-type {data_type} passed.{closest_language_match_string}{closest_data_type_match_string}"

        raise ValueError(value_error)
