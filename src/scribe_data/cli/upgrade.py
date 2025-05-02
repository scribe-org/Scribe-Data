# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to update the Scribe-Data CLI based on install method.
"""

import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import requests

from scribe_data.cli.version import get_latest_version, get_local_version


def upgrade_cli():
    """
    Upgrade the Scribe-Data CLI to the latest version.

    Returns
    -------
    None
        The package is updated if possible.
    """
    local_version = get_local_version()
    latest_version = get_latest_version()
    latest_version = latest_version.split("v")[-1]

    if local_version == latest_version:
        print("You already have the latest version of Scribe-Data.")

    if local_version < latest_version:
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

        except subprocess.CalledProcessError as e:
            print(
                f"Failed to install the local version of Scribe-Data with error {e}. Please try manually running 'pip install -e .'"
            )

    else:
        print(f"Failed to download the update. Status code: {response.status_code}")
