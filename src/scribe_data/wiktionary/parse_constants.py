# SPDX-License-Identifier: GPL-3.0-or-later
"""
Parsing constants and config loading for the Wiktionary extraction module.
"""

import re

import yaml

try:
    from importlib import resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources


# MARK: Parsing Utilities


def get_wiktionary_config(source_iso: str, source_lang_name: str) -> dict:
    """
    Load the Wiktionary config for the given source ISO and compile its regex/set fields.

    Parameters
    ----------
    source_iso : str
        ISO code of the source Wiktionary edition (e.g. ``"en"``, ``"de"``).

    source_lang_name : str
        English name of the source language (e.g. ``"German"``).

    Returns
    -------
    dict
        The config dict with compiled regex patterns and converted sets/tuples.
    """
    import scribe_data.resources

    with pkg_resources.path(
        scribe_data.resources, "wiktionary_configs.yaml"
    ) as yaml_path:
        with open(yaml_path, "r", encoding="utf-8") as f:
            all_configs = yaml.safe_load(f)

    if source_iso in all_configs:
        config = all_configs[source_iso]
    else:
        config = all_configs.get("en", {})

    # Default the header to the source language's English name (e.g. "German")
    # if neither a plain header nor a pattern is set in the YAML.
    if "lang_header" not in config and not config.get("lang_header_pattern"):
        config["lang_header"] = source_lang_name

    # Compile the regex and convert lists to sets/tuples once here so parsers
    # don't have to repeat this work on every page.
    if config.get("lang_header_pattern"):
        config["lang_header_pattern"] = re.compile(
            config["lang_header_pattern"], re.IGNORECASE
        )

    config["ignored_strings"] = set(config.get("ignored_strings", []))
    config["ignored_prefixes"] = tuple(config.get("ignored_prefixes", []))

    return config
