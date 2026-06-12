# SPDX-License-Identifier: GPL-3.0-or-later
"""
Interactive mode execution for the Scribe-Data CLI to allow users to select request arguments.
"""

import logging

import questionary
from rich import print as rprint
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from tqdm import tqdm

from scribe_data.cli.get import get_data
from scribe_data.cli.interactive.config import (
    THANK_YOU_MESSAGE,
    interactive_mode_config,
)
from scribe_data.cli.interactive.prompt import (
    prompt_for_data_types,
    prompt_for_languages,
)
from scribe_data.cli.total.wrapper import total_wrapper
from scribe_data.wikidata.wikidata_utils import parse_wd_lexeme_dump

# MARK: Logging

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],  # Enable markup for colors
)
console = Console()
logger = logging.getLogger("rich")

# MARK: Execute Request


def execute_request() -> None:
    """
    Execute the interactive mode request based on current configuration.

    Returns
    -------
    None
        An interactive mode request is ran.
    """
    if (
        not interactive_mode_config.selected_languages
        or not interactive_mode_config.selected_data_types
    ):
        rprint("[bold red]Error: Please configure languages and data types.[/bold red]")
        return

    # Calculate total operations
    total_operations = len(interactive_mode_config.selected_languages) * len(
        interactive_mode_config.selected_data_types
    )

    with tqdm(
        total=total_operations,
        desc="Exporting data",
        unit="operation",
    ) as pbar:
        for language in interactive_mode_config.selected_languages:
            for data_type in interactive_mode_config.selected_data_types:
                pbar.set_description(f"Exporting {language} {data_type} data")

                try:
                    get_data(
                        languages=[language],
                        data_types=[data_type],
                        output_type=interactive_mode_config.output_type,
                        overwrite=interactive_mode_config.overwrite,
                        interactive=True,
                    )
                    # The data was successfully written to file, so we can log success.
                    logger.info(
                        f"[green]✔ Successfully exported {language} {data_type} data.[/green]"
                    )

                except Exception as e:
                    logger.error(
                        f"[red]✖ Failed to export {language} {data_type} data: {str(e)}[/red]"
                    )

                pbar.update(1)

    if interactive_mode_config.overwrite:
        rprint("[bold green]Data request completed successfully![/bold green]")


def request_total_lexeme_loop() -> None:
    """
    Continuously prompts for lexeme requests until exit.
    """
    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                questionary.Choice("Configure total lexemes request", "total"),
                questionary.Choice("Run total lexemes request", "run"),
                questionary.Choice(
                    "Run total lexemes request with lexeme dumps", "run_all"
                ),
                questionary.Choice("Exit", "exit"),
            ],
        ).ask()

        if choice == "run":
            total_wrapper(
                languages=interactive_mode_config.selected_languages,
                data_types=interactive_mode_config.selected_data_types,
                all_bool=False,
            )
            (
                interactive_mode_config.selected_languages,
                interactive_mode_config.selected_data_types,
            ) = [], []
            rprint(THANK_YOU_MESSAGE)
            break

        elif choice == "run_all":
            parse_wd_lexeme_dump(
                languages=interactive_mode_config.selected_languages,
                wikidata_dump_type=["total"],
                interactive_mode=True,
            )
            break

        elif choice == "exit":
            return

        else:
            prompt_for_languages()
            prompt_for_data_types()


# MARK: Summary


def display_summary() -> None:
    """
    Display a summary of the interactive mode request to run.
    """
    table = Table(
        title="Scribe-Data Request Configuration Summary", style="bright_white"
    )

    table.add_column("Setting", style="bold cyan", no_wrap=True)
    table.add_column("Value(s)", style="magenta")

    table.add_row(
        "Languages",
        ", ".join(interactive_mode_config.selected_languages) or "None",
    )
    table.add_row(
        "Data Types",
        ", ".join(interactive_mode_config.selected_data_types) or "None",
    )
    table.add_row("Output Type", interactive_mode_config.output_type)
    table.add_row("Overwrite", "Yes" if interactive_mode_config.overwrite else "No")

    console.print("\n")
    console.print(table, justify="left")
    console.print("\n")
