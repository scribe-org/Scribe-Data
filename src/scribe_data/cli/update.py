"""
Functions to update the Scribe-Data CLI based on install method.

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

import sys
import os
import shutil
import requests
import tarfile
import subprocess
from pathlib import Path
from scribe_data.cli.version import get_local_version, get_latest_version


def update_cli():
    local_version = get_local_version()
    latest_version = get_latest_version()
    latest_version = latest_version.split("v")[-1]

    pointer = True
    if local_version == latest_version:
        user_input = input(
            f"You are already using the latest Scribe-Data v{latest_version} version.\nDo you want to overwrite upgrade anyway? (y/n): "
        )
        pointer = False
        if user_input.lower() != "y":
            print("Update cancelled.")
            return
    if pointer:
        print(f"Current version: {local_version}")
        print(f"Latest version: {latest_version}")
    print("Updating Scribe-Data...")

    url = f"https://github.com/scribe-org/Scribe-Data/archive/refs/tags/{latest_version}.tar.gz"
    print(f"Downloading Scribe-Data v{latest_version}...")
    response = requests.get(url)

    if response.status_code == 200:
        with open(f"Scribe-Data-{latest_version}.tar.gz", "wb") as f:
            f.write(response.content)
        print(f"Download complete: Scribe-Data-{latest_version}.tar.gz")

        print("Extracting files...")
        temp_dir = Path(f"temp_Scribe-Data-{latest_version}")
        with tarfile.open(f"Scribe-Data-{latest_version}.tar.gz", "r:gz") as tar:
            tar.extractall(path=temp_dir)
        print("Extraction complete.")

        print("Updating local files...")
        extracted_dir = temp_dir / f"Scribe-Data-{latest_version}"
        for item in extracted_dir.iterdir():
            if item.is_dir():
                if (Path.cwd() / item.name).exists():
                    shutil.rmtree(Path.cwd() / item.name)
                shutil.copytree(item, Path.cwd() / item.name)
            else:
                shutil.copy2(item, Path.cwd())
        print("Local files updated successfully.")

        print("Cleaning up temporary files...")
        shutil.rmtree(temp_dir)
        os.remove(f"Scribe-Data-{latest_version}.tar.gz")
        print("Cleanup complete.")

        print("Installing the updated version of Scribe-Data locally...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
            print("Local installation successful.")
        except subprocess.CalledProcessError as e:
            print(f"Local installation failed with error: {e}")
            print(
                "Failed to install the local version of Scribe-Data. Please try manually running 'pip install -e .'"
            )

        print(f"Scribe-Data has been successfully updated to version {latest_version}")
        print("Please restart your application to use the updated version.")
    else:
        print(f"Failed to download the update. Status code: {response.status_code}")
        print("Please try again later or update manually.")

    print("Update process completed.")
