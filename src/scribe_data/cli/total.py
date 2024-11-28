"""
Functions to check the total language data available on Wikidata.

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

from http.client import IncompleteRead
from typing import List, Union
from urllib.error import HTTPError

import requests
from SPARQLWrapper import JSON

from scribe_data.utils import (
    LANGUAGE_DATA_EXTRACTION_DIR,
    data_type_metadata,
    format_sublanguage_name,
    language_metadata,
    language_to_qid,
    list_all_languages,
)
from scribe_data.wikidata.wikidata_utils import sparql


def get_qid_by_input(input_str):
    """
    Retrieve the QID for a given language or data type input string.

    Parameters
    ----------
        input_str : str
            The input string representing a language or data type.

    Returns
    -------
        str or None
            The QID corresponding to the input string, or- None if not found.
    """
    if input_str:
        if input_str in language_to_qid:
            return language_to_qid[input_str]

        elif input_str in data_type_metadata:
            return data_type_metadata[input_str]

    return None


def get_datatype_list(language):
    """
    Get the data types for a given language based on the project directory structure, including handling sub-languages.

    Parameters
    ----------
        language : str
            The language to return data types for.

    Returns
    -------
        data_types : list[str] or None
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
                    LANGUAGE_DATA_EXTRACTION_DIR / sub_languages[sub_lang_key]["iso"]
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
            language_dir = LANGUAGE_DATA_EXTRACTION_DIR / language_key
            if not language_dir.exists():
                raise ValueError(f"Directory '{language_dir}' does not exist.")

            data_types = [f.name for f in language_dir.iterdir() if f.is_dir()]

            if not data_types:
                raise ValueError(
                    f"No data types available for language '{formatted_language.capitalize()}'."
                )

            return sorted(data_types)

    else:  # return all data types
        return data_type_metadata


def check_qid_is_language(qid: str):
    """
    Parameters
    ----------
        qid : str
            The QID to check Wikidata to see if it's a language and return its English label.

    Outputs
    -------
        str
            The English label of the Wikidata language entity.

    Raises
    ------
        ValueError
            An invalid QID that's not a language has been passed.
    """
    api_endpoint = "https://www.wikidata.org/w/rest.php/wikibase/v0"
    request_string = f"{api_endpoint}/entities/items/{qid}"

    request = requests.get(request_string, timeout=5)
    request_result = request.json()

    if request_result["statements"]["P31"]:
        instance_of_values = request_result["statements"]["P31"]
        for val in instance_of_values:
            if val["value"]["content"] == "Q34770":
                print(f"{request_result['labels']['en']} ({qid}) is a language.\n")
                return request_result["labels"]["en"]

    raise ValueError("The passed Wikidata QID is not a language.")


# MARK: Print


def print_total_lexemes(language: str = None):
    """
    Displays the total number of available entities for all data types for a given language or all the languages.

    Parameters
    ----------
        language : str (Default=None)
            The language to display data type entity counts for.

    Outputs
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

    def print_total_header(language, dt, total_lexemes):
        """
        Prints the header of the total command output.
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
                total_lexemes = get_total_lexemes(
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
            for t in ["autosuggestions", "emoji_keywords"]:
                if t in data_types:
                    del data_types[t]

        else:
            data_types = get_datatype_list(language)

        for dt in data_types:
            total_lexemes = get_total_lexemes(
                language=language, data_type=dt, do_print=False
            )
            total_lexemes = f"{total_lexemes:,}"
            if first_row:
                print_total_header(language, dt, total_lexemes)
                first_row = False

            else:
                print(f"{'':<20} {dt.replace('_', ' '): <25} {total_lexemes:<25}")

        print()


# MARK: Get Total


def get_total_lexemes(language, data_type, do_print=True):
    """
    Get the total number of lexemes for a given language and data type from Wikidata.

    Parameters
    ----------
    language : str
        The language for which to count lexemes.

    data_type : str
        The data type (e.g., "nouns", "verbs") for which to count lexemes.

    Outputs
    -------
    str
        A formatted string indicating the language, data type and total number of lexemes, if found.
    """

    if language is not None and language.startswith("Q") and language[1:].isdigit():
        language_qid = language

    else:
        language_qid = get_qid_by_input(language)

    if data_type is not None and data_type.startswith("Q") and data_type[1:].isdigit():
        data_type_qid = data_type

    else:
        data_type_qid = get_qid_by_input(data_type)

    # MARK: Construct Query

    query_template = """
    SELECT
        (COUNT(DISTINCT ?lexeme) as ?total)

    WHERE {{
        ?lexeme a ontolex:LexicalEntry .
        {language_filter}
        {data_type_filter}
    }}
    """

    language_filter = (
        f"?lexeme dct:language wd:{language_qid} ."
        if language_qid
        else "?lexeme dct:language ?language ."
    )

    data_type_filter = (
        f"?lexeme wikibase:lexicalCategory wd:{data_type_qid} ."
        if data_type_qid
        else "?lexeme wikibase:lexicalCategory ?category ."
    )

    query = query_template.format(
        language_filter=language_filter, data_type_filter=data_type_filter
    )

    # MARK: Query Results

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try_count = 0
    max_retries = 2
    results = None

    while try_count <= max_retries and results is None:
        try:
            results = sparql.query().convert()

        except HTTPError as http_err:
            print(f"HTTPError occurred: {http_err}")

        except IncompleteRead as read_err:
            print(f"Incomplete read error occurred: {read_err}")

        try_count += 1

        if results is None:
            if try_count <= max_retries:
                print("The query will be retried...")

            else:
                print("Query failed after retries.")

    # Check if the query returned any results.
    if (
        "results" in results
        and "bindings" in results["results"]
        and len(results["results"]["bindings"]) > 0
    ):
        total_lexemes = int(results["results"]["bindings"][0]["total"]["value"])

        output_template = ""
        if language:
            output_template += f"\nLanguage: {language.capitalize()}\n"

        if data_type:
            output_template += f"Data type: {data_type}\n"

        output_template += f"Total number of lexemes: {total_lexemes:,}\n"
        if do_print:
            print(output_template)

        return total_lexemes

    else:
        print("Total number of lexemes: Not found")
        return None


# MARK: Wrapper


def total_wrapper(
    language: Union[str, List[str]] = None,
    data_type: Union[str, List[str]] = None,
    all_bool: bool = False,
) -> None:
    """
    Conditionally provides the full functionality of the total command.
    Now accepts lists for language and data type to output a table of total lexemes.

    Parameters
    ----------
        language : Union[str, List[str]]
            The language(s) to potentially total data types for.

        data_type : Union[str, List[str]]
            The data type(s) to check for.

        all_bool : boolean
            Whether all languages and data types should be listed.
    """

    if (not language and not data_type) and all_bool:
        print_total_lexemes()

    elif isinstance(language, list) or isinstance(data_type, list):
        languages = language if isinstance(language, list) else [language]
        data_types = data_type if isinstance(data_type, list) else [data_type]

        print(f"{'Language':<20} {'Data Type':<25} {'Total Lexemes':<25}")
        print("=" * 70)

        for lang in languages:
            first_row = (
                True  # flag to check if it's the first data type for the language
            )
            for dt in data_types:
                total_lexemes = get_total_lexemes(
                    language=lang, data_type=dt, do_print=False
                )
                total_lexemes = (
                    f"{total_lexemes:,}" if total_lexemes is not None else "N/A"
                )
                if first_row:
                    print(f"{lang:<20} {dt:<25} {total_lexemes:<25}")
                    first_row = False
                else:
                    print(
                        f"{'':<20} {dt:<25} {total_lexemes:<25}"
                    )  # print empty space for language
            print()

    elif language is not None and data_type is None:
        print_total_lexemes(language=language)

    elif language is not None and not all_bool:
        get_total_lexemes(language=language, data_type=data_type)

    elif language is not None:
        print(
            f"You have already specified language {language.capitalize()} and data type {data_type} - no need to specify --all."
        )
        get_total_lexemes(language=language, data_type=data_type)

    else:
        raise ValueError("Invalid input or missing information")
