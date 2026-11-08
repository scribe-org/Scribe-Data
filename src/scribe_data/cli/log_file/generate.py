# SPDX-License-Identifier: GPL-3.0-or-later
"""
Generate a Scribe-Data log file with total data from a get process.
"""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from scribe_data.utils import DEFAULT_JSON_EXPORT_DIR, DEFAULT_LOG_FILES_EXPORT_DIR


def generate_log_file(
    output_dir: Path = DEFAULT_JSON_EXPORT_DIR, include_fields: bool = False
) -> None:
    """
    Generate a log file of the total data from a Scribe-Data get command.

    Parameters
    ----------
    output_dir : Path, optional, default=DEFAULT_JSON_EXPORT_DIR
        The output directory path to generate a log file for.

    include_fields : bool, default=False
        Whether to include data type fields rather than just data types.
    """
    # Use provided output dir or default.
    export_dir = Path(output_dir) if output_dir else DEFAULT_JSON_EXPORT_DIR
    export_dir.mkdir(parents=True, exist_ok=True)
    DEFAULT_LOG_FILES_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    # MARK: Derive Log

    log_file_dict = {}
    for language_dir in export_dir.iterdir():
        if not language_dir.is_dir():
            continue

        log_file_dict[language_dir.name] = {}

        for data_type_path in language_dir.glob("*.json"):
            with data_type_path.open(encoding="utf-8") as file:
                data_type_file = json.load(file)
                if not include_fields:
                    log_file_dict[language_dir.name][data_type_path.stem] = len(
                        data_type_file
                    )

                else:
                    log_file_dict[language_dir.name][data_type_path.stem] = {}
                    for lexeme in data_type_file.keys():
                        for form in data_type_file[lexeme].keys():
                            if form == "lastModified":
                                pass

                            elif (
                                form
                                not in log_file_dict[language_dir.name][
                                    data_type_path.stem
                                ]
                            ):
                                log_file_dict[language_dir.name][data_type_path.stem][
                                    form
                                ] = 1

                            else:
                                log_file_dict[language_dir.name][data_type_path.stem][
                                    form
                                ] = (
                                    log_file_dict[language_dir.name][
                                        data_type_path.stem
                                    ][form]
                                    + 1
                                )

    # MARK: Save Log

    log_timestamp = datetime.now(tz=ZoneInfo("UTC"))
    log_timestamp = log_timestamp.strftime("%Y%m%d%H%M%S")
    log_type_identifier = "data_type_fields" if include_fields else "data_types"
    log_file_name = f"scribe_data_log_file_{log_type_identifier}_{log_timestamp}.json"
    log_file_path = DEFAULT_LOG_FILES_EXPORT_DIR / log_file_name

    with log_file_path.open("w", encoding="utf-8") as file:
        json.dump(log_file_dict, file, sort_keys=True, ensure_ascii=False, indent=2)

    print(f"Scribe-Data total data log file generated at {log_file_path}.")
