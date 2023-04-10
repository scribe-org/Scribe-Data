"""
Update Utils
------------

Utility functions for data updates.

Contents:
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
    add_num_commas
"""


def get_language_qid(language):
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
            f"{language.upper()} is not currently not a supported language for QID conversion."
        )

    return language_qid_dict[language]


def get_language_iso(language):
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
            f"{language.capitalize()} is not currently not a supported language for ISO conversion."
        )

    return language_iso_dict[language]


def get_language_from_iso(iso):
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
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "es": "Spanish",
        "sv": "Swedish",
    }

    if iso not in iso_language_dict:
        raise ValueError(
            f"{iso.upper()} is not currently not a supported ISO for language conversion."
        )

    return iso_language_dict[iso]


def get_language_words_to_remove(language):
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
    language_iso_dict = {
        "french": ["of", "the", "The", "and",],
        "german": ["of", "the", "The", "and", "NeinJa", "et", "redirect"],
        "italian": ["of", "the", "The", "and", "text", "from"],
        "portuguese": ["of", "the", "The", "and", "jbutadptflora"],
        "russian": ["of", "the", "The", "and",],  # and all non-Cyrillic characters
        "spanish": ["of", "the", "The", "and"],
        "swedish": ["of", "the", "The", "and", "Checklist", "Catalogue"],
    }

    return language_iso_dict[language]


def get_language_words_to_ignore(language):
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
    language_iso_dict = {
        "french": ["XXe",],
        "german": ["Gemeinde", "Familienname"],
        "italian": ["The", "ATP"],
        "portuguese": [],
        "russian": [],
        "spanish": [],
        "swedish": ["databasdump"],
    }

    return language_iso_dict[language]


def get_path_from_format_file():
    """
    Returns the directory path from a data formatting file to scribe-org.
    """
    return "../../../../../.."


def get_path_from_load_dir():
    """
    Returns the directory path from the load directory to scribe-org.
    """
    return "../../../.."


def get_path_from_et_dir():
    """
    Returns the directory path from the extract_transform directory to scribe-org.
    """
    return "../../../.."


def get_ios_data_path(language: str):
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


def get_android_data_path(language: str):
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


def get_desktop_data_path(language: str):
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


def add_num_commas(num):
    """
    Adds commas to a numeric string for readability.

    Parameters
    ----------
        num : int or float
            A number to have commas added to.

    Returns
    -------
        str_with_commas : str
            The original number with commas to make it more readable.
    """
    num_str = str(num)
    num_str_no_decimal = num_str.split(".")[0]
    decimal = num_str.split(".")[1] if "." in num_str else None

    str_list = num_str_no_decimal[::-1]
    str_list_with_commas = [
        f"{s}," if i % 3 == 0 and i != 0 else s for i, s in enumerate(str_list)
    ]

    str_list_with_commas = str_list_with_commas[::-1]
    str_with_commas = "".join(str_list_with_commas)

    return str_with_commas if decimal is None else f"{str_with_commas}.{decimal}"
