# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for checking current version of the Scribe-Data CLI.
"""

import importlib.metadata

import requests


def get_local_version():
    """
    Get the version of Scribe-Data that is currently running.

    Returns
    -------
    str
        The version of the package that is installed.
    """
    try:
        return importlib.metadata.version("scribe-data")

    except importlib.metadata.PackageNotFoundError:
        return "Unknown (Not installed via pip)"


def get_latest_version():
    """
    Get the latest version of Scribe-Data from the GitHub repository.

    Returns
    -------
    str
        The latest version of the package.
    """
    try:
        response = requests.get(
            "https://api.github.com/repos/scribe-org/Scribe-Data/releases/latest"
        )
        return response.json()["name"]

    except Exception:
        return "Unknown (Unable to fetch version)"


def get_version_message():
    """
    Return a message about the current and up to date versions of Scribe-Data.

    Returns
    -------
    str
        A message about the current version of Scribe-Data and whether it can be updated.
    """
    local_version = get_local_version()
    latest_version = get_latest_version()

    if local_version == "Unknown (Not installed via pip)":
        return f"Scribe-Data {local_version}"

    elif latest_version == "Unknown (Unable to fetch version)":
        return f"Scribe-Data {latest_version}"

    local_version_clean = local_version.strip()
    latest_version_clean = latest_version.replace("Scribe-Data", "").strip()

    if local_version_clean == latest_version_clean:
        return f"Scribe-Data v{local_version_clean}"

    return f"Scribe-Data v{local_version_clean} (Upgrade available: Scribe-Data v{latest_version_clean})\nTo update: pip install --upgrade scribe-data"
