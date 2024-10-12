"""
Interactive mode functionality for the Scribe-Data CLI to allow users to select request arguments.

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

from pathlib import Path
from typing import List
from tqdm import tqdm
import logging
import questionary

from rich.logging import RichHandler
from questionary import Choice
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from scribe_data.cli.cli_utils import data_type_metadata, language_metadata
from scribe_data.cli.get import get_data
from scribe_data.cli.version import get_version_message
from scribe_data.utils import DEFAULT_JSON_EXPORT_DIR

# MARK: Config coloring
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],  # Enable markup for colors
)
console = Console()
logger = logging.getLogger("rich")


class ScribeDataConfig:
    def __init__(self):
        self.languages = [
            lang["language"].capitalize() for lang in language_metadata["languages"]
        ]
        self.data_types = list(data_type_metadata.keys())
        self.selected_languages: List[str] = []
        self.selected_data_types: List[str] = []
        self.output_type: str = "json"
        self.output_dir: Path = Path(DEFAULT_JSON_EXPORT_DIR)
        self.overwrite: bool = False


config = ScribeDataConfig()


# MARK: Summary


def display_summary():
    """
    Displays a summary of the interactive mode request to run.
    """
    table = Table(title="Scribe-Data Configuration Summary", style="bright_white")

    table.add_column("Setting", style="bold cyan", no_wrap=True)
    table.add_column("Value(s)", style="magenta")

    table.add_row("Languages", ", ".join(config.selected_languages) or "None")
    table.add_row("Data Types", ", ".join(config.selected_data_types) or "None")
    table.add_row("Output Type", config.output_type)
    table.add_row("Output Directory", str(config.output_dir))
    table.add_row("Overwrite", "Yes" if config.overwrite else "No")

    console.print(table, justify="center")


def configure_settings():
    """
    Configures the settings of the interactive mode request.

    Asks for:
        - Languages
        - Data types
        - Output type
        - Output directory
        - Whether to overwrite
    """
    # MARK: Languages

    if not config.selected_languages:
        language_selected = False
        language_choices = ["All"] + config.languages
        selected_languages = questionary.checkbox(
            message="Select languages and press enter:",
            choices=language_choices,
        ).ask()

        if "All" in selected_languages:
            config.selected_languages = config.languages
            language_selected = True

        elif selected_languages:
            config.selected_languages = selected_languages
            language_selected = True

        else:
            rprint(
                "[yellow]No language selected. Please select at least one option with space followed by enter.[/yellow]"
            )
            if questionary.confirm("Continue?", default=True).ask():
                return configure_settings()

    else:
        language_selected = True

    if language_selected:
        # MARK: Data Types

        data_type_selected = False
        data_type_choices = ["All"] + config.data_types
        selected_data_types = questionary.checkbox(
            "Select data types and press enter:",
            choices=data_type_choices,
        ).ask()

        if "All" in selected_data_types:
            config.selected_data_types = config.data_types
            data_type_selected = True

        elif selected_data_types:
            config.selected_data_types = selected_data_types
            data_type_selected = True

        else:
            rprint(
                "[yellow]No data type selected. Please select at least one option with space followed by enter.[/yellow]"
            )
            if questionary.confirm("Continue?", default=True).ask():
                return configure_settings()

        if data_type_selected:
            # MARK: Output Type

            config.output_type = questionary.select(
                "Select output type:", choices=["json", "csv", "tsv"]
            ).ask()

            config.output_dir = Path(
                questionary.text(
                    "Enter output directory:", default=str(config.output_dir)
                ).ask()
            )

            config.overwrite = questionary.confirm(
                "Overwrite existing files?", default=config.overwrite
            ).ask()

            display_summary()


def run_request():
    """
    Runs the interactive mode request given the configuration.
    """
    if not config.selected_languages or not config.selected_data_types:
        rprint("[bold red]Error: Please configure languages and data types.[/bold red]")
        return

    # Calculate total operations
    total_operations = len(config.selected_languages) * len(config.selected_data_types)

    # MARK: Export Data
    with tqdm(
        total=total_operations,
        desc="Exporting data",
        unit="operation",
        colour="MAGENTA",
    ) as pbar:
        for language in config.selected_languages:
            for data_type in config.selected_data_types:
                pbar.set_description(f"Exporting {language} {data_type} data")

                result = get_data(
                    language=language,
                    data_type=data_type,
                    output_type=config.output_type,
                    output_dir=str(config.output_dir),
                    overwrite=config.overwrite,
                    interactive=True,
                )
                if result:
                    logger.info(
                        f"[green]✔ Exported {language} {data_type} data.[/green]"
                    )
                else:
                    logger.info(
                        f"[red]✘ Failed to export {language} {data_type} data.[/red]"
                    )

                # Update the progress bar
                pbar.update(1)

    if config.overwrite:
        rprint("[bold green]Data export completed successfully![/bold green]")


# MARK: Start


def start_interactive_mode():
    """
    Provides base options and forwarding to other interactive mode functionality.
    """
    rprint(
        f"[bold green]Welcome to {get_version_message()} interactive mode![/bold green]"
    )

    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                Choice("Configure request", "configure"),
                Choice("Run configured data request", "run"),
                Choice("Exit", "exit"),
            ],
        ).ask()

        if choice == "configure":
            configure_settings()

        elif choice == "run":
            run_request()
            rprint("[bold cyan]Thank you for using Scribe-Data![/bold cyan]")
            break

        else:
            break


if __name__ == "__main__":
    start_interactive_mode()
