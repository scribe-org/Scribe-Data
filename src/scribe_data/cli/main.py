"""
Setup and commands for the Scribe-Data command line interface.

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

#!/usr/bin/env python3
import argparse

from scribe_data.cli.convert import convert_to_csv_or_tsv, convert_to_sqlite
from scribe_data.cli.get import get_data
from scribe_data.cli.interactive import start_interactive_mode
from scribe_data.cli.list import list_wrapper
from scribe_data.cli.total import get_total_lexemes
from scribe_data.cli.version import get_version_message

LIST_DESCRIPTION = "List languages, data types and combinations of each that Scribe-Data can be used for."
GET_DESCRIPTION = (
    "Get data from Wikidata and other sources for the given languages and data types."
)
TOTAL_DESCRIPTION = "Check Wikidata for the total available data for the given languages and data types."
CONVERT_DESCRIPTION = "Convert data returned by Scribe-Data to different file types."
CLI_EPILOG = "Visit the codebase at https://github.com/scribe-org/Scribe-Data and documentation at https://scribe-data.readthedocs.io to learn more!"


def main() -> None:
    # MARK: CLI Base

    parser = argparse.ArgumentParser(
        description="The Scribe-Data CLI is a tool for extracting language data from Wikidata and other sources.",
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser._actions[0].help = "Show this help message and exit."
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{get_version_message()}",
        help="Show the local and latest versions of the Scribe-Data CLI.",
    )
    parser.add_argument("-u", "--upgrade", help="Upgrade the Scribe-Data CLI.")

    # MARK: List

    list_parser = subparsers.add_parser(
        "list",
        aliases=["l"],
        help=LIST_DESCRIPTION,
        description=LIST_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )
    list_parser._actions[0].help = "Show this help message and exit."
    list_parser.add_argument(
        "-lang",
        "--language",
        nargs="?",
        const=True,
        help="List options for all or given languages.",
    )
    list_parser.add_argument(
        "-dt",
        "--data-type",
        nargs="?",
        const=True,
        help="List options for all or given data types.",
    )
    list_parser.add_argument(
        "-a",
        "--all",
        action=argparse.BooleanOptionalAction,
        help="List all languages and data types.",
    )

    # MARK: GET

    get_parser = subparsers.add_parser(
        "get",
        aliases=["g"],
        help=GET_DESCRIPTION,
        description=GET_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )
    get_parser._actions[0].help = "Show this help message and exit."
    get_parser.add_argument(
        "-lang", "--language", type=str, help="The language(s) to get."
    )
    get_parser.add_argument(
        "-dt", "--data-type", type=str, help="The data type(s) to get."
    )
    get_parser.add_argument(
        "-od", "--output-dir", type=str, help="The output directory path for results."
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
        "-a",
        "--all",
        action=argparse.BooleanOptionalAction,
        help="Get all languages and data types.",
    )
    get_parser.add_argument(
        "-i", "--interactive", action="store_true", help="Run in interactive mode"
    )

    # MARK: Total

    total_parser = subparsers.add_parser(
        "total",
        aliases=["t"],
        help=TOTAL_DESCRIPTION,
        description=TOTAL_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )
    total_parser._actions[0].help = "Show this help message and exit."
    total_parser.add_argument(
        "-lang", "--language", type=str, help="The language(s) to check totals for."
    )
    total_parser.add_argument(
        "-dt", "--data-type", type=str, help="The data type(s) to check totals for."
    )

    # MARK: Convert

    convert_parser = subparsers.add_parser(
        "convert",
        aliases=["c"],
        help=CONVERT_DESCRIPTION,
        description=CONVERT_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )
    convert_parser._actions[0].help = "Show this help message and exit."
    convert_parser.add_argument(
        "-f", "--file", type=str, help="The file to convert to a new type."
    )
    convert_parser.add_argument(
        "-ot",
        "--output-type",
        type=str,
        choices=["json", "csv", "tsv", "sqlite"],
        help="The output file type.",
    )
    convert_parser.add_argument(
        "-ko",
        "--keep-original",
        action="store_false",
        help="Whether to keep the file to be converted (default: True).",
    )

    # MARK: Setup CLI

    args = parser.parse_args()

    if args.command in ["list", "l"]:
        list_wrapper(args.language, args.data_type, args.all)

    elif args.command in ["get", "g"]:
        if args.interactive:
            start_interactive_mode()

        else:
            get_data(
                args.language,
                args.data_type,
                args.output_dir,
                args.overwrite,
                args.output_type,
                args.outputs_per_entry,
                args.all,
            )

    elif args.command in ["total", "t"]:
        if not args.language and not args.data_type:
            print(
                "Error: You must provide either at least one of the --language (-l) or --data-type (-dt) options"
            )
            total_parser.print_help()
            return

        get_total_lexemes(args.language, args.data_type)

    elif args.command in ["convert", "c"]:
        if args.output_type in ["csv", "tsv"]:
            convert_to_csv_or_tsv(
                args.language,
                args.data_type,
                args.output_dir,
                args.overwrite,
            )

        elif args.output_type == "sqlite":
            convert_to_sqlite(
                args.language,
                args.data_type,
                args.output_dir,
                args.overwrite,
            )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
