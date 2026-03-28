# SPDX-License-Identifier: GPL-3.0-or-later
"""
Parsing constants and config loading for the Wiktionary extraction module.
"""

import os

import yaml
from rich import print as rprint

try:
    from importlib import resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources


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
    import scribe_data.resources

    if not os.path.exists(
        os.path.join(
            scribe_data.resources,
            "wiktionary_configs",
            f"{source_iso}_wiktionary_config.yaml",
        )
    ):
        rprint(
            f"[bold red]Scribe-Data currently does not have a Wiktionary config file for '{source_iso}'.[/bold red]"
        )
        print(
            "Please reach out to the team at https://github.com/scribe-org/Scribe-Data for adding it to the next version."
        )

    with pkg_resources.path(
        scribe_data.resources, f"wiktionary_configs/{source_iso}_wiktionary_config.yaml"
    ) as yaml_path:
        with open(yaml_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

    return config
