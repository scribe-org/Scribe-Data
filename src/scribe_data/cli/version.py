"""
Functions for checking current version of the Scribe-Data CLI.

# SPDX-License-Identifier: AGPL-3.0-or-later
"""

import pkg_resources
import requests


def get_local_version():
    try:
        return pkg_resources.get_distribution("scribe-data").version

    except pkg_resources.DistributionNotFound:
        return "Unknown (Not installed via pip)"


def get_latest_version():
    try:
        response = requests.get(
            "https://api.github.com/repos/scribe-org/Scribe-Data/releases/latest"
        )
        return response.json()["name"]

    except Exception:
        return "Unknown (Unable to fetch version)"


def get_version_message():
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
