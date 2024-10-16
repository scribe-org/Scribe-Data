import re
from pathlib import Path

from scribe_data.cli.cli_utils import (
    LANGUAGE_DATA_EXTRACTION_DIR,
    language_metadata,
    data_type_metadata,
)


def extract_qid_from_sparql(file_path: Path, pattern: str) -> str:
    """
    Extracts the QID from a SPARQL query file based on the provided pattern.

    Parameters
    ----------
    file_path : Path
        The path to the SPARQL query file from which to extract the QID.
    pattern : str
        The regex pattern used to match the QID (either for language or data type).

    Returns
    -------
    str
        The extracted QID if found, otherwise None.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            match = re.search(pattern, content)
            if match:
                return match.group(0).split("wd:")[1]
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None


def check_queries():
    """
    Validates SPARQL queries in the specified directory to check for correct language
    and data type QIDs.

    This function scans all SPARQL query files in the LANGUAGE_DATA_EXTRACTION_DIR
    and prints out any files with incorrect QIDs for both languages and data types.
    """
    language_pattern = r"\?lexeme dct:language wd:Q\d+"
    data_type_pattern = r"wikibase:lexicalCategory\s+wd:Q\d+"
    incorrect_languages = []
    incorrect_data_types = []

    language_extraction_dir = LANGUAGE_DATA_EXTRACTION_DIR
    for query_file in language_extraction_dir.glob("**/*.sparql"):
        lang_qid = extract_qid_from_sparql(query_file, language_pattern)
        data_type_qid = extract_qid_from_sparql(query_file, data_type_pattern)

        # Validate language QID and data type QID
        if not is_valid_language(query_file, lang_qid):
            incorrect_languages.append(query_file)
        if not is_valid_data_type(query_file, data_type_qid):
            incorrect_data_types.append(query_file)

    if incorrect_languages:
        print("Incorrect Language QIDs found in the following files:")
        for file in incorrect_languages:
            print(f"- {file}")
    print("\n----------------------------------------------------------------\n")

    if incorrect_data_types:
        print("Incorrect Data Type QIDs found in the following files:")
        for file in incorrect_data_types:
            print(f"- {file}")
    print("\n----------------------------------------------------------------\n")


def is_valid_language(query_file: Path, lang_qid: str) -> bool:
    """
    Validates the language QID against the expected QID for the directory.

    Parameters
    ----------
    query_file : Path
        The path to the SPARQL query file being validated.
    lang_qid : str
        The QID of the language extracted from the SPARQL query.

    Returns
    -------
    bool
        True if the language QID is valid, otherwise False.
    """
    lang_directory_name = query_file.parent.parent.name.lower()
    languages = language_metadata.get(
        "languages"
    )  # might not work since language_metadata file is not fully updated
    language_entry = next(
        (lang for lang in languages if lang["language"] == lang_directory_name), None
    )

    if not language_entry:
        return False

    expected_language_qid = language_entry["qid"]

    if lang_qid != expected_language_qid:
        return False
    return True


def is_valid_data_type(query_file: Path, data_type_qid: str) -> bool:
    """
    Validates the data type QID against the expected QID for the directory.

    Parameters
    ----------
    query_file : Path
        The path to the SPARQL query file being validated.
    data_type_qid : str
        The QID of the data type extracted from the SPARQL query.

    Returns
    -------
    bool
        True if the data type QID is valid, otherwise False.
    """
    directory_name = query_file.parent.name  # e.g., "nouns" or "verbs"
    expected_data_type_qid = data_type_metadata.get(directory_name)

    if data_type_qid != expected_data_type_qid:
        return False
    return True


# Run the check_queries function
# MARK: TODO: Remove Call
# check_queries()
