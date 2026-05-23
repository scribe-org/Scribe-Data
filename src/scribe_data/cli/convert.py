# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to convert data returned from the Scribe-Data CLI to other file types.
"""

import csv
import json
from pathlib import Path
from typing import List, Optional, Union

from scribe_data.load.data_to_sqlite import data_to_sqlite
from scribe_data.utils import (
    DEFAULT_CSV_EXPORT_DIR,
    DEFAULT_JSON_EXPORT_DIR,
    DEFAULT_SQLITE_EXPORT_DIR,
    DEFAULT_TSV_EXPORT_DIR,
    DEFAULT_WIKTIONARY_JSON_EXPORT_DIR,
    camel_to_snake,
    check_index_exists,
)

# MARK: JSON


def convert_to_json(
    language: str,
    data_types: Union[str, List[str]],
    input_file: Path,
    output_dir: Path,
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

    output_dir : Path
        The output directory path for results.

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

    if output_dir is None:
        output_dir = DEFAULT_JSON_EXPORT_DIR

    json_output_dir = Path(output_dir) / language.capitalize()
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
                data = {}

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

                            if key not in data:
                                data[key] = []

                            data[key].append(entry)

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


# MARK: CSV or TSV


def convert_to_csv_or_tsv(
    language: str,
    data_types: Union[str, List[str]],
    input_file: Path,
    output_dir: Path,
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

    output_dir : Path
        The output directory path for results.

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

        if output_dir is None:
            output_dir = (
                DEFAULT_CSV_EXPORT_DIR
                if output_type == "csv"
                else DEFAULT_TSV_EXPORT_DIR
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


# MARK: Convert Wrapper


def convert_wrapper(
    languages: Optional[List[str]],
    data_types: Optional[List[str]],
    input_path: Path,
    output_dir: Path,
    output_type: str,
    overwrite: bool = False,
    identifier_case: str = "camel",
    all: bool = False,
) -> None:
    """
    Convert data to the specified output type: JSON, CSV/TSV, or SQLite.

    Parameters
    ----------
    languages : Optional[List[str]]
        The language(s) of the data to convert.

    data_types : Optional[List[str]]
        The data type(s) of the data to convert.

    input_path : Path
        The path to the input file or directory.

    output_dir : Path
        The output directory where converted files will be stored.

    output_type : str
        The desired output format. Can be 'json', 'csv', 'tsv', or 'sqlite'.

    overwrite : bool, optional, default=False
        Whether to overwrite existing output files.

    identifier_case : str, optional, default='camel'
        The case format for identifiers.

    all : bool, optional, default=False
        Convert all languages and data types.

    Returns
    -------
    None
        This function does not return any value; it performs a conversion operation.
    """
    # Route the function call to the correct conversion function.
    if output_dir is None:
        output_dir = {
            "json": DEFAULT_JSON_EXPORT_DIR,
            "csv": DEFAULT_CSV_EXPORT_DIR,
            "tsv": DEFAULT_TSV_EXPORT_DIR,
            "sqlite": DEFAULT_SQLITE_EXPORT_DIR,
        }.get(output_type, DEFAULT_JSON_EXPORT_DIR)

    if input_path is None and data_types:
        is_wiktionary = any(
            isinstance(dt, str) and dt.startswith("wiktionary")
            for dt in (data_types if isinstance(data_types, list) else [data_types])
        )
        input_path = (
            DEFAULT_WIKTIONARY_JSON_EXPORT_DIR
            if is_wiktionary
            else DEFAULT_JSON_EXPORT_DIR
        )

    if output_type == "json" and languages and data_types:
        convert_to_json(
            language=languages[0],  # only one language possible
            data_types=data_types,
            input_file=input_path,
            output_dir=output_dir,
            output_type=output_type,
            overwrite=overwrite,
            identifier_case=identifier_case,
        )

    elif output_type in {"csv", "tsv"} and languages and data_types:
        convert_to_csv_or_tsv(
            language=languages[0],  # only one language possible
            data_types=data_types,
            input_file=input_path,
            output_dir=output_dir,
            output_type=output_type,
            overwrite=overwrite,
            identifier_case=identifier_case,
        )

    elif output_type == "sqlite":
        data_to_sqlite(
            languages=languages,
            specific_tables=data_types,
            identifier_case=identifier_case,
            input_file=input_path,
            output_file=output_dir,
            overwrite=overwrite,
        )

    else:
        raise ValueError(
            f"Unsupported output type '{output_type}'. Must be 'json', 'csv', 'tsv' or 'sqlite'."
        )
