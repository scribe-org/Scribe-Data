# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for filtering data by data contracts.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

from scribe_data.utils import DEFAULT_JSON_EXPORT_DIR, get_language_from_iso

scribe_data_contracts = (
    Path(__file__).parent.parent.parent.parent.parent / "scribe_data_contracts"
)
DATA_CONTRACTS_EXPORT_DIR = (
    Path(__file__).parent.parent.parent.parent.parent
    / "scribe_data_filtered_json_export"
)


def filter_contract_metadata(contract_file: Path) -> Dict[str, Any]:
    """
    Extract and filter metadata from a language-specific data contract file.

    Parameters
    ----------
    contract_file : Path
        Path to the JSON contract file for a specific language.

    Returns
    -------
    Dict[str, Any]
        A structured dictionary containing filtered metadata with keys:
        - 'nouns': {'numbers': [...], 'genders': [...]}
        - 'verbs': {'conjugations': [...]}
    """
    try:
        with open(contract_file, "r", encoding="utf-8") as f:
            contract_data = json.load(f)

        filtered_metadata = {
            "nouns": {"numbers": [], "genders": []},
            "verbs": {"conjugations": []},
        }

        # Filter Numbers
        if "numbers" in contract_data:
            numbers = contract_data["numbers"]
            # Handle different possible structures of numbers.
            filtered_numbers = []

            # Case 1: Simple key-value pair like {"singular": "plural"}.
            if isinstance(numbers, dict):
                for key, value in numbers.items():
                    # Ignore empty strings
                    if key:
                        filtered_numbers.append(key)

                    # If value is a non-empty string, include it too.
                    if isinstance(value, str) and value:
                        filtered_numbers.append(value)

            # Case 2: List of number types.
            elif isinstance(numbers, list):
                # Filter out empty strings
                filtered_numbers = [n for n in numbers if n]

            # Case 3: String of number types.
            elif isinstance(numbers, str):
                # Split and filter out empty strings.
                filtered_numbers = [n for n in numbers.split() if n]

            # Remove duplicates and store
            filtered_metadata["nouns"]["numbers"] = list(set(filtered_numbers))

        # Filter Genders.
        if "genders" in contract_data:
            genders = contract_data["genders"]

            # Collect gender-related keys from all gender lists.
            gender_keys = []
            for gender_list in genders.values():
                if isinstance(gender_list, list):
                    # Filter out empty strings and "NOT_INCLUDED".
                    gender_keys.extend(
                        [g for g in gender_list if g and g != "NOT_INCLUDED"]
                    )

            # Remove duplicates and filter.
            filtered_metadata["nouns"]["genders"] = list(set(gender_keys))

        # Filter Conjugations.
        if "conjugations" in contract_data:
            conjugations = contract_data["conjugations"]

            # Collect all conjugation forms.
            conj_forms = set()

            # Handle nested conjugation structure.
            if isinstance(conjugations, dict):
                for tense_group in conjugations.values():
                    if isinstance(tense_group, dict):
                        for person_group in tense_group.values():
                            if isinstance(person_group, dict):
                                for form in person_group.values():
                                    # Handle both string and list forms.
                                    if isinstance(form, str):
                                        # Remove square brackets and split.
                                        cleaned_forms = [
                                            f.strip()
                                            for f in form.replace("[", "")
                                            .replace("]", "")
                                            .split()
                                            if not f.startswith("[")
                                            and not f.endswith("]")
                                        ]
                                        conj_forms.update(cleaned_forms)
                                    elif isinstance(form, list):
                                        # Remove square brackets.
                                        cleaned_forms = [
                                            f
                                            for f in form
                                            if not isinstance(f, str)
                                            or (
                                                not f.startswith("[")
                                                and not f.endswith("]")
                                            )
                                        ]
                                        conj_forms.update(cleaned_forms)

            # If conjugations is a string, split it.
            elif isinstance(conjugations, str):
                # Remove square brackets and split.
                cleaned_forms = [
                    f.strip()
                    for f in conjugations.replace("[", "").replace("]", "").split()
                    if not f.startswith("[") and not f.endswith("]")
                ]
                conj_forms.update(cleaned_forms)

            # If conjugations is a list, use it directly.
            elif isinstance(conjugations, list):
                # Remove square bracketed items.
                cleaned_forms = [
                    f
                    for f in conjugations
                    if not isinstance(f, str)
                    or (not f.startswith("[") and not f.endswith("]"))
                ]
                conj_forms.update(cleaned_forms)

            # Store unique conjugation forms.
            filtered_metadata["verbs"]["conjugations"] = list(conj_forms)

        return filtered_metadata

    except (json.JSONDecodeError, IOError) as e:
        print(f"Error processing {contract_file}: {e}")
        return {}


def filter_exported_data(
    input_file: Path, contract_metadata: Dict[str, Any], data_type: str
) -> Dict[str, Any]:
    """
    Filter exported language data based on contract metadata requirements.

    This function processes JSON export files, keeping only the data forms
    specified in the corresponding language contract.

    Parameters
    ----------
    input_file : Path
        Path to the input JSON file with exported language data.

    contract_metadata : Dict[str, Any]
        Metadata from the language's contract file.

    data_type : str
        Type of data to filter ('nouns' or 'verbs').

    Returns
    -------
    Dict[str, Any]
        Filtered dictionary of lexemes, containing only specified forms.
        Preserves 'lastModified' and 'lexemeID' for each lexeme.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            exported_data = json.load(f)

        filtered_data = {}

        # Determine which columns to keep based on contract metadata.
        if data_type == "nouns":
            columns_to_keep = (
                contract_metadata["nouns"]["numbers"]
                + contract_metadata["nouns"]["genders"]
            )

        elif data_type == "verbs":
            columns_to_keep = contract_metadata["verbs"]["conjugations"]

        else:
            return {}

        # Filter each lexeme's data.
        for lexeme_id, lexeme_data in exported_data.items():
            filtered_lexeme = {
                "lastModified": lexeme_data.get("lastModified", ""),
                "lexemeID": lexeme_id,
            }

            # Add only the specified columns.
            for col in columns_to_keep:
                if col in lexeme_data:
                    filtered_lexeme[col] = lexeme_data[col]

            # Only add if we have more than just lastModified and lexemeID.
            if len(filtered_lexeme) > 2:
                filtered_data[lexeme_id] = filtered_lexeme

        return filtered_data

    except (json.JSONDecodeError, IOError) as e:
        print(f"Error processing {input_file}: {e}")
        return {}


def export_data_filtered_by_contracts(
    contracts_dir: str = None, input_dir: str = None, output_dir: str = None
):
    """
    Export contract-filtered data to a new directory with a standardized structure.

    This function processes data contracts for all languages, filtering and
    exporting data that meets the specified contract requirements.

    Parameters
    ----------
    contracts_dir : str, optional
        Directory containing the contracts to filter with.
        Defaults to scribe_data_contracts.

    input_dir : str, optional
        Directory containing original JSON export data.
        Defaults to DEFAULT_JSON_EXPORT_DIR.

    output_dir : str, optional
        Directory to export filtered contract data.
        Defaults to scribe_data_filtered_* based on the data type.

    Returns
    -------
    None
        Prints information on the data that has been filtered.
    """
    # Use provided output dir or default.
    export_dir = Path(output_dir) if output_dir else DATA_CONTRACTS_EXPORT_DIR
    export_dir.mkdir(parents=True, exist_ok=True)

    input_dir = input_dir or DEFAULT_JSON_EXPORT_DIR

    if not contracts_dir:
        contracts_dir = scribe_data_contracts

    for contract_filename in os.listdir(contracts_dir):
        if not contract_filename.endswith(".json"):
            continue

        language_name = os.path.splitext(contract_filename)[0].lower()
        contract_file = contracts_dir / contract_filename

        matched_language = get_language_from_iso(language_name)

        if not matched_language:
            print(f"Warning: Could not find language match for {language_name}")
            continue

        # Filter metadata for this contract.
        contract_metadata = filter_contract_metadata(contract_file)

        if not contract_metadata:
            continue

        # Create language directory in export path.
        lang_export_dir = export_dir / matched_language.lower().replace(" ", "_")
        lang_export_dir.mkdir(parents=True, exist_ok=True)

        # Data types to process.
        data_types = ["nouns", "verbs"]

        for data_type in data_types:
            # Input file path.
            input_file = (
                Path(input_dir)
                / matched_language.lower().replace(" ", "_")
                / f"{data_type}.json"
            )

            # Skip if input file doesn't exist.
            if not input_file.exists():
                print(f"No {data_type} data found for {matched_language}")
                continue

            # Export filtered data.
            if filtered_data := filter_exported_data(
                input_file, contract_metadata, data_type
            ):
                output_file = lang_export_dir / f"{data_type}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(filtered_data, f, ensure_ascii=False, indent=2)

                print(
                    f"Exported {matched_language} {data_type} with {len(filtered_data)} entries"
                )
