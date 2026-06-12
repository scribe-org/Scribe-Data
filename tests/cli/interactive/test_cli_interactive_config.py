# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI interactive mode configuration functionality.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scribe_data.cli.interactive.config import ScribeDataConfig
from scribe_data.cli.interactive.run import configure_settings


class TestScribeDataCLIInteractiveConfig(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        """
        self.config = ScribeDataConfig()
        # Mock the language_metadata and data_type_metadata.
        self.config.languages = ["english", "spanish", "french"]
        self.config.data_types = ["nouns", "verbs"]

    def test_cli_interactive_config_initialization(self) -> None:
        """
        Test ScribeDataConfig initialization.
        """
        self.assertEqual(self.config.selected_languages, [])
        self.assertEqual(self.config.selected_data_types, [])
        self.assertEqual(self.config.output_type, "json")
        self.assertIsInstance(self.config.output_dir, Path)
        self.assertFalse(self.config.overwrite)
        self.assertFalse(self.config.configured)

    @patch("scribe_data.cli.interactive.run.prompt_for_data_types")
    @patch("scribe_data.cli.interactive.run.prompt_for_languages")
    @patch("scribe_data.cli.interactive.run.prompt")
    @patch("scribe_data.cli.interactive.run.rprint")
    def test_cli_interactive_configure_settings_all_languages(
        self,
        mock_rprint: MagicMock,
        mock_prompt: MagicMock,
        mock_prompt_languages: MagicMock,
        mock_prompt_data_types: MagicMock,
    ) -> None:
        """
        Test configure_settings with 'All' languages selection.
        """

        # Simulate the internal changes made by the prompt_for_* functions.
        def mock_lang():
            self.config.selected_languages = self.config.languages

        def mock_data():
            self.config.selected_data_types = ["nouns"]

        mock_prompt_languages.side_effect = mock_lang
        mock_prompt_data_types.side_effect = mock_data

        responses = iter(
            [
                "json",  # output type
                "",  # output directory (default)
                "y",  # overwrite
            ]
        )
        mock_prompt.side_effect = lambda *args, **kwargs: next(responses)

        with patch(
            "scribe_data.cli.interactive.run.interactive_mode_config", self.config
        ):
            with patch("scribe_data.cli.interactive.run.display_summary"):
                configure_settings()

                self.assertEqual(self.config.selected_languages, self.config.languages)
                self.assertEqual(self.config.selected_data_types, ["nouns"])
                self.assertEqual(self.config.output_type, "json")
                self.assertTrue(self.config.configured)

    @patch("scribe_data.cli.interactive.run.prompt_for_data_types")
    @patch("scribe_data.cli.interactive.run.prompt_for_languages")
    @patch("scribe_data.cli.interactive.run.prompt")
    @patch("scribe_data.cli.interactive.run.rprint")
    def test_cli_interactive_configure_settings_specific_languages(
        self,
        mock_rprint: MagicMock,
        mock_prompt: MagicMock,
        mock_prompt_languages: MagicMock,
        mock_prompt_data_types: MagicMock,
    ) -> None:
        """
        Test configure_settings with specific language selection.
        """

        # Simulate the internal changes made by the prompt_for_* functions.
        def mock_lang():
            self.config.selected_languages = ["english", "spanish"]

        def mock_data():
            self.config.selected_data_types = ["nouns", "verbs"]

        mock_prompt_languages.side_effect = mock_lang
        mock_prompt_data_types.side_effect = mock_data

        responses = iter(
            [
                "csv",  # output type
                "/custom/path",  # output directory
                "n",  # overwrite
            ]
        )
        mock_prompt.side_effect = lambda *args, **kwargs: next(responses)

        with patch(
            "scribe_data.cli.interactive.run.interactive_mode_config", self.config
        ):
            with patch("scribe_data.cli.interactive.run.display_summary"):
                configure_settings()

                self.assertEqual(self.config.selected_languages, ["english", "spanish"])
                self.assertEqual(self.config.selected_data_types, ["nouns", "verbs"])
                self.assertEqual(self.config.output_type, "csv")
                self.assertEqual(self.config.output_dir.as_posix(), "/custom/path")
                self.assertFalse(self.config.overwrite)
