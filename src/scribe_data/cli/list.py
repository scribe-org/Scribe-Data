"""
Functions for listing languages and word types for the Scribe-Data CLI.

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

from .cli_utils import correct_word_type

# Load language metadata from JSON file.
METADATA_FILE = Path(__file__).parent.parent / "resources" / "language_metadata.json"
LANGUAGE_DATA_EXTRACTION_DIR = Path(__file__).parent.parent / "language_data_extraction"

with METADATA_FILE.open("r", encoding="utf-8") as file:
    language_metadata = json.load(file)

language_map = {
    lang["language"].lower(): lang for lang in language_metadata["languages"]
}


def list_languages() -> None:
    """
    Generates a table of languages, their ISO-2 codes and their Wikidata QIDs.
    """
    languages = list(language_metadata["languages"])
    languages.sort(key=lambda x: x["language"])

    language_col_width = max(len(lang["language"]) for lang in languages) + 2
    iso_col_width = max(len(lang["iso"]) for lang in languages) + 2
    qid_col_width = max(len(lang["qid"]) for lang in languages) + 2

    table_line_length = language_col_width + iso_col_width + qid_col_width

    print()
    print(
        f"{'Language':<{language_col_width}} {'ISO':<{iso_col_width}} {'QID':<{qid_col_width}}"
    )
    print("-" * table_line_length)

    for lang in languages:
        print(
            f"{lang['language'].capitalize():<{language_col_width}} {lang['iso']:<{iso_col_width}} {lang['qid']:<{qid_col_width}}"
        )

    print("-" * table_line_length)
    print()


def list_word_types(language: str = None) -> None:
    """
    Lists all word types or those available for a given language.

    Parameters
    ----------
        language : str
            The language to potentially list word types for.
    """
    if language:
        language_data = language_map.get(language.lower())
        language_capitalized = language.capitalize()
        language_dir = LANGUAGE_DATA_EXTRACTION_DIR / language_capitalized

        if not language_data:
            raise ValueError(f"Language '{language}' is not recognized.")

        word_types = [f.name for f in language_dir.iterdir() if f.is_dir()]
        if not word_types:
            raise ValueError(
                f"No word types available for language '{language_capitalized}'."
            )

        table_header = f"Available word types: {language_capitalized}"

    else:
        word_types = set()
        for lang in language_metadata["languages"]:
            language_dir = LANGUAGE_DATA_EXTRACTION_DIR / lang["language"].capitalize()
            if language_dir.is_dir():
                word_types.update(f.name for f in language_dir.iterdir() if f.is_dir())

        table_header = "Available word types: All languages"

    table_line_length = max(len(table_header), max(len(wt) for wt in word_types))

    print()
    print(table_header)
    print("-" * table_line_length)

    word_types = sorted(word_types)
    for wt in word_types:
        print(wt)

    print("-" * table_line_length)
    print()


def list_all() -> None:
    """
    Lists all available languages and word types.
    """
    list_languages()
    list_word_types()


def list_languages_for_word_type(word_type: str) -> None:
    """
    Lists the available languages for a given word type.

    Parameters
    ----------
        word_type : str
            The word type to check for.
    """
    word_type = correct_word_type(word_type)
    available_languages = []
    for lang in language_metadata["languages"]:
        language_dir = LANGUAGE_DATA_EXTRACTION_DIR / lang["language"].capitalize()
        if language_dir.is_dir():
            wt_path = language_dir / word_type
            if wt_path.exists():
                available_languages.append(lang["language"])

    available_languages.sort()
    table_header = f"Available languages: {word_type}"
    table_line_length = max(
        len(table_header), max(len(lang) for lang in available_languages)
    )

    print()
    print(table_header)
    print("-" * table_line_length)

    for lang in available_languages:
        print(f"{lang.capitalize()}")

    print("-" * table_line_length)
    print()


def list_wrapper(language: str = None, word_type: str = None) -> None:
    """
    Conditionally provides the full functionality of the list command.

    Parameters
    ----------
        language : str
            The language to potentially list word types for.

        word_type : str
            The word type to check for.
    """
    if not language and not word_type:
        list_all()

    elif language is True and not word_type:
        list_languages()

    elif not language and word_type is True:
        list_word_types()

    elif language is True and word_type is True:
        print("Please specify either a language or a word type.")

    elif word_type is not None:
        list_languages_for_word_type(word_type)

    elif language is not None:
        list_word_types(language)
