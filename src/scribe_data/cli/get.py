"""
Functions for getting languages-data types packs for the Scribe-Data CLI.

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

import subprocess
from pathlib import Path
from typing import List, Union
import os  # For removing the JSON file

from scribe_data.unicode.generate_emoji_keywords import generate_emoji
from scribe_data.utils import (
    DEFAULT_CSV_EXPORT_DIR,
    DEFAULT_JSON_EXPORT_DIR,
    DEFAULT_SQLITE_EXPORT_DIR,
    DEFAULT_TSV_EXPORT_DIR,
)
from scribe_data.wikidata.query_data import query_data
from scribe_data.cli.convert import convert


def get_data(
    language: str = None,
    data_type: Union[str, List[str]] = None,
    output_type: str = None,
    output_dir: str = None,
    overwrite: bool = False,
    outputs_per_entry: int = None,
    all: bool = False,
    interactive: bool = False,
) -> None:
    """
    Function for controlling the data get process for the CLI.

    Parameters
    ----------
        language : str
            The language(s) to get.

        data_type : str
            The data type(s) to get.

        output_type : str
            The output file type.

        output_dir : str
            The output directory path for results.

        outputs_per_entry : str
            How many outputs should be generated per data entry.

        overwrite : bool (default: False)
            Whether to overwrite existing files.

        all : bool
            Get all languages and data types.

        interactive : bool (default: False)
            Whether it's running in interactive mode.

    Returns
    -------
        The requested data saved locally given file type and location arguments.
    """
    # MARK: Defaults

    output_type = output_type or "json"
    if output_dir is None:
        if output_type == "csv":
            output_dir = DEFAULT_CSV_EXPORT_DIR
        elif output_type == "json":
            output_dir = DEFAULT_JSON_EXPORT_DIR
        elif output_type == "sqlite":
            output_dir = DEFAULT_SQLITE_EXPORT_DIR
        elif output_type == "tsv":
            output_dir = DEFAULT_TSV_EXPORT_DIR

    languages = [language] if language else None

    subprocess_result = False

    # MARK: Get All

    if all:
        print("Updating all languages and data types ...")
        query_data(None, None, None, overwrite)
        subprocess_result = True

    # MARK: Emojis

    elif data_type in {"emoji-keywords", "emoji_keywords"}:
        generate_emoji(language=language, output_dir=output_dir)

    # MARK: Query Data

    elif language or data_type:
        data_type = data_type[0] if isinstance(data_type, list) else data_type

        print(
            f"Updating data for language(s): {language}; data type(s): {', '.join([data_type])}"
        )
        query_data(
            languages=languages,
            data_type=data_type,
            output_dir=output_dir,
            overwrite=overwrite,
            interactive=interactive,
        )
        subprocess_result = True

    else:
        raise ValueError(
            "You must provide at least one of the --language (-l) or --data-type (-dt) options, or use --all (-a)."
        )

    if (
        isinstance(subprocess_result, subprocess.CompletedProcess)
        and subprocess_result.returncode != 1
    ) or (isinstance(subprocess_result, bool) and subprocess_result is not False):
        print(f"Updated data was saved in: {Path(output_dir).resolve()}.")

        json_input_path = Path(output_dir) / f"{language}/{data_type}.json"

        # Proceed with conversion only if the output type is not JSON
        if output_type != "json":
            if json_input_path.exists():
                convert(
                    language=language,
                    data_type=data_type,
                    output_type=output_type,
                    input_file=str(json_input_path),
                    output_dir=output_dir,
                    overwrite=overwrite,
                )

                os.remove(json_input_path)
            else:
                print(f"Error: Input file '{json_input_path}' does not exist.")

        if interactive:
            return True

    # Handle emoji keywords process failure
    elif data_type in {"emoji-keywords", "emoji_keywords"}:
        print(
            "\nThe Scribe-Data emoji functionality is powered by PyICU, which is currently not installed."
        )
        print(
            "Please check the installation guide at https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/unicode/UNICODE_INSTALLTION.md for more information.\n"
        )
