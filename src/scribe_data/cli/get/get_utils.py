# SPDX-License-Identifier: GPL-3.0-or-later
"""
Utility functions for getting data from Wikidata and other data sources.
"""

from rich import print as rprint


def print_get_execution_error_and_suggestions(error_message: str) -> None:
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
