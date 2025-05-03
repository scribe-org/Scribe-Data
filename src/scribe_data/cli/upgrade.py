# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to update the Scribe-Data CLI based on install method.
"""

import os
import re
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
    
    # Sanitize latest_version to extract semantic version (e.g., '4.1.0')
    version_match = re.search(r'\d+\.\d+\.\d+', latest_version)
    if not version_match:
        print(f"Error: Invalid version format in '{latest_version}'")
        return
    latest_version = version_match.group(0)  # e.g., '4.1.0'

    # Compare versions and exit if they match
    if local_version == latest_version:
        print(f"You already have the latest version of Scribe-Data: {local_version}")
        return

    print(f"Current version: {local_version}")
    print(f"Latest version: {latest_version}")
    print("Updating Scribe-Data...")

    # Construct the correct GitHub tag and URL
    tag_version = f"v{latest_version}"  # e.g., 'v4.1.0'
    url = f"https://github.com/scribe-org/Scribe-Data/archive/refs/tags/{tag_version}.tar.gz"
    print(f"Downloading Scribe-Data {tag_version}...")

    # Validate the URL before downloading
    response = requests.head(url, allow_redirects=True)
    if response.status_code != 200:
        print(f"Failed to download the update from {url}. Status code: {response.status_code}")
        print("Please check if the version exists or try again later.")
        return

    # Download the update
    response = requests.get(url)
    with open(f"Scribe-Data-{latest_version}.tar.gz", "wb") as f:
        f.write(response.content)
    print(f"Download complete: Scribe-Data-{latest_version}.tar.gz")

    print("Extracting files...")
    temp_dir = Path(f"temp_Scribe-Data-{latest_version}")
    with tarfile.open(f"Scribe-Data-{latest_version}.tar.gz", "r:gz") as tar:
        tar.extractall(path=temp_dir)
    print("Extraction complete.")

    # Define Scribe-Data-managed directories and files to update
    MANAGED_DIRS = ["scribe_data", "tests", "docs", "cli", "load", "resources", "wikidata"]  # Based on project structure
    MANAGED_FILES = ["setup.py", "README.md", "LICENSE", "CHANGELOG", "CONTRIBUTING", "MANIFEST.in", "pyproject.toml", "Brewfile", "pre-commit-config.yaml", "requirements.txt", "requirements-dev.in"]  # Root files managed by Scribe-Data
    EXCLUDE_DIRS = ["venv", ".venv", ".git", "data", "user_data"]  # Directories to preserve

    print("Updating local files...")
    extracted_dir = temp_dir / f"Scribe-Data-{latest_version}"
    for item in extracted_dir.iterdir():
        dest_path = Path.cwd() / item.name
        if item.is_dir():
            # Skip if the directory is excluded or not managed
            if item.name in EXCLUDE_DIRS or item.name not in MANAGED_DIRS:
                continue
            # Only delete and update managed directories
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.copytree(item, dest_path)
        else:
            # Only update managed files
            if item.name not in MANAGED_FILES:
                continue
            shutil.copy2(item, Path.cwd())
    print("Local files updated successfully.")

    print("Cleaning up temporary files...")
    shutil.rmtree(temp_dir)
    os.remove(f"Scribe-Data-{latest_version}.tar.gz")
    print("Cleanup complete.")

    print("Installing the updated version of Scribe-Data locally...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("Installation complete. Scribe-Data is now updated!")
    except subprocess.CalledProcessError as e:
        print(f"Installation failed: {e}. Run 'pip install -e .' manually to complete the update.")
        return