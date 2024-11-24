"""
Functions for listing languages and data types for the Scribe-Data CLI.

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
from pathlib import Path

from scribe_data.cli.cli_utils import (
    correct_data_type,
)
from scribe_data.utils import (
    LANGUAGE_DATA_EXTRACTION_DIR,
    format_sublanguage_name,
    get_language_iso,
    get_language_qid,
    language_map,
    language_metadata,
    list_all_languages,
    list_languages_with_metadata_for_data_type,
)


def list_languages() -> None:
    """
    Generates a table of languages, their ISO-2 codes and their Wikidata QIDs.
    """
    languages = list_all_languages(language_metadata)

    language_col_width = max(len(lang) for lang in languages) + 2
    iso_col_width = max(len(get_language_iso(lang)) for lang in languages) + 2
    qid_col_width = max(len(get_language_qid(lang)) for lang in languages) + 2

    table_line_length = language_col_width + iso_col_width + qid_col_width

    print()
    print(
        f"{'Language':<{language_col_width}} {'ISO':<{iso_col_width}} {'QID':<{qid_col_width}}"
    )
    print("=" * table_line_length)

    for lang in languages:
        print(
            f"{lang.title():<{language_col_width}} {get_language_iso(lang):<{iso_col_width}} {get_language_qid(lang):<{qid_col_width}}"
        )

    print()


def list_data_types(language: str = None) -> None:
    """
    Lists all data types or those available for a given language.

    Parameters
    ----------
        language : str
            The language to potentially list data types for.
    """
    languages = list_all_languages(language_metadata)
    if language:
        language = format_sublanguage_name(language, language_metadata)
        language_data = language_map.get(language.lower())
        language_dir = LANGUAGE_DATA_EXTRACTION_DIR / language.lower()

        if not language_data:
            raise ValueError(f"Language '{language.capitalize()}' is not recognized.")

        data_types = {f.name for f in language_dir.iterdir() if f.is_dir()}

        # Add emoji keywords if available.
        iso = get_language_iso(language=language)
        path_to_cldr_annotations = (
            Path(__file__).parent.parent
            / "unicode"
            / "cldr-annotations-full"
            / "annotations"
        )
        if iso in os.listdir(path_to_cldr_annotations):
            data_types.add("emoji-keywords")

        if not data_types:
            raise ValueError(
                f"No data types available for language '{language.capitalize()}'."
            )

        table_header = f"Available data types: {language.capitalize()}"

    else:
        data_types = set()
        for lang in languages:
            language_dir = LANGUAGE_DATA_EXTRACTION_DIR / format_sublanguage_name(
                lang, language_metadata
            )
            if language_dir.is_dir():
                data_types.update(f.name for f in language_dir.iterdir() if f.is_dir())

        data_types.add("emoji-keywords")

        table_header = "Available data types: All languages"

    table_line_length = max(len(table_header), max(len(dt) for dt in data_types))

    print()
    print(table_header)
    print("=" * table_line_length)

    data_types = sorted(data_types)
    for dt in data_types:
        print(dt.replace("_", "-"))

    print()


def list_all() -> None:
    """
    Lists all available languages and data types.
    """
    list_languages()
    list_data_types()


def list_languages_for_data_type(data_type: str) -> None:
    """
    Lists the available languages for a given data type.

    Parameters
    ----------
        data_type : str
            The data type to check for.
    """
    data_type = correct_data_type(data_type=data_type)
    all_languages = list_languages_with_metadata_for_data_type(language_metadata)

    # Set column widths for consistent formatting.
    language_col_width = max(len(lang["name"]) for lang in all_languages) + 2
    iso_col_width = max(len(lang["iso"]) for lang in all_languages) + 2
    qid_col_width = max(len(lang["qid"]) for lang in all_languages) + 2

    table_line_length = language_col_width + iso_col_width + qid_col_width

    # Print table header.
    print()
    print(
        f"{'Language':<{language_col_width}} {'ISO':<{iso_col_width}} {'QID':<{qid_col_width}}"
    )
    print("=" * table_line_length)

    # Iterate through the list of languages and format each row.
    for lang in all_languages:
        print(
            f"{lang['name'].capitalize():<{language_col_width}} {lang['iso']:<{iso_col_width}} {lang['qid']:<{qid_col_width}}"
        )

    print()


def list_wrapper(
    language: str = None, data_type: str = None, all_bool: bool = False
) -> None:
    """
    Conditionally provides the full functionality of the list command.

    Parameters
    ----------
        language : str
            The language to potentially list data types for.

        data_type : str
            The data type to check for.

        all_bool : boolean
            Whether all languages and data types should be listed.
    """
    if (not language and not data_type) or all_bool:
        list_all()

    elif language is True and not data_type:
        list_languages()

    elif not language and data_type is True:
        list_data_types()

    elif language is True and data_type is True:
        print("Please specify either a language or a data type.")

    elif language is True and data_type is not None:
        list_languages_for_data_type(data_type)

    elif language is not None and data_type is True:
        list_data_types(language)
