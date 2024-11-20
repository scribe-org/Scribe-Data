"""
Check the Scribe-Data metadata files to make sure that all information is included.

Example
-------
    python3 src/scribe_data/check/check_project_metadata.py

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
import sys

from scribe_data.utils import (
    LANGUAGE_DATA_EXTRACTION_DIR,
    _languages,
    data_type_metadata,
)

all_data_types = tuple(data_type_metadata.keys())


def get_available_languages() -> dict[str, list[str]]:
    """
    Get available languages from the data extraction folder.

    Returns
    -------
        dict[str, list[str]]: A dictionary with the language name as the key and a list of its sub-languages (if available) as the value.
    """
    extraction_dir = LANGUAGE_DATA_EXTRACTION_DIR
    available_languages = {}

    for lang_folder in extraction_dir.iterdir():
        if lang_folder.is_dir():  # check if it's a directory
            lang_name = (
                lang_folder.name
            )  # normalize keys to lowercase for case-insensitive comparison
            sub_languages = []

            # Check if lang_folder contains subdirectories.
            for sub_folder in lang_folder.iterdir():
                if sub_folder.is_dir():
                    sub_lang_name = (
                        sub_folder.name
                    )  # normalize to lowercase for case-insensitive comparison.

                    # Check for almost similar keys using difflib.
                    close_matches = difflib.get_close_matches(  # verb, noun, etc.
                        sub_lang_name, all_data_types, n=1, cutoff=0.8
                    )

                    # Append sub-language name if no close match found (not a data type).
                    if not close_matches:
                        sub_languages.append(sub_lang_name)

            # If we found sub-languages, add them to available_languages.s
            if sub_languages:
                available_languages[lang_name] = {"sub_languages": sub_languages}
            else:
                available_languages[lang_name] = {}

    return available_languages


def get_missing_languages(
    reference_languages: dict, target_languages: dict
) -> list[str]:
    """
    Compare two language dictionaries and return a list of languages and sub-languages
    that exist in target_languages but not in reference_languages.

    Parameters
    ----------
        reference_languages : dict
            A dictionary of languages from the reference source.

        target_languages : dict
            A dictionary of languages from the target source to check for missing entries.

    Returns
    -------
        list[str]
            A list of languages and sub-languages that are in target_languages but not in reference_languages.
    """
    missing_languages = []
    reference_keys = reference_languages.keys()

    for lang, details in target_languages.items():
        # Check if the parent language exists.
        if lang not in reference_keys:
            # If it's a parent language, check for sub-languages and append them.
            if "sub_languages" in details:
                for sub_lang in details["sub_languages"]:
                    missing_languages.append(f"{lang}/{sub_lang}")
            else:
                # Individual language, append directly.
                missing_languages.append(lang)
        else:
            # If the parent exists, only check for missing sub-languages.
            ref_sub_languages = reference_languages[lang].get("sub_languages", {})

            if "sub_languages" in details:
                for sub_lang in details["sub_languages"]:
                    if sub_lang not in ref_sub_languages:
                        missing_languages.append(f"{lang}/{sub_lang}")

    return missing_languages


def validate_language_properties(languages_dict: dict) -> dict:
    """
    Validates the presence of 'qid' and 'iso' properties for each language and its sub-languages.

    Parameters
    ----------
        languages_dict : dict
            A dictionary where each key is a language, and the value is another dictionary containing details about the language. If the language has sub-languages, they are stored under the 'sub_languages' key.

    Returns
    -------
        dict: A dictionary with two lists:
            - "missing_qids": Languages or sub-languages missing the 'qid' property.
            - "missing_isos": Languages or sub-languages missing the 'iso' property.

            Each entry in these lists is in the format "parent_language - sub_language" for sub-languages,
            or simply "parent_language" for the parent languages.
    """
    missing_qids = []
    missing_isos = []

    for lang, details in languages_dict.items():
        # Check if the language has sub-languages.
        if "sub_languages" in details:
            sub_languages = details["sub_languages"]

            # Validate each sub-language.
            for sub_lang, sub_details in sub_languages.items():
                if "qid" not in sub_details:
                    missing_qids.append(f"{lang}/{sub_lang}")
                if "iso" not in sub_details:
                    missing_isos.append(f"{lang}/{sub_lang}")
        else:
            # Validate the parent language itself.
            if "qid" not in details:
                missing_qids.append(lang)
            if "iso" not in details:
                missing_isos.append(lang)

    return {"missing_qids": missing_qids, "missing_isos": missing_isos}


def check_language_metadata():
    """
    Validates language metadata by performing the following checks:

    1. Ensures that all languages listed in `language_data_extraction` are present in `language_metadata.json`, and vice versa.

    2. Checks if each language in `language_metadata.json` has the required properties:
        - 'qid' (a unique identifier)
        - 'iso' (ISO language code)

    This function helps identify missing languages or missing properties, ensuring data consistency across both sources.

    Raises:
    -------
        SystemExit:
            If any missing languages or properties are found, the function exits the script with a status code of 1.
    """
    languages_in_metadata = {key: value for key, value in _languages.items()}

    languages_in_directory = get_available_languages()

    missing_languages_extraction = get_missing_languages(
        languages_in_directory, languages_in_metadata
    )

    languages_with_missing_properties = validate_language_properties(
        languages_in_metadata
    )

    if (
        missing_languages_extraction
        or languages_with_missing_properties["missing_qids"]
        or languages_with_missing_properties["missing_isos"]
    ):
        if missing_languages_extraction:
            print(
                "There are missing languages or inconsistencies between language_metadata.json and language_data_extraction.\n"
            )

        if missing_languages_extraction:
            print("\nLanguages missing from language_data_extraction:")
            for lang in missing_languages_extraction:
                print(f"  - {lang.title()}")

        if languages_with_missing_properties["missing_qids"]:
            print("\nLanguages missing the `qid` property:")
            for lang in languages_with_missing_properties["missing_qids"]:
                print(f"  - {lang.title()}")

        if languages_with_missing_properties["missing_isos"]:
            print("\nLanguages missing the `iso` property:")
            for lang in languages_with_missing_properties["missing_isos"]:
                print(f"  - {lang.title()}")

        # Exit with a non-zero status code to indicate failure.
        sys.exit(1)

    print(
        "All languages in language_metadata.json are included in Scribe-Data.\nLanguages in language_metadata.json have the correct properties."
    )


if __name__ == "__main__":
    check_language_metadata()
