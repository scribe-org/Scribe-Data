"""
Functions to convert data returned from the Scribe-Data CLI to other file types.

.. raw:: html
    <!--
    * Copyright (C) 2024 Scribe
    *
    * This program is free software: you can redistribute it and/or modify
    * it under the terms of the GNU General Public License as published by
    * the Free Software Foundation, either version 3 of the License, or
    * (at your option) any later version.
    *
    * This program is distributed in the hope that it will be useful,
    * but WITHOUT ANY WARRANTY; without even the implied warranty of
    * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    * GNU General Public License for more details.
    *
    * You should have received a copy of the GNU General Public License
    * along with this program.  If not, see <https://www.gnu.org/licenses/>.
    -->
"""

import csv
import json
import shutil
from pathlib import Path
from typing import List, Union

from scribe_data.cli.cli_utils import language_map
from scribe_data.load.data_to_sqlite import data_to_sqlite
from scribe_data.utils import (
    DEFAULT_SQLITE_EXPORT_DIR,
    DEFAULT_JSON_EXPORT_DIR,
    DEFAULT_CSV_EXPORT_DIR,
    DEFAULT_TSV_EXPORT_DIR,
    get_language_iso,
)

# MARK: JSON


def convert_to_json(
    language: str,
    data_type: Union[str, List[str]],
    output_type: str,
    input_file: str,
    output_dir: str = None,
    overwrite: bool = False,
) -> None:
    """
    Convert a CSV/TSV file to JSON.

    Parameters
    ----------
        language : str
            The language of the file to convert.

        data_type : Union[str, List[str]]
            The data type of the file to convert.

        output_type : str
            The output format, should be "json".

        input_file : str
            The input CSV/TSV file path.

        output_dir : Path
            The output directory path for results.

        overwrite : bool
            Whether to overwrite existing files.

    Returns
    -------
        None
    """
    normalized_language = language_map.get(language.lower())

    if not normalized_language:
        raise ValueError(f"Language '{language.capitalize()}' is not recognized.")

    data_types = [data_type] if isinstance(data_type, str) else data_type

    if output_dir is None:
        output_dir = DEFAULT_JSON_EXPORT_DIR

    json_output_dir = Path(output_dir) / normalized_language["language"].capitalize()
    json_output_dir.mkdir(parents=True, exist_ok=True)

    for dtype in data_types:
        input_file_path = Path(input_file)

        if not input_file_path.exists():
            print(f"No data found for input file '{input_file_path}'.")
            continue

        delimiter = "," if input_file_path.suffix.lower() == ".csv" else "\t"

        try:
            with input_file_path.open("r", encoding="utf-8") as file:
                reader = csv.DictReader(file, delimiter=delimiter)
                rows = list(reader)

                if not rows:
                    print(f"No data found in '{input_file_path}'.")
                    continue

                # Use the first row to inspect column headers
                first_row = rows[0]
                keys = list(first_row.keys())
                data = {}

                if len(keys) == 1:
                    # Handle Case: { key: None }
                    data[first_row[keys[0]]] = None

                elif len(keys) == 2:
                    # Handle Case: { key: value }
                    for row in rows:
                        key = row[keys[0]]
                        value = row[keys[1]]
                        data[key] = value

                elif len(keys) > 2:
                    if all(col in first_row for col in ["emoji", "is_base", "rank"]):
                        # Handle Case: { key: [ { emoji: ..., is_base: ..., rank: ... }, { emoji: ..., is_base: ..., rank: ... } ] }
                        for row in rows:
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
                        # Handle Case: { key: { value1: ..., value2: ... } }
                        for row in rows:
                            data[row[keys[0]]] = {k: row[k] for k in keys[1:]}

        except (IOError, csv.Error) as e:
            print(f"Error reading '{input_file_path}': {e}")
            continue

        # Define output file path
        output_file = json_output_dir / f"{dtype}.{output_type}"

        if output_file.exists() and not overwrite:
            user_input = input(
                f"File '{output_file}' already exists. Overwrite? (y/n): "
            )
            if user_input.lower() != "y":
                print(f"Skipping {normalized_language['language']} - {dtype}")
                continue

        try:
            with output_file.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

        except IOError as e:
            print(f"Error writing to '{output_file}': {e}")
            continue

        print(
            f"Data for {normalized_language['language'].capitalize()} {dtype} written to {output_file}"
        )


#
# MARK: CSV or TSV


def convert_to_csv_or_tsv(
    language: str,
    data_type: Union[str, List[str]],
    output_type: str,
    input_file: str,
    output_dir: str = None,
    overwrite: bool = False,
) -> None:
    """
    Convert a JSON File to CSV/TSV file.

    Parameters
    ----------
    language : str
        The language of the file to convert.

    data_type : Union[str, List[str]]
        The data type of the file to convert.

    output_type : str
        The output format, should be "csv" or "tsv".

    input_file : str
        The input JSON file path.

    output_dir : str
        The output directory path for results.

    overwrite : bool
        Whether to overwrite existing files.

    Returns
    -------
        None
    """

    # Normalize the language
    normalized_language = language_map.get(language.lower())
    if not normalized_language:
        print(f"Language '{language}' is not recognized.")
        return

    # Split the data_type string by commas
    data_types = [dtype.strip() for dtype in data_type.split(",")]

    for dtype in data_types:
        input_file = Path(input_file)
        if not input_file.exists():
            print(f"No data found for {dtype} conversion at '{input_file}'.")
            continue

        try:
            with input_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading '{input_file}': {e}")
            continue

        # Determine the delimiter based on output type
        delimiter = "," if output_type == "csv" else "\t"

        if output_dir is None:
            output_dir = (
                DEFAULT_CSV_EXPORT_DIR
                if output_type == "csv"
                else DEFAULT_TSV_EXPORT_DIR
            )

        final_output_dir = (
            Path(output_dir) / normalized_language["language"].capitalize()
        )
        final_output_dir.mkdir(parents=True, exist_ok=True)

        output_file = final_output_dir / f"{dtype}.{output_type}"
        if output_file.exists() and not overwrite:
            user_input = input(
                f"File '{output_file}' already exists. Overwrite? (y/n): "
            )
            if user_input.lower() != "y":
                print(f"Skipping {dtype}")
                continue

        try:
            with output_file.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file, delimiter=delimiter)

                # Handle different JSON structures based on the format
                if isinstance(data, dict):
                    first_key = list(data.keys())[0]

                    if isinstance(data[first_key], dict):
                        # Handle case: { key: { value1: ..., value2: ... } }
                        columns = set()
                        for value in data.values():
                            columns.update(value.keys())
                        writer.writerow([dtype[:-1]] + list(columns))

                        for key, value in data.items():
                            row = [key] + [value.get(col, "") for col in columns]
                            writer.writerow(row)

                    elif isinstance(data[first_key], list):
                        if all(isinstance(item, dict) for item in data[first_key]):
                            # Handle case: { key: [ { value1: ..., value2: ... } ] }
                            if "emoji" in data[first_key][0]:  # Emoji specific case
                                columns = ["word", "emoji", "is_base", "rank"]
                                writer.writerow(columns)

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
                                columns = [dtype[:-1]] + list(data[first_key][0].keys())
                                writer.writerow(columns)

                                for key, value in data.items():
                                    for item in value:
                                        row = [key] + [
                                            item.get(col, "") for col in columns[1:]
                                        ]
                                        writer.writerow(row)

                        elif all(isinstance(item, str) for item in data[first_key]):
                            # Handle case: { key: [value1, value2, ...] }
                            writer.writerow(
                                [dtype[:-1]]
                                + [
                                    f"autosuggestion_{i+1}"
                                    for i in range(len(data[first_key]))
                                ]
                            )
                            for key, value in data.items():
                                row = [key] + value
                                writer.writerow(row)

                    else:
                        # Handle case: { key: value }
                        writer.writerow([dtype[:-1], "value"])
                        for key, value in data.items():
                            writer.writerow([key, value])

        except IOError as e:
            print(f"Error writing to '{output_file}': {e}")
            continue

        print(f"Data for '{dtype}' written to '{output_file}'")


# MARK: SQLITE


def convert_to_sqlite(
    language: str,
    data_type: str,
    output_type: str,
    input_file: str = None,
    output_dir: str = None,
    overwrite: bool = False,
) -> None:
    """
    Converts a Scribe-Data output file to an SQLite file.

    Parameters
    ----------
        language : str
            The language of the file to convert.

        data_type : str
            The data type of the file to convert.

        output_type : str
            The output format, should be "sqlite".

        input_file : Path
            The input file path for the data to be converted.

        output_dir : Path
            The output directory path for results.

        overwrite : bool
            Whether to overwrite existing files.

    Returns
    -------
        A SQLite file saved in the given location.
    """
    if not language:
        raise ValueError("Language must be specified for SQLite conversion.")

    if input_file:
        input_file = Path(input_file)
    if not input_file.exists():
        raise ValueError(f"Input file does not exist: {input_file}")

    languages = [language]
    specific_tables = [data_type] if data_type else None

    if output_dir is None:
        output_dir = Path(DEFAULT_SQLITE_EXPORT_DIR)
    else:
        output_dir = Path(output_dir)

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"Converting data for language: {language}, data type: {data_type} to {output_type}"
    )
    data_to_sqlite(languages, specific_tables)

    source_file = f"{get_language_iso(language).upper()}LanguageData.sqlite"
    source_path = input_file.parent / source_file
    target_path = output_dir / source_file

    if source_path.exists():
        if target_path.exists() and not overwrite:
            print(f"File {target_path} already exists. Use --overwrite to replace.")
        else:
            shutil.copy(source_path, target_path)
            print(f"SQLite database copied to: {target_path}")
    else:
        print(f"Warning: SQLite file not found at {source_path}")

    print("SQLite file conversion complete.")
