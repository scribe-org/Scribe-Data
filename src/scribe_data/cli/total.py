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

from scribe_data.cli.cli_utils import data_type_metadata as data_type_to_qid

from scribe_data.cli.cli_utils import (
    language_metadata,
    language_map,
    LANGUAGE_DATA_EXTRACTION_DIR,
)
from pathlib import Path
from scribe_data.utils import DEFAULT_JSON_EXPORT_DIR

LANGUAGE_METADATA_FILE = (
    Path(__file__).parent.parent / "resources" / "language_metadata.json"
)


data_type_to_qid = data_type_to_qid["data-types"]

DATA_TYPE_METADATA_FILE = (
    Path(__file__).parent.parent / "resources" / "data_type_metadata.json"
)
DATA_DIR = Path(DEFAULT_JSON_EXPORT_DIR)


DataType_LIST = {
    "nouns": "Q1084",
    "proper nouns": "Q147276",
    "pronouns": "Q36224",
    "personal pronouns": "Q468801",
    "verbs": "Q24905",
    "adjectives": "Q34698",
    "adverbs": "Q380057",
    "prepositions": "Q4833830",
    "postpositions": "Q161873",
    "conjunctions": "Q191536",
    "articles": "Q103184",
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
        The QID corresponding to the input string, or- None if not found.
    """
    if input_str:
        input_str_lower = input_str.lower()
        if input_str_lower in language_to_qid:
            return language_to_qid[input_str_lower]

        elif input_str_lower in data_type_to_qid:
            return data_type_to_qid[input_str_lower]

    return None


def get_datatype_list(language):
    languages = list(language_metadata["languages"])
    language_list = [lang["language"] for lang in languages]

    if language.lower() in language_list:
        language_data = language_map.get(language.lower())
        language_capitalized = language.capitalize()
        language_dir = LANGUAGE_DATA_EXTRACTION_DIR / language_capitalized

        if not language_data:
            raise ValueError(f"Language '{language}' is not recognized.")
        data_types = [f.name for f in language_dir.iterdir() if f.is_dir()]
        if not data_types:
            raise ValueError(
                f"No data types available for language '{language_capitalized}'."
            )

        data_types = sorted(data_types)
        data_types.remove("translations")  # removing translation from list
        return data_types

    else:
        print(f"language not present {language}")
        return None


def get_all_lexemes(language: str = None):
    """
    Get the total number of lexemes for all the languages and data types from Wikidata.

    Outputs
    -------
    str
        A formatted string indicating the language, data type, and total number of lexemes for all the languages, if found.
    """

    # get all the languages
    # get all the data types
    print("Please wait while we retrieve the data...\n")
    print(f"{'Language':<15} {'Data Type':<25} {'Total Number of Lexemes':<25}")
    print("=" * 65)

    # when language is none, we will get all the languages from metadata file
    if language is None:
        languages = list(language_metadata["languages"])
        languages.sort(key=lambda x: x["language"])
        language_list = [lang["language"] for lang in languages]

        for lang in language_list:
            # getting datatype of the language

            data_types = get_datatype_list(lang)

            first_row = True
            for dt in data_types:
                total_lexemes = print_total_lexemes(lang, dt, False)
                if first_row:
                    print(
                        f"{lang.capitalize():<15} {dt.replace('_', '-'): <25} {total_lexemes:<25}"
                    )
                    first_row = False
                else:
                    print(f"{'':<15} {dt.replace('_', '-'): <25} {total_lexemes:<25}")

    else:
        # if name passed we will check if we have their data then will send datatype of data we already have, else just get data
        if language.startswith("Q") and language[1:].isdigit():
            data_types = DataType_LIST
            first_row = True
            for dt_key, dt_value in data_types.items():
                total_lexemes = print_total_lexemes(language, dt_value, False)
                if first_row:
                    print(
                        f"{language.capitalize():<15} {dt_key.replace('_', '-'): <25} {total_lexemes:<25}"
                    )
                    first_row = False
                else:
                    print(
                        f"{'':<15} {dt_key.replace('_', '-'): <25} {total_lexemes:<25}"
                    )

        else:
            data_types = get_datatype_list(language)
            if data_types is None:
                print("Language is not present in Scribe")
                data_types = DataType_LIST
            first_row = True
            for dt in data_types:
                total_lexemes = print_total_lexemes(language, dt, False)
                if first_row:
                    print(
                        f"{language.capitalize():<15} {dt.replace('_', '-'): <25} {total_lexemes:<25}"
                    )
                    first_row = False
                else:
                    print(f"{'':<15} {dt.replace('_', '-'): <25} {total_lexemes:<25}")


def print_total_lexemes(language, data_type, doPrint=True):
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
        if doPrint:
            print(output_template)
    else:
        print("Total number of lexemes: Not found")

    return total_lexemes


def total_wrapper(
    language: str = None, data_type: str = None, all_bool: bool = False
) -> None:
    """
    Conditionally provides the full functionality of the total command.

    Parameters
    ----------
        language : str
            The language to potentially total data types for.

        data_type : str
            The data type to check for.

        all_bool : boolean
            Whether all languages and data types should be listed.
    """

    if (not language and not data_type) and all_bool:
        get_all_lexemes()

    elif language is not None and data_type is None:
        get_all_lexemes(language)

    elif language is not None and data_type is not None and not all_bool:
        print_total_lexemes(language, data_type)

    elif language is not None and data_type is not None and all_bool:
        print(
            f"You have already specified language: {language} and datatype: {data_type}, no need to specify -all"
        )
        print_total_lexemes(language, data_type)

    else:
        print("Invalid input or missing information")
