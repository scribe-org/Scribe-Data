"""
Utility functions for data extraction, formatting and loading.

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

import ast
import json
import os
import sys
from importlib import resources
from typing import Any, Optional

from iso639 import Lang
from iso639.exceptions import DeprecatedLanguageValue, InvalidLanguageValue

PROJECT_ROOT = "Scribe-Data"
DEFAULT_JSON_EXPORT_DIR = "scribe_data_json_export"
DEFAULT_CSV_EXPORT_DIR = "scribe_data_csv_export"
DEFAULT_TSV_EXPORT_DIR = "scribe_data_tsv_export"
DEFAULT_SQLITE_EXPORT_DIR = "scribe_data_sqlite_export"


def _load_json(package_path: str, file_name: str, root: str) -> Any:
    """
    Loads a JSON resource from a package into a python entity.

    Parameters
    ----------
        package_path : str
            The fully qualified package that contains the resource.

        file_name : str
            The name of the file (resource) that contains the JSON data.

        root : str
            The root node of the JSON document.

    Returns
    -------
        A python entity starting at 'root'.
    """

    with resources.files(package_path).joinpath(file_name).open(
        encoding="utf-8"
    ) as in_stream:
        contents = json.load(in_stream)
        return contents[root]


_languages = _load_json(
    package_path="scribe_data.resources",
    file_name="language_metadata.json",
    root="languages",
)


def _find(source_key: str, source_value: str, target_key: str, error_msg: str) -> Any:
    """
    Each 'language', (english, german,..., etc) is a dictionary of key/value pairs:

        entry = {
            "language": "english",
            "iso": "en",
            "qid": "Q1860",
            "remove-words": [...],
            "ignore-words": [...]
        }

    Given a key/value pair, the 'source' and the 'target' key get the 'target' value.

    Parameters
    ----------
        source_value : str
            The source value to find equivalents for (e.g. 'english').

        source_key : str
            The source key to reference (e.g. 'language').

        target_key : str
            The key to target (e.g. 'iso').

        error_msg : str
            The message displayed when a value cannot be found.

    Returns
    -------
        The 'target' value given the passed arguments.

    Raises
    ------
        ValueError : when a source_value is not supported.
    """
    norm_source_value = source_value.lower()

    if target_value := [
        entry[target_key]
        for entry in _languages
        if entry[source_key] == norm_source_value
    ]:
        assert len(target_value) == 1, f"More than one entry for '{norm_source_value}'"
        return target_value[0]

    raise ValueError(error_msg)


def get_scribe_languages() -> list[str]:
    """
    Returns the list of currently implemented Scribe languages.
    """
    return sorted(entry["language"].capitalize() for entry in _languages)


def get_language_qid(language: str) -> str:
    """
    Returns the QID of the given language.

    Parameters
    ----------
        language : str
            The language the QID should be returned for.

    Returns
    -------
        str
            The Wikidata QID for the language.
    """
    return _find(
        "language",
        language,
        "qid",
        f"{language.upper()} is currently not a supported language for QID conversion.",
    )


def get_language_iso(language: str) -> str:
    """
    Returns the ISO code of the given language.

    Parameters
    ----------
        language : str
            The language the ISO should be returned for.

    Returns
    -------
        str
            The ISO code for the language.
    """
    try:
        iso_code = str(Lang(language.capitalize()).pt1)
    except InvalidLanguageValue:
        raise ValueError(
            f"{language.capitalize()} is currently not a supported language for ISO conversion."
        ) from None
    return iso_code


def get_language_from_iso(iso: str) -> str:
    """
    Returns the language name for the given ISO.

    Parameters
    ----------
        iso : str
            The ISO the language name should be returned for.

    Returns
    -------
        str
            The name for the language which has an ISO value of iso.
    """
    try:
        language_name = str(Lang(iso.lower()).name)
    except DeprecatedLanguageValue as e:
        raise ValueError(
            f"{iso.upper()} is currently not a supported ISO language."
        ) from e
    return language_name


def get_language_words_to_remove(language: str) -> list[str]:
    """
    Returns the words that should be removed during the data cleaning process for the given language.

    Parameters
    ----------
        language : str
            The language the words should be returned for.

    Returns
    -------
        list[str]
            The words that that be removed during the data cleaning process for the given language.
    """
    return _find(
        "language",
        language,
        "remove-words",
        f"{language.capitalize()} is currently not a supported language.",
    )


def get_language_words_to_ignore(language: str) -> list[str]:
    """
    Returns the words that should not be included as autosuggestions for the given language.

    Parameters
    ----------
        language : str
            The language the words should be returned for.

    Returns
    -------
        list[str]
            The words that should not be included as autosuggestions for the given language.
    """
    return _find(
        "language",
        language,
        "ignore-words",
        f"{language.capitalize()} is currently not a supported language.",
    )


def load_queried_data(
    file_path: str, language: str, data_type: str
) -> tuple[Any, bool, str]:
    """
    Loads queried data from a JSON file for a specific language and data type.

    Parameters
    ----------
        file_path : str
            The path to the file containing the queried data.

        language : str
            The language for which the data is being loaded.

        data_type : str
            The type of data being loaded (e.g. 'nouns', 'verbs').

    Returns
    -------
        tuple[Any, bool, str]
            A tuple containing the loaded data, a boolean indicating whether the data is in use,
            and the path to the data file.
    """
    queried_data_file = f"{data_type}_queried.json"
    update_data_in_use = False

    if f"language_data_extraction/{language}/{data_type}/" not in file_path:
        data_path = queried_data_file
    else:
        update_data_in_use = True
        PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
        LANG_DIR_PATH = f"{PATH_TO_SCRIBE_ORG}/Scribe-Data/src/scribe_data/language_data_extraction/{language}"
        data_path = f"{LANG_DIR_PATH}/{data_type}/{queried_data_file}"

    with open(data_path, encoding="utf-8") as f:
        return json.load(f), update_data_in_use, data_path


def export_formatted_data(
    formatted_data: dict, update_data_in_use: bool, language: str, data_type: str
) -> None:
    """
    Exports formatted data to a JSON file for a specific language and data type.

    Parameters
    ----------
        formatted_data : dict
            The data to be exported.

        update_data_in_use : bool
            A flag indicating whether the data is currently in use.

        language : str
            The language for which the data is being exported.

        data_type : str
            The type of data being exported (e.g. 'nouns', 'verbs').

    Returns
    -------
        None
    """
    if update_data_in_use:
        PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
        export_path = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/{DEFAULT_JSON_EXPORT_DIR}/{language}/{data_type.replace('-', '_')}.json"

    else:
        export_path = f"{data_type.replace('-', '_')}.json"

    with open(export_path, "w", encoding="utf-8") as file:
        json.dump(formatted_data, file, ensure_ascii=False, indent=0)
        file.write("\n")

    print(
        f"Wrote file {language}/{data_type.replace('-', '_')}.json with {len(formatted_data):,} {data_type}."
    )


def get_path_from_format_file() -> str:
    """
    Returns the directory path from a data formatting file to scribe-org.
    """
    return "../../../../../.."


def get_path_from_wikidata_dir() -> str:
    """
    Returns the directory path from the wikidata directory to scribe-org.
    """
    return "../../../.."


def get_ios_data_path(language: str) -> str:
    """
    Returns the path to the data json of the iOS app given a language.

    Parameters
    ----------
        language : str
            The language the path should be returned for.

    Returns
    -------
        str
            The path to the data json for the given language.
    """
    return f"Scribe-iOS/Keyboards/LanguageKeyboards/{language}"


def check_command_line_args(
    file_name: str, passed_values: Any, values_to_check: list[str]
) -> list[str]:
    """
    Checks command line arguments passed to Scribe-Data files.

    Parameters
    ----------
        file_name : str
            The name of the file for clear error outputs if necessary.

        passed_values : UNKNOWN (will be checked)
            An argument to be checked against known values.

        values_to_check : list(str)
            The values that should be checked against.

    Returns
    -------
        args: list(str)
            The arguments or an error are returned depending on if they're correct.
    """
    try:
        args = ast.literal_eval(passed_values)
    except ValueError as invalid_arg:
        raise ValueError(
            f"""The argument type of '{passed_values}' passed to {file_name} is invalid.
            Only lists are allowed, and can be passed via:
            python {file_name} '["comma_separated_args_in_quotes"]'
            """
        ) from invalid_arg

    if not isinstance(args, list):
        raise ValueError(
            f"""The argument type of '{passed_values}' passed to {file_name} is invalid.
            Only lists are allowed, and can be passed via:
            python {file_name} '["comma_separated_args_in_quotes"]'
            """
        )

    if set(args).issubset(values_to_check):
        return args

    args_list = ", ".join(values_to_check)[:-1] + ", or " + values_to_check[-1]
    raise ValueError(
        f"""An invalid argument '{passed_values}' was specified.
            Please choose from {args_list}.
            Pass arguments via the following:
            python {file_name} '["comma_separated_args_in_quotes"]'
            """
    )


def check_and_return_command_line_args(
    all_args: list[str],
    first_args_check: list[str] = None,
    second_args_check: list[str] = None,
) -> tuple[Optional[list[str]], Optional[list[str]]]:
    """
    Checks command line arguments passed to Scribe-Data files and returns them if correct.

    Parameters
    ----------
        all_args : list[str]
            The arguments passed to the Scribe-Data file.

        first_args_check : list[str]
            The values that the first argument should be checked against.

        second_args_check : list[str]
            The values that the second argument should be checked against.

    Returns
    -------
        first_args, second_args: Tuple[Optional[list[str]], Optional[list[str]]]
            The subset of possible first and second arguments that have been verified as being valid.
    """
    if len(all_args) == 1:
        return None, None

    if len(all_args) == 2:
        arg_1 = all_args[1]
        first_args = check_command_line_args(
            file_name=all_args[0], passed_values=arg_1, values_to_check=first_args_check
        )

        return first_args, None

    if len(all_args) == 3:
        arg_1 = all_args[1]
        arg_2 = all_args[2]

        first_args = check_command_line_args(
            file_name=all_args[0], passed_values=arg_1, values_to_check=first_args_check
        )
        second_args = check_command_line_args(
            file_name=all_args[0],
            passed_values=arg_2,
            values_to_check=second_args_check,
        )

        return first_args, second_args

    raise ValueError(
        f"""An invalid number of arguments were specified.
        At this time only two sets of values can be passed.
        Pass argument sets via the following:
        python {all_args[0]} '["comma_separated_sets_in_quotes"]'
        """
    )


def get_target_langcodes(source_lang: str) -> list[str]:
    """
    Returns a list of target language ISO codes for translation.

    Parameters
    ----------
        source_lang : str
            The source language being translated from.

    Returns
    -------
        list[str]
            A list of target language ISO codes.
    """
    return [
        get_language_iso(lang) for lang in get_scribe_languages() if lang != source_lang
    ]


def map_genders(wikidata_gender: str) -> str:
    """
    Maps genders from Wikidata to succinct versions.

    Parameters
    ----------
        wikidata_gender : str
            The gender of the noun that was queried from WikiData.
    """
    gender_map = {
        "masculine": "M",
        "Q499327": "M",
        "feminine": "F",
        "Q1775415": "F",
        "common gender": "C",
        "Q1305037": "C",
        "neuter": "N",
        "Q1775461": "N",
    }

    return gender_map.get(
        wikidata_gender, ""
    )  # nouns could have a gender that is not a valid attribute


def map_cases(wikidata_case: str) -> str:
    """
    Maps cases from Wikidata to more succinct versions.

    Parameters
    ----------
        wikidata_case : str
            The case of the noun that was queried from WikiData.
    """
    case_map = {
        "accusative": "Acc",
        "Q146078": "Acc",
        "dative": "Dat",
        "Q145599": "Dat",
        "genitive": "Gen",
        "Q146233": "Gen",
        "instrumental": "Ins",
        "Q192997": "Ins",
        "prepositional": "Pre",
        "Q2114906": "Pre",
        "locative": "Loc",
        "Q202142": "Loc",
    }
    case = wikidata_case.split(" case")[0]
    return case_map.get(case, "")


def order_annotations(annotation: str) -> str:
    """
    Standardizes the annotations that are provided to users where more than one is applicable.

    Parameters
    ----------
        annotation : str
            The annotation to be returned to the user in the command bar.
    """
    if "/" not in annotation:
        return annotation

    # Remove repeat annotations, if present.
    annotation_split = sorted(list(set(filter(None, annotation.split("/")))))

    return "/".join(annotation_split)
