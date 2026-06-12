# SPDX-License-Identifier: GPL-3.0-or-later
"""
Utility functions for accessing data from Wikidata.
"""

from pathlib import Path

from rich import print as rprint
from SPARQLWrapper import JSON, POST, SPARQLWrapper

from scribe_data.cli.download.wikidata_lexeme_dump import (
    wd_lexeme_dump_download_wrapper,
)
from scribe_data.utils import data_type_metadata, language_metadata
from scribe_data.wikidata.parse_dump import parse_dump

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)
sparql.setMethod(POST)


def parse_wd_lexeme_dump(
    languages: str | list[str] | None,
    data_types: list[str] | None = None,
    wikidata_dump_type: str | list[str] | None = None,
    overwrite_all: bool = False,
    interactive_mode: bool = False,
) -> None:
    """
    Check for the existence of a Wikidata lexeme dump and parses it if possible.

    Parameters
    ----------
    languages : Union[str, List[str]]
        The language(s) to parse the data for. Use "all" for all languages.

    data_types : List[str]
        The categories to parse when using "form" type (e.g. ["nouns", "adverbs"]).

    wikidata_dump_type : List[str]
        The type(s) of Wikidata lexeme dump to parse (e.g. ["total", "form"]).

    overwrite_all : bool, default=False
        If True, automatically overwrite existing files without prompting.

    interactive_mode : bool, default=False
        Whether the function is being ran via interactive mode.

    Returns
    -------
    None
        A parsed Wikidata lexeme dump.
    """
    # Convert "all" to list of all languages including sub-languages.
    if languages == ["all"]:
        languages = []
        for main_lang, lang_data in language_metadata.items():
            # Add main language
            languages.append(main_lang)
            # Add sub-languages if they exist.
            if "sub_languages" in lang_data:
                languages.extend(iter(lang_data["sub_languages"]))

    # For processing: exclude translations and emoji-keywords.
    if data_types == ["all"]:
        data_types = [
            dt
            for dt in data_type_metadata.keys()
            if dt not in ["translations", "emoji_keywords", "articles"]
        ]

    if not interactive_mode:
        if isinstance(languages, list):
            print(
                f"Languages to process: {', '.join([lang.capitalize() for lang in languages])}"
            )

        else:
            if isinstance(languages, str):
                print(f"Language to process: {languages.capitalize()}")

        print(
            f"Data types to process: {', '.join([d.capitalize() for d in data_types or []])}"
        )

    file_path = wd_lexeme_dump_download_wrapper(dump_snapshot=None)

    if isinstance(file_path, (str, Path)):
        path = Path(file_path)
        if path.exists():
            rprint(
                "[bold green]We'll use the following lexeme dump[/bold green]",
                file_path,
            )
            normalized_languages = languages or ""
            if isinstance(wikidata_dump_type, str):
                normalized_dump_type = [wikidata_dump_type]
            elif wikidata_dump_type is None:
                normalized_dump_type = []
            else:
                normalized_dump_type = wikidata_dump_type

            parse_dump(
                languages=normalized_languages,
                parse_type=normalized_dump_type,
                data_types=data_types,
                file_path=file_path,
                overwrite_all=overwrite_all,
            )

        return
