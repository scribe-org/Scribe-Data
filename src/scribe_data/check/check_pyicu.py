# SPDX-License-Identifier: GPL-3.0-or-later
"""
Check to see if the requirements of the emoji process are installed.

Examples
--------
>>> python3 src/scribe_data/check/check_pyicu.py
"""

import importlib.metadata
import os
import platform
import subprocess
import sys
from pathlib import Path

import questionary
import requests


def check_if_pyicu_installed():
    """
    Check to see if PyICU is installed or not.

    Returns
    -------
    bool
        Whether PyICU is installed.
    """
    try:
        # Check if PyICU is installed using importlib.metadata.
        importlib.metadata.version("PyICU")
        return True

    except importlib.metadata.PackageNotFoundError:
        return False


def get_python_version_and_architecture():
    """
    Get the current Python version and architecture.

    Returns
    -------
        python_version : str
            The Python version in the format 'cpXY'.

        architecture : str
            The architecture type ('amd64' or 'win32').
    """
    version = sys.version_info
    python_version = f"cp{version.major}{version.minor}"
    architecture = "win_amd64" if sys.maxsize > 2**32 else "win32"
    return python_version, architecture


def fetch_wheel_releases():
    """
    Fetch the release data for PyICU from GitHub with error handling for rate limits.

    Returns
    -------
        available_wheels : list
            A list of tuples containing wheel file names and their download URLs.

        total_size_mb : float
            The total size of all available wheels in MB.
    """
    url = "https://api.github.com/repos/cgohlke/pyicu-build/releases"
    response = requests.get(url)
    response.raise_for_status()  # raise an error for bad responses

    available_wheels = []
    total_size_bytes = 0

    for release in response.json():
        for asset in release["assets"]:
            if asset["name"].endswith(".whl"):
                available_wheels.append((asset["name"], asset["browser_download_url"]))
                total_size_bytes += asset["size"]

    total_size_mb = total_size_bytes / (1024 * 1024)  # convert bytes to MB
    return available_wheels, total_size_mb


def download_wheel_file(wheel_url, output_dir):
    """
    Download the wheel file from the given URL.

    Parameters
    ----------
    wheel_url : str
        The URL of the wheel file to download.

    output_dir : str
        The directory to save the downloaded file.

    Returns
    -------
    str
        Path to the downloaded wheel file.
    """
    response = requests.get(wheel_url)
    response.raise_for_status()  # raise an error for bad responses

    wheel_filename = os.path.basename(wheel_url)
    wheel_path = os.path.join(output_dir, wheel_filename)

    with open(wheel_path, "wb") as wheel_file:
        wheel_file.write(response.content)

    return wheel_path


def find_matching_wheel(wheels, python_version, architecture):
    """
    Find the matching wheel file based on Python version and architecture.

    Parameters
    ----------
    wheels : list
        The list of available wheels.

    python_version : str
        The Python version (e.g., 'cp311').

    architecture : str
        The architecture type (e.g., 'win_amd64').

    Returns
    -------
    str
        The download URL of the matching wheel or None if not found.
    """
    return next(
        (
            download_url
            for name, download_url in wheels
            if python_version in name and architecture in name
        ),
        None,
    )


def check_and_install_pyicu():
    """
    Check whether PyICU is installed and install it if it's not already.

    Returns
    -------
    bool
        Whether PyICU is installed.
    """
    package_name = "PyICU"
    try:
        version = importlib.metadata.version(package_name)
        print(f"PyICU version: {version}")
        return True

    except importlib.metadata.PackageNotFoundError:
        # Fetch available wheels from GitHub to estimate download size.
        wheels, total_size_mb = fetch_wheel_releases()

        if questionary.confirm(
            f"{package_name} is not installed.\nScribe-Data can install the package and the needed dependencies."
            f"\nApproximately {total_size_mb:.2f} MB will be downloaded.\nDo you want to proceed?"
        ).ask():
            print("Proceeding with installation...")

        else:
            print("Installation aborted by the user.")
            return False

        # Check the operating system.
        if platform.system() != "Windows":
            # If not Windows, directly use pip to install PyICU.
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package_name], check=True
                )
                print(f"{package_name} has been installed successfully.")

            except subprocess.CalledProcessError as e:
                print(f"Error occurred while installing {package_name}: {e}")
                return False

        else:
            # Windows-specific installation using wheel files.
            python_version, architecture = get_python_version_and_architecture()

            # Find the matching wheel for the current Python version and architecture.
            wheel_url = find_matching_wheel(wheels, python_version, architecture)

            if not wheel_url:
                print(
                    "No matching wheel file found for your Python version and architecture."
                )
                return False

            # Download the wheel file.
            output_dir = Path.cwd()  # use the current directory for simplicity
            wheel_path = download_wheel_file(wheel_url, output_dir)

            # Install PyICU using pip.
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", wheel_path],
                    check=True,
                )
                print(f"{package_name} has been installed successfully.")

                # Remove the downloaded wheel file.
                os.remove(wheel_path)
                print(f"Removed temporary file: {wheel_path}")

            except subprocess.CalledProcessError as e:
                print(f"Error occurred while installing {package_name}: {e}")
                return False

    return True


if __name__ == "__main__":
    check_and_install_pyicu()
