"""
Script to update the Scribe-Data unicode data from CLDR.

Example
-------
    python3 src/scribe_data/unicode/update_unicode_data.py

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

import os
from pathlib import Path


def check_install_node_modules():
    """
    Checks to see if node modules have been installed in Scribe-Data, and if not installs them.
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
