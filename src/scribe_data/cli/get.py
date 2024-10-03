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
from typing import Optional

from scribe_data.cli.convert import convert_to_csv_or_tsv, export_json
from scribe_data.utils import DEFAULT_JSON_EXPORT_DIR
from scribe_data.wikidata.query_data import query_data

DATA_DIR = Path(DEFAULT_JSON_EXPORT_DIR)


def get_data(
    language: Optional[str] = None,
    data_type: Optional[str] = None,
    output_dir: Optional[str] = None,
    overwrite: bool = False,
    output_type: Optional[str] = None,
    outputs_per_entry: int = None,
    all: bool = False,
) -> None:
    """
    Function for controlling the data get process for the CLI.
    """
    languages = [language] if language else None

    subprocess_result = False

    if all:
        print("Updating all languages and data types ...")
        query_data(None, None, overwrite)
        subprocess_result = True

    elif data_type in ["emoji-keywords", "emoji_keywords"]:
        for lang in languages:
            emoji_keyword_extraction_script = (
                Path(__file__).parent.parent
                / "language_data_extraction"
                / lang
                / "emoji_keywords"
                / "generate_emoji_keywords.py"
            )

            subprocess_result = subprocess.run(
                ["python", emoji_keyword_extraction_script]
            )

    elif data_type == "translations":
        for lang in languages:
            translation_generation_script = (
                Path(__file__).parent.parent
                / "language_data_extraction"
                / lang
                / "translations"
                / "translate_words.py"
            )

            subprocess_result = subprocess.run(
                ["python", translation_generation_script]
            )

    elif language or data_type:
        data_type = data_type[0] if isinstance(data_type, list) else data_type

        data_type = [data_type] if data_type else None
        print(f"Updating data for language: {language}, data type: {data_type}")
        query_data(languages, data_type, overwrite)
        subprocess_result = True

    else:
        raise ValueError(
            "You must provide at least one of the --language (-l) or --data-type (-dt) options, or use --all (-a)."
        )

    if output_dir:
        output_dir = Path(output_dir).resolve()
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        if output_type == "json" or output_type is None:
            export_json(language, data_type, output_dir, overwrite)

        elif output_type in ["csv", "tsv"]:
            convert_to_csv_or_tsv(
                language, data_type, output_dir, overwrite, output_type
            )

        else:
            raise ValueError(
                "Unsupported output type. Please use 'json', 'csv', or 'tsv'."
            )

    elif (
        isinstance(subprocess_result, subprocess.CompletedProcess)
        and subprocess_result.returncode != 1
    ) or (isinstance(subprocess_result, bool) and subprocess_result is not False):
        print(
            "No output directory specified for exporting results.",
            f"Updated data was saved in: {Path(DEFAULT_JSON_EXPORT_DIR).resolve()}.",
        )

    elif data_type in ["emoji-keywords", "emoji_keywords"]:
        print(
            "\nThe Scribe-Data emoji functionality is powered by PyICU, which is currently not installed."
        )
        print(
            "Please check the installation steps at https://gitlab.pyicu.org/main/pyicu for more information.\n"
        )
