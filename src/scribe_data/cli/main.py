# SPDX-License-Identifier: GPL-3.0-or-later
"""
Setup and commands for the Scribe-Data command line interface.
"""

#!/usr/bin/env python3
import argparse

from questionary import select, text
from rich import print as rprint

from scribe_data.cli.cli_utils import validate_language_and_data_type
from scribe_data.cli.contracts.check import check_contract_data_print_missing
from scribe_data.cli.contracts.export import export_contracts
from scribe_data.cli.contracts.filter import export_data_filtered_by_contracts
from scribe_data.cli.convert.wrapper import convert_wrapper
from scribe_data.cli.download.wikidata_lexeme_dump import (
    wd_lexeme_dump_download_wrapper,
)
from scribe_data.cli.download.wiktionary_dump import download_wiktionary_dumps
from scribe_data.cli.get import get_data
from scribe_data.cli.interactive.run import run_interactive_mode
from scribe_data.cli.list.wrapper import list_wrapper
from scribe_data.cli.total.wrapper import total_wrapper
from scribe_data.cli.upgrade import upgrade_cli
from scribe_data.cli.version import get_version_message

CLI_EPILOG = "Visit the codebase at https://github.com/scribe-org/Scribe-Data and documentation at https://scribe-data.readthedocs.io to learn more!"
CLI_HELP_MSG = "Show this help message and exit."


def main() -> None:
    """
    The function that controls the Scribe-Data CLI.

    Returns
    -------
    None
        A command is ran via inputs from the user.
    """
    # MARK: CLI Base

    parser = argparse.ArgumentParser(
        description="The Scribe-Data CLI is a tool for extracting language data from Wikidata, Wiktionary and other sources.",
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30),
    )
    subparsers = parser.add_subparsers(dest="command")

    parser._actions[0].help = CLI_HELP_MSG

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=get_version_message(),
        help="Show the version of the Scribe-Data CLI.",
    )
    parser.add_argument(
        "-u",
        "--upgrade",
        action="store_true",
        help="Upgrade the Scribe-Data CLI to the latest version.",
    )

    # MARK: List Args

    LIST_DESCRIPTION = "List languages, data types and combinations of each that Scribe-Data can be used for."

    list_parser = subparsers.add_parser(
        "list",
        aliases=["l"],
        help=LIST_DESCRIPTION,
        description=LIST_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )

    list_parser._actions[0].help = CLI_HELP_MSG

    list_parser.add_argument(
        "-lang",
        "--language",
        const=True,
        nargs="?",
        help="List options for all or given languages.",
    )
    list_parser.add_argument(
        "-dt",
        "--data-type",
        const=True,
        nargs="?",
        help="List options for all or given data types (e.g., nouns, verbs).",
    )
    list_parser.add_argument(
        "-a",
        "--all",
        action=argparse.BooleanOptionalAction,
        help="List all languages and data types.",
    )

    # MARK: Get Args

    GET_DESCRIPTION = "Get data from Wikidata, Wiktionary and other sources for the given languages and data types."

    get_parser = subparsers.add_parser(
        "get",
        aliases=["g"],
        help=GET_DESCRIPTION,
        description=GET_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )

    get_parser._actions[0].help = CLI_HELP_MSG

    get_parser.add_argument(
        "-lang",
        "--language",
        type=str,
        nargs="+",
        help="The language(s) to get data for.",
    )
    get_parser.add_argument(
        "-dt",
        "--data-type",
        type=str,
        nargs="+",
        help="The data type(s) to get data for (e.g., nouns, verbs).",
    )
    get_parser.add_argument(
        "-ot",
        "--output-type",
        type=str,
        choices=["json", "csv", "tsv", "sqlite"],
        help="The output file type.",
    )
    get_parser.add_argument(
        "-ope",
        "--outputs-per-entry",
        type=int,
        help="How many outputs should be generated per data entry.",
    )
    get_parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="Whether to overwrite existing files (default: False).",
    )
    get_parser.add_argument(
        "-ic",
        "--identifier-case",
        type=str,
        choices=["camel", "snake"],
        default="camel",
        help="The case format for identifiers in the output data (default: camel).",
    )
    get_parser.add_argument(
        "-a",
        "--all",
        action=argparse.BooleanOptionalAction,
        help="Get all languages and data types.",
    )
    get_parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run Scribe-Data in interactive mode to choose your commands from an helpful terminal interface",
    )

    # MARK: Total Args

    TOTAL_DESCRIPTION = "Check Wikidata for the total available data for the given languages and data types."

    total_parser = subparsers.add_parser(
        "total",
        aliases=["t"],
        help=TOTAL_DESCRIPTION,
        description=TOTAL_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )

    total_parser._actions[0].help = CLI_HELP_MSG

    total_parser.add_argument(
        "-lang", "--language", type=str, help="The language(s) to check totals for."
    )
    total_parser.add_argument(
        "-dt",
        "--data-type",
        type=str,
        help="The data type(s) to check totals for (e.g., nouns, verbs).",
    )
    total_parser.add_argument(
        "-a",
        "--all",
        action=argparse.BooleanOptionalAction,
        help="Check totals for all languages and data types.",
    )
    total_parser.add_argument(
        "-i", "--interactive", action="store_true", help="Run in interactive mode"
    )

    # MARK: Convert Args

    CONVERT_DESCRIPTION = (
        "Convert data returned by Scribe-Data to different file types."
    )

    convert_parser = subparsers.add_parser(
        "convert",
        aliases=["c"],
        help=CONVERT_DESCRIPTION,
        description=CONVERT_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )

    convert_parser._actions[0].help = CLI_HELP_MSG

    convert_parser.add_argument(
        "-lang",
        "--language",
        type=str,
        required=False,
        nargs="+",
        help="The language(s) of the file to convert.",
    )
    convert_parser.add_argument(
        "-dt",
        "--data-type",
        type=str,
        required=False,
        nargs="+",
        help="The data type(s) of the file to convert (e.g., nouns, verbs).",
    )
    convert_parser.add_argument(
        "-ot",
        "--output-type",
        type=str,
        choices=["json", "csv", "tsv", "sqlite"],
        default="False",
        help="The output file type.",
    )
    convert_parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="Whether to overwrite existing files (default: False).",
    )
    convert_parser.add_argument(
        "-ko",
        "--keep-original",
        action="store_true",
        default=True,
        help="Whether to keep the original file to be converted (default: True).",
    )
    convert_parser.add_argument(
        "-ic",
        "--identifier-case",
        type=str,
        choices=["camel", "snake"],
        default="camel",
        help="The case format for identifiers in the output data (default: camel).",
    )
    convert_parser.add_argument(
        "-a",
        "--all",
        action=argparse.BooleanOptionalAction,
        help="Convert all languages and data types.",
    )
    convert_parser.add_argument(
        "-i", "--interactive", action="store_true", help="Run in interactive mode"
    )

    # MARK: Download Args

    DOWNLOAD_DESCRIPTION = (
        "Download Wikidata lexeme or Wiktionary dumps from dumps.wikimedia.org."
    )

    download_parser = subparsers.add_parser(
        "download",
        aliases=["d"],
        help=DOWNLOAD_DESCRIPTION,
        description=DOWNLOAD_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )

    download_parser._actions[0].help = CLI_HELP_MSG

    download_parser.add_argument(
        "-lang",
        "--language",
        type=str,
        nargs="+",
        help="Target language or ISO code for the Wiktionary dump(s) to download.",
    )
    download_parser.add_argument(
        "-ds",
        "--dump-snapshot",
        type=str,
        default="latest",
        nargs="?",
        help="The desired snapshot of a Wikidata or Wiktionary dump (default 'latest'). Optionally specify date in YYYYMMDD format.",
    )

    # MARK: Interactive Args

    interactive_parser = subparsers.add_parser(
        "interactive",
        aliases=["i"],
        help="Run in interactive mode.",
        description="Run in interactive mode.",
    )

    interactive_parser._actions[0].help = CLI_HELP_MSG

    # MARK: Contract Args

    EXPORT_CONTRACTS_DESCRIPTION = (
        "Export Scribe-Data contracts to the current working directory."
    )

    export_contracts_parser = subparsers.add_parser(
        "export_contracts",
        aliases=["ec"],
        help=EXPORT_CONTRACTS_DESCRIPTION,
        description=EXPORT_CONTRACTS_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )
    export_contracts_parser._actions[0].help = CLI_HELP_MSG

    CHECK_CONTRACTS_DESCRIPTION = "Check the data in a Scribe-Data export directory against data contracts to see that all needed language data is included."

    check_contracts_parser = subparsers.add_parser(
        "check_contracts",
        aliases=["cc"],
        help=CHECK_CONTRACTS_DESCRIPTION,
        description=CHECK_CONTRACTS_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )
    check_contracts_parser._actions[0].help = CLI_HELP_MSG

    FILTER_BY_CONTRACTS_DESCRIPTION = (
        "Filter exported Scribe-Data data based on provided data contracts."
    )

    filter_data_parser = subparsers.add_parser(
        "filter_data",
        aliases=["fd"],
        help=FILTER_BY_CONTRACTS_DESCRIPTION,
        description=FILTER_BY_CONTRACTS_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )
    filter_data_parser._actions[0].help = CLI_HELP_MSG

    # MARK: Setup CLI

    args = parser.parse_args()

    if args.upgrade:
        upgrade_cli()
        return

    if not args.command:
        parser.print_help()
        return

    try:
        # Only validate language and data_type for relevant commands.
        if args.command in ["list", "l", "get", "g", "total", "t", "convert", "c"]:
            if (
                hasattr(args, "data_type")
                and args.data_type
                and isinstance(args.data_type, str)
            ):
                args.data_type = args.data_type.replace("-", "_")

            if hasattr(args, "language") or hasattr(args, "data_type"):
                try:
                    validate_language_and_data_type(
                        language=args.language if hasattr(args, "language") else None,
                        data_type=args.data_type
                        if hasattr(args, "data_type")
                        else None,
                    )

                except ValueError as e:
                    print(f"Input validation failed with error: {e}")
                    return

        # MARK: List

        if args.command in ["list", "l"]:
            list_wrapper(
                language=args.language, data_type=args.data_type, all_bool=args.all
            )

        # MARK: Get

        elif args.command in ["get", "g"]:
            if args.interactive:
                run_interactive_mode(operation="get")
                return

            else:
                # Handle multiple languages and data types.
                languages = ""
                if args.language is not None:
                    languages = (
                        [lang.lower() for lang in args.language]
                        if isinstance(args.language, list)
                        else [args.language.lower()]
                    )

                data_types = ""
                if args.data_type is not None:
                    data_types = (
                        [dt.lower() for dt in args.data_type]
                        if isinstance(args.data_type, list)
                        else [args.data_type.lower()]
                    )

                # Process each language-datatype combination.
                if languages and data_types:
                    for language in languages:
                        for data_type in data_types:
                            get_data(
                                languages=[language],
                                data_types=[data_type],
                                output_type=args.output_type,
                                outputs_per_entry=args.outputs_per_entry,
                                overwrite=args.overwrite,
                                all_bool=args.all,
                                identifier_case=args.identifier_case,
                                wikidata_dump_path=args.wikidata_dump_path,
                                wiktionary_dump=args.wiktionary_dump_path,
                            )

                else:
                    # Handle case where only language or data_type is provided.
                    get_data(
                        languages=languages or None,
                        data_types=data_types or None,
                        output_type=args.output_type,
                        outputs_per_entry=args.outputs_per_entry,
                        overwrite=args.overwrite,
                        all_bool=args.all,
                        identifier_case=args.identifier_case,
                        wikidata_dump_path=args.wikidata_dump_path,
                        wiktionary_dump=args.wiktionary_dump_path,
                    )

        # MARK: Total

        elif args.command in ["total", "t"]:
            if args.interactive:
                run_interactive_mode(operation="total")

            else:
                total_wrapper(
                    languages=args.language.lower()
                    if args.language is not None
                    else ["all"],
                    data_types=args.data_type.lower()
                    if args.data_type is not None
                    else ["all"],
                    all_bool=args.all,
                    wikidata_dump=args.wikidata_dump_path,
                )

        # MARK: Convert

        elif args.command in ["convert", "c"]:
            if args.interactive:
                run_interactive_mode(operation="convert")
                return

            # Handle language(s) - could be string or list.
            languages = None
            if args.language is not None:
                if isinstance(args.language, list):
                    languages = [lang.lower() for lang in args.language]

                else:
                    languages = args.language.lower()

            data_types = None
            if args.data_type is not None:
                data_types = (
                    [dt.lower() for dt in args.data_type]
                    if isinstance(args.data_type, list)
                    else args.data_type.lower()
                )

            convert_wrapper(
                languages=languages,
                data_types=data_types,
                input_path=args.input_file,
                output_type=args.output_type,
                overwrite=args.overwrite,
                identifier_case=args.identifier_case,
                all=args.all,
            )

        # MARK: Download

        elif args.command in ["download", "d"]:
            if getattr(args, "wiktionary_dump_path", False):
                download_wiktionary_dumps(
                    dump_snapshot=args.dump_snapshot,
                    **(
                        dict(language_isos=args.language)
                        if args.language is not None
                        else {}
                    ),
                )

            elif getattr(args, "wikidata_dump_path", False):
                wd_lexeme_dump_download_wrapper(
                    dump_snapshot=args.dump_snapshot,
                )

            else:
                rprint(
                    "[bold red]Please indicate if a Wikidata or Wiktionary dump should be downloaded by passing the -wdp or -wtp arguments respectively.[/bold red]"
                )

        # MARK: Interactive

        elif args.command in ["interactive", "i"]:
            rprint(
                f"[bold cyan]Welcome to {get_version_message()} interactive mode![/bold cyan]"
            )
            action = select(
                "What would you like to do?",
                choices=[
                    "Download a Wikidata lexemes dump",
                    "Download a Wiktionary dump",
                    "Check for totals",
                    "Get data",
                    "Get translations",
                    "Convert JSON",
                    "Exit",
                ],
            ).ask()

            if action == "Download a Wikidata lexemes dump":
                wd_lexeme_dump_download_wrapper()

            elif action == "Download a Wiktionary dump":
                if lang := text(
                    "Which language dump do you want to download?",
                    default="en",
                ).ask():
                    download_wiktionary_dumps(language_isos=[lang])

            elif action == "Check for totals":
                run_interactive_mode(operation="total")

            elif action == "Get data":
                run_interactive_mode(operation="get")

            elif action == "Get translations":
                run_interactive_mode(operation="translations")

            elif action == "Convert JSON":
                run_interactive_mode(operation="convert")

            else:
                print("Skipping action")

        # MARK: Contracts

        elif args.command in ["export_contracts", "ec"]:
            export_contracts()

        elif args.command in ["check_contracts", "cc"]:
            check_contract_data_print_missing(contracts_dir=args.contracts_dir)

        elif args.command in ["filter_data", "fd"]:
            export_data_filtered_by_contracts(contracts_dir=args.contracts_dir)

        else:
            parser.print_help()

    except KeyboardInterrupt:
        rprint("[bold red]Execution was interrupted by the user.[/bold red]")


if __name__ == "__main__":
    main()
