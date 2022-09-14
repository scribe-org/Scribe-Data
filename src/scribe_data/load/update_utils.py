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
    return (
        f"/Scribe-Android/Keyboards/LanguageKeyboards/{language}/Data/{word_type}.json"
    )


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
