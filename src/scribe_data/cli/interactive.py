"""
Interactive mode functionality for the Scribe-Data CLI.

This module provides an interactive interface for users to select languages,
data types and output options for getting Wikidata data using Scribe-Data.

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

from scribe_data.cli.cli_utils import (
    data_type_metadata,
    language_metadata,
)
from scribe_data.cli.get import get_data
from scribe_data.utils import (
    DEFAULT_CSV_EXPORT_DIR,
    DEFAULT_JSON_EXPORT_DIR,
    DEFAULT_TSV_EXPORT_DIR,
)


def get_selection(user_input: str, options: list[str]) -> list[str]:
    """
    Parse user input to get selected options.

    Parameters
    ----------
        user_input : str
            The user's input string.

        options : List[str]
            The list of available options given the interactive mode stage.

    Returns
    -------
        List[str]
            The options available in interactive mode and CLI directions.
    """
    if user_input.lower() == "a":
        return options

    try:
        indices = [int(i.strip()) - 1 for i in user_input.split(",")]

        return [options[i] for i in indices]

    except (ValueError, IndexError):
        return [opt for opt in user_input.split(",") if opt in options]


def select_languages() -> list[str]:
    """
    Display language options and get user selection.

    Returns
    -------
        List[str]
            The languages available in Scribe-Data and CLI directions.
    """
    print("\nLanguage options:")
    languages = [
        lang["language"].capitalize() for lang in language_metadata["languages"]
    ]
    for i, lang in enumerate(languages, 1):
        print(f"{i}. {lang}")

    lang_input = input(
        "\nPlease enter the languages to get data for, their numbers or (a) for all languages: "
    )

    return get_selection(lang_input, languages)


def select_data_types() -> list[str]:
    """
    Display data type options and get user selection.

    Returns
    -------
        List[str]
            The data types available in Scribe-Data and CLI directions.
    """
    print("\nData type options:")
    data_types = data_type_metadata["data-types"]

    for i, dt in enumerate(data_types, 1):
        print(f"{i}. {dt}")

    dt_input = input(
        "\nPlease enter the data types to get, their numbers or (a) for all data types: "
    )

    return get_selection(dt_input, list(data_types.keys()))


def get_output_options() -> dict:
    """
    Get output options from user.

    Returns
    -------
        dict
            Output options including type, directory, and overwrite flag
    """
    valid_types = ["json", "csv", "tsv"]
    output_type = (
        input("File type to export (json, csv, tsv) [json]: ").strip().lower() or "json"
    )

    while output_type not in valid_types:
        print(
            f"Invalid output type '{output_type}'. Please choose from 'json', 'csv', or 'tsv'."
        )
        output_type = (
            input("File type to export (json, csv, tsv) [json]: ").strip().lower()
            or "json"
        )

    if output_type == "csv":
        default_export_dir = DEFAULT_CSV_EXPORT_DIR

    elif output_type == "tsv":
        default_export_dir = DEFAULT_TSV_EXPORT_DIR

    else:
        default_export_dir = DEFAULT_JSON_EXPORT_DIR

    output_dir = (
        input(f"Export directory path [./{default_export_dir}]: ").strip()
        or f"./{default_export_dir}"
    )
    overwrite = (
        input("Overwrite existing data without asking (y/n) [n]: ").strip().lower()
        == "y"
    )

    return {"type": output_type, "dir": output_dir, "overwrite": overwrite}


def run_interactive_mode():
    """
    Run the interactive mode for Scribe-Data CLI.

    This function guides the user through selecting languages, data types and output options.
    The process is then executed based on these selections.
    """
    selected_languages = select_languages()
    selected_data_types = select_data_types()
    output_options = get_output_options()

    print(
        f"Data will be exported as {output_options['type'].upper()} files to '{output_options['dir']}'."
    )

    for language in selected_languages:
        for data_type in selected_data_types:
            get_data(
                language,
                data_type,
                output_options["dir"],
                output_options["overwrite"],
                output_options["type"],
            )


# This function can be called from main.py when the -i or --interactive flag is used.
def start_interactive_mode():
    print("Welcome to Scribe-Data interactive mode!")
    run_interactive_mode()


if __name__ == "__main__":
    # This allows for testing the interactive mode directly.
    start_interactive_mode()
