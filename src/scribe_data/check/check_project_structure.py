"""
Check the structure of Scribe-Data to make sure that all files are correctly named and included.

Example
-------
    python3 src/scribe_data/check/check_project_structure.py

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

import os

from scribe_data.utils import (
    LANGUAGE_DATA_EXTRACTION_DIR,
    data_type_metadata,
    language_metadata,
)

# Expected languages and data types.
LANGUAGES = list(language_metadata.keys())
DATA_TYPES = data_type_metadata.keys()
SUB_DIRECTORIES = {
    k: list(v["sub_languages"].keys())
    for k, v in language_metadata.items()
    if len(v.keys()) == 1 and "sub_languages" in v.keys()
}


def check_for_sparql_files(folder_path, data_type, language, subdir, missing_queries):
    """
    Check if a data-type folder contains at least one .sparql file.

    Parameters
    ----------
        folder_path : str
            The path to the data-type folder.

        data_type : str
            The name of the data type being checked.

        language : str
            The name of the language being processed.

        subdir : str or None
            The name of the sub-directory (for languages with sub-dialects), or None.

        missing_queries : list
            A list to which missing SPARQL query files will be appended.

    Returns
    -------
        bool: True if at least one .sparql file is found, False otherwise.
    """
    sparql_files = [f for f in os.listdir(folder_path) if f.endswith(".sparql")]

    if not sparql_files:
        subdir_name = f"/{subdir}" if subdir else ""
        missing_queries.append(
            f"{language}{subdir_name}/{data_type}/query_{data_type}.sparql"
        )
        return False

    return True


def check_data_type_folders(
    path, language, subdir, errors, missing_folders, missing_queries
):
    """
    Validate the contents of data type folders within a language directory.

    This function checks each data type folder for the presence of expected files
    and reports any unexpected files. It allows for multiple SPARQL query files,
    a format Python file, and a queried JSON file for each data type.

    Parameters
    ----------
    path : str
        The path to the directory containing data type folders.

    language : str
        The name of the language being processed.

    subdir : str or None
        The name of the sub-directory (for languages with sub-dialects), or None.

    errors : list
        A list to which error messages will be appended.

    The function checks for the following valid files in each data type folder:
        - Files starting with 'query_' and ending with '.sparql'
        - A 'format_{data_type}.py' file
        - A '{data_type}_queried.json' file

    It skips validation for the 'emoji_keywords' data type folder.

    Any files not matching these patterns (except '__init__.py') are reported as unexpected.
    """
    existing_data_types = set(os.listdir(path)) - {"__init__.py"}
    missing_data_types = DATA_TYPES - existing_data_types - {"emoji_keywords"}

    for missing_type in missing_data_types:
        subdir_name = f"/{subdir}" if subdir else ""
        missing_folders.append(f"{language}{subdir_name}/{missing_type}")

    for item in existing_data_types:
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            errors.append(f"Unexpected file found in {language}{subdir_name}: {item}")

        elif item not in DATA_TYPES:
            errors.append(
                f"Unexpected directory found in {language}{subdir_name}: {item}"
            )

        else:
            if item == "emoji_keywords":
                continue

            check_for_sparql_files(item_path, item, language, subdir, missing_queries)

            valid_files = [
                f for f in os.listdir(item_path) if f.endswith(".sparql")
            ] + [f"format_{item}.py", f"{item}_queried.json", "__init__.py"]

            for file in os.listdir(item_path):
                if file not in valid_files:
                    errors.append(
                        f"Unexpected file in {language}{subdir_name}/{item}: {file}"
                    )


def check_project_structure():
    """
    Validate that all directories follow the expected project structure and check for unexpected files and directories.
    Also validate SPARQL query file names in data_type folders and SUBDIRECTORIES.
    """
    errors = []
    missing_folders = []
    missing_queries = []

    if not os.path.exists(LANGUAGE_DATA_EXTRACTION_DIR):
        print(f"Error: Base directory '{LANGUAGE_DATA_EXTRACTION_DIR}' does not exist.")
        exit(1)

    # Check for unexpected files in LANGUAGE_DATA_EXTRACTION_DIR.
    for item in os.listdir(LANGUAGE_DATA_EXTRACTION_DIR):
        item_path = os.path.join(LANGUAGE_DATA_EXTRACTION_DIR, item)
        if os.path.isfile(item_path) and item != "__init__.py":
            errors.append(
                f"Unexpected file found in the 'language_data_extraction' files: {item}"
            )

    # Iterate through the language directories.
    for language in os.listdir(LANGUAGE_DATA_EXTRACTION_DIR):
        language_path = os.path.join(LANGUAGE_DATA_EXTRACTION_DIR, language)

        if not os.path.isdir(language_path) or language == "__init__.py":
            continue

        if language not in LANGUAGES:
            errors.append(f"Unexpected language directory given: {language}")
            continue

        # Check for unexpected files in language directory.
        for item in os.listdir(language_path):
            item_path = os.path.join(language_path, item)
            if os.path.isfile(item_path) and item != "__init__.py":
                errors.append(f"Unexpected file found in {language} directory: {item}")

        found_subdirs = {
            item
            for item in os.listdir(language_path)
            if os.path.isdir(os.path.join(language_path, item))
            and item != "__init__.py"
        }

        if language in SUB_DIRECTORIES:
            expected_subdirs = set(SUB_DIRECTORIES[language])
            unexpected_subdirs = found_subdirs - expected_subdirs
            missing_subdirs = expected_subdirs - found_subdirs

            if unexpected_subdirs:
                errors.append(
                    f"Unexpected sub-subdirectories in '{language}': {unexpected_subdirs}"
                )
            if missing_subdirs:
                errors.append(
                    f"Missing sub-subdirectories in '{language}': {missing_subdirs}"
                )

            # Check contents of expected sub-subdirectories.
            for subdir in expected_subdirs:
                subdir_path = os.path.join(language_path, subdir)
                if os.path.exists(subdir_path):
                    check_data_type_folders(
                        subdir_path,
                        language,
                        subdir,
                        errors,
                        missing_folders,
                        missing_queries,
                    )

        else:
            check_data_type_folders(
                language_path, language, None, errors, missing_folders, missing_queries
            )

    # Attn: Removed for now.
    if errors:  # or missing_folders or missing_queries
        if errors:
            print("Errors found:")
            for error in errors:
                print(f" - {error}")

        # if missing_folders:
        #     print("\nMissing data type folders:")
        #     for folder in missing_folders:
        #         print(f" - {folder}")

        # if missing_queries:
        #     print("\nMissing SPARQL query files:")
        #     for query in missing_queries:
        #         print(f" - {query}")

        exit(1)

    else:
        print(
            "All directories and files are correctly named and organized, and no unexpected files or directories were found."
        )


if __name__ == "__main__":
    check_project_structure()
