# SPDX-FileCopyrightText: 2024 Scribe-Data contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Export functionality for Scribe-Data contracts."""

import shutil
from pathlib import Path


def export_contracts(output_dir: str = ".") -> None:
    """
    Export Scribe-Data contracts to the given directory.

    Parameters
    ----------
    output_dir : str
        The directory to export contracts to.

    Returns
    -------
    None
        Contracts are exported to the given directory.
    """
    contracts_source = (
        Path(__file__).parent.parent.parent / "resources" / "data_contracts"
    )
    output_path = Path(output_dir) / "contracts"

    if not contracts_source.exists():
        print(f"Error: Contracts source directory not found at {contracts_source}")
        return

    if output_path.exists():
        response = input(
            f"A 'contracts' folder already exists at {output_path}. "
            "Do you want to overwrite it? (y/n): "
        ).strip().lower()

        if response != "y":
            print("Export cancelled.")
            return

        shutil.rmtree(output_path)

    shutil.copytree(contracts_source, output_path)
    print(f"Contracts successfully exported to {output_path}")