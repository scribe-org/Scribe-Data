# SPDX-License-Identifier: GPL-3.0-or-later
"""
Utility functions for accessing data from Wikidata.
"""

from pathlib import Path
from typing import List, Union

import requests
from rich import print as rprint
from SPARQLWrapper import JSON, POST, SPARQLWrapper

from scribe_data.cli.download import wd_lexeme_dump_download_wrapper
from scribe_data.utils import data_type_metadata, language_metadata
from scribe_data.wiktionary.parse_dump import parse_dump

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)
sparql.setMethod(POST)


def mediaWiki_query(query: str) -> dict:
    """
    Query the Wikidata API using a MediaWiki query.

    Parameters
    ----------
    query : str
        The MediaWiki query to execute.

    Returns
    -------
    dict
        The JSON response from the API.
    """
    url = (
        f"https://en.wiktionary.org/w/api.php?"
        f"action=query&format=json&titles={query}/translations&prop=revisions&rvprop=content"
    )
    response = requests.get(url)
    return response.json()


def parse_wd_lexeme_dump(
    language: Union[str, List[str]] = None,
    wikidata_dump_type: List[str] = None,
    data_types: List[str] = None,
    type_output_dir: str = None,
    wikidata_dump_path: str = None,
):
    """
    Checks for the existence of a Wikidata lexeme dump and parses it if possible.

    Parameters
    ----------
    language : Union[str, List[str]]
        The language(s) to parse the data for. Use "all" for all languages.

    wikidata_dump_type : List[str]
        The type(s) of Wikidata lexeme dump to parse (e.g. ["total", "translations", "form"]).

    data_types : List[str]
        The categories to parse when using "form" type (e.g. ["nouns", "adverbs"]).

    type_output_dir : str, optional
        The directory to save the parsed JSON data. If None, uses default directory.

    wikidata_dump_path : str, optional
        The local Wikidata lexeme dump directory that should be used to get data.
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
