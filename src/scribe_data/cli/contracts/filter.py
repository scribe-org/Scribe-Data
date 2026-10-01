# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for filtering data by data contracts.
"""

import json
import os
from pathlib import Path
from typing import Any

import yaml

from scribe_data.cli.generate.generate_utils import extract_data_contract_values
from scribe_data.utils import (
    DATA_CONTRACTS_DIR,
    DEFAULT_FILTERED_JSON_EXPORT_DIR,
    DEFAULT_JSON_EXPORT_DIR,
    data_type_metadata,
    get_language_from_iso,
)

# MARK: Filter Metadata


def filter_contract_metadata(contract_file: Path) -> dict[str, list[str]]:
    """
    Extract the data fields required by a language-specific data contract file.

    Parameters
    ----------
    contract_file : Path
        Path to the YAML contract file for a specific language.

    Returns
    -------
    dict[str, list[str]]
        A dictionary mapping each lexeme data type in the contract to the fields it requires.

        {
            'nouns': ['gender', 'nominativePlural', 'nominativeSingular'],
            'verbs': ['indicativePresentFirstPersonSingular', ...],
        }.
    """
    try:
        with open(contract_file, "r", encoding="utf-8") as f:
            contract_data = yaml.safe_load(f) or {}

        return {
            data_type: extract_data_contract_values(contract_entry=contract_entry)
            for data_type, contract_entry in contract_data.items()
            if data_type_metadata.get(data_type) and isinstance(contract_entry, dict)
        }

    except (yaml.YAMLError, IOError) as e:
        print(f"Error processing {contract_file}: {e}")
        return {}


# MARK: Filter Export Data


def filter_exported_data(
    input_file: Path, contract_metadata: dict[str, list[str]], data_type: str
) -> dict[str, Any]:
    """
    Filter exported language data based on contract metadata requirements.

    This function processes JSON export files, keeping only the data forms
    specified in the corresponding language contract.

    Parameters
    ----------
    input_file : Path
        Path to the input JSON file with exported language data.

    contract_metadata : dict[str, list[str]]
        The fields required by each data type as returned by filter_contract_metadata().

    data_type : str
        Type of data to filter (e.g. 'nouns', 'verbs' or 'prepositions').

    Returns
    -------
    dict[str, Any]
        Filtered dictionary of lexemes, containing only specified forms.
        Preserves 'lastModified' and 'lexemeID' for each lexeme.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            exported_data = json.load(f)

        filtered_data = {}

        # Determine which columns to keep based on contract metadata.
        columns_to_keep = contract_metadata.get(data_type)
        if not columns_to_keep:
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


# MARK: Export Filtered Data


def export_data_filtered_by_contracts(
    contracts_dir: Path, input_dir: Path, output_dir: Path
) -> None:
    """
    Export contract-filtered data to a new directory with a standardized structure.

    This function processes data contracts for all languages, filtering and
    exporting data that meets the specified contract requirements.

    Parameters
    ----------
    contracts_dir : Path, optional, default=DATA_CONTRACTS_DIR
        Directory containing the contracts to filter with.

    input_dir : Path, optional, default=DEFAULT_JSON_EXPORT_DIR
        Directory containing original JSON export data.

    output_dir : Path, optional, default=DEFAULT_FILTERED_JSON_EXPORT_DIR
        Directory to export filtered contract data.

    Returns
    -------
    None
        Prints information on the data that has been filtered.
    """
    # Use provided output dir or default.
    export_dir = Path(output_dir) if output_dir else DEFAULT_FILTERED_JSON_EXPORT_DIR
    export_dir.mkdir(parents=True, exist_ok=True)

    input_dir = input_dir or DEFAULT_JSON_EXPORT_DIR

    contracts_dir = Path(contracts_dir) if contracts_dir else DATA_CONTRACTS_DIR

    for contract_filename in os.listdir(contracts_dir):
        if not contract_filename.endswith(".yaml"):
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

        lang_input_dir = Path(input_dir) / matched_language.lower().replace(" ", "_")
        if not lang_input_dir.exists():
            print(f"No input directory found for {matched_language}")
            continue

        data_files = list(lang_input_dir.glob("*.json"))
        for input_file in data_files:
            data_type = (
                input_file.stem
            )  # e.g., nouns, verbs, prepositions, translations

            # Skip unsupported types if needed.
            if data_type not in contract_metadata:
                output_file = (
                    export_dir
                    / matched_language.lower().replace(" ", "_")
                    / f"{data_type}.json"
                )
                output_file.parent.mkdir(parents=True, exist_ok=True)

                with (
                    open(input_file, "r", encoding="utf-8") as src,
                    open(output_file, "w", encoding="utf-8") as dst,
                ):
                    dst.write(src.read())

                print(f"Copied unfiltered {data_type} for {matched_language}")
                continue

            # Filter if contract metadata exists.
            if filtered_data := filter_exported_data(
                input_file, contract_metadata, data_type
            ):
                output_file = (
                    export_dir
                    / matched_language.lower().replace(" ", "_")
                    / f"{data_type}.json"
                )
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(filtered_data, f, ensure_ascii=False, indent=2)

                print(
                    f"Exported {matched_language} {data_type} with {len(filtered_data)} entries"
                )
