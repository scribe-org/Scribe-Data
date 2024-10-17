import requests
import pkg_resources
import sys
import os
from pathlib import Path
import subprocess


def check_if_pyicu_installed():
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    if "pyicu" in installed_packages:
        return True
    return False


def get_python_version_and_architecture():
    """
    Get the current Python version and architecture.

    Returns
    -------
        str : python_version
            The Python version in the format 'cpXY'.
        str : architecture
            The architecture type ('amd64' or 'win32').
    """
    version = sys.version_info
    python_version = f"cp{version.major}{version.minor}"
    architecture = "win_amd64" if sys.maxsize > 2**32 else "win32"
    return python_version, architecture


def fetch_wheel_releases():
    """
    Fetch the release data for PyICU from GitHub.

    Returns
    -------
        list : available_wheels
            A list of tuples containing wheel file names and their download URLs.
    """
    url = "https://api.github.com/repos/cgohlke/pyicu-build/releases"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    available_wheels = []
    for release in response.json():
        for asset in release["assets"]:
            if asset["name"].endswith(".whl"):
                available_wheels.append((asset["name"], asset["browser_download_url"]))

    return available_wheels


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
        str : path to the downloaded wheel file.
    """
    response = requests.get(wheel_url)
    response.raise_for_status()  # Raise an error for bad responses

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
        str : The download URL of the matching wheel or None if not found.
    """
    for name, download_url in wheels:
        if python_version in name and architecture in name:
            return download_url
    return None


def check_and_install_pyicu():
    """
    Check if PyICU is installed, and if not, download and install it dynamically.
    """
    package_name = "PyICU"

    # Check if PyICU is already installed using pkg_resources
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    if package_name.lower() not in installed_packages:
        print(f"{package_name} not found. Installing...")

        # Get Python version and architecture
        python_version, architecture = get_python_version_and_architecture()

        # Fetch available wheels from GitHub
        wheels = fetch_wheel_releases()

        # Find the matching wheel for the current Python version and architecture
        wheel_url = find_matching_wheel(wheels, python_version, architecture)

        if not wheel_url:
            print(
                "No matching wheel file found for your Python version and architecture."
            )
            return False

        # Download the wheel file
        output_dir = Path.cwd()  # Use the current directory for simplicity
        wheel_path = download_wheel_file(wheel_url, output_dir)

        # Install PyICU using pip
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", wheel_path],
                check=True,
            )
            print(f"{package_name} has been installed successfully.")

            # Remove the downloaded wheel file
            os.remove(wheel_path)
            print(f"Removed temporary file: {wheel_path}")

        except subprocess.CalledProcessError as e:
            print(f"Error occurred while installing {package_name}: {e}")
            return False
    else:
        print(f"{package_name} is already installed.")

    return True
