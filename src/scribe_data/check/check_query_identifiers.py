"""
Check the queries within Scribe-Data to make sure the language and data type are correct.

Example
-------
    python3 src/scribe_data/check/check_query_identifiers.py

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

import re
import sys
from pathlib import Path

from scribe_data.utils import (
    LANGUAGE_DATA_EXTRACTION_DIR,
    data_type_metadata,
    language_metadata,
)


def is_valid_language(query_file: Path, lang_qid: str) -> bool:
    """
    Validates the language QID against the expected QID for the directory.

    Parameters
    ----------
        query_file : Path
            The path to the SPARQL query file being validated.

        lang_qid : str
            The QID of the language extracted from the SPARQL query.

    Returns
    -------
        bool
            True if the language QID is valid, otherwise False.

    Example
    -------
        > is_valid_language(Path("path/to/query.sparql"), "Q123456")
        True
    """
    lang_directory_name = query_file.parent.parent.name.lower()
    language_entry = language_metadata.get(lang_directory_name)

    if not language_entry:
        # Look for sub-languages.
        for lang, details in language_metadata.items():
            if "sub_languages" in details:
                if sub_language_entry := details["sub_languages"].get(
                    lang_directory_name
                ):
                    language_entry = sub_language_entry
                    break

    return lang_qid == language_entry["qid"] if language_entry else False


def is_valid_data_type(query_file: Path, data_type_qid: str) -> bool:
    """
    Validates the data type QID against the expected QID for the directory.

    Parameters
    ----------
        query_file : Path
            The path to the SPARQL query file being validated.

        data_type_qid : str
            The QID of the data type extracted from the SPARQL query.

    Returns
    -------
        bool
            True if the data type QID is valid, otherwise False.

    Example
    -------
        > is_valid_data_type(Path("path/to/query.sparql"), "Q654321")
        True
    """
    directory_name = query_file.parent.name  # e.g., "nouns" or "verbs"
    expected_data_type_qid = data_type_metadata.get(directory_name)

    return data_type_qid == expected_data_type_qid


def extract_qid_from_sparql(file_path: Path, pattern: str) -> str:
    """
    Extracts the QID from a SPARQL query file based on the provided pattern.

    Parameters
    ----------
        file_path : Path
            The path to the SPARQL query file from which to extract the QID.

        pattern : str
            The regex pattern used to match the QID (either for language or data type).

    Returns
    -------
        str
            The extracted QID if found, otherwise None.

    Raises
    ------
        FileNotFoundError
            If the specified file does not exist.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            query_text = file.read()
            if match := re.search(pattern=pattern, string=query_text):
                return match[0].split("wd:")[1]

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return None


def check_query_identifiers() -> None:
    """
    Validates SPARQL queries in the language data directory to check for correct language and data type QIDs.
    """
    language_pattern = r"\?lexeme dct:language wd:Q\d+"
    data_type_pattern = r"wikibase:lexicalCategory\s+wd:Q\d+"
    incorrect_languages = []
    incorrect_data_types = []

    for query_file in LANGUAGE_DATA_EXTRACTION_DIR.glob("**/*.sparql"):
        lang_qid = extract_qid_from_sparql(
            file_path=query_file, pattern=language_pattern
        )
        data_type_qid = extract_qid_from_sparql(
            file_path=query_file, pattern=data_type_pattern
        )

        # Validate language QID and data type QID.
        if not is_valid_language(query_file=query_file, lang_qid=lang_qid):
            incorrect_languages.append(query_file)

        if not is_valid_data_type(query_file=query_file, data_type_qid=data_type_qid):
            incorrect_data_types.append(query_file)

    if incorrect_languages:
        print("Incorrect Language QIDs found in the following files:")
        for file in incorrect_languages:
            print(f"- {file}")

    if incorrect_data_types:
        print("Incorrect Data Type QIDs found in the following files:")
        for file in incorrect_data_types:
            print(f"- {file}")

    # Exit with an error code if any incorrect QIDs are found.
    if incorrect_languages or incorrect_data_types:
        sys.exit(1)

    else:
        print("All query language and data type QIDs are correct.")


if __name__ == "__main__":
    check_query_identifiers()
