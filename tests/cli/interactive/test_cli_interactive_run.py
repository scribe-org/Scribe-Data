# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI interactive mode runner functionality.
"""

import unittest
from pathlib import Path
from unittest.mock import patch

from scribe_data.cli.interactive.config import ScribeDataConfig
from scribe_data.cli.interactive.run import run_interactive_mode


class TestScribeDataCLIInteractiveRun(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        """
        self.config = ScribeDataConfig()
        # Mock the language_metadata and data_type_metadata.
        self.config.languages = ["english", "spanish", "french"]
        self.config.data_types = ["nouns", "verbs"]

    @patch(
        "scribe_data.cli.interactive.prompt.resolve_wiktionary_dump_path",
        return_value=Path("/dump/path"),
    )
    @patch("scribe_data.wiktionary.parse_translations.parse_wiktionary_translations")
    @patch("prompt_toolkit.prompt")
    @patch("scribe_data.cli.interactive.execute.prompt_for_languages")
    @patch("questionary.select")
    def test_cli_interactive_run_translations(
        self,
        mock_select,
        mock_prompt_languages,
        mock_prompt,
        mock_parse_wiktionary,
        mock_resolve_dump,
    ):
        mock_select.return_value.ask.side_effect = ["translations"]
        mock_prompt.side_effect = [
            "german",
            "/dump/path",
            "scribe_data_wiktionary_json_export",
            "false",
        ]
        self.config.selected_languages = ["english"]

        run_interactive_mode(operation="translations")

        mock_parse_wiktionary.assert_called_once_with(
            target_languages=["english"],
            wiktionary_dump_path=Path("/dump/path"),
            output_dir=Path("scribe_data_wiktionary_json_export"),
            overwrite=False,
        )
