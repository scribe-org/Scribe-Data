"""
Utility functions for data extraction, formatting and loading.

Contents:
    _load_json,
    _find,
    get_scribe_languages,
    get_language_qid,
    get_language_iso,
    get_language_from_iso,
    get_language_words_to_remove,
    get_language_words_to_ignore,
    get_path_from_format_file,
    get_path_from_load_dir,
    get_path_from_et_dir,
    get_ios_data_path,
    get_android_data_path,
    get_desktop_data_path,
    check_command_line_args,
    check_and_return_command_line_args
"""

import ast
import json
import sys
from importlib import resources
from pathlib import Path
from typing import Any

import langcodes
from langcodes import Language

PROJECT_ROOT = "Scribe-Data"


def _load_json(package_path: str, file_name: str, root: str):
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
    # Add 'Scribe-Data/src' to PYTHONPATH so that resources.files() can find 'package_path'.
    parts = Path(__file__).resolve().parts
    prj_root_idx = parts.index(PROJECT_ROOT)
    package_root = str(Path(*parts[: prj_root_idx + 1], "src"))

    if package_root not in sys.path:
        sys.path.insert(0, package_root)

    with resources.files(package_path).joinpath(file_name).open(
        encoding="utf-8"
    ) as in_stream:
        contents = json.load(in_stream)
        return contents[root]


_languages = _load_json(
    package_path="scribe_data/resources",
    file_name="language_meta_data.json",
    root="languages",
)


def _find(source_key: str, source_value: str, target_key: str, error_msg: str):
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

    Raises
    ------
        ValueError : when a source_value is not supported.

    Returns
    -------
        The 'target' value given the passed arguments.
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
        iso_code = str(langcodes.find(language).language)
    except LookupError as e:
        raise ValueError(
            f"{language.capitalize()} is currently not a supported language for ISO conversion."
        ) from e
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

    language_name = str(Language.make(language=iso).display_name())
    if "Unknown language" in language_name:
        raise ValueError(f"{iso.upper()} is currently not a supported ISO language.")
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


def get_path_from_format_file() -> str:
    """
    Returns the directory path from a data formatting file to scribe-org.
    """
    return "../../../../../.."


def get_path_from_load_dir() -> str:
    """
    Returns the directory path from the load directory to scribe-org.
    """
    return "../../../.."


def get_path_from_et_dir() -> str:
    """
    Returns the directory path from the extract_transform directory to scribe-org.
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
    return f"/Scribe-iOS/Keyboards/LanguageKeyboards/{language}"


def get_android_data_path(language: str) -> str:
    """
    Returns the path to the data json of the Android app given a language.

    Parameters
    ----------
        language : str
            The language the path should be returned for.

    Returns
    -------
        str
            The path to the data json for the given language.
    """
    return f"/Scribe-Android/app/src/main/LanguageKeyboards/{language}"


def get_desktop_data_path(language: str) -> str:
    """
    Returns the path to the data json of the desktop app given a language.

    Parameters
    ----------
        language : str
            The language the path should be returned for.

    Returns
    -------
        str
            The path to the data JSON for the given language.
    """
    return f"/Scribe-Desktop/scribe/language_guis/{language}"


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
    all_args, first_args_check=None, second_args_check=None
):
    """
    Checks command line arguments passed to Scribe-Data files and returns them if correct.

    Parameters
    ----------
        all_args : list (str)
            The arguments passed to the Scribe-Data file.

        first_args_check : list(str)
            The values that the first argument should be checked against.

        second_args_check : list(str)
            The values that the second argument should be checked against.

    Returns
    -------
        first_args, second_args: list(str)
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
