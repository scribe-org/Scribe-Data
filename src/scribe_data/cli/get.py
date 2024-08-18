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

import os
from pathlib import Path
from typing import Optional

from scribe_data.cli.convert import convert_to_csv_or_tsv, export_json
from scribe_data.utils import DEFAULT_JSON_EXPORT_DIR
from scribe_data.wikidata.update_data import update_data

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
    if not outputs_per_entry and (data_type in ["emoji-keywords", "emoji_keywords"]):
        print(
            "\nNo value set for 'outputs-per-entry'. Setting a default value of 3 outputs per entry.\n"
        )
        outputs_per_entry = 3

    languages = [language] if language else None

    if all:
        print("Updating all languages and data types ...")
        update_data()

    elif data_type in ["emoji-keywords", "emoji_keywords"]:
        for lang in languages:
            emoji_keyword_extraction_script = (
                Path(__file__).parent.parent
                / "language_data_extraction"
                / lang
                / "emoji_keywords"
                / "generate_emoji_keywords.py"
            )

            os.system(f"python3 {emoji_keyword_extraction_script}")

    elif data_type == "translations":
        for lang in languages:
            translation_generation_script = (
                Path(__file__).parent.parent
                / "language_data_extraction"
                / lang
                / "translations"
                / "translate_words.py"
            )

            os.system(f"python3 {translation_generation_script}")

    elif language or data_type:
        data_type = [data_type] if data_type else None
        print(f"Updating data for language: {language}, data type: {data_type}")
        update_data(languages, data_type)

    else:
        raise ValueError(
            "You must provide either at least one of the --language (-l) or --data-type (-dt) options, or use --all (-a)."
        )

    if output_dir:
        output_dir = Path(output_dir)
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

    else:
        print(
            f"No output directory specified for exporting results. Updated data was saved in: {Path(DEFAULT_JSON_EXPORT_DIR).resolve()}."
        )

    # Check if data was actually updated.
    data_path = Path(DEFAULT_JSON_EXPORT_DIR)
    if language:
        lang_path = data_path / language.capitalize()
        if not lang_path.exists():
            print(f"Warning: No data directory found for language '{language}'")

        elif data_type:
            dt_file = lang_path / f"{data_type.replace('-', '_')}.json"
            if not dt_file.exists():
                print(
                    f"Warning: No data file found for '{language}' {data_type}. The command must not have worked."
                )

        else:
            print(f"Data updated for language: {language}")

    elif data_type:
        dt_updated = any(
            lang_dir.is_dir() and (lang_dir / f"{data_type}.json").exists()
            for lang_dir in data_path.iterdir()
        )

        if not dt_updated:
            print(f"Warning: No data files found for data type '{data_type}'")

        else:
            print(f"Data updated for data type: {data_type}")
