# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for checking current version of the Scribe-Data CLI.
"""

import importlib.metadata

import requests

UNKNOWN_VERSION = "Unknown Scribe-Data version"
UNKNOWN_VERSION_NOT_PIP = f"{UNKNOWN_VERSION} (Not installed via pip)"
UNKNOWN_VERSION_NOT_FETCHED = f"{UNKNOWN_VERSION} (Unable to fetch version)"


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
        return UNKNOWN_VERSION_NOT_PIP


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
        return UNKNOWN_VERSION_NOT_FETCHED


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

    if local_version == UNKNOWN_VERSION_NOT_PIP:
        return UNKNOWN_VERSION_NOT_PIP

    elif latest_version == UNKNOWN_VERSION_NOT_FETCHED:
        return UNKNOWN_VERSION_NOT_FETCHED

    local_version_clean = local_version.strip()
    latest_version_clean = latest_version.replace("Scribe-Data", "").strip()

    if local_version_clean == latest_version_clean:
        return f"Scribe-Data v{local_version_clean}"

    elif local_version_clean > latest_version_clean:
        return f"Scribe-Data v{local_version_clean} is higher than the currently released version Scribe-Data v{latest_version_clean}. Hopefully this is a development build, and if so, thanks for your work on Scribe-Data! If not, please report this to the team at https://github.com/scribe-org/Scribe-Data/issues."

    else:
        return f"Scribe-Data v{local_version_clean} (Upgrade available: Scribe-Data v{latest_version_clean}). To upgrade: scribe-data -u"
