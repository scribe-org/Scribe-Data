"""
Interactive for the list file functions.

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

import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
from scribe_data.cli.interactive import (
    ScribeDataConfig,
    configure_settings,
    display_summary,
    run_request,
    request_total_lexeme,
)


class TestScribeDataInteractive(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = ScribeDataConfig()
        # Mock the language_metadata and data_type_metadata
        self.config.languages = ["english", "spanish", "french"]
        self.config.data_types = ["nouns", "verbs"]

    def test_scribe_data_config_initialization(self):
        """Test ScribeDataConfig initialization."""
        self.assertEqual(self.config.selected_languages, [])
        self.assertEqual(self.config.selected_data_types, [])
        self.assertEqual(self.config.output_type, "json")
        self.assertIsInstance(self.config.output_dir, Path)
        self.assertFalse(self.config.overwrite)
        self.assertFalse(self.config.configured)

    @patch("scribe_data.cli.interactive.prompt")
    @patch("scribe_data.cli.interactive.rprint")
    def test_configure_settings_all_languages(self, mock_rprint, mock_prompt):
        """Test configure_settings with 'All' languages selection."""
        # Set up mock responses
        responses = iter(
            [
                "All",  # languages
                "nouns",  # data types
                "json",  # output type
                "",  # output directory (default)
                "y",  # overwrite
            ]
        )
        mock_prompt.side_effect = lambda *args, **kwargs: next(responses)

        with patch("scribe_data.cli.interactive.config", self.config):
            with patch("scribe_data.cli.interactive.display_summary"):
                configure_settings()

                self.assertEqual(self.config.selected_languages, self.config.languages)
                self.assertEqual(self.config.selected_data_types, ["nouns"])
                self.assertEqual(self.config.output_type, "json")
                self.assertTrue(self.config.configured)

    @patch("scribe_data.cli.interactive.prompt")
    @patch("scribe_data.cli.interactive.rprint")
    def test_configure_settings_specific_languages(self, mock_rprint, mock_prompt):
        """Test configure_settings with specific language selection."""
        # Set up mock responses
        responses = iter(
            [
                "english, spanish",  # languages
                "nouns, verbs",  # data types
                "csv",  # output type
                "/custom/path",  # output directory
                "n",  # overwrite
            ]
        )
        mock_prompt.side_effect = lambda *args, **kwargs: next(responses)

        with patch("scribe_data.cli.interactive.config", self.config):
            with patch("scribe_data.cli.interactive.display_summary"):
                configure_settings()

                self.assertEqual(self.config.selected_languages, ["english", "spanish"])
                self.assertEqual(self.config.selected_data_types, ["nouns", "verbs"])
                self.assertEqual(self.config.output_type, "csv")
                self.assertEqual(self.config.output_dir.as_posix(), "/custom/path")
                self.assertFalse(self.config.overwrite)

    @patch("scribe_data.cli.interactive.get_data")
    @patch("scribe_data.cli.interactive.tqdm")
    @patch("scribe_data.cli.interactive.logger")
    def test_run_request(self, mock_logger, mock_tqdm, mock_get_data):
        """Test run_request functionality."""
        # Setup
        self.config.selected_languages = ["english"]
        self.config.selected_data_types = ["nouns"]
        self.config.configured = True

        mock_get_data.return_value = True
        mock_progress = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        with patch("scribe_data.cli.interactive.config", self.config):
            run_request()

            mock_get_data.assert_called_once_with(
                language="english",
                data_type="nouns",
                output_type=self.config.output_type,
                output_dir=str(self.config.output_dir),
                overwrite=self.config.overwrite,
                interactive=True,
            )

    @patch("scribe_data.cli.interactive.prompt")
    @patch("scribe_data.cli.interactive.rprint")
    def test_request_total_lexeme(self, mock_rprint, mock_prompt):
        """Test request_total_lexeme functionality."""
        # Set up mock responses
        mock_prompt.side_effect = [
            "english, french",  # First call for languages
            "nouns",  # First call for data types
        ]

        with patch("scribe_data.cli.interactive.config", self.config):
            with patch(
                "scribe_data.cli.interactive.list_all_languages",
                return_value=["english", "french"],
            ):
                request_total_lexeme()

                # Verify the config was updated correctly
                self.assertEqual(self.config.selected_languages, ["english", "french"])
                self.assertEqual(self.config.selected_data_types, ["nouns"])

                # Verify prompt was called with correct arguments
                expected_calls = [
                    call(
                        "Select languages (comma-separated or 'All'): ",
                        completer=unittest.mock.ANY,
                        default="",
                    ),
                    call(
                        "Select data types (comma-separated or 'All'): ",
                        completer=unittest.mock.ANY,
                        default="",
                    ),
                ]
                mock_prompt.assert_has_calls(expected_calls, any_order=False)

    @patch("rich.console.Console.print")
    def test_display_summary(self, mock_print):
        """Test display_summary functionality."""
        self.config.selected_languages = ["english"]
        self.config.selected_data_types = ["nouns"]
        self.config.output_type = "json"

        with patch("scribe_data.cli.interactive.config", self.config):
            display_summary()
            mock_print.assert_called()


if __name__ == "__main__":
    unittest.main()
