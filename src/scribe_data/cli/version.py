"""
Functions for checking current version of the Scribe-Data CLI.

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
    local_version = f"Scribe-Data v{get_local_version()}"
    latest_version = get_latest_version()

    if (
        local_version == "Unknown (Not installed via pip)"
        or latest_version == "Unknown (Unable to fetch version)"
    ):
        return f"{local_version}"

    if local_version == latest_version:
        return f"{local_version}"

    update_message = f"{local_version} (Upgrade available: {latest_version})\n"
    update_message += "To update: pip scribe-data --upgrade"

    return update_message
