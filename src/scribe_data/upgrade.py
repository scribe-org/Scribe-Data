# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Update the Scribe-Data CLI based on install method.
"""

import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import requests

from scribe_data.cli.version import get_latest_version, get_local_version


def compute_file_hash(file_path):
    """
    Compute the SHA256 hash of a file.

    Parameters
    ----------
    file_path : Path
        The path to the file to hash.

    Returns
    -------
    str
        The SHA256 hash of the file as a hexadecimal string.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the specified path.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"No such file or directory: {file_path}")
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def needs_update(existing_file, new_file):
    """
    Check if a file needs updating based on its hash.

    Parameters
    ----------
    existing_file : Path
        The path to the existing file.
    new_file : Path
        The path to the new file to compare against.

    Returns
    -------
    bool
        True if the file needs to be updated, False otherwise.
    """
    if not existing_file.exists():
        return True
    return compute_file_hash(existing_file) != compute_file_hash(new_file)


def upgrade_cli():
    """
    Upgrade Scribe-Data to the latest version.

    This function downloads the latest release from GitHub, replaces local files
    while preserving specific directories and user files, and installs the new version.

    Raises
    ------
    subprocess.CalledProcessError
        If the pip install command fails during the upgrade process.
    """
    local_version = get_local_version()
    latest_version = get_latest_version()
    latest_version = latest_version.split("v")[-1]

    if local_version == latest_version:
        print("You already have the latest version of Scribe-Data.")
        return

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

        # Define directories and files to preserve
        preserve_dirs = {"venv"}
        preserve_files = set()
        # Identify user-created files (files not in the new version)
        source_files = {item.name for item in extracted_dir.iterdir() if item.is_file()}
        for item in Path.cwd().iterdir():
            if (
                item.is_file()
                and item.name not in source_files
                and item.name != f"Scribe-Data-{latest_version}.tar.gz"
            ):
                preserve_files.add(item.name)

        # Update files and directories
        for item in extracted_dir.iterdir():
            dest_path = Path.cwd() / item.name
            if item.is_dir():
                if item.name in preserve_dirs:
                    print(f"Preserving directory: {item.name}")
                    continue
                if dest_path.exists():
                    print(f"Removing existing directory: {item.name}")
                    shutil.rmtree(dest_path)
                print(f"Copying directory: {item.name}")
                shutil.copytree(item, dest_path)
            elif item.is_file():
                if item.name in preserve_files:
                    print(f"Preserving user file: {item.name}")
                    continue
                if needs_update(dest_path, item):
                    print(f"Updating file: {item.name}")
                    shutil.copy2(item, dest_path)
                else:
                    print(f"File unchanged, skipping: {item.name}")

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
                f"Failed to install the local version of Scribe-Data with error {e}. "
                "Please try manually running 'pip install -e .'"
            )

    else:
        print(f"Failed to download the update. Status code: {response.status_code}")


if __name__ == "__main__":
    upgrade_cli()
