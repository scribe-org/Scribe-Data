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

from typing import List
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
import questionary
from questionary import Choice
from scribe_data.cli.cli_utils import data_type_metadata, language_metadata
from scribe_data.cli.get import get_data
from scribe_data.utils import DEFAULT_JSON_EXPORT_DIR
from scribe_data.cli.version import get_version_message

console = Console()


class ScribeDataConfig:
    def __init__(self):
        self.languages = [
            lang["language"].capitalize() for lang in language_metadata["languages"]
        ]
        self.data_types = list(data_type_metadata["data-types"].keys())
        self.selected_languages: List[str] = []
        self.selected_data_types: List[str] = []
        self.output_type: str = "json"
        self.output_dir: Path = Path(DEFAULT_JSON_EXPORT_DIR)
        self.overwrite: bool = False


config = ScribeDataConfig()


# MARK: Display Summary
def display_summary():
    table = Table(title="Scribe-Data Configuration Summary")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Languages", ", ".join(config.selected_languages) or "None")
    table.add_row("Data Types", ", ".join(config.selected_data_types) or "None")
    table.add_row("Output Type", config.output_type)
    table.add_row("Output Directory", str(config.output_dir))
    table.add_row("Overwrite", "Yes" if config.overwrite else "No")

    console.print(table)


def configure_settings():
    # MARK: Language selection
    language_choices = ["All"] + config.languages
    selected_languages = questionary.checkbox(
        "Select languages (use spacebar to select, enter to confirm):",
        choices=language_choices,
    ).ask()

    if "All" in selected_languages:
        config.selected_languages = config.languages
    elif selected_languages:
        config.selected_languages = selected_languages
    else:
        rprint(
            "[yellow]Warning: No languages selected. Please select at least one language.[/yellow]"
        )
        return configure_settings()

    # MARK: Data type selection
    data_type_choices = ["All"] + config.data_types
    selected_data_types = questionary.checkbox(
        "Select data types (use spacebar to select, enter to confirm):",
        choices=data_type_choices,
    ).ask()

    if "All" in selected_data_types:
        config.selected_data_types = config.data_types
    elif selected_data_types:
        config.selected_data_types = selected_data_types
    else:
        rprint(
            "[yellow]Warning: No data types selected. Please select at least one data type.[/yellow]"
        )
        return configure_settings()

    # MARK: Output type selection
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


def run_export():
    if not config.selected_languages or not config.selected_data_types:
        rprint(
            "[bold red]Error: Please configure languages and data types before running export.[/bold red]"
        )
        return

    # MARK: Exporting data
    with console.status("[bold green]Exporting data...[/bold green]") as status:
        for language in config.selected_languages:
            for data_type in config.selected_data_types:
                status.update(
                    f"[bold green]Exporting {language} {data_type} data...[/bold green]"
                )
                get_data(
                    language,
                    data_type,
                    config.output_type,
                    str(config.output_dir),
                    config.overwrite,
                    config.output_type,
                )
                rprint(f"[green]✓[/green] Exported {language} {data_type} data.")

    rprint(Panel.fit("[bold green]Data export completed successfully![/bold green]"))


# MARK: Start interactive mode functionality
def start_interactive_mode():
    rprint(
        f"[bold green]Welcome to {get_version_message()} interactive mode![/bold green]"
    )

    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                Choice("Configure settings", "configure"),
                Choice("Run data export", "run"),
                Choice("Exit", "exit"),
            ],
        ).ask()

        if choice == "configure":
            configure_settings()
        elif choice == "run":
            run_export()
            rprint("[bold yellow]Thank you for using Scribe-Data![/bold yellow]")
            break


if __name__ == "__main__":
    start_interactive_mode()
