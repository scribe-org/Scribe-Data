# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to check the total language data available on Wikidata.
"""

from http.client import IncompleteRead
from typing import Any, cast
from urllib.error import HTTPError

from SPARQLWrapper import JSON

from scribe_data.utils import (
    data_type_metadata,
    language_to_qid,
)
from scribe_data.wikidata.wikidata_utils import sparql

# MARK: QIDs


def get_qid_by_input(input_str: str | None) -> str | None:
    """
    Retrieve the QID for a given language or data type input string.

    Parameters
    ----------
    input_str : str, optional
        The input string representing a language or data type.

    Returns
    -------
    str | None
        The QID corresponding to the input string, or- None if not found.
    """
    if input_str:
        if input_str in language_to_qid:
            return language_to_qid[input_str]

        elif input_str in data_type_metadata:
            return data_type_metadata[input_str]

    return None


# MARK: Query Total


def query_total_lexemes(
    language: str, data_type: str, do_print: bool = True
) -> int | None:
    """
    Query the total number of lexemes for a given language and data type from Wikidata.

    Parameters
    ----------
    language : str
        The language for which to count lexemes.

    data_type : str
        The data type (e.g., "nouns", "verbs") for which to count lexemes.

    do_print : bool
        Print the total lexemes for the given language and data type.

    Returns
    -------
    str
        A formatted string indicating the language, data type and total number of lexemes, if found.
    """
    if (
        language is not None
        and (language.startswith("Q") or language.startswith("q"))
        and language[1:].isdigit()
    ):
        language_qid = language.capitalize()

    else:
        language_qid = get_qid_by_input(language)

    if (
        data_type is not None
        and (data_type.startswith("Q") or data_type.startswith("q"))
        and data_type[1:].isdigit()
    ):
        data_type_qid = data_type.capitalize()

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
                return None

    # Check if the query returned any results.
    if results is None:
        print("Total number of lexemes: Not found")
        return None

    res_dict = cast(dict[str, Any], results)
    if (
        "results" in res_dict
        and "bindings" in res_dict["results"]
        and len(res_dict["results"]["bindings"]) > 0
    ):
        total_lexemes = int(
            res_dict.get("results", {}).get("bindings", [])[0]["total"]["value"]
        )

        output_template = ""
        if language:
            output_template += f"\nLanguage: {language.capitalize()}\n"

        if data_type:
            output_template += f"Data type: {data_type}\n"

        output_template += f"Total number of lexemes: {total_lexemes:,}\n"
        if do_print:
            print(output_template)

        return total_lexemes

    print("Total number of lexemes: Not found")
    return None
