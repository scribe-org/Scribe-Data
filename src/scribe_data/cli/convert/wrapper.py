# SPDX-License-Identifier: GPL-3.0-or-later
"""
Wrapper function to convert data returned from the Scribe-Data CLI to other file types.
"""

from pathlib import Path

from scribe_data.cli.convert.to_csv_or_tsv import convert_to_csv_or_tsv
from scribe_data.cli.convert.to_json import convert_to_json
from scribe_data.cli.convert.to_sqlite import convert_to_sqlite
from scribe_data.utils import (
    DEFAULT_CSV_EXPORT_DIR,
    DEFAULT_JSON_EXPORT_DIR,
    DEFAULT_SQLITE_EXPORT_DIR,
    DEFAULT_TSV_EXPORT_DIR,
    DEFAULT_WIKTIONARY_JSON_EXPORT_DIR,
)

# MARK: Wrapper


def convert_wrapper(
    languages: list[str] | None,
    data_types: list | None,
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
        convert_to_sqlite(
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
