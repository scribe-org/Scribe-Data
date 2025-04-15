# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to update the Scribe-Data CLI based on install method.
"""

import hashlib
import os  # noqa: F401
import shutil
import subprocess  # noqa: F401
import sys  # noqa: F401
import tarfile  # noqa: F401
from pathlib import Path

import requests  # noqa: F401

from scribe_data.cli.version import get_latest_version, get_local_version  # noqa: F401


def compute_file_hash(file_path):
    """Compute the SHA256 hash of a file.

    Args:
        file_path (Path): Path to the file.

    Returns:
        str: The SHA256 hash of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"No such file or directory: {file_path}")
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def needs_update(existing_file, new_file):
    """Check if the existing file needs to be updated based on its hash."""
    if not existing_file.exists():
        return True
    return compute_file_hash(existing_file) != compute_file_hash(new_file)


def upgrade_cli():
    """Upgrade Scribe-Data to the latest version."""
    # Mock the version check for testing
    local_version = "1.0.0"  # Hardcode for testing
    latest_version = "1.0.1"  # Hardcode for testing

    if local_version == latest_version:
        print("You already have the latest version of Scribe-Data.")
        return

    if local_version < latest_version:
        print(f"Current version: {local_version}")
        print(f"Latest version: {latest_version}")

    print("Updating Scribe-Data...")

    # Mock the download for testing
    print("Using local new-version directory for testing...")
    temp_dir = Path(f"temp_Scribe-Data-{latest_version}")
    temp_dir.mkdir(exist_ok=True)
    shutil.copytree(
        Path("../new-version/Scribe-Data-1.0.1"),
        temp_dir / f"Scribe-Data-{latest_version}",
    )
    print("Local test setup complete.")

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
    print("Cleanup complete.")

    # Skip pip install for testing
    print("Skipping pip install for testing.")

    print("Upgrade complete!")


if __name__ == "__main__":
    upgrade_cli()
