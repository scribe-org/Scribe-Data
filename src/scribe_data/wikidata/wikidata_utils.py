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

from scribe_data.cli.download import wd_lexeme_dump_download_wrapper
from scribe_data.wiktionary.parse_dump import parse_dump

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)
sparql.setMethod(POST)


def parse_wd_lexeme_dump(
    language: str = None,
    wikidata_dump_type: str = None,
    type_output_dir: str = None,
    wikidata_dump_path: str = None,
):
    """
    Checks for the existence of a Wikidata dump and parses it if possible.

    Parameters
    ----------
    language : str
        The language to parse the data for.
    wikidata_dump_type : str
        The type of Wikidata dump to parse (e.g. "total", "translations").
    type_output_dir : str
        The directory to save the parsed JSON data.
    wikidata_dump_path : str
        The local Wikidata dump directory that should be used to get data.
    Returns
    -------
        The requested data saved locally given file type and location arguments.
    """
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
                type_output_dir=type_output_dir,
                file_path=file_path,
            )

            return

    rprint(f"[bold red]No valid dumps found in {file_path}.[/bold red]")
