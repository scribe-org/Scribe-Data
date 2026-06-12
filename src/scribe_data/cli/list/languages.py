# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for listing languages for the Scribe-Data CLI.
"""

from scribe_data.utils import (
    get_language_iso,
    get_language_qid,
    language_metadata,
    list_all_languages,
)

# MARK: Languages


def list_languages() -> None:
    """
    Generate a table of languages with their ISO-2 codes and Wikidata QIDs.

    Returns
    -------
    None
        A table of all languages with their ISO-2 codes and Wikidata QIDs is printed.
    """
    languages = list_all_languages(language_metadata)

    language_col_width = max(len(lang) for lang in languages) + 2
    iso_col_width = max(len(get_language_iso(lang)) for lang in languages) + 2
    qid_col_width = max(len(get_language_qid(lang)) for lang in languages) + 2

    table_line_length = language_col_width + iso_col_width + qid_col_width

    print(
        f"{'\nLanguage':<{language_col_width}} {'ISO':<{iso_col_width}} {'QID':<{qid_col_width}}"
    )
    print("=" * table_line_length)

    for lang in languages:
        print(
            f"{lang.title():<{language_col_width}} {get_language_iso(lang):<{iso_col_width}} {get_language_qid(lang):<{qid_col_width}}"
        )

    print()


def list_languages_for_data_type(data_type: str) -> None:
    """
    List the available languages for a given data type.

    Parameters
    ----------
    data_type : str
        The data type to check for.

    Returns
    -------
    None
        A list of languages for data types is printed to the terminal.
    """
    list_languages()
