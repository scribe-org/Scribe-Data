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
        languages_in_metadata = {
            lang["language"]: {"iso": lang["iso"], "qid": lang["qid"]}
            for lang in language_metadata["languages"]
        }  # current language metadata

        # languages_in_metadata = { # proposed language metadata
        #     key.lower(): value for key, value in language_metadata.items()
        # }  # Normalize keys to lowercase for case-insensitive comparison

except (IOError, json.JSONDecodeError) as e:
    print(f"Error reading language metadata: {e}")

try:
    with DATA_TYPE_METADATA_FILE.open("r", encoding="utf-8") as file:
        data_type_metadata = json.load(file)
        all_data_types = tuple(data_type_metadata.keys())

except (IOError, json.JSONDecodeError) as e:
    print(f"Error reading data type metadata: {e}")


def get_available_languages() -> dict[str, list[str]]:
    """
    Get available languages from the data extraction folder.
    Returns:
        dict[str, list[str]]: A dictionary with the language name as the key and a list of its sub-languages (if available) as the value.
    """
    extraction_dir = LANGUAGE_DATA_EXTRACTION_DIR
    available_languages = {}

    for lang_folder in extraction_dir.iterdir():
        if lang_folder.is_dir():  # Check if it's a directory
            lang_name = (
                lang_folder.name.lower()
            )  # Normalize keys to lowercase for case-insensitive comparison
            sub_languages = []
            has_data_type_sub_dir = False  # Track if we find valid data type matches

            # Check if lang_folder contains subdirectories
            for sub_folder in lang_folder.iterdir():
                if sub_folder.is_dir():
                    sub_lang_name = (
                        sub_folder.name.lower()
                    )  # Normalize to lowercase for case-insensitive comparison

                    # Check for almost similar keys using difflib
                    close_matches = difflib.get_close_matches(
                        sub_lang_name, all_data_types, n=1, cutoff=0.8
                    )

                    if close_matches:
                        has_data_type_sub_dir = True  # Found a valid data type match
                    else:
                        sub_languages.append(
                            sub_lang_name
                        )  # Append sub-language name if no close match found (not a data type)

            if (
                has_data_type_sub_dir
            ):  # Indicates that this language does not have sub-languages
                available_languages[
                    lang_name
                ] = {}  # Initialize the language entry without sub-languages
            else:
                available_languages[lang_name] = {}  # Initialize the language entry
                available_languages[lang_name]["sub_languages"] = (
                    sub_languages  # Add the associated sub-languages
                )

    return available_languages


def get_missing_languages(
    reference_languages: dict, target_languages: dict
) -> list[str]:
    """
    Compare two language dictionaries and return a list of languages and sub-languages
    that exist in target_languages but not in reference_languages.

    Parameters
    ----------
    reference_languages : dict
        A dictionary where the keys are language names and values are their details.
    target_languages : dict
        A dictionary where the keys are language names and values may include sub-languages.

    Returns
    -------
    list[str]
        A list of languages and sub-languages that are in target_languages but not in reference_languages.
    """
    missing_languages = []
    reference_keys = {lang for lang in reference_languages.keys()}

    for lang, details in target_languages.items():
        # Check if the parent language exists
        if lang not in reference_keys:
            # If it's a parent language, check for sub-languages and append them
            if "sub_languages" in details:
                for sub_lang in details["sub_languages"]:
                    missing_languages.append(f"{lang} - {sub_lang}")
            else:
                # Individual language, append directly
                missing_languages.append(lang)
        else:
            # If the parent exists, only check for missing sub-languages
            ref_sub_languages = reference_languages[lang].get("sub_languages", {})
            ref_sub_languages_keys = {sub for sub in ref_sub_languages}

            if "sub_languages" in details:
                for sub_lang in details["sub_languages"]:
                    if sub_lang not in ref_sub_languages_keys:
                        missing_languages.append(f"{lang} - {sub_lang}")

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
                print(lang.title())

        if missing_languages_extraction:
            print("\nThese languages are missing from language_data_extraction:")
            for lang in missing_languages_extraction:
                print(lang.title())

    else:
        print(
            "All languages match correctly between language_metadata.json and language_data_extraction."
        )


if __name__ == "__main__":
    check_language_metadata()
