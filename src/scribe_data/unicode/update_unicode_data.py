# SPDX-License-Identifier: GPL-3.0-or-later
"""
Script to update the Scribe-Data unicode data from CLDR.

Examples
--------
>>> python3 src/scribe_data/unicode/update_unicode_data.py
"""

import subprocess
from pathlib import Path


def check_install_node_modules() -> None:
    """
    Check to see if node modules have been installed in Scribe-Data, and if not installs them.
    """
    if not (Path.cwd() / "node_modules").exists():
        print(
            "\nInstalling necessary Node modules to allow for emoji keyword extraction.\n"
        )
        subprocess.run(["npm", "install"], check=True)

    print("Moving Unicode files to appropriate location within Scribe-Data.")
    subprocess.run(
        ["mv", "node_modules/cldr-annotations-derived-full", "src/scribe_data/unicode"],
        check=True,
    )
    subprocess.run(
        ["mv", "node_modules/cldr-annotations-full", "src/scribe_data/unicode"],
        check=True,
    )
    print("Removing `node_modules` from the current working directory.")
    subprocess.run(["rm", "-rf", "node_modules"], check=True)


if __name__ == "__main__":
    check_install_node_modules()
