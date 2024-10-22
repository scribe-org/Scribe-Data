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
import logging
from pathlib import Path
from typing import Optional, List, Union

from scribe_data.utils import (
    DEFAULT_CSV_EXPORT_DIR,
    DEFAULT_JSON_EXPORT_DIR,
    DEFAULT_SQLITE_EXPORT_DIR,
    DEFAULT_TSV_EXPORT_DIR,
)
from scribe_data.wikidata.query_data import query_data
from scribe_data.wikipedia.process_wiki import gen_autosuggestions
from scribe_data.utils.validation import validate_lexeme_forms

def validate_data_availability(language: str, data_type: str) -> bool:
    """
    Validates if the requested data type is available for the given language.
    
    Parameters
    ----------
    language : str
        The language to check
    data_type : str
        The type of data to validate
        
    Returns
    -------
    bool
        True if data is available, False otherwise
    """
    try:
        # Check if lexeme forms metadata exists and is valid for this language
        if data_type in ['verbs', 'nouns']:
            forms_valid = validate_lexeme_forms(language, data_type)
            if not forms_valid:
                logging.warning(f"No valid lexeme form data available for {language} {data_type}")
                return False
        return True
    except Exception as e:
        logging.error(f"Error validating data availability: {str(e)}")
        return False

def get_data(
    language: str = None,
    data_type: str = None,
    output_type: str = None,
    output_dir: str = None,
    overwrite: bool = False,
    outputs_per_entry: int = None,
    all: bool = False,
    interactive: bool = False,
) -> Optional[bool]:
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
        Optional[bool]: True if successful, None if failed
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO if interactive else logging.WARNING,
        format='%(levelname)s: %(message)s'
    )

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

    try:
        # MARK: Get All
        if all:
            logging.info("Updating all languages and data types ...")
            query_data(None, None, None, overwrite)
            subprocess_result = True

        # MARK: Emojis
        elif data_type in {"emoji-keywords", "emoji_keywords"}:
            for lang in languages:
                if not validate_data_availability(lang, "emoji_keywords"):
                    continue
                    
                emoji_keyword_extraction_script = (
                    Path(__file__).parent.parent
                    / "language_data_extraction"
                    / lang
                    / "emoji_keywords"
                    / "generate_emoji_keywords.py"
                )

                if not emoji_keyword_extraction_script.exists():
                    logging.error(f"Emoji keyword script not found for language: {lang}")
                    continue

                subprocess_result = subprocess.run(
                    ["python", str(emoji_keyword_extraction_script)],
                    capture_output=True
                )

        # MARK: Autosuggestions
        elif data_type in {"autosuggestions", "auto_suggestions"}:
            for lang in languages:
                if not validate_data_availability(lang, "autosuggestions"):
                    logging.warning(f"Skipping autosuggestions for {lang} - no data available")
                    continue
                    
                logging.info(f"Generating autosuggestions for {lang}...")
                try:
                    corpus = load_text_corpus(lang)
                    if not corpus:
                        logging.warning(f"No text corpus available for {lang}")
                        continue
                        
                    autosuggestions = gen_autosuggestions(
                        text_corpus=corpus,
                        language=lang,
                        update_local_data=True,
                        verbose=interactive
                    )
                    subprocess_result = True if autosuggestions else False
                except Exception as e:
                    logging.error(f"Error generating autosuggestions for {lang}: {str(e)}")
                    continue

        # MARK: Query Data
        elif language or data_type:
            data_type = data_type[0] if isinstance(data_type, list) else data_type
            data_type = [data_type] if data_type else None

            if data_type and language:
                # Validate data availability before querying
                if not all(validate_data_availability(lang, dt) for lang in languages for dt in data_type):
                    logging.warning("Some requested data is not available")
                
            logging.info(f"Updating data for language(s): {language}; data type(s): {', '.join(data_type) if data_type else 'all'}")
            
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

        # Handle results
        if (
            isinstance(subprocess_result, subprocess.CompletedProcess)
            and subprocess_result.returncode == 0
        ) or subprocess_result is True:
            logging.info(f"Updated data was saved in: {Path(output_dir).resolve()}")
            if interactive:
                return True

        # Handle emoji keywords failure
        elif data_type in {"emoji-keywords", "emoji_keywords"}:
            logging.error(
                "\nThe Scribe-Data emoji functionality is powered by PyICU, which is currently not installed."
                "\nPlease check the installation guide at "
                "https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/unicode/UNICODE_INSTALLTION.md "
                "for more information.\n"
            )
            
        return None

    except Exception as e:
        logging.error(f"Error in get_data: {str(e)}")
        return None

def load_text_corpus(language: str) -> List[str]:
    """
    Load the text corpus for a given language.
    This is a placeholder that should be implemented based on your data storage.
    
    Parameters
    ----------
    language : str
        The language to load corpus for
        
    Returns
    -------
    List[str]
        The text corpus for the language
    """
    try:
        # Implement actual corpus loading logic here
        return []
    except Exception as e:
        logging.error(f"Error loading text corpus for {language}: {str(e)}")
        return []