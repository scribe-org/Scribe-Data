"""
Update Utils
------------

Utility functions for data extraction, formatting and loading.

Contents:
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
from typing import Any


def get_scribe_languages() -> list[str]:
    """
    Returns the list of currently implemented Scribe languages.
    """
    return [
        "English",
        "French",
        "German",
        "Italian",
        "Portuguese",
        "Russian",
        "Spanish",
        "Swedish",
    ]


def get_language_qid(language: str) -> str:
    """
    Returns the QID of the given language.

    Parameters
    ----------
        language : str
            The language the QID should be returned for.

    Returns
    -------
        The Wikidata QID for the language as a value of a dictionary.
    """
    language = language.lower()

    language_qid_dict = {
        "english": "Q1860",
        "french": "Q150",
        "german": "Q188",
        "italian": "Q652",
        "portuguese": "Q5146",
        "russian": "Q7737",
        "spanish": "Q1321",
        "swedish": "Q9027",
    }

    if language not in language_qid_dict:
        raise ValueError(
            f"{language.upper()} is currently not a supported language for QID conversion."
        )

    return language_qid_dict[language]


def get_language_iso(language: str) -> str:
    """
    Returns the ISO code of the given language.

    Parameters
    ----------
        language : str
            The language the ISO should be returned for.

    Returns
    -------
        The ISO code for the language as a value of a dictionary.
    """
    language = language.lower()

    language_iso_dict = {
        "english": "en",
        "french": "fr",
        "german": "de",
        "italian": "it",
        "portuguese": "pt",
        "russian": "ru",
        "spanish": "es",
        "swedish": "sv",
    }

    if language not in language_iso_dict:
        raise ValueError(
            f"{language.capitalize()} is currently not a supported language for ISO conversion."
        )

    return language_iso_dict[language]


def get_language_from_iso(iso: str) -> str:
    """
    Returns the language name for the given ISO.

    Parameters
    ----------
        iso : str
            The ISO the language name should be returned for.

    Returns
    -------
        The name for the language as a value of a dictionary.
    """
    iso = iso.lower()

    iso_language_dict = {
        "en": "English",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "es": "Spanish",
        "sv": "Swedish",
    }

    if iso not in iso_language_dict:
        raise ValueError(f"{iso.upper()} is currently not a supported ISO language.")

    return iso_language_dict[iso]


def get_language_words_to_remove(language: str) -> list[str]:
    """
    Returns the words that should not be included as autosuggestions for the given language.

    Parameters
    ----------
        language : str
            The language the words should be returned for.

    Returns
    -------
        The words that should not be included as autosuggestions for the given language as values of a dictionary.
    """
    language = language.lower()
    words_to_remove: dict[str, list[str]] = {
        "english": [
            "of",
            "the",
            "The",
            "and",
        ],
        "french": [
            "of",
            "the",
            "The",
            "and",
        ],
        "german": ["of", "the", "The", "and", "NeinJa", "et", "redirect"],
        "italian": ["of", "the", "The", "and", "text", "from"],
        "portuguese": ["of", "the", "The", "and", "jbutadptflora"],
        "russian": [
            "of",
            "the",
            "The",
            "and",
        ],  # and all non-Cyrillic characters
        "spanish": ["of", "the", "The", "and"],
        "swedish": ["of", "the", "The", "and", "Checklist", "Catalogue"],
    }

    if language not in words_to_remove:
        raise ValueError(
            f"{language.capitalize()} is currently not a supported language."
        )

    return words_to_remove[language]


def get_language_words_to_ignore(language: str) -> list[str]:
    """
    Returns the words that should not be included as autosuggestions for the given language.

    Parameters
    ----------
        language : str
            The language the words should be returned for.

    Returns
    -------
        The words that should not be included as autosuggestions for the given language as values of a dictionary.
    """
    language = language.lower()
    words_to_ignore: dict[str, list[str]] = {
        "french": [
            "XXe",
        ],
        "german": ["Gemeinde", "Familienname"],
        "italian": ["The", "ATP"],
        "portuguese": [],
        "russian": [],
        "spanish": [],
        "swedish": ["databasdump"],
    }

    if language not in words_to_ignore:
        raise ValueError(
            f"{language.capitalize()} is currently not a supported language."
        )

    return words_to_ignore[language]


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
        The path to the data json for the given language.
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

    elif len(all_args) == 3:
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

    else:
        raise ValueError(
            f"""An invalid number of arguments were specified.
            At this time only two sets of values can be passed.
            Pass argument sets via the following:
            python {all_args[0]} '["comma_separated_sets_in_quotes"]'
            """
        )
