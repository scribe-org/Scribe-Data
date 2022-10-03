"""
Update Utils
------------

Utility functions for data updates.
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

    return language_iso_dict[language]


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


def get_path_from_update_data():
    """
    Returns the directory path from update_data.py to scribe-org.
    """
    return "../../../.."


def get_path_from_process_wiki():
    """
    Returns the directory path from process_wiki.py to scribe-org.
    """
    return "../../../.."


def get_ios_data_path(language: str, word_type: str):
    """
    Returns the path to the data json of the iOS app given a language and word type.

    Parameters
    ----------
        language : str
            The language the path should be returned for.

        word_type : str
            The type of word that should be accessed in the path.

    Returns
    -------
        The path to the data json for the given language and word type.
    """
    return f"/Scribe-iOS/Keyboards/LanguageKeyboards/{language}/Data/{word_type}.json"


def get_android_data_path(language: str, word_type: str):
    """
    Returns the path to the data json of the Android app given a language and word type.

    Parameters
    ----------
        language : str
            The language the path should be returned for.

        word_type : str
            The type of word that should be accessed in the path.

    Returns
    -------
        The path to the data json for the given language and word type.
    """
    return f"/Scribe-Android/app/src/main/LanguageKeyboards/{language}/Data/{word_type}.json"


def get_desktop_data_path(language: str, word_type: str):
    """
    Returns the path to the data json of the desktop app given a language and word type.

    Parameters
    ----------
        language : str
            The language the path should be returned for.

        word_type : str
            The type of word that should be accessed in the path.

    Returns
    -------
        The path to the data json for the given language and word type.
    """
    return f"/Scribe-Desktop/scribe/language_guis/{language}/data/{word_type}.json"


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
