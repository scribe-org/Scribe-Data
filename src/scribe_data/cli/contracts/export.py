# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to export data contracts to the current working directory.
"""

import shutil
from pathlib import Path

from rich import print as rprint

from scribe_data.cli.contracts.filter import scribe_data_contracts


def export_contracts(destination: Path):
    """
    Export the internal data contracts to the specified destination.

    Parameters
    ----------
    destination : Path
        The directory path where the 'contracts' folder should be exported.

    Returns
    -------
    None
        This function does not return a value; it performs a file system operation.

    Raises
    ------
    FileExistsError
        Raised if a 'contracts' directory already exists at the destination.
    Exception
        Raised for unexpected I/O errors during the directory copy process.
    """
    source_path = scribe_data_contracts
    dest_path = destination / "contracts"
    try:
        shutil.copytree(source_path, dest_path)
        rprint("[bold green]Successfully exported data contracts.[/bold green]")
    except FileExistsError as e:
        rprint(f"[bold red]Error exporting data contracts: {e}[/bold red]")

    except Exception as e:
        rprint(f"[bold red]An error occurred: {e}[/bold red]")
