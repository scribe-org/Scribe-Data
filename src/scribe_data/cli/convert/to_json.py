# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to convert data returned from the Scribe-Data CLI to JSON files.
"""

import csv
import json
from pathlib import Path

from scribe_data.utils import (
    DEFAULT_JSON_EXPORT_DIR,
    camel_to_snake,
    check_index_exists,
)

# MARK: JSON


def convert_to_json(
    language: str,
    data_types: str | list[str] | None,
    input_file: Path,
    output_type: str,
    overwrite: bool = False,
    identifier_case: str = "camel",
) -> None:
    """
    Convert a CSV/TSV file to JSON.

    Parameters
    ----------
    language : str
        The language of the file to convert.

    data_types : Union[str, List[str]]
        The data type of the file to convert.

    input_file : Path
        The input CSV/TSV file path.

    output_type : str
        The output format, should be "json".

    overwrite : bool
        Whether to overwrite existing files.

    identifier_case : str
        The case format for identifiers. Default is "camel".

    Returns
    -------
    None
        A JSON file.
    """
    if not language:
        raise ValueError(f"Language '{language.capitalize()}' is not recognized.")

    data_types = [data_types] if isinstance(data_types, str) else data_types

    if not data_types:
        return

    json_output_dir = Path(DEFAULT_JSON_EXPORT_DIR) / language.capitalize()
    json_output_dir.mkdir(parents=True, exist_ok=True)

    for dtype in data_types:
        if not input_file.exists():
            print(f"No data found for {dtype} conversion at '{input_file}'.")
            continue

        delimiter = {".csv": ",", ".tsv": "\t"}.get(input_file.suffix.lower())

        if not delimiter:
            raise ValueError(
                f"Unsupported file extension '{input_file.suffix}' for {str(input_file)}. Please provide a '.csv' or '.tsv' file."
            )

        try:
            with input_file.open("r", encoding="utf-8") as file:
                reader = csv.DictReader(file, delimiter=delimiter)
                rows = list(reader)

                if not rows:
                    print(f"No data found in '{input_file}'.")
                    continue

                # Use the first row to inspect column headers.
                first_row = rows[0]
                keys = list(first_row.keys())
                data: dict = {}

                if len(keys) == 1:
                    # Handle Case: { key: None }.
                    for row in rows:
                        data[row[keys[0]]] = None

                elif len(keys) == 2:
                    # Handle Case: { key: value }.
                    for row in rows:
                        key = (
                            camel_to_snake(row[keys[0]])
                            if identifier_case == "snake"
                            else row[keys[0]]
                        )
                        value = row[keys[1]]
                        data[key] = value

                elif len(keys) > 2:
                    if all(col in first_row for col in ["emoji", "is_base", "rank"]):
                        # Handle Case: { key: [ { emoji: ..., is_base: ..., rank: ... }, { emoji: ..., is_base: ..., rank: ... } ] }.
                        for row in rows:
                            if reader.fieldnames and len(reader.fieldnames) > 0:
                                if identifier_case == "snake":
                                    raw_value = row.get(reader.fieldnames[0])
                                    key = camel_to_snake(raw_value or "")

                                else:
                                    key = row.get(reader.fieldnames[0])

                            emoji = row.get("emoji", "").strip()
                            is_base = (
                                row.get("is_base", "false").strip().lower() == "true"
                            )
                            rank = row.get("rank", None)
                            rank = int(rank) if rank and rank.isdigit() else None

                            entry = {"emoji": emoji, "is_base": is_base, "rank": rank}

                            if key is None:
                                continue

                            data.setdefault(key, []).append(entry)

                    else:
                        # Handle Case: { key: { value1: ..., value2: ... } }.
                        for row in rows:
                            data[row[keys[0]]] = {
                                (
                                    camel_to_snake(k)
                                    if identifier_case == "snake"
                                    else k
                                ): row[k]
                                for k in keys[1:]
                            }

        except (IOError, csv.Error) as e:
            print(f"Error reading '{input_file}': {e}")
            continue

        # Define output file path
        output_file = json_output_dir / f"{dtype}.{output_type}"

        if check_index_exists(output_file, overwrite):
            print(f"Skipping {dtype}")
            continue

        try:
            with output_file.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

        except IOError as e:
            print(f"Error writing to '{output_file}': {e}")
            continue

        print(f"Data for {language.capitalize()} {dtype} written to {output_file}")
