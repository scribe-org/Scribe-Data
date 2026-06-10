# SPDX-License-Identifier: GPL-3.0-or-later
"""
Export functionality for Scribe-Data contracts.
"""

import shutil
from pathlib import Path

from scribe_data.utils import DEFAULT_CONTRACTS_EXPORT_DIR


def export_contracts(output_dir: Path = DEFAULT_CONTRACTS_EXPORT_DIR) -> None:
    """
    Export Scribe-Data contracts to the given directory.

    Parameters
    ----------
    output_dir : str, default=DEFAULT_CONTRACTS_EXPORT_DIR
        The directory to export contracts to.

    Returns
    -------
    None
        Contracts are exported to the given directory.
    """
    contracts_source = (
        Path(__file__).parent.parent.parent / "resources" / "data_contracts"
    )

    assert (
        contracts_source.exists()
    ), f"Contracts source directory not found at {contracts_source}."

    if output_dir.exists():
        response = (
            input(
                f"A '{output_dir}' folder already exists with the Scribe-Data contracts. "
                "Do you want to overwrite it? (y/[n]): "
            )
            .strip()
            .lower()
        )

        if response != "y":
            print("Export cancelled.")
            return

        shutil.rmtree(output_dir)

    shutil.copytree(contracts_source, output_dir)
    print(f"Contracts successfully exported to {output_dir}.")