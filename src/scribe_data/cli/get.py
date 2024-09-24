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

    if all:
        print("Updating all languages and data types ...")
        query_data(None, None, overwrite)

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
        query_data(languages, data_type, overwrite)

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
