# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for getting languages-data types packs for the Scribe-Data CLI.
"""

import json
import os
import urllib.error
from http.client import IncompleteRead
from pathlib import Path
from typing import List, Union
from urllib.error import URLError

import questionary
from rich import print as rprint
from SPARQLWrapper.SPARQLExceptions import EndPointInternalError

from scribe_data.cli.convert import convert_wrapper
from scribe_data.unicode.generate_emoji_keywords import generate_emoji
from scribe_data.utils import (
    DEFAULT_CSV_EXPORT_DIR,
    DEFAULT_DUMP_EXPORT_DIR,
    DEFAULT_JSON_EXPORT_DIR,
    DEFAULT_SQLITE_EXPORT_DIR,
    DEFAULT_TSV_EXPORT_DIR,
    check_index_exists,
)
from scribe_data.wikidata.query_data import query_data
from scribe_data.wikidata.wikidata_utils import parse_wd_lexeme_dump
from scribe_data.wikipedia.generate_autosuggestions import generate_autosuggestions


def get_data(
    language: str = None,
    data_type: Union[str, List[str]] = None,
    output_type: str = None,
    output_dir: str = None,
    overwrite: bool = False,
    outputs_per_entry: int = None,
    all_bool: bool = False,
    interactive: bool = False,
    identifier_case: str = "camel",
    wikidata_dump: str = None,
    dump_id: str = None,
    force_download: bool = False,
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

    overwrite : bool (default: False)
        Whether to overwrite existing files.

    outputs_per_entry : str
        How many outputs should be generated per data entry.

    all_bool : bool
        Get all languages and data types.

    interactive : bool (default: False)
        Whether it's running in interactive mode.

    identifier_case : str
        The case format for identifiers. Default is "camel".

    wikidata_dump : str
        The local Wikidata lexeme dump that can be used to process data.

    dump_id : str (default=None)
        The id of an explicit Wikipedia dump that the user wants to download.

    force_download : bool
        Whether a download of a Wikipedia dump should be forced.

    Returns
    -------
    None
        The requested data saved locally given file type and location arguments.

    Notes
    -----
    A value of None for dump_id will select the third from the last (latest stable dump).
    """
    # MARK: Defaults

    output_type = output_type or "json"
    if output_dir is None:
        output_dir = {
            "csv": DEFAULT_CSV_EXPORT_DIR,
            "json": DEFAULT_JSON_EXPORT_DIR,
            "sqlite": DEFAULT_SQLITE_EXPORT_DIR,
            "tsv": DEFAULT_TSV_EXPORT_DIR,
        }.get(output_type, DEFAULT_JSON_EXPORT_DIR)

    data_types = [data_type] if data_type else None

    # MARK: Get All

    def prompt_user_download_all():
        """
        Check with the user if they'd rather use Wikidata lexeme dumps before a download all call.

        Returns
        -------
        bool
            A boolean response from the user on whether they'd like to download all data.
        """
        return questionary.confirm(
            "Do you want to query Wikidata directly? (selecting 'no' will use a Wikidata lexemes dump locally to avoid large Query Service calls)",
            default=False,
        ).ask()

    if all_bool:
        if language:
            if prompt_user_download_all():
                language_or_sub_language = language.split(" ")[0]
                print(f"Updating all data types for language: {language.title()}")
                query_data(
                    languages=[language_or_sub_language],
                    data_type=None,
                    output_dir=output_dir,
                    overwrite=overwrite,
                )
                print(
                    f"Query completed for all data types for language {language.title()}."
                )

            else:
                parse_wd_lexeme_dump(
                    language=language,
                    wikidata_dump_type=["form"],
                    data_types="all",
                    type_output_dir=output_dir,
                    wikidata_dump_path=wikidata_dump,
                    overwrite_all=overwrite,
                )

        elif data_type:
            if prompt_user_download_all():
                print(f"Updating all languages for data type: {data_type.capitalize()}")
                query_data(
                    languages=None,
                    data_type=[data_type],
                    output_dir=output_dir,
                    overwrite=overwrite,
                )
                print(
                    f"Query completed for all languages for data type {data_type.capitalize()}."
                )

            else:
                parse_wd_lexeme_dump(
                    language="all",
                    wikidata_dump_type=["form"],
                    data_types=[data_type],
                    type_output_dir=output_dir,
                    wikidata_dump_path=wikidata_dump,
                    overwrite_all=overwrite,
                )

        else:
            print("Updating all languages and data types...")
            rprint(
                "[bold red]Note that the download all functionality must use Wikidata lexeme dumps to observe responsible Wikidata Query Service usage practices.[/bold red]"
            )
            parse_wd_lexeme_dump(
                language="all",
                wikidata_dump_type=["form", "translations"],
                data_types="all",
                type_output_dir=output_dir,
                wikidata_dump_path=wikidata_dump,
                overwrite_all=overwrite,
            )

    # MARK: Emojis

    elif data_type in {"emoji-keywords", "emoji_keywords"}:
        generate_emoji(language=language, output_dir=output_dir)

    # MARK: Translations

    elif data_type == "translations":
        # If no language specified, use "all".
        if language is None:
            language = "all"

        parse_wd_lexeme_dump(
            language=language,
            wikidata_dump_type=["translations"],
            type_output_dir=output_dir,
            wikidata_dump_path=wikidata_dump,
            overwrite_all=overwrite,
        )
        return

    # MARK: Autosugestions

    elif data_type == "autosuggestions":
        generate_autosuggestions(
            language=language, dump_id=dump_id, force_download=force_download
        )
        return

    # MARK: Form Dump

    elif wikidata_dump is not None:
        # If wikidata_dump is an empty string, use the default path.
        if not wikidata_dump:
            wikidata_dump = DEFAULT_DUMP_EXPORT_DIR

        parse_wd_lexeme_dump(
            language=language,
            wikidata_dump_type=["form"],
            data_types=data_types,
            type_output_dir=output_dir,
            wikidata_dump_path=wikidata_dump,
            overwrite_all=overwrite,
        )
        return

    # MARK: Query Data

    elif language and data_type:
        language_or_sub_language = language.split(" ")[0]
        data_type = data_type[0] if isinstance(data_type, list) else data_type
        print(
            f"Updating data for language(s): {language.title()}; data type(s): {data_type.capitalize()}"
        )

        json_path = Path(output_dir) / language / f"{data_type}.json"
        if not overwrite and check_index_exists(json_path):
            print(f"Skipping update for {language.title()} {data_type}.")
            return {"success": False, "skipped": True}

        def print_error_and_suggestions(error_message):
            """
            Prints an error message and suggestions for the user.
            """
            rprint(error_message)
            rprint("\n[bold yellow]Suggestions:[/bold yellow]")
            rprint(
                "[yellow]1. Try again in a few minutes\n"
                "2. Consider using a Wikidata dump with --wikidata-dump-path (-wdp)\n"
                "3. Try querying a smaller subset of data\n"
                "4. Check your network connection[/yellow]"
            )

        try:
            query_data(
                languages=[language_or_sub_language],
                data_type=data_types,
                output_dir=output_dir,
                overwrite=overwrite,
                interactive=interactive,
            )

            # Only print this line if no exception was raised.
            if not all_bool:
                print(f"Updated data was saved in: {Path(output_dir).resolve()}.")

        except json.decoder.JSONDecodeError:
            print_error_and_suggestions(
                "[bold red]Error: Invalid response from Wikidata query service. The query may be too large or the service is unavailable.[/bold red]"
            )
        except urllib.error.HTTPError as e:
            error_msg = (
                "[bold red]Error: A client error occurred. Check your request.[/bold red]"
                if 400 <= e.code < 500
                else "[bold red]Error: A server error occurred. Please try again later.[/bold red]"
            )
            print_error_and_suggestions(error_msg)
        except EndPointInternalError:
            print_error_and_suggestions(
                "[bold red]Error: The Wikidata endpoint encountered an internal error.[/bold red]"
            )
        except (IncompleteRead, URLError) as e:
            print_error_and_suggestions(
                f"[bold red]Error: Network or data transfer issue occurred: {str(e)}[/bold red]"
            )

    else:
        raise ValueError(
            "You must provide at least one --language (-l) and one --data-type (-dt). You can also use --all (-a) for all combinations or all data types using --all (-a) in place of --data-type (-dt)."
        )

    # Output Conversion

    json_input_path = Path(output_dir) / f"{language}/{data_type}.json"

    if output_type != "json" and json_input_path.exists():
        convert_wrapper(
            language=language,
            data_type=data_type,
            output_type=output_type,
            input_file=str(json_input_path),
            output_dir=output_dir,
            overwrite=overwrite,
            identifier_case=identifier_case,
        )
        os.remove(json_input_path)
