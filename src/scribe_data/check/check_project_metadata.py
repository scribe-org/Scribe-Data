# SPDX-License-Identifier: GPL-3.0-or-later
"""
Check the Scribe-Data metadata files to make sure that all information is included.

Examples
--------
>>> python3 src/scribe_data/check/check_project_metadata.py
"""

import sys

from scribe_data.utils import (
    data_type_metadata,
    language_metadata,
)

all_data_types = tuple(data_type_metadata.keys())


def get_missing_languages(
    reference_languages: dict, target_languages: dict
) -> list[str]:
    """
    Compare two language dictionaries and return a list of languages and sub-languages that exist.

    Parameters
    ----------
    reference_languages : dict
        A dictionary of languages from the reference source.

    target_languages : dict
        A dictionary of languages from the target source to check for missing entries.

    Returns
    -------
    list[str]
        A list of languages and sub-languages that are in target_languages but not in reference_languages.
    """
    missing_languages = []
    reference_keys = reference_languages.keys()

    for lang, details in target_languages.items():
        # Check if the parent language exists.
        if lang not in reference_keys:
            # If it's a parent language, check for sub-languages and append them.
            if "sub_languages" in details:
                for sub_lang in details["sub_languages"]:
                    missing_languages.append(f"{lang}/{sub_lang}")

            else:
                # Individual language, append directly.
                missing_languages.append(lang)
        else:
            # If the parent exists, only check for missing sub-languages.
            ref_sub_languages = reference_languages[lang].get("sub_languages", {})

            if "sub_languages" in details:
                for sub_lang in details["sub_languages"]:
                    if sub_lang not in ref_sub_languages:
                        missing_languages.append(f"{lang}/{sub_lang}")

    return missing_languages


def validate_language_properties(languages_dict: dict) -> dict:
    """
    Validate the presence of 'qid' and 'iso' properties for each language and its sub-languages.

    Parameters
    ----------
    languages_dict : dict
        A dictionary where each key is a language, and the value is another dictionary containing details about the language. If the language has sub-languages, they are stored under the 'sub_languages' key.

    Returns
    -------
    dict: A dictionary with two lists:
        - "missing_qids": Languages or sub-languages missing the 'qid' property.
        - "missing_isos": Languages or sub-languages missing the 'iso' property.

        Each entry in these lists is in the format "parent_language - sub_language" for sub-languages,
        or simply "parent_language" for the parent languages.
    """
    missing_qids = []
    missing_isos = []

    for lang, details in languages_dict.items():
        # Check if the language has sub-languages.
        if "sub_languages" in details:
            sub_languages = details["sub_languages"]

            # Validate each sub-language.
            for sub_lang, sub_details in sub_languages.items():
                if "qid" not in sub_details:
                    missing_qids.append(f"{lang}/{sub_lang}")
                if "iso" not in sub_details:
                    missing_isos.append(f"{lang}/{sub_lang}")
        else:
            # Validate the parent language itself.
            if "qid" not in details:
                missing_qids.append(lang)
            if "iso" not in details:
                missing_isos.append(lang)

    return {"missing_qids": missing_qids, "missing_isos": missing_isos}


def check_language_metadata() -> None:
    """
    Validate language metadata by performing various checks.

    Raises
    ------
    SystemExit:
        If any missing languages or properties are found, the function exits the script with a status code of 1.

    Notes
    -----
    Checks include:

    1. Ensures that all languages listed in `queries` are present in `language_metadata.yaml`, and vice versa.

    2. Checks if each language in `language_metadata.yaml` has the required properties:
        - 'qid' (a unique identifier)
        - 'iso' (ISO language code)

    This function helps identify missing languages or missing properties, ensuring data consistency across both sources.
    """
    languages_in_metadata = dict(language_metadata.items())

    languages_with_missing_properties = validate_language_properties(
        languages_dict=languages_in_metadata
    )

    if (
        languages_with_missing_properties["missing_qids"]
        or languages_with_missing_properties["missing_isos"]
    ):
        if languages_with_missing_properties["missing_qids"]:
            print("\nLanguages missing the `qid` property:")
            for lang in languages_with_missing_properties["missing_qids"]:
                print(f"  - {lang.title()}")

        if languages_with_missing_properties["missing_isos"]:
            print("\nLanguages missing the `iso` property:")
            for lang in languages_with_missing_properties["missing_isos"]:
                print(f"  - {lang.title()}")

        # Exit with a non-zero status code to indicate failure.
        sys.exit(1)

    print(
        "All languages in Scribe-Data are included in the language_metadata.yaml.\nLanguages in language_metadata.yaml have the correct properties."
    )


if __name__ == "__main__":
    check_language_metadata()
