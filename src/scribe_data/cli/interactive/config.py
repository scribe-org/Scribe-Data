# SPDX-License-Identifier: GPL-3.0-or-later
"""
Interactive mode configuration for the Scribe-Data CLI to allow users to select request arguments.
"""

from pathlib import Path

# from scribe_data.cli.list import list_wrapper
from scribe_data.utils import (
    DEFAULT_JSON_EXPORT_DIR,
    DEFAULT_SQLITE_EXPORT_DIR,
    data_type_metadata,
    language_metadata,
    list_all_languages,
)

THANK_YOU_MESSAGE = "[bold cyan]Thank you for using Scribe-Data![/bold cyan]"


class ScribeDataConfig:
    """
    Class for the configuration of the interactive mode.
    """

    def __init__(self) -> None:
        """
        Configure the interactive mode.
        """
        self.languages = list_all_languages(language_metadata)
        self.data_types = list(data_type_metadata.keys())
        self.selected_languages: list[str] = []
        self.selected_data_types: list[str] = []
        self.output_type: str = "json"
        self.output_dir: Path = DEFAULT_JSON_EXPORT_DIR
        self.overwrite: bool = False
        self.configured: bool = False
        self.identifier_case: str = "camel"
        self.input_dir: Path = DEFAULT_JSON_EXPORT_DIR
        self.output_dir_sqlite: Path = DEFAULT_SQLITE_EXPORT_DIR


interactive_mode_config = ScribeDataConfig()
