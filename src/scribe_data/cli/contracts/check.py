# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for checking data exports against their contracts.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from scribe_data.cli.contracts.filter import (
    DEFAULT_JSON_EXPORT_DIR,
    filter_contract_metadata,
    scribe_data_contracts,
)
from scribe_data.utils import get_language_from_iso, get_language_iso

data_contracts_lang = [
    f.stem for f in Path(scribe_data_contracts).iterdir() if f.is_file()
]

for i in range(len(data_contracts_lang)):
    data_contracts_lang[i] = get_language_from_iso(data_contracts_lang[i])


def check_contracts(output_dir: Optional[str] = None) -> None:
    """
    Check data contracts in the specified or default output directory to ensure data completeness.

    Parameters
    ----------
    output_dir : Optional[str], optional
        Directory containing exported contract data.
        If None, uses the default DEFAULT_JSON_EXPORT_DIR.
    """
    export_dir = Path(output_dir or DEFAULT_JSON_EXPORT_DIR)

    if not export_dir.exists():
        print(
            f"Error: Directory {export_dir} does not exist.\nPlease use export JSON first."
        )
        return

    missing_forms = check_contract_data_completeness(export_dir)
    print_missing_forms(missing_forms)


def check_contract_data_completeness(
    export_dir: Path, language: Optional[str] = None
) -> Dict[str, Dict[str, List[str]]]:
    """
    Validate exported data contracts against their metadata requirements.

    This function checks if the exported data for a given language (or all languages)
    contains all the required forms specified in the data contracts.

    Parameters
    ----------
    export_dir : Path
        Directory containing exported contract data.

    language : Optional[str], optional
        Specific language to check. If None, checks all languages in the directory.

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
    if language:
        languages_to_check = [language]

    elif export_dir.exists():
        unique_dirs = {}
        for item in export_dir.iterdir():
            if item.is_dir():
                lower_name = item.name.lower()
                # Prioritize strictly lowercase directory names to avoid checking capitalized duplicates.
                if lower_name not in unique_dirs or item.name == lower_name:
                    unique_dirs[lower_name] = item.name

        languages_to_check = list(unique_dirs.values())

    else:
        languages_to_check = [
            Path(f).stem.lower() for f in scribe_data_contracts.glob("*.yaml")
        ]

    languages_to_check = [
        lang
        for lang in languages_to_check
        if lang.lower() in [lang_item.lower() for lang_item in data_contracts_lang]
    ]

    missing_forms = {}
    for lang_dir_name in languages_to_check:
        lang = " ".join(word.capitalize() for word in lang_dir_name.split("_"))

        # Get ISO code and contract file.
        try:
            iso_code = get_language_iso(lang.lower())
            contract_file = scribe_data_contracts / f"{iso_code.lower()}.yaml"

            if not contract_file.exists():
                print(f"Warning: No contract file found for {lang}")
                continue

        except ValueError:
            print(f"Warning: Could not find ISO code for {lang}")
            continue

        # Get contract metadata.
        contract_metadata = filter_contract_metadata(contract_file)
        export_lang_dir = export_dir / lang_dir_name

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


def print_missing_forms(missing_forms: Dict[str, Dict[str, List[str]]]) -> None:
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
