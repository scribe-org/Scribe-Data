# SPDX-License-Identifier: GPL-3.0-or-later
"""
Download Wikidata lexeme dump.
"""

import os
from pathlib import Path

import requests

from scribe_data.cli.download import download_wd_lexeme_dump
from scribe_data.utils import DEFAULT_DUMP_EXPORT_DIR


def wd_lexeme_dump_download(wikidata_dump=None, output_dir=None):
    """
    Download Wikidata lexeme dumps automatically.

    Parameters
    ----------
    wikidata_dump : str, optional
        Date string in YYYYMMDD format for specific dumps.
        If None, downloads the latest dump.

    output_dir : str, optional
        Directory path for the downloaded file.
        If None, uses DEFAULT_DUMP_EXPORT_DIR.

    Returns
    -------
    str or False
        Path to downloaded file if successful, False otherwise.

    Notes
    -----
    - Downloads are skipped if the file already exists in the output directory.
    - Progress is displayed every 50MB during download.
    - Creates output directory if it doesn't exist.
    """
    dump_url = download_wd_lexeme_dump(wikidata_dump or "latest-lexemes")

    if not dump_url:
        print("No dump URL found.")
        return False

    output_dir = output_dir or DEFAULT_DUMP_EXPORT_DIR
    os.makedirs(output_dir, exist_ok=True)

    filename = dump_url.split("/")[-1]
    output_path = str(Path(output_dir) / filename)

    # Check if the file already exists.
    if os.path.exists(output_path):
        print(f"File already exists: {output_path}. Skipping download.")
        return output_path

    # Proceed with the download if the file does not exist.
    print(f"Downloading dump to {output_path}...")

    try:
        response = requests.get(dump_url, stream=True)
        total_size = int(response.headers.get("content-length", 0))
        downloaded_size = 0

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    # Print progress percentage every 50MB.
                    if total_size and downloaded_size % (50 * 1024 * 1024) < 8192:
                        progress = (downloaded_size / total_size) * 100
                        print(f"Download progress: {progress:.1f}%")

        print("Download completed successfully!")
        return output_path

    except requests.exceptions.RequestException as e:
        print(f"Error downloading dump: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if output_path := wd_lexeme_dump_download():
        print(f"DOWNLOAD_PATH={output_path}")
