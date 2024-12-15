"""
Functions for downloading Wikidata lexeme dumps.

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

import os
from pathlib import Path
from typing import Optional

import requests
from rich import print as rprint
from tqdm import tqdm

from scribe_data.utils import DEFAULT_DUMP_EXPORT_DIR, check_lexeme_dump_prompt_download
from scribe_data.wikidata.wikidata_utils import download_wiki_lexeme_dump


def download_wrapper(
    wikidata_dump: Optional[str] = None, output_dir: Optional[str] = None
) -> None:
    """
    Download Wikidata lexeme dumps given user preferences.

    Parameters
    ----------
        wikidata_dump : str
            Optional date string in YYYYMMDD format for specific dumps.

        output_dir : str
            Optional directory path for the downloaded file. Defaults to 'scribe_data_wikidumps' directory.
    """
    dump_url = download_wiki_lexeme_dump(wikidata_dump or "latest-lexemes")

    if not dump_url:
        rprint("[bold red]No dump URL found.[/bold red]")
        return False

    try:
        output_dir = output_dir or DEFAULT_DUMP_EXPORT_DIR

        os.makedirs(output_dir, exist_ok=True)

        # Don't check for lexeme if date given.
        if not wikidata_dump:
            if useable_file_dir := check_lexeme_dump_prompt_download(output_dir):
                return useable_file_dir

        filename = dump_url.split("/")[-1]
        output_path = str(Path(output_dir) / filename)

        user_response = (
            input(
                "We'll be using the Wikidata lexeme dump from dumps.wikimedia.org/wikidatawiki/entities."
                "Do you want to proceed? (y/n): "
            )
            .strip()
            .lower()
        )

        if user_response == "y":
            rprint(f"[bold blue]Downloading dump to {output_path}...[/bold blue]")

            response = requests.get(dump_url, stream=True)
            total_size = int(response.headers.get("content-length", 0))

            with open(output_path, "wb") as f:
                with tqdm(
                    total=total_size, unit="iB", unit_scale=True, desc=output_path
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            rprint("[bold green]Download completed successfully![/bold green]")

            return output_path

        else:
            return

    except requests.exceptions.RequestException as e:
        rprint(f"[bold red]Error downloading dump: {e}[/bold red]")

    except Exception as e:
        rprint(f"[bold red]An error occurred: {e}[/bold red]")
