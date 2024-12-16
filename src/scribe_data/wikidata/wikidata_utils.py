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

from rich import print as rprint
from SPARQLWrapper import JSON, POST, SPARQLWrapper

from scribe_data.cli.download import wd_lexeme_dump_download_wrapper

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)
sparql.setMethod(POST)


def parse_wd_lexeme_dump(wikidata_dump: str = None):
    """
    Checks for the existence of a Wikidata dump and parses it if possible.

    Parameters
    ----------
        wikidata_dump : str
            The local Wikidata dump that should be used to get data.

    Returns
    -------
        The requested data saved locally given file type and location arguments.
    """
    if wikidata_dump:
        wd_lexeme_dump_download_wrapper(None, wikidata_dump)

    else:
        file_path = wd_lexeme_dump_download_wrapper()
        if isinstance(file_path, str) and file_path:
            rprint(
                "[bold green]We'll use the following lexeme dump[/bold green]",
                file_path,
            )
            rprint(
                "[bold red]Parsing Wikidata lexeme dump feature will be available soon...[/bold red]"
            )
