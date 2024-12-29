"""
Utility functions for accessing data from Wikidata.

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

from pathlib import Path
from rich import print as rprint
from SPARQLWrapper import JSON, POST, SPARQLWrapper
from typing import List, Union

from scribe_data.cli.download import wd_lexeme_dump_download_wrapper
from scribe_data.wiktionary.parse_dump import parse_dump
from scribe_data.utils import language_metadata, data_type_metadata

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)
sparql.setMethod(POST)


def parse_wd_lexeme_dump(
    language: Union[str, List[str]] = None,
    wikidata_dump_type: List[str] = None,
    data_types: List[str] = None,
    type_output_dir: str = None,
    wikidata_dump_path: str = None,
):
    """
    Checks for the existence of a Wikidata dump and parses it if possible.

    Parameters
    ----------
    language : Union[str, List[str]]
        The language(s) to parse the data for. Use "all" for all languages.
    wikidata_dump_type : List[str]
        The type(s) of Wikidata dump to parse (e.g. ["total", "translations", "form"]).
    data_types : List[str]
        The categories to parse when using "form" type (e.g. ["nouns", "adverbs"]).
    type_output_dir : str, optional
        The directory to save the parsed JSON data. If None, uses default directory.
    wikidata_dump_path : str, optional
        The local Wikidata dump directory that should be used to get data.
    """
    # Convert "all" to list of all languages
    if isinstance(language, str) and language.lower() == "all":
        language = list(language_metadata.keys())
    if isinstance(data_types, str) and data_types.lower() == "all":
        # Exclude translations as it's a separate section
        data_types = [
            dt
            for dt in data_type_metadata.keys()
            if dt != "translations" and dt != "emoji-keywords"
        ]

    file_path = wd_lexeme_dump_download_wrapper(None, wikidata_dump_path)

    if isinstance(file_path, (str, Path)):
        path = Path(file_path)
        if path.exists():
            rprint(
                "[bold green]We'll use the following lexeme dump[/bold green]",
                file_path,
            )
            parse_dump(
                language=language,
                parse_type=wikidata_dump_type,
                data_types=data_types,
                file_path=file_path,
                output_dir=type_output_dir,
            )
            return

    rprint(f"[bold red]No valid dumps found in {file_path}.[/bold red]")
