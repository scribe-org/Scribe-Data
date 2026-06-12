# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for checking data exports against their contracts.
"""

import json
from pathlib import Path

from scribe_data.cli.contracts.filter import (
    DEFAULT_DATA_CONTRACTS_DIR,
    DEFAULT_JSON_DIR,
    filter_contract_metadata,
)
from scribe_data.utils import get_language_from_iso, get_language_iso

data_contracts_langs = [
    f.stem for f in DEFAULT_DATA_CONTRACTS_DIR.iterdir() if f.is_file()
]

for i in range(len(data_contracts_langs)):
    data_contracts_langs[i] = get_language_from_iso(data_contracts_langs[i])


# MARK: Check Contracts


def check_contract_data_completeness(
    contracts_dir: Path = DEFAULT_DATA_CONTRACTS_DIR,
) -> dict[str, dict[str, list[str]]]:
    """
    Validate exported data contracts against their metadata requirements.

    This function checks if the exported data for a given language (or all languages)
    contains all the required forms specified in the data contracts.

    Parameters
    ----------
    contracts_dir : Path
        Directory containing the contracts to filter with.
        Defaults to DEFAULT_DATA_CONTRACTS_DIR.

    Returns
    -------
    Dict[str, Dict[str, List[str]]]
        A nested dictionary containing missing forms by language and data type.

        {
            'Language Name': {
                'nouns': ['missing_noun_form1', 'missing_noun_form2'],
                'verbs': ['missing_verb_form1']
            }
        }

        The above is the expected structure.
    """
    # Determine languages to check.
    languages_to_check = [
        get_language_from_iso(iso=Path(f).stem.lower())
        for f in contracts_dir.glob("*.yaml")
    ]
    languages_to_check = [
        lang
        for lang in languages_to_check
        if lang.lower() in [lang_item.lower() for lang_item in data_contracts_langs]
    ]

    missing_forms = {}
    for lang_dir_name in languages_to_check:
        lang = " ".join(word.capitalize() for word in lang_dir_name.split("_"))

        # Get ISO code and contract file.
        try:
            iso_code = get_language_iso(lang.lower())
            contract_file = contracts_dir / f"{iso_code.lower()}.yaml"

            if not contract_file.exists():
                print(f"Warning: No contract file found for {lang}")
                continue

        except ValueError:
            print(f"Warning: Could not find ISO code for {lang}")
            continue

        # Get contract metadata.
        contract_metadata = filter_contract_metadata(contract_file)
        export_lang_dir = DEFAULT_JSON_DIR / lang_dir_name

        # Check missing forms for nouns and verbs.
        lang_missing_forms = {}
        for data_type in ["nouns", "verbs"]:
            # Determine required forms.
            required_forms = (
                contract_metadata["nouns"]["numbers"]
                + contract_metadata["nouns"]["genders"]
                if data_type == "nouns"
                else contract_metadata["verbs"]["conjugations"]
            )

            exported_data_file = export_lang_dir / f"{data_type}.json"

            if not exported_data_file.exists():
                print(f"Warning: No exported data found for {lang} {data_type}")
                if required_forms:
                    lang_missing_forms[data_type] = required_forms
                continue

            try:
                with open(exported_data_file, "r", encoding="utf-8") as f:
                    exported_data = json.load(f)

            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading {exported_data_file}: {e}")
                if required_forms:
                    lang_missing_forms[data_type] = required_forms
                continue

            if missing_type_forms := [
                form
                for form in required_forms
                if all(
                    form not in lexeme_data for lexeme_data in exported_data.values()
                )
            ]:
                lang_missing_forms[data_type] = missing_type_forms

        # Add to overall missing forms if any.
        if lang_missing_forms:
            missing_forms[lang] = lang_missing_forms

    return missing_forms


# MARK: Print Missing


def print_missing_forms(missing_forms: dict[str, dict[str, list[str]]]) -> None:
    """
    Print missing forms from data contracts.

    Parameters
    ----------
    missing_forms : Dict[str, Dict[str, List[str]]]
        A dictionary of missing forms, structured as returned by
        check_contract_data_completeness().
    """
    if not missing_forms:
        print("All languages have complete data contracts!")
        return

    print("Missing Forms:")
    for lang, data_types in missing_forms.items():
        print(f"\n{lang}:")
        for data_type, forms in data_types.items():
            print(f"  {data_type.capitalize()}:")
            for form in forms:
                print(f"    - {form}")


def check_contract_data_print_missing(contracts_dir: Path) -> None:
    """
    Check data contracts in the specified or default output directory to ensure data completeness.

    Parameters
    ----------
    contracts_dir : Path
        Directory containing the contracts to filter with.
        Defaults to DEFAULT_DATA_CONTRACTS_DIR.
    """

    contracts_dir = Path(contracts_dir) if contracts_dir else DEFAULT_DATA_CONTRACTS_DIR

    if not contracts_dir.exists():
        print(
            f"Error: Directory {contracts_dir} does not exist.\nPlease provide a valid path to the data contracts or don't pass an argument to use the default contracts."
        )
        return

    missing_forms = check_contract_data_completeness(contracts_dir=contracts_dir)
    print_missing_forms(missing_forms)
