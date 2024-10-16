import os

# Expected languages and data types.
LANGUAGES = {
    "Arabic",
    "English",
    "Greek",
    "Italian",
    "Malayalam",
    "Russian",
    "Tamil",
    "Basque",
    "Esperanto",
    "Hausa",
    "Japanese",
    "Norwegian",
    "Slovak",
    "Ukrainian",
    "Bengali",
    "Estonian",
    "Hebrew",
    "Korean",
    "Pidgin",
    "Spanish",
    "Yoruba",
    "Chinese",
    "Finnish",
    "Hindustani",
    "Kurmanji",
    "Polish",
    "Swahili",
    "Czech",
    "French",
    "Indonesian",
    "Latin",
    "Portuguese",
    "Swedish",
    "Danish",
    "German",
    "Malay",
    "Punjabi",
    "Tajik",
}

DATA_TYPES = {
    "adjectives",
    "adverbs",
    "articles",
    "autosuggestions",
    "conjunctions",
    "emoji_keywords",
    "nouns",
    "personal_pronouns",
    "postpositions",
    "prepositions",
    "pronouns",
    "proper_nouns",
    "verbs",
}

# Sub-subdirectories expected for specific languages.
SUB_DIRECTORIES = {
    "Chinese": ["Mandarin"],
    "Hindustani": ["Urdu", "Hindi"],
    "Norwegian": ["Nynorsk", "Bokmål"],
    "Pidgin": ["Nigerian"],
    "Punjabi": ["Shahmukhi", "Gurmukhi"],
}


# Base directory path.
BASE_DIR = "../language_data_extraction"


def check_data_type_folders(path, language, subdir, errors):
    """
    Validate the contents of data type folders within a language directory.

    This function checks each data type folder for the presence of expected files
    and reports any unexpected files. It allows for multiple SPARQL query files,
    a format Python file, and a queried JSON file for each data type.

    Args:
    path (str): The path to the directory containing data type folders.
    language (str): The name of the language being processed.
    subdir (str or None): The name of the sub-directory (for languages with sub-dialects), or None.
    errors (list): A list to which error messages will be appended.

    The function checks for the following valid files in each data type folder:
    - Files starting with 'query_' and ending with '.sparql'
    - A 'format_{data_type}.py' file
    - A '{data_type}_queried.json' file

    It skips validation for the 'emoji_keywords' data type folder.

    Any files not matching these patterns (except '__init__.py') are reported as unexpected.
    """
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path) and item != "__init__.py":
            errors.append(f"Unexpected file found in {language}/{subdir or ''}: {item}")
        elif os.path.isdir(item_path):
            if item not in DATA_TYPES:
                errors.append(
                    f"Unexpected directory found in {language}/{subdir or ''}: {item}"
                )
            else:
                # Skip validation for emoji_keywords
                if item == "emoji_keywords":
                    continue

                # Check for correctly formatted files
                valid_files = [
                    f
                    for f in os.listdir(item_path)
                    if (f.startswith(f"query_{item}") and f.endswith(".sparql"))
                    or f == f"format_{item}.py"
                    or f == f"{item}_queried.json"
                ]

                for file in os.listdir(item_path):
                    if file not in valid_files and file != "__init__.py":
                        error_subdir = f"{subdir}/" or ""
                        errors.append(
                            f"Unexpected file in {language}/{error_subdir}{item}: {file}"
                        )


def validate_project_structure():
    """
    Validate that all directories follow the expected project structure and check for unexpected files and directories.
    Also validate SPARQL query file names in data_type folders and SUBDIRECTORIES.
    """
    errors = []

    if not os.path.exists(BASE_DIR):
        print(f"Error: Base directory '{BASE_DIR}' does not exist.")
        exit(1)

    # Check for unexpected files in BASE_DIR
    for item in os.listdir(BASE_DIR):
        item_path = os.path.join(BASE_DIR, item)
        if os.path.isfile(item_path) and item != "__init__.py":
            errors.append(f"Unexpected file found in BASE_DIR: {item}")

    # Iterate through the language directories
    for language in os.listdir(BASE_DIR):
        language_path = os.path.join(BASE_DIR, language)

        if not os.path.isdir(language_path) or language == "__init__.py":
            continue

        if language not in LANGUAGES:
            errors.append(f"Unexpected language directory: {language}")
            continue

        # Check for unexpected files in language directory
        for item in os.listdir(language_path):
            item_path = os.path.join(language_path, item)
            if os.path.isfile(item_path) and item != "__init__.py":
                errors.append(f"Unexpected file found in {language} directory: {item}")

        found_subdirs = {
            item
            for item in os.listdir(language_path)
            if os.path.isdir(os.path.join(language_path, item))
            and item != "__init__.py"
        }

        if language in SUB_DIRECTORIES:
            expected_subdirs = set(SUB_DIRECTORIES[language])
            unexpected_subdirs = found_subdirs - expected_subdirs
            missing_subdirs = expected_subdirs - found_subdirs

            if unexpected_subdirs:
                errors.append(
                    f"Unexpected sub-subdirectories in '{language}': {unexpected_subdirs}"
                )
            if missing_subdirs:
                errors.append(
                    f"Missing sub-subdirectories in '{language}': {missing_subdirs}"
                )

            # Check contents of expected sub-subdirectories
            for subdir in expected_subdirs:
                subdir_path = os.path.join(language_path, subdir)
                if os.path.exists(subdir_path):
                    check_data_type_folders(subdir_path, language, subdir, errors)

        else:
            check_data_type_folders(language_path, language, None, errors)

    if errors:
        print("Errors found:")
        for error in errors:
            print(f" - {error}")
        exit(1)

    else:
        print(
            "All directories and files are correctly named and organized, and no unexpected files or directories were found."
        )


if __name__ == "__main__":
    validate_project_structure()
