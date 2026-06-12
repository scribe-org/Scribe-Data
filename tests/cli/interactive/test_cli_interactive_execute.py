# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI interactive mode execution functionality.
"""

import unittest
from unittest.mock import MagicMock, patch

from scribe_data.cli.interactive.config import ScribeDataConfig
from scribe_data.cli.interactive.execute import (
    display_summary,
    execute_request,
)


class TestScribeDataCLIInteractiveExecute(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        """
        self.config = ScribeDataConfig()
        # Mock the language_metadata and data_type_metadata.
        self.config.languages = ["english", "spanish", "french"]
        self.config.data_types = ["nouns", "verbs"]

    @patch("scribe_data.cli.interactive.get_data")
    @patch("scribe_data.cli.interactive.tqdm")
    @patch("scribe_data.cli.interactive.logger")
    def test_cli_interactive_execute_request(
        self, mock_logger: MagicMock, mock_tqdm: MagicMock, mock_get_data: MagicMock
    ) -> None:
        """
        Test execute_request functionality.
        """
        self.config.selected_languages = ["english"]
        self.config.selected_data_types = ["nouns"]
        self.config.configured = True

        mock_get_data.return_value = True
        mock_progress = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        with patch("scribe_data.cli.interactive.config", self.config):
            execute_request()

            mock_get_data.assert_called_once_with(
                languages=["english"],
                data_types=["nouns"],
                output_type=self.config.output_type,
                output_dir=self.config.output_dir,
                overwrite=self.config.overwrite,
                interactive=True,
            )

    @patch("rich.console.Console.print")
    def test_cli_interactive_display_summary(self, mock_print: MagicMock) -> None:
        """
        Test display_summary functionality.
        """
        self.config.selected_languages = ["english"]
        self.config.selected_data_types = ["nouns"]
        self.config.output_type = "json"

        with patch("scribe_data.cli.interactive.config", self.config):
            display_summary()
            mock_print.assert_called()
