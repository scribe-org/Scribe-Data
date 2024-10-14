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
import json
import difflib

from scribe_data.cli.cli_utils import (
    LANGUAGE_DATA_EXTRACTION_DIR,
    data_type_metadata,
    language_map,
    language_metadata,
    language_to_qid,
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
        input_str_lower = input_str.lower()
        if input_str_lower in language_to_qid:
            return language_to_qid[input_str_lower]

        elif input_str_lower in data_type_metadata:
            return data_type_metadata[input_str_lower]

    return None


def get_datatype_list(language):
    """
    Get the data types for a given language based on the project directory structure.

    Parameters
    ----------
        language : str
            The language to return data types for.

    Returns
    -------
        data_types : list[str] or None
            A list of the corresponding data types.
    """
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

        for t in ["autosuggestions", "emoji_keywords"]:
            if t in data_types:
                data_types.remove(t)

        return data_types

    else:  # return all data types
        print("Language is not present in Scribe-Data. Checking all data types.")
        return data_type_metadata


# MARK: Print


def print_total_lexemes(language: str = None, language_mapping=None, data_type_mapping=None):
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
    elif language.startswith("Q") and language[1:].isdigit():
        print(f"Wikidata QID {language} passed. Checking all data types.\n")
    else:
        print(f"Returning total counts for {language} data types...\n")

    print(f"{'Language':<15} {'Data Type':<25} {'Total Wikidata Lexemes':<25}")
    print("=" * 64)

    if language is None:
        languages = list(language_mapping["languages"])
        languages.sort(key=lambda x: x["language"])
        language_list = [lang["language"] for lang in languages]
        for lang in language_list:
            data_types = get_datatype_list(lang)
            first_row = True
            for dt in data_types:
                total_lexemes = get_total_lexemes(lang, dt, False, language_mapping, data_type_mapping)
                total_lexemes = f"{total_lexemes:,}"
                if first_row:
                    print(f"{lang.capitalize():<15} {dt.replace('_', '-'): <25} {total_lexemes:<25}")
                    first_row = False
                else:
                    print(f"{'':<15} {dt.replace('_', ' '): <25} {total_lexemes:<25}")
            print()
    else:
        first_row = True
        if language.startswith("Q") and language[1:].isdigit():
            data_types = data_type_mapping
            for t in ["autosuggestions", "emoji_keywords"]:
                if t in data_types:
                    del data_types[t]
        else:
            data_types = get_datatype_list(language)
        for dt in data_types:
            total_lexemes = get_total_lexemes(language, dt, False, language_mapping, data_type_mapping)
            total_lexemes = f"{total_lexemes:,}"
            if first_row:
                print(f"{language.capitalize():<15} {dt.replace('_', '-'): <25} {total_lexemes:<25}")
                first_row = False
            else:
                print(f"{'':<15} {dt.replace('_', ' '): <25} {total_lexemes:<25}")
        print()


# MARK: Get Total


def get_total_lexemes(language, data_type, doPrint=True, language_mapping=None, data_type_mapping=None):
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
    try:
        # Validate language and data type, raise error if invalid.
        language_qid, data_type_qid = validate_language_and_data_type(language, data_type, language_mapping, data_type_mapping)

    except ValueError as e:
        print(str(e))
        return

    # SPARQL query construction
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

    # Assuming sparql is already initialized
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
            output_template += f"\nLanguage: {language}\n"

        if data_type:
            output_template += f"Data type: {data_type}\n"

        output_template += f"Total number of lexemes: {total_lexemes}\n"
        if doPrint:
            print(output_template)

        return total_lexemes

    else:
        print("Total number of lexemes: Not found")
        return None


# Load language and data type mappings


def load_mappings(language_file: str, data_type_file: str):
    """
    Load language and data type mappings from JSON files.

    Parameters
    ----------
    language_file : str
        The file path of the JSON file containing language mappings.
    
    data_type_file : str
        The file path of the JSON file containing data type mappings.

    Returns
    -------
    tuple
        A tuple containing two dictionaries:
        - language_mapping: A dictionary mapping language names to their QIDs.
        - data_type_mapping: A dictionary mapping data type names to their QIDs.
    """
    with open(language_file, 'r') as lang_file:
        language_mapping = json.load(lang_file)
    
    with open(data_type_file, 'r') as dt_file:
        data_type_mapping = json.load(dt_file)

    return language_mapping, data_type_mapping


# Helper function to find the closest match


def suggest_correction(user_input: str, valid_options: list):
    """
    Suggests the closest valid option for the given input by comparing it with a list of valid options.

    Parameters
    ----------
        user_input : str
            The incorrect string entered by the user.
        valid_options : list
            List of valid options to compare against.

    Returns
    -------
        str or None
            The closest valid option or None if no match is found.
    """
    closest_match = difflib.get_close_matches(user_input, valid_options, n=1)
    return closest_match[0] if closest_match else None


# MARK: Validate


def validate_language_and_data_type(language: str, data_type: str, language_mapping: dict, data_type_mapping: dict):
    """
    Validates that both the language and data type QIDs are correct or provides suggestions.

    Parameters
    ----------
        language : str
            The language string to validate.
        data_type : str
            The data type string to validate.

    Returns
    -------
        tuple
            A tuple of validated language QID and data type QID if valid.

    Raises
    ------
        ValueError
            If the language or data type is invalid.
    """
    language_qid = language_mapping.get(language.lower())
    data_type_qid = data_type_mapping.get(data_type.lower())

    if language_qid is None:
        suggestion = suggest_correction(language, list(language_mapping.keys()))
        if suggestion:
            raise ValueError(f"Invalid language. Did you mean '{suggestion}'?")
        else:
            raise ValueError("Invalid language. No suggestions found.")

    if data_type_qid is None:
        suggestion = suggest_correction(data_type, list(data_type_mapping.keys()))
        if suggestion:
            raise ValueError(f"Invalid data type. Did you mean '{suggestion}'?")
        else:
            raise ValueError("Invalid data type. No suggestions found.")

    return language_qid, data_type_qid


# MARK: Wrapper


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
        print_total_lexemes()

    elif language is not None and data_type is None:
        print_total_lexemes(language)

    elif language is not None and not all_bool:
        get_total_lexemes(language, data_type)

    elif language is not None:
        print(
            f"You have already specified language {language} and data type {data_type} - no need to specify --all."
        )
        get_total_lexemes(language, data_type)

    else:
        raise ValueError("Invalid input or missing information")
