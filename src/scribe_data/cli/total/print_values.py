# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to check the total language data available on Wikidata.
"""

from scribe_data.cli.total.query import query_total_lexemes
from scribe_data.utils import (
    WIKIDATA_QUERIES_ALL_DATA_DIR,
    check_qid_is_language,
    data_type_metadata,
    format_sublanguage_name,
    language_metadata,
    list_all_languages,
)

# MARK: Data Types


def get_datatype_list(language: str) -> list | dict:
    """
    Get the data types for a given language based on the project directory structure.

    Parameters
    ----------
    language : str
        The language to return data types for.

    Returns
    -------
    list | dict
        A list of the corresponding data types.
    """
    language_key = language.strip().lower()  # normalize input
    languages = list_all_languages(language_metadata)

    # Adjust language_key for sub-languages using the format_sublanguage_name function.
    formatted_language = format_sublanguage_name(language_key, language_metadata)
    language_key = formatted_language.split(" ")[
        0
    ].lower()  # use the main language part if formatted

    if language_key in languages:
        if "sub_languages" in language_metadata[language_key]:
            sub_languages = language_metadata[language_key]["sub_languages"]
            data_types = []

            for sub_lang_key in sub_languages:
                sub_lang_dir = (
                    WIKIDATA_QUERIES_ALL_DATA_DIR / sub_languages[sub_lang_key]["iso"]
                )
                if sub_lang_dir.exists():
                    data_types.extend(
                        [f.name for f in sub_lang_dir.iterdir() if f.is_dir()]
                    )

            if not data_types:
                raise ValueError(
                    f"No data types available for sub-languages of '{formatted_language.capitalize()}'."
                )

            return sorted(set(data_types))  # remove duplicates and sort

        else:
            language_dir = WIKIDATA_QUERIES_ALL_DATA_DIR / language_key
            if not language_dir.exists():
                raise ValueError(f"Directory '{language_dir}' does not exist.")

            data_types = [f.name for f in language_dir.iterdir() if f.is_dir()]

            if not data_types:
                raise ValueError(
                    f"No data types available for language '{formatted_language.capitalize()}'."
                )

            return sorted(data_types)

    else:
        return data_type_metadata


# MARK: Print


def print_total_lexemes(language: str | None = None) -> None:
    """
    Print the total number of available entities for all data types.

    Parameters
    ----------
    language : str, optional
        The language to display data type entity counts for.

    Returns
    -------
    str
        A formatted string indicating the language, data type, and total number of lexemes for all the languages, if found.
    """
    if language is None:
        print("Returning total counts for all languages and data types...\n")

    elif (
        isinstance(language, str)
        and language.startswith("Q")
        and language[1:].isdigit()
    ):
        print(
            f"Wikidata QID {language.capitalize()} passed. Checking validity and then all data types."
        )
        language = check_qid_is_language(qid=language)

    else:
        print(f"Returning total counts for {language.capitalize()} data types...\n")

    def print_total_header(language: str, dt: str, total_lexemes: str) -> None:
        """
        Print the header of the total command output.

        Parameters
        ----------
        language : str
            The language for which to count lexemes.

        dt : str
            The data type (e.g., "nouns", "verbs") for which to count lexemes.

        total_lexemes : str
            The total number of lexemes derived formatted as a string.

        Returns
        -------
        None
            A message is printed to the terminal about the total number of lexemes.
        """
        language_display = (
            "All Languages" if language is None else language.capitalize()
        )
        print(f"{'Language':<20} {'Data Type':<25} {'Total Wikidata Lexemes':<25}")
        print("=" * 70)
        print(f"{language_display:<20} {dt.replace('_', '-'): <25} {total_lexemes:<25}")

    if language is None:  # all languages
        languages = list_all_languages(language_metadata)

        for lang in languages:
            data_types = get_datatype_list(lang)

            first_row = True
            for dt in data_types:
                total_lexemes = query_total_lexemes(
                    language=lang, data_type=dt, do_print=False
                )
                total_lexemes = f"{total_lexemes:,}"
                if first_row:
                    print_total_header(lang, dt, total_lexemes)
                    first_row = False

                else:
                    print(f"{'':<20} {dt.replace('_', ' '): <25} {total_lexemes:<25}")

            print()

    else:  # individual language
        first_row = True
        if language.startswith("Q") and language[1:].isdigit():
            data_types = data_type_metadata
            for t in ["emoji_keywords"]:
                if t in data_types:
                    del data_types[t]

        else:
            data_types = get_datatype_list(language)

        for dt in data_types:
            total_lexemes = query_total_lexemes(
                language=language, data_type=dt, do_print=False
            )
            total_lexemes = f"{total_lexemes:,}"
            if first_row:
                print_total_header(language, dt, total_lexemes)
                first_row = False

            else:
                print(f"{'':<20} {dt.replace('_', ' '): <25} {total_lexemes:<25}")

        print()
