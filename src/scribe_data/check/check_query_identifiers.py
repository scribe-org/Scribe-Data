import re
from pathlib import Path

from scribe_data.cli.cli_utils import (
    LANGUAGE_DATA_EXTRACTION_DIR,
    language_metadata,
    data_type_metadata,
)


def extract_qid_from_sparql(file_path: Path, pattern: str) -> str:
    """
    Extract the QID based on the pattern provided (either language or data type).
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            match = re.search(pattern, content)
            if match:
                return match.group(0).replace("wd:", "")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None


def check_queries():
    language_pattern = r"\?lexeme dct:language wd:Q\d+"
    data_type_pattern = r"wikibase:lexicalCategory wd:Q\d+"
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
        print("Queries with incorrect languages QIDs are:")
        for file in incorrect_languages:
            print(f"- {file}")

    if incorrect_data_types:
        print("Queries with incorrect data type QIDs are:")
        for file in incorrect_data_types:
            print(f"- {file}")


def is_valid_language(query_file, lang_qid):
    lang_directory_name = query_file.parent.parent.name.lower()
    languages = language_metadata.get(
        "languages"
    )  # might not work since language_metadata file is not fully updated
    language_entry = next(
        (lang for lang in languages if lang["language"] == lang_directory_name), None
    )

    if not language_entry:
        print(
            f"Warning: Language '{lang_directory_name}' not found in language_metadata.json."
        )
        return False

    expected_language_qid = language_entry["qid"]
    print("Expected language QID:", expected_language_qid)

    if lang_qid != expected_language_qid:
        print(
            f"Incorrect language QID in {lang_directory_name}. "
            f"Found: {lang_qid}, Expected: {expected_language_qid}"
        )
        return False
    return True


def is_valid_data_type(query_file, data_type_qid):
    directory_name = query_file.parent.name  # e.g., "nouns" or "verbs"
    expected_data_type_qid = data_type_metadata.get(directory_name)

    if data_type_qid != expected_data_type_qid:
        print(
            f"Warning: Incorrect data type QID in {query_file}. Found: {data_type_qid}, Expected: {expected_data_type_qid}"
        )
        return False
    return True


# Examples:

# file_path = Path("French/verbs/query_verbs.sparql")
# print(is_valid_data_type(file_path, "QW24907")) # check for data type
# print(is_valid_language(file_path, "Q150")) # check for if valid language

check_queries()
