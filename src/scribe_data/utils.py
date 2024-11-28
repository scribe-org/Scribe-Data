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
import re
from importlib import resources
from pathlib import Path
from typing import Any, Optional

# MARK: Utils Variables

PROJECT_ROOT = "Scribe-Data"
DEFAULT_JSON_EXPORT_DIR = "scribe_data_json_export"
DEFAULT_CSV_EXPORT_DIR = "scribe_data_csv_export"
DEFAULT_TSV_EXPORT_DIR = "scribe_data_tsv_export"
DEFAULT_SQLITE_EXPORT_DIR = "scribe_data_sqlite_export"

LANGUAGE_DATA_EXTRACTION_DIR = (
    Path(__file__).parent / "wikidata" / "language_data_extraction"
)

LANGUAGE_METADATA_FILE = Path(__file__).parent / "resources" / "language_metadata.json"
DATA_TYPE_METADATA_FILE = (
    Path(__file__).parent / "resources" / "data_type_metadata.json"
)
LEXEME_FORM_METADATA_FILE = (
    Path(__file__).parent / "resources" / "lexeme_form_metadata.json"
)
DATA_DIR = Path(DEFAULT_JSON_EXPORT_DIR)

try:
    with LANGUAGE_METADATA_FILE.open("r", encoding="utf-8") as file:
        language_metadata = json.load(file)

except (IOError, json.JSONDecodeError) as e:
    print(f"Error reading language metadata: {e}")


try:
    with DATA_TYPE_METADATA_FILE.open("r", encoding="utf-8") as file:
        data_type_metadata = json.load(file)

except (IOError, json.JSONDecodeError) as e:
    print(f"Error reading data type metadata: {e}")

try:
    with LEXEME_FORM_METADATA_FILE.open("r", encoding="utf-8") as file:
        lexeme_form_metadata = json.load(file)

except (IOError, json.JSONDecodeError) as e:
    print(f"Error reading lexeme form metadata: {e}")


language_map = {}
language_to_qid = {}

# Process each language and its potential sub-languages in one pass.
for lang, lang_data in language_metadata.items():
    if "sub_languages" in lang_data:
        for sub_lang, sub_lang_data in lang_data["sub_languages"].items():
            sub_lang_lower = sub_lang
            sub_qid = sub_lang_data.get("qid")

            if sub_qid is None:
                print(
                    f"Warning: 'qid' missing for sub-language {sub_lang.capitalize()} of {lang.capitalize()}"
                )

            else:
                language_map[sub_lang_lower] = sub_lang_data
                language_to_qid[sub_lang_lower] = sub_qid

    else:
        qid = lang_data.get("qid")
        if qid is None:
            print(f"Warning: 'qid' missing for language {lang.capitalize()}")

        else:
            language_map[lang] = lang_data
            language_to_qid[lang] = qid


def _load_json(package_path: str, file_name: str) -> Any:
    """
    Loads a JSON resource from a package into a python entity.

    Parameters
    ----------
        package_path : str
            The fully qualified package that contains the resource.

        file_name : str
            The name of the file (resource) that contains the JSON data.

    Returns
    -------
        A python entity representing the JSON content.
    """
    with resources.files(package_path).joinpath(file_name).open(
        encoding="utf-8"
    ) as in_stream:
        return json.load(in_stream)


_languages = _load_json(
    package_path="scribe_data.resources", file_name="language_metadata.json"
)


def _find(source_key: str, source_value: str, target_key: str, error_msg: str) -> Any:
    """
    Finds a target value based on a source key/value pair from the language metadata.

    This version handles both regular languages and those with sub-languages (e.g., Norwegian).

    Parameters
    ----------
        source_value : str
            The source value to find equivalents for (e.g., 'english', 'nynorsk').

        source_key : str
            The source key to reference (e.g., 'language').

        target_key : str
            The key to target (e.g., 'qid').

        error_msg : str
            The message displayed when a value cannot be found.

    Returns
    -------
        The 'target' value given the passed arguments.

    Raises
    ------
        ValueError : when a source_value is not supported or the language only has sub-languages.
    """
    # Check if we're searching by language name.
    if source_key == "language":
        # First, check the main language entries (e.g., mandarin, french, etc.).
        for language, entry in _languages.items():
            # If the language name matches the top-level key, return the target value.
            if language == source_value:
                if "sub_languages" in entry:
                    sub_languages = entry["sub_languages"].keys()
                    sub_languages = ", ".join(
                        lang.capitalize() for lang in sub_languages
                    )
                    raise ValueError(
                        f"'{language.capitalize()}' has sub-languages, but is not queryable directly. Available sub-languages: {sub_languages}"
                    )
                return entry.get(target_key)

            # If there are sub-languages, check them too.
            if "sub_languages" in entry:
                for sub_language, sub_entry in entry["sub_languages"].items():
                    if sub_language == source_value:
                        return sub_entry.get(target_key)

    # If no match was found, raise an error.
    raise ValueError(error_msg)


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
        source_key="language",
        source_value=language.split(" ")[0],
        target_key="qid",
        error_msg=f"{language.capitalize()} is currently not a supported language for QID conversion.",
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

    return _find(
        source_key="language",
        source_value=language.split(" ")[0],
        target_key="iso",
        error_msg=f"{language.capitalize()} is currently not a supported language for ISO conversion.",
    )


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
    # Iterate over the languages and their properties.
    for language, properties in _languages.items():
        # Check if the current language's ISO matches the provided ISO.
        if properties.get("iso") == iso:
            return language.capitalize()

        # If there are sub-languages, check those as well.
        if "sub_languages" in properties:
            for sub_lang, sub_properties in properties["sub_languages"].items():
                if sub_properties.get("iso") == iso:
                    return sub_lang.capitalize()

    # If no match is found, raise a ValueError.
    raise ValueError(f"{iso.upper()} is currently not a supported ISO language.")


def load_queried_data(
    dir_path: str, language: str, data_type: str
) -> tuple[Any, bool, str]:
    """
    Loads queried data from a JSON file for a specific language and data type.

    Parameters
    ----------
        dir_path : str
            The path to the directory containing the queried data.

        language : str
            The language for which the data is being loaded.

        data_type : str
            The type of data being loaded (e.g. 'nouns', 'verbs').

    Returns
    -------
        tuple(Any, str)
            A tuple containing the loaded data and the path to the data file.
    """
    data_path = (
        Path(dir_path) / language.lower().replace(" ", "_") / f"{data_type}.json"
    )

    with open(data_path, encoding="utf-8") as f:
        return json.load(f), data_path


def remove_queried_data(dir_path: str, language: str, data_type: str) -> None:
    """
    Removes queried data for a specific language and data type as a new formatted file has been generated.

    Parameters
    ----------
        dir_path : str
            The path to the directory containing the queried data.

        language : str
            The language for which the data is being loaded.

        data_type : str
            The type of data being loaded (e.g. 'nouns', 'verbs').

    Returns
    -------
        None : The file is deleted.
    """
    data_path = (
        Path(dir_path)
        / language.lower().replace(" ", "_")
        / f"{data_type}_queried.json"
    )

    try:
        os.remove(data_path)

    except OSError:
        pass


def export_formatted_data(
    dir_path: str,
    formatted_data: dict,
    language: str,
    data_type: str,
    query_data_in_use: bool = False,
) -> None:
    """
    Exports formatted data to a JSON file for a specific language and data type.

    Parameters
    ----------
        dir_path : str
            The path to the directory containing the queried data.

        formatted_data : dict
            The data to be exported.

        language : str
            The language for which the data is being exported.

        data_type : str
            The type of data being exported (e.g. 'nouns', 'verbs').

    Returns
    -------
        None
    """
    export_path = (
        Path(dir_path)
        / language.lower().replace(" ", "_")
        / f"{data_type.replace('-', '_')}.json"
    )

    with open(export_path, "w", encoding="utf-8") as file:
        json.dump(formatted_data, file, ensure_ascii=False, indent=0)
        file.write("\n")

    print(
        f"Wrote file {language.lower()}/{data_type.replace('-', '_')}.json with {len(formatted_data):,} {data_type}."
    )


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
            The path to the language folder for the given language.
    """
    return Path("Scribe-iOS") / "Keyboards" / "LanguageKeyboards" / f"{language}"


def get_android_data_path() -> str:
    """
    Returns the path to the data json of the Android app given a language.

    Parameters
    ----------
        language : str
            The language the path should be returned for.

    Returns
    -------
        str
            The path to the assets data folder for the application.
    """
    return Path("Scribe-Android") / "app" / "src" / "main" / "assets" / "data"


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


def format_sublanguage_name(lang, language_metadata=_languages):
    """
    Formats the name of a sub-language by appending its main language
    in the format 'SUB_LANG MAIN_LANG'. If the language is not a sub-language,
    the original language name is returned as-is.

    Parameters
    ----------
        lang : str
            The name of the language or sub-language to format.

        language_metadata : dict
            The metadata containing information about main languages and their sub-languages.

    Returns
    -------
        str
            The formatted language name if it's a sub-language (e.g., 'Nynorsk Norwegian').
            Otherwise the original name.

    Raises
    ------
        ValueError: If the provided language or sub-language is not found.

    Example
    -------
        > format_sublanguage_name("nynorsk", language_metadata)
        'Nynorsk Norwegian'

        > format_sublanguage_name("english", language_metadata)
        'English'
    """
    for main_lang, lang_data in language_metadata.items():
        # If it's not a sub-language, return the original name.
        if main_lang == lang:
            return lang

        # Check if the main language has sub-languages.
        lang = lang.split(" ")[0]
        if "sub_languages" in lang_data:
            # Check if the provided language is a sub-language.
            for sub_lang in lang_data["sub_languages"]:
                if lang == sub_lang:
                    # Return the formatted name SUB_LANG MAIN_LANG.
                    return f"{sub_lang} {main_lang}"

    # Raise ValueError if no match is found.
    raise ValueError(f"{lang.capitalize()} is not a valid language or sub-language.")


def list_all_languages(language_metadata=_languages):
    """
    Returns a sorted list of all languages from the provided metadata dictionary, including sub-languages.
    """
    current_languages = []

    # Iterate through the language metadata.
    for lang_key, lang_data in language_metadata.items():
        # Check if there are sub-languages.
        if "sub_languages" in lang_data:
            # Add the sub-languages to current_languages.
            current_languages.extend(
                [f"{sub} {lang_key}" for sub in lang_data["sub_languages"].keys()]
            )
        else:
            # If no sub-languages, add the main language.
            current_languages.append(lang_key)

    return sorted(current_languages)


def list_languages_with_metadata_for_data_type(language_metadata=_languages):
    """
    Returns a sorted list of languages and their metadata (name, iso, qid) for a specific data type.
    The list includes sub-languages where applicable.
    """
    current_languages = []

    # Iterate through the language metadata.
    for lang_key, lang_data in language_metadata.items():
        # Check if there are sub-languages.
        if "sub_languages" in lang_data:
            # Add the sub-languages to current_languages with metadata.
            for sub_key, sub_data in lang_data["sub_languages"].items():
                current_languages.append(
                    {
                        "name": f"{lang_data.get('name', lang_key)}/{sub_data.get('name', sub_key)}",
                        "iso": sub_data.get("iso", ""),
                        "qid": sub_data.get("qid", ""),
                    }
                )
        else:
            # If no sub-languages, add the main language with metadata.
            current_languages.append(
                {
                    "name": lang_data.get("name", lang_key),
                    "iso": lang_data.get("iso", ""),
                    "qid": lang_data.get("qid", ""),
                }
            )

    return sorted(current_languages, key=lambda x: x["name"])


# MARK: Case Conversion


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
