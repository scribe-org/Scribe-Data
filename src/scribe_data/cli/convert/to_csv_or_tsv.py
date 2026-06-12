# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to convert data returned from the Scribe-Data CLI to CSV or TSV files.
"""

import csv
import json
from pathlib import Path

from scribe_data.utils import (
    DEFAULT_CSV_EXPORT_DIR,
    DEFAULT_JSON_EXPORT_DIR,
    DEFAULT_TSV_EXPORT_DIR,
    camel_to_snake,
    check_index_exists,
)

# MARK: CSV or TSV


def convert_to_csv_or_tsv(
    language: str,
    data_types: str | list[str],
    input_file: Path,
    output_type: str,
    overwrite: bool = False,
    identifier_case: str = "camel",
) -> None:
    """
    Convert a JSON File to CSV/TSV file.

    Parameters
    ----------
    language : str
        The language of the file to convert.

    data_types : Union[str, List[str]]
        The data type of the file to convert.

    input_file : Path
        The input JSON file path.

    output_type : str
        The output format, should be "csv" or "tsv".

    overwrite : bool
        Whether to overwrite existing files.

    identifier_case : str
        The case format for identifiers. Default is "camel".

    Returns
    -------
    None
        A CSV/TSV files.
    """
    if not language:
        raise ValueError(f"Language '{language.capitalize()}' is not recognized.")

    data_types = [data_types] if isinstance(data_types, str) else data_types

    # Modify input file path to use the provided input_file or default JSON export path.
    input_file_path = (
        input_file
        or DEFAULT_JSON_EXPORT_DIR / language.lower() / f"{data_types[0]}.json"
    )

    for dtype in data_types:
        if not input_file_path.exists():
            print(f"No data found for {dtype} conversion at '{input_file_path}'.")
            continue

        try:
            with input_file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading '{input_file_path}': {e}")
            continue

        # Determine the delimiter based on output type.
        delimiter = "," if output_type == "csv" else "\t"

        output_dir = (
            DEFAULT_CSV_EXPORT_DIR if output_type == "csv" else DEFAULT_TSV_EXPORT_DIR
        )

        final_output_dir = output_dir / language.capitalize()
        final_output_dir.mkdir(parents=True, exist_ok=True)

        output_file = final_output_dir / f"{dtype}.{output_type}"

        if check_index_exists(output_file, overwrite):
            print(f"Skipping {dtype}")
            continue

        try:
            with output_file.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file, delimiter=delimiter)

                # Handle different JSON structures based on the format.
                if isinstance(data, dict):
                    first_key = list(data.keys())[0]

                    first_val = next(iter(data.values())) if data else None
                    if isinstance(first_val, dict):
                        # Handle case: { key: { value1: ..., value2: ... } }.
                        columns = sorted(first_val.keys())
                        header = [
                            camel_to_snake(dtype[:-1])
                            if identifier_case == "snake"
                            else dtype[:-1]
                        ]
                        header += [
                            camel_to_snake(col) if identifier_case == "snake" else col
                            for col in columns
                        ]
                        writer.writerow(header)

                        for key, value in data.items():
                            row = [key] + [value.get(col, "") for col in columns]
                            writer.writerow(row)

                    elif isinstance(data[first_key], list):
                        if all(isinstance(item, dict) for item in data[first_key]):
                            # Handle case: { key: [ { value1: ..., value2: ... } ] }.
                            if "emoji" in data[first_key][0]:  # emoji specific case
                                columns = ["word", "emoji", "is_base", "rank"]
                                writer.writerow(
                                    [camel_to_snake(col) for col in columns]
                                    if identifier_case == "snake"
                                    else columns
                                )

                                for key, value in data.items():
                                    for item in value:
                                        row = [
                                            key,
                                            item.get("emoji", ""),
                                            item.get("is_base", ""),
                                            item.get("rank", ""),
                                        ]
                                        writer.writerow(row)

                            else:
                                if identifier_case == "snake":
                                    columns = [camel_to_snake(dtype[:-1])] + [
                                        camel_to_snake(col)
                                        for col in data[first_key][0].keys()
                                    ]

                                else:
                                    columns = [dtype[:-1]] + list(
                                        data[first_key][0].keys()
                                    )
                                writer.writerow(columns)

                                for key, value in data.items():
                                    for item in value:
                                        row = [key] + [
                                            item.get(col, "") for col in columns[1:]
                                        ]
                                        writer.writerow(row)

                        elif all(isinstance(item, str) for item in data[first_key]):
                            # Handle case: { key: [value1, value2, ...] }.
                            header = [
                                camel_to_snake(dtype[:-1])
                                if identifier_case == "snake"
                                else dtype[:-1]
                            ]
                            header += [
                                f"autosuggestion_{i + 1}"
                                for i in range(len(data[first_key]))
                            ]
                            writer.writerow(header)
                            for key, value in data.items():
                                row = [key] + value
                                writer.writerow(row)

                    else:
                        # Handle case: { key: value }.
                        writer.writerow(
                            [
                                camel_to_snake(dtype[:-1])
                                if identifier_case == "snake"
                                else dtype[:-1],
                                "value",
                            ]
                        )

                        for key, value in data.items():
                            writer.writerow([key, value])

        except IOError as e:
            print(f"Error writing to '{output_file}': {e}")
            continue

        print(f"Data for {language.capitalize()} {dtype} written to '{output_file}'")
