# SPDX-License-Identifier: GPL-3.0-or-later
"""
Script to update the Scribe-Data unicode data from CLDR.

Examples
--------
>>> python3 src/scribe_data/unicode/update_unicode_data.py
"""

import os
from pathlib import Path


def check_install_node_modules():
    """
    Check to see if node modules have been installed in Scribe-Data, and if not installs them.
    """
    if not (Path.cwd() / "node_modules").exists():
        print(
            "\nInstalling necessary Node modules to allow for emoji keyword extraction.\n"
        )
        os.system("npm install")

    print("Moving Unicode files to appropriate location within Scribe-Data.")
    os.system("mv node_modules/cldr-annotations-derived-full src/scribe_data/unicode")
    os.system("mv node_modules/cldr-annotations-full src/scribe_data/unicode")

    print("Removing `node_modules` from the current working directory.")
    os.system("rm -rf node_modules")


if __name__ == "__main__":
    check_install_node_modules()
