# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to update the Scribe-Data CLI based on install method.
"""

import subprocess
import sys

from scribe_data.cli.version import (
    UNKNOWN_VERSION_NOT_FETCHED,
    get_latest_version,
    get_local_version,
)


def upgrade_cli() -> None:
    """
    Upgrade the CLI tool to the latest available version on PyPI.

    Raises
    ------
    subprocess.CalledProcessError
        If the installation of the latest version fails.
    """
    local_version = get_local_version()
    latest_version_message = get_latest_version()

    if latest_version_message == UNKNOWN_VERSION_NOT_FETCHED:
        print(
            "Unable to fetch the latest version from GitHub. Please check the GitHub repository or your internet connection."
        )
        return

    latest_version = latest_version_message.split("v")[-1]
    local_version_clean = local_version.strip()
    latest_version_clean = latest_version.replace("Scribe-Data", "").strip()

    if local_version_clean == latest_version_clean:
        print("You already have the latest version of Scribe-Data.")

    elif local_version_clean > latest_version_clean:
        print(
            f"Scribe-Data v{local_version_clean} is higher than the currently released version Scribe-Data v{latest_version_clean}. Hopefully this is a development build, and if so, thanks for your work on Scribe-Data! If not, please report this to the team at https://github.com/scribe-org/Scribe-Data/issues."
        )

    else:
        print(f"Current version: {local_version}")
        print(f"Latest version: {latest_version}")
        print("Updating Scribe-Data with pip...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", "scribe-data"]
            )

        except subprocess.CalledProcessError as e:
            print(
                f"Failed to install the latest version of Scribe-Data with error {e}. Please check the error message and report any issues to the team at https://github.com/scribe-org/Scribe-Data/issues."
            )


if __name__ == "__main__":
    upgrade_cli()
