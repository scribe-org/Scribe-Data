# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for listing data types for the Scribe-Data CLI.
"""

import os
from pathlib import Path

from scribe_data.utils import (
    WIKIDATA_QUERIES_ALL_DATA_DIR,
    format_sublanguage_name,
    get_language_iso,
    language_map,
    language_metadata,
    list_all_languages,
)

# MARK: Data Types


def list_data_types(language: str = "") -> None:
    """
    List all data types or those available for a given language.

    Parameters
    ----------
    language : str
        The language to potentially list data types for.
    """
    languages = list_all_languages(language_metadata)
    if language:
        language = format_sublanguage_name(language, language_metadata)
        language_data = language_map.get(language.lower())
        language_dir = WIKIDATA_QUERIES_ALL_DATA_DIR / language.lower()

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
            language_dir = WIKIDATA_QUERIES_ALL_DATA_DIR / format_sublanguage_name(
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
