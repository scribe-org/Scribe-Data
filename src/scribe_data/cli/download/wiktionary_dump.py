# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for downloading Wiktionary dumps.
"""

from pathlib import Path

import questionary
import requests
from rich import print as rprint
from tqdm import tqdm

from scribe_data.utils import (
    DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR,
    resolve_lang_iso,
)


def download_wiktionary_dumps(
    output_dir: Path = DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR,
    language_isos: list[str] = ["en"],
    dump_snapshot: str | None = "latest",
) -> Path | None:
    """
    Download the latest Wiktionary pages-articles dump based on passed language isos.

    Parameters
    ----------
    output_dir : Path, optional, default=DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR
        Directory to save the dump. Defaults to DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR.

    language_isos : List[str], optional, default=['en']
        A list of ISO-2 codes for desired Wiktionary dumps.

    dump_snapshot : str, optional, default='latest'
        The Wiktionary dump snapshot to be downloaded.

    Returns
    -------
    Path
        Path to the downloaded file, or None if aborted/failed.
    """
    if isinstance(language_isos, str):
        language_isos = [language_isos]

    resolved_isos = []
    not_included_isos = []
    for lang in language_isos:
        iso = resolve_lang_iso(lang)
        if iso:
            resolved_isos.append(iso)

        else:
            not_included_isos.append(lang)

    if not_included_isos:
        iso_or_isos = "iso" if len(not_included_isos) == 1 else "isos"
        is_or_are = "is" if len(not_included_isos) == 1 else "are"
        rprint(
            f"[bold red]The following {iso_or_isos} {is_or_are} not included: {', '.join(not_included_isos)}[/bold red]"
        )
        return None

    language_isos = resolved_isos
    wiktionaries = [f"{iso}wiktionary" for iso in language_isos]
    wiktionary_urls = [f"https://dumps.wikimedia.org/{w}" for w in wiktionaries]

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for i, w, u in zip(language_isos, wiktionaries, wiktionary_urls):
        # Note: Remove the snapshot from the resulting filename so Scribe-Server always looks for one file.
        filename = f"{w}-pages-articles.xml.bz2"
        download_filename = f"{w}-{dump_snapshot}-pages-articles.xml.bz2"
        download_url = f"{u}/{dump_snapshot}/{download_filename}"

        rprint(f"[bold blue]Checking dump validity at {download_url}...[/bold blue]")
        try:
            response = requests.head(download_url, timeout=30)
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            rprint(f"[bold red]Invalid dump date or dump not found: {e}[/bold red]")
            return None

        output_path = output_dir / filename

        if output_path.exists():
            rprint(f"[bold yellow]Dump already exists: {output_path}[/bold yellow]")
            user_input = questionary.select(
                "Do you want to:",
                choices=[
                    "Skip download",
                    "Download and overwrite",
                ],
            ).ask()
            if user_input == "Skip download":
                rprint("[bold green]Skipping download.[/bold green]")
                return output_path

        rprint(f"[bold blue]Downloading to {output_path}...[/bold blue]")
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))

            with open(output_path, "wb") as f:
                with tqdm(
                    total=total_size,
                    unit="iB",
                    unit_scale=True,
                    desc=download_filename,
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            rprint(
                f"[bold green]{i.upper()}Wiktionary dump download completed successfully![/bold green]"
            )
            return output_path

        except requests.exceptions.RequestException as e:
            rprint(f"[bold red]Download failed: {e}[/bold red]")
            return None

    iso_or_isos = "iso" if len(not_included_isos) == 1 else "isos"
    iso_or_isos = "iso" if len(language_isos) == 1 else "isos"
    was_or_were = "was" if len(language_isos) == 1 else "were"
    rprint(
        f"[bold green]The following {iso_or_isos} {was_or_were} successfully downloaded: {', '.join(language_isos)}[/bold green]"
    )
