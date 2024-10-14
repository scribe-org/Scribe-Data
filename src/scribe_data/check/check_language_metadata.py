import difflib
import json
from pathlib import Path

LANGUAGE_DATA_EXTRACTION_DIR = Path(__file__).parent.parent / "language_data_extraction"

LANGUAGE_METADATA_FILE = (
    Path(__file__).parent.parent / "resources" / "language_metadata.json"
)

DATA_TYPE_METADATA_FILE = (
    Path(__file__).parent.parent / "resources" / "data_type_metadata.json"
)

try:
    with LANGUAGE_METADATA_FILE.open("r", encoding="utf-8") as file:
        language_metadata = json.load(file)
        languages_in_metadata = [
            lang["language"] for lang in language_metadata["languages"]
        ]

except (IOError, json.JSONDecodeError) as e:
    print(f"Error reading language metadata: {e}")

try:
    with DATA_TYPE_METADATA_FILE.open("r", encoding="utf-8") as file:
        data_type_metadata = json.load(file)
        all_data_types = tuple(data_type_metadata.keys())

except (IOError, json.JSONDecodeError) as e:
    print(f"Error reading data type metadata: {e}")


def get_available_languages() -> list[tuple[str, str]]:
    """
    Get available languages from the data extraction folder.
    Returns:
        list[tuple[str, str]]: A list of tuples with the language name and its QID.
    """
    extraction_dir = LANGUAGE_DATA_EXTRACTION_DIR
    available_languages = []
    for lang_folder in extraction_dir.iterdir():
        if lang_folder.is_dir():  # Check if it's a directory
            lang_name = lang_folder.name

            # Check if lang_folder contains subdirectories
            for sub_folder in lang_folder.iterdir():
                if sub_folder.is_dir():  # If a subdirectory exists
                    sub_lang_name = sub_folder.name

                    # Check for almost similar keys using difflib
                    close_matches = difflib.get_close_matches(
                        sub_lang_name.lower(), all_data_types, n=1, cutoff=0.8
                    )

                    if not close_matches:
                        available_languages.append(
                            sub_lang_name
                        )  # Append sub-language name if no close match found
                else:
                    available_languages.append(
                        lang_name
                    )  # Append just the main language if no subdirectories

    return available_languages


def get_missing_languages(
    reference_languages: list[str], target_languages: list[str]
) -> list[str]:
    """
    Compare two sources and return a list of languages that exist in target_languages but not in reference_languages.

    Parameters
    ----------
    reference_languages : list[str]
        A list of languages from the reference source.
    target_languages : list[str]
        A list of languages from the target source to check for missing entries.

    Returns
    -------
    list[str]
        A list of languages that are in target_languages but not in reference_languages.
    """
    # Convert both lists to lowercase for case-insensitive comparison
    reference_languages_lower = {lang.lower() for lang in reference_languages}
    missing_languages = [
        lang
        for lang in target_languages
        if lang.lower() not in reference_languages_lower
    ]

    return missing_languages


def check_language_metadata():
    """
    Check if there's any missing language in language_data_extraction or language_metadata.json
    """
    languages_in_directory = get_available_languages()
    missing_languages_metadata = get_missing_languages(
        languages_in_metadata, languages_in_directory
    )
    missing_languages_extraction = get_missing_languages(
        languages_in_directory, languages_in_metadata
    )

    if missing_languages_metadata or missing_languages_extraction:
        print(
            "There are missing languages or inconsistencies between language_metadata.json and language_data_extraction.\n"
        )

        if missing_languages_metadata:
            print("These languages are missing from language_metadata.json:")
            for lang in missing_languages_metadata:
                print(lang)

        if missing_languages_extraction:
            print("\nThese languages are missing from language_data_extraction:")
            for lang in missing_languages_extraction:
                print(lang)

    else:
        print(
            "All languages match correctly between language_metadata.json and language_data_extraction."
        )


if __name__ == "__main__":
    check_language_metadata()
