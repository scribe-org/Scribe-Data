# SPDX-License-Identifier: GPL-3.0-or-later
"""
Parsing constants and config loading for the Wiktionary extraction module.
"""

import os
import re
from pathlib import Path

import yaml
from rich import print as rprint

# MARK: Parsing Utilities


def get_wiktionary_config(source_iso: str) -> dict:
    """
    Load the Wiktionary config for the given source ISO and compile its regex/set fields.

    Parameters
    ----------
    source_iso : str
        ISO code of the source Wiktionary edition (e.g. ``"en"``, ``"de"``).

    Returns
    -------
    dict
        The config dict with compiled regex patterns and converted sets/tuples.
    """
    iso_yaml_config_file = (
        Path(__file__).parent.parent
        / "resources"
        / "wiktionary_configs"
        / f"{source_iso}_wiktionary_config.yaml"
    )
    if not os.path.exists(iso_yaml_config_file):
        rprint(
            f"[bold red]Scribe-Data currently does not have a Wiktionary config file for '{source_iso}'.[/bold red]"
        )
        print(
            "Please reach out to the team at https://github.com/scribe-org/Scribe-Data for adding it to the next version."
        )

    with iso_yaml_config_file.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if isinstance(config.get("lang_header_pattern"), str):
        config["lang_header_pattern"] = re.compile(
            config["lang_header_pattern"], re.IGNORECASE
        )

    return config
