# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for getting languages-data types packs for the Scribe-Data CLI.
"""

import json
import os
import urllib.error
from http.client import IncompleteRead
from pathlib import Path
from urllib.error import URLError

import questionary
from rich import print as rprint
from SPARQLWrapper.SPARQLExceptions import EndPointInternalError

from scribe_data.cli.convert.wrapper import convert_wrapper
from scribe_data.unicode.generate_emoji_keywords import generate_emoji
from scribe_data.utils import (
    DEFAULT_CSV_EXPORT_DIR,
    DEFAULT_JSON_EXPORT_DIR,
    DEFAULT_SQLITE_EXPORT_DIR,
    DEFAULT_TSV_EXPORT_DIR,
    DEFAULT_WIKIDATA_DUMP_EXPORT_DIR,
    DEFAULT_WIKTIONARY_JSON_EXPORT_DIR,
    check_index_exists,
)
from scribe_data.wikidata.query_data import query_data
from scribe_data.wikidata.wikidata_utils import parse_wd_lexeme_dump


def get_data(
    languages: list[str] | None = None,
    data_types: list[str] | None = None,
    output_type: str = "json",
    overwrite: bool = False,
    outputs_per_entry: int = 0,
    all_bool: bool = False,
    interactive: bool = False,
    identifier_case: str = "camel",
    wikidata_dump_path: Path | None = None,
    wiktionary_dump: str | None = None,
) -> dict[str, bool] | None:
    """
    Function for controlling the data get process for the CLI.

    Parameters
    ----------
    languages : list[str]
        The language(s) to get.

    data_types : list[str]
        The data type(s) to get.

    output_type : str
        The output file type.

    overwrite : bool, default=False
        Whether to overwrite existing files.

    outputs_per_entry : str
        How many outputs should be generated per data entry.

    all_bool : bool
        Get all languages and data types.

    interactive : bool, default: False
        Whether it's running in interactive mode.

    identifier_case : str
        The case format for identifiers. Default is "camel".

    wikidata_dump_path : Path
        The local Wikidata lexeme dump that can be used to process data.

    wiktionary_dump : str
        Path to enwiktionary-*-pages-articles.xml.bz2 for translations.
        Use "enwiktionary" to search output directory.

    Returns
    -------
    Dict[str, bool] | None
        The requested data saved locally given file type and location arguments.
    """
    # MARK: Defaults

    if data_types == ["translations"]:
        output_dir = DEFAULT_WIKTIONARY_JSON_EXPORT_DIR

    else:
        output_dir = {
            "csv": DEFAULT_CSV_EXPORT_DIR,
            "json": DEFAULT_JSON_EXPORT_DIR,
            "sqlite": DEFAULT_SQLITE_EXPORT_DIR,
            "tsv": DEFAULT_TSV_EXPORT_DIR,
        }.get(output_type, DEFAULT_JSON_EXPORT_DIR)

    language_or_languages = (
        "language" if languages and len(languages) == 1 else "languages"
    )
    type_or_types = "type" if data_types and len(data_types) == 1 else "types"

    # MARK: Get All

    def prompt_user_download_all() -> bool:
        """
        Check with the user if they'd rather use Wikidata lexeme dumps before a download all call.

        Returns
        -------
        bool
            A boolean response from the user on whether they'd like to download all data.
        """
        return questionary.confirm(
            "Do you want to query Wikidata directly? Selecting 'no' will use a Wikidata lexemes dump locally to avoid large Wikidata Query Service calls. (y/[n]): ",
            default=False,
        ).ask()

    if all_bool:
        if languages:
            if prompt_user_download_all():
                language = languages[0]  # only one passed
                language_or_sub_language = language.split(" ")[0]
                print(f"Updating all data types for language: {language.title()}")
                query_data(
                    languages=[language_or_sub_language],
                    data_types=["all"],
                    output_dir=output_dir,
                    overwrite=overwrite,
                )
                print(
                    f"Query completed for all data types for language {language.title()}."
                )

            else:
                parse_wd_lexeme_dump(
                    languages=languages,
                    data_types=["all"],
                    wikidata_dump_type=["form"],
                    output_dir=output_dir,
                    wikidata_dump_path=wikidata_dump_path,
                    overwrite_all=overwrite,
                )

        elif data_types:
            if prompt_user_download_all():
                data_type = data_types[0]
                print(f"Updating all languages for data type: {data_type}")
                query_data(
                    languages=["all"],
                    data_types=data_types,
                    output_dir=output_dir,
                    overwrite=overwrite,
                )
                print(f"Query completed for all languages for data type: {data_type}")

            else:
                parse_wd_lexeme_dump(
                    languages=["all"],
                    data_types=data_types,
                    wikidata_dump_type=["form"],
                    output_dir=output_dir,
                    wikidata_dump_path=wikidata_dump_path,
                    overwrite_all=overwrite,
                )

        else:
            print("Updating all languages and data types...")
            rprint(
                "[bold red]Note that the download all functionality must use Wikidata lexeme dumps to observe responsible Wikidata Query Service usage practices.[/bold red]"
            )
            parse_wd_lexeme_dump(
                languages=["all"],
                data_types=["all"],
                wikidata_dump_type=["form", "translations"],
                output_dir=output_dir,
                wikidata_dump_path=wikidata_dump_path,
                overwrite_all=overwrite,
            )

    # MARK: Emojis

    elif (
        languages
        and data_types
        and len(data_types) == 1
        and data_types[0] in {"emoji-keywords", "emoji_keywords"}
    ):
        generate_emoji(
            language=languages[0],  # only one possible
            output_dir=output_dir,
        )

    # MARK: Translations

    elif data_types == ["translations"]:
        from scribe_data.wiktionary.parse_translations import (
            parse_wiktionary_translations,
        )

        parse_wiktionary_translations(
            target_languages=languages,
            wiktionary_dump_path=wiktionary_dump,
            output_dir=output_dir,
            overwrite=overwrite,
        )
        return

    # MARK: Form Dump

    elif wikidata_dump_path is not None:
        # If wikidata_dump is an empty string, use the default path.
        if not wikidata_dump_path:
            wikidata_dump_path = DEFAULT_WIKIDATA_DUMP_EXPORT_DIR

        parse_wd_lexeme_dump(
            languages=languages or ["all"],
            data_types=data_types,
            wikidata_dump_type=["form"],
            output_dir=output_dir,
            wikidata_dump_path=wikidata_dump_path,
            overwrite_all=overwrite,
        )
        return

    # MARK: Query Data

    elif languages and data_types:
        language_or_sub_language = languages[0].split(" ")[0]
        data_type = data_types[0] if isinstance(data_types, list) else data_types
        print(
            f"Getting data for {language_or_languages}: {language_or_sub_language.title()}; data {type_or_types}: "
            f"{', '.join([t.capitalize() for t in data_types])}"
        )

        json_path = Path(output_dir) / language_or_sub_language / f"{data_type}.json"
        if not overwrite and check_index_exists(json_path):
            print(
                f"Skipping update for {language_or_sub_language.title()} {data_type}."
            )
            return {"success": False, "skipped": True}

        def print_error_and_suggestions(error_message: str) -> None:
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
                data_types=data_types,
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

        # MARK: Output Conversion

        json_input_path = (
            Path(output_dir) / f"{language_or_sub_language}/{data_type}.json"
        )

        if output_type and output_type != "json" and json_input_path.exists():
            convert_wrapper(
                languages=[language_or_sub_language],
                data_types=data_types,
                input_path=json_input_path,
                output_type=output_type,
                overwrite=overwrite,
                identifier_case=identifier_case,
            )
            os.remove(json_input_path)

    else:
        raise ValueError(
            "You must provide at least one --language (-l) and one --data-type (-dt). You can also use --all (-a) for all combinations or all data types using --all (-a) in place of --data-type (-dt)."
        )
