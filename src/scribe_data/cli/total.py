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

from SPARQLWrapper import JSON

from scribe_data.cli.cli_utils import language_to_qid
from scribe_data.wikidata.wikidata_utils import sparql

# Dictionary to map data types to their Wikidata Q-IDs.
data_type_to_qid = {
    "nouns": "Q1084",
    "prepositions": "Q37649",
    "verbs": "Q24905",
    "translations": "Q7553789",
}


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
        The QID corresponding to the input string, or None if not found.
    """
    if input_str:
        input_str_lower = input_str.lower()
        if input_str_lower in language_to_qid:
            return language_to_qid[input_str_lower]

        elif input_str_lower in data_type_to_qid:
            return data_type_to_qid[input_str_lower]

    return None


def get_total_lexemes(language, data_type):
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

    language_qid = get_qid_by_input(language)
    data_type_qid = get_qid_by_input(data_type)

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

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Check if the query returned any results.
    if (
        "results" in results
        and "bindings" in results["results"]
        and len(results["results"]["bindings"]) > 0
    ):
        total_lexemes = int(results["results"]["bindings"][0]["total"]["value"])

        output_template = ""
        if language:
            output_template += f"Language: {language}\n"

        if data_type:
            output_template += f"Data type: {data_type}\n"

        output_template += f"Total number of lexemes: {total_lexemes}"
        print(output_template)

    else:
        print("Total number of lexemes: Not found")
