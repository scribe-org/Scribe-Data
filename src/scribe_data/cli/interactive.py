"""
Interactive mode functionality for the Scribe-Data CLI.

This module provides an interactive interface for users to select languages,
data types and output options for querying Wikidata data using Scribe-Data.

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
from scribe_data.cli.query import query_data
from scribe_data.utils import DEFAULT_JSON_EXPORT_DIR


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
        indices = [int(i) - 1 for i in user_input.split(",")]
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
    print("Language options:")
    languages = [
        lang["language"].capitalize() for lang in language_metadata["languages"]
    ]
    for i, lang in enumerate(languages, 1):
        print(f"{i}. {lang}")

    lang_input = input(
        "\nPlease enter the languages to query data for, their numbers or (a) for all languages: "
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
        "\nPlease enter the data types to query, their numbers or (a) for all data types: "
    )

    return get_selection(dt_input, data_types)


def get_output_options() -> dict:
    """
    Get output options from user.

    Returns
    -------
        dict
            Output options including type, directory, and overwrite flag
    """
    output_type = (
        input("File type to export (json, csv, tsv) [json]: ").lower() or "json"
    )
    output_dir = (
        input(f"Export directory path [./{DEFAULT_JSON_EXPORT_DIR}]: ")
        or f"./{DEFAULT_JSON_EXPORT_DIR}"
    )
    overwrite = (
        input("Overwrite existing data without asking (y/n) [n]: ").lower() == "y"
    )

    return {"type": output_type, "dir": output_dir, "overwrite": overwrite}


def run_interactive_mode():
    """
    Run the interactive mode for Scribe-Data CLI.

    This function guides the user through selecting languages, data types and output options.
    The query is then executed based on these selections.
    """
    selected_languages = select_languages()
    selected_data_types = select_data_types()
    output_options = get_output_options()

    if len(selected_languages) == 1:
        print(
            f"\nQuerying {', '.join(selected_data_types)} for {', '.join(selected_languages)}."
        )

    else:
        print(
            f"\nQuerying {', '.join(selected_data_types)} for {', '.join(selected_languages)} languages."
        )

    print(
        f"Data will be exported as {output_options['type'].upper()} files to '{output_options['dir']}'."
    )

    # Convert lists to comma-separated strings for query_data.
    languages_str = ",".join(selected_languages)
    data_types_str = ",".join(selected_data_types)

    query_data(
        languages_str,
        data_types_str,
        output_options["dir"],
        output_options["overwrite"],
        output_options["type"],
    )


# This function can be called from main.py when the -i or --interactive flag is used.
def start_interactive_mode():
    print("Welcome to Scribe-Data interactive mode!\n")
    run_interactive_mode()


if __name__ == "__main__":
    # This allows for testing the interactive mode directly.
    start_interactive_mode()
