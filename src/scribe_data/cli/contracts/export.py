# SPDX-License-Identifier: GPL-3.0-or-later
"""
Export functionality for Scribe-Data contracts.
"""

import shutil
from pathlib import Path

from scribe_data.utils import DEFAULT_CONTRACTS_EXPORT_DIR

# MARK: Export Contracts


def export_contracts() -> None:
    """
    Export Scribe-Data contracts to the default contract export directory.

    Returns
    -------
    None
        Contracts are exported to the default contract export directory.
    """
    contracts_source = (
        Path(__file__).parent.parent.parent / "resources" / "data_contracts"
    )

    assert contracts_source.exists(), (
        f"Contracts source directory not found at {contracts_source}."
    )

    if DEFAULT_CONTRACTS_EXPORT_DIR.exists():
        response = (
            input(
                f"A '{DEFAULT_CONTRACTS_EXPORT_DIR}' folder already exists with the Scribe-Data contracts. "
                "Do you want to overwrite it? (y/[n]): "
            )
            .strip()
            .lower()
        )

        if response != "y":
            print("Export cancelled.")
            return

        shutil.rmtree(DEFAULT_CONTRACTS_EXPORT_DIR)

    shutil.copytree(contracts_source, DEFAULT_CONTRACTS_EXPORT_DIR)
    print(f"Contracts successfully exported to {DEFAULT_CONTRACTS_EXPORT_DIR}.")
