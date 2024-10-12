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

import re

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
    language_metadata = {"languages": []}

try:
    with DATA_TYPE_METADATA_FILE.open("r", encoding="utf-8") as file:
        data_type_metadata = json.load(file)
except (IOError, json.JSONDecodeError) as e:
    print(f"Error reading data type metadata: {e}")
    data_type_metadata = {"data-types": []}

language_map = {
    lang["language"].lower(): lang for lang in language_metadata["languages"]
}

# Create language_to_qid dictionary.
language_to_qid = {
    lang["language"].lower(): lang["qid"] for lang in language_metadata["languages"]
}


def get_available_languages() -> list[tuple[str, str]]:
    """
    Get available languages from the data extraction folder.

    Returns:
        list[tuple[str, str]]: A list of tuples with the language name and its QID.
    """
    extraction_dir = LANGUAGE_DATA_EXTRACTION_DIR
    available_languages = []
    for lang_folder in extraction_dir.iterdir():
        if lang_folder.is_dir():  # Check if it's a directory
            lang_name = lang_folder.name
            sparql_file_path = lang_folder / "verbs" / "query_verbs.sparql"
            qid = extract_qid_from_sparql(sparql_file_path)
            if qid:
                available_languages.append((lang_name, qid))
            else:
                available_languages.append((lang_name, ""))
    return available_languages


def extract_qid_from_sparql(file_path: Path) -> str:
    """
    Extract the QID from the specified SPARQL file.

    Args:
        file_path (Path): Path to the SPARQL file.

    Returns:
        str | None: The extracted QID or None if not found.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            # Use regex to find the QID (e.g., wd:Q34311)
            match = re.search(r"wd:Q\d+", content)
            if match:
                return match.group(0).replace("wd:", "")  # Return the found QID
    except Exception as _:
        pass
        # print(f"Error reading {file_path}: {e}")
    return None  # Return None if not found or an error occurs


def check_and_update_languages():
    """
    Check for missing languages in the metadata and update if necessary.
    """
    available_languages = get_available_languages()
    existing_languages = {
        lang["language"].lower() for lang in language_metadata["languages"]
    }
    missing_languages = [
        lang
        for lang in available_languages
        if lang[0].lower() not in existing_languages
    ]
    if missing_languages:
        update_language_metadata(missing_languages)


def update_language_metadata(missing_languages: list[tuple[str, str]]):
    """
    Update the language metadata with missing languages.

    Args:
        missing_languages (list[tuple[str, str]]): Missing languages and their QIDs.

    Returns:
        None
    """
    try:
        with LANGUAGE_METADATA_FILE.open("r+", encoding="utf-8") as file:
            language_metadata = json.load(file)

            for lang in missing_languages:
                language_metadata["languages"].append(
                    {"language": lang[0].lower(), "qid": lang[1]}
                )
            # Move the file pointer to the beginning and overwrite the existing file
            file.seek(0)
            json.dump(language_metadata, file, ensure_ascii=False, indent=4)
            file.truncate()  # Remove any leftover data
        print("Language metadata updated successfully.")
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error updating language metadata: {e}")


def set_metadata(language_name: str, qid: str):
    """
    Set or update the language metadata in the language_metadata.json file.

    Args:
        language_name (str): The name of the language to set.
        qid (str): The QID associated with the language.
    """
    try:
        with LANGUAGE_METADATA_FILE.open("r+", encoding="utf-8") as file:
            language_metadata = json.load(file)

            # Check if the language already exists
            for lang in language_metadata["languages"]:
                if lang["language"].lower() == language_name.lower():
                    # Update existing language QID
                    lang["qid"] = qid
                    print(f"Updated metadata for {language_name}.")
                    break
            else:
                # Add new language metadata if it doesn't exist
                language_metadata["languages"].append(
                    {"language": language_name.lower(), "qid": qid}
                )
                print(f"Added new metadata for {language_name}.")

            # Move the file pointer to the beginning and overwrite the existing file
            file.seek(0)
            json.dump(language_metadata, file, ensure_ascii=False, indent=4)
            file.truncate()  # Remove any leftover data
        print("Language metadata updated successfully.")
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error updating language metadata: {e}")


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
