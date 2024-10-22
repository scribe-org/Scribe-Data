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

import json
import subprocess
from pathlib import Path

from scribe_data.utils import (
    DEFAULT_CSV_EXPORT_DIR,
    DEFAULT_JSON_EXPORT_DIR,
    DEFAULT_SQLITE_EXPORT_DIR,
    DEFAULT_TSV_EXPORT_DIR,
)
from scribe_data.wikidata.query_data import query_data
from scribe_data.wikipedia.wikipedia_utils import get_wikipedia_articles
from scribe_data.wikipedia.process_wiki import gen_autosuggestions, clean


def load_text_corpus(language):
    """
    Load and process the Wikipedia text corpus for a given language.
    
    Parameters
    ----------
    language : str
        The language to load the corpus for.
        
    Returns
    -------
    list
        The processed text corpus ready for autosuggestion generation.
    """
    # Get Wikipedia articles for the language
    articles = get_wikipedia_articles(language=language)
    
    # Clean the articles
    cleaned_corpus = clean(articles, language=language)
    
    return cleaned_corpus


def get_data(
    language: str = None,
    data_type: str = None,
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
    None
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

    # MARK: Autosuggestions
    elif data_type in {"autosuggestions", "auto_suggestions"}:
        subprocess_result = True
        for lang in languages:
            try:
                print(f"Loading text corpus for {lang}...")
                text_corpus = load_text_corpus(lang)
                
                print(f"Generating autosuggestions for {lang}...")
                autosuggestions = gen_autosuggestions(
                    text_corpus,
                    language=lang,
                    num_words=500,
                    update_local_data=True,
                    verbose=interactive
                )
                
                output_path = Path(output_dir) / lang
                output_path.mkdir(parents=True, exist_ok=True)
                
                # Save autosuggestions according to output type
                if output_type == "json":
                    with open(output_path / "autosuggestions.json", "w", encoding="utf-8") as f:
                        json.dump(autosuggestions, f, ensure_ascii=False, indent=2)
                
                print(f"Autosuggestions for {lang} generated and saved.")
                
            except Exception as e:
                print(f"Error generating autosuggestions for {lang}: {str(e)}")
                subprocess_result = False

    # MARK: Query Data
    elif language or data_type:
        data_type = data_type[0] if isinstance(data_type, list) else data_type
        data_type = [data_type] if data_type else None
        print(
            f"Updating data for language(s): {language}; data type(s): {', '.join(data_type) if data_type else ''}"
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
        print(
            f"Updated data was saved in: {Path(output_dir).resolve()}.",
        )
        if interactive:
            return True

    # The emoji keywords process has failed.
    elif data_type in {"emoji-keywords", "emoji_keywords"}:
        print(
            "\nThe Scribe-Data emoji functionality is powered by PyICU, which is currently not installed."
        )
        print(
            "Please check the installation guide at https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/unicode/UNICODE_INSTALLTION.md for more information.\n"
        )