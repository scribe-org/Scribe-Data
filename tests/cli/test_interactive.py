# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI interactive mode functionality.
"""

import unittest
from pathlib import Path
from unittest.mock import ANY, MagicMock, call, patch

from prompt_toolkit.completion import WordCompleter

from scribe_data.cli.interactive import (
    ScribeDataConfig,
    configure_settings,
    display_summary,
    prompt_for_data_types,
    prompt_for_languages,
    run_request,
)


class TestScribeDataInteractive(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = ScribeDataConfig()
        # Mock the language_metadata and data_type_metadata.
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
        # Set up mock responses.
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
        # Set up mock responses.
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
        # Set up mock responses.
        mock_prompt.side_effect = [
            "english, french",  # first call for languages
            "nouns",  # first call for data types
        ]

        with patch("scribe_data.cli.interactive.config", self.config):
            with patch(
                "scribe_data.cli.interactive.list_all_languages",
                return_value=["english", "french"],
            ):
                prompt_for_languages()
                prompt_for_data_types()

                # Verify the config was updated correctly.
                self.assertEqual(self.config.selected_languages, ["english", "french"])
                self.assertEqual(self.config.selected_data_types, ["nouns"])

                # Verify prompt was called with correct arguments.
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

    def test_create_word_completer(self):
        """Test create_word_completer functionality."""
        from scribe_data.cli.interactive import create_word_completer

        # Test without 'All' option.
        options = ["english", "spanish", "french"]
        completer = create_word_completer(options, include_all=False)
        self.assertIsInstance(completer, WordCompleter)
        self.assertEqual(completer.words, options)

        # Test with 'All' option.
        completer_with_all = create_word_completer(options, include_all=True)
        self.assertEqual(completer_with_all.words, ["All"] + options)

    @patch("questionary.select")
    @patch("scribe_data.cli.interactive.total_wrapper")
    @patch("scribe_data.cli.interactive.parse_wd_lexeme_dump")
    @patch("scribe_data.cli.interactive.prompt")
    def test_request_total_lexeme_loop(
        self, mock_prompt, mock_parse_dump, mock_total_wrapper, mock_select
    ):
        """
        Test request_total_lexeme_loop functionality with both WDQS and lexeme dumps.
        """
        from scribe_data.cli.interactive import config, request_total_lexeme_loop

        # Test running total lexemes request via WDQS.
        mock_select.return_value.ask.side_effect = ["run", "exit"]
        config.selected_languages = ["english"]
        config.selected_data_types = ["nouns"]

        request_total_lexeme_loop()

        mock_total_wrapper.assert_called_once_with(
            language=["english"], data_type=["nouns"], all_bool=False
        )

        # Reset mocks and reconfigure for lexeme dumps test.
        mock_total_wrapper.reset_mock()
        mock_parse_dump.reset_mock()
        mock_select.return_value.ask.side_effect = ["run_all", "exit"]

        # Important: Reset and set the config again for the second test.
        config.selected_languages = ["english"]  # ensure languages are set again
        mock_prompt.return_value = "/custom/dump/path"

        request_total_lexeme_loop()

        mock_parse_dump.assert_called_once_with(
            language=["english"],
            wikidata_dump_type=["total"],
            wikidata_dump_path=Path("/custom/dump/path"),
            interactive_mode=True,
        )

    @patch("questionary.select")
    @patch("scribe_data.cli.interactive.configure_settings")
    @patch("scribe_data.cli.interactive.run_request")
    @patch("scribe_data.cli.interactive.parse_wd_lexeme_dump")
    @patch("scribe_data.cli.interactive.prompt")
    def test_start_interactive_mode(
        self,
        mock_prompt,
        mock_parse_dump,
        mock_run_request,
        mock_configure,
        mock_select,
    ):
        """Test start_interactive_mode functionality."""
        from scribe_data.cli.interactive import config, start_interactive_mode

        # Test get data request flow.
        config.configured = True
        config.selected_languages = ["english"]
        config.selected_data_types = ["nouns"]

        mock_select.return_value.ask.return_value = "run"
        start_interactive_mode(operation="get")
        mock_run_request.assert_called_once()

        # Reset mocks.
        mock_run_request.reset_mock()
        mock_parse_dump.reset_mock()
        mock_prompt.reset_mock()

        # Test get data with dumps flow.
        mock_select.return_value.ask.return_value = "run_all"
        mock_prompt.return_value = "/custom/dump/path"

        start_interactive_mode(operation="get")

        mock_parse_dump.assert_called_with(
            language=["english"],
            wikidata_dump_type=["form"],
            data_types=["nouns"],
            type_output_dir=ANY,
            wikidata_dump_path=Path("/custom/dump/path"),
            overwrite_all=False,
            interactive_mode=True,
        )

    @patch("questionary.select")
    @patch("scribe_data.cli.interactive.convert_wrapper")
    @patch("scribe_data.cli.interactive.prompt")
    @patch("scribe_data.cli.interactive.prompt_for_languages")
    @patch("scribe_data.cli.interactive.prompt_for_data_types")
    def test_start_interactive_mode_convert(
        self,
        mock_prompt_data_types,
        mock_prompt_languages,
        mock_prompt,
        mock_convert,
        mock_select,
    ):
        """Test start_interactive_mode with convert operation."""
        from scribe_data.cli.interactive import config, start_interactive_mode

        # Setup mock responses.
        mock_select.return_value.ask.return_value = "convert"
        mock_prompt.side_effect = [
            "/input/dir",  # input directory
            "/output/dir",  # output directory
            "snake",  # identifier case
            "sqlite",  # output type
            "true",  # overwrite
        ]

        config.selected_languages = ["english"]
        config.selected_data_types = ["nouns"]

        start_interactive_mode(operation="convert")

        mock_convert.assert_called_once_with(
            languages=["english"],
            data_types=["nouns"],
            output_type="sqlite",
            input_files=Path("/input/dir"),
            output_dir=Path("/output/dir"),
            identifier_case="snake",
            overwrite=True,
        )

    @patch("questionary.select")
    @patch("scribe_data.cli.interactive.parse_wd_lexeme_dump")
    @patch("scribe_data.cli.interactive.prompt")
    @patch("scribe_data.cli.interactive.prompt_for_languages")
    def test_start_interactive_mode_translations(
        self, mock_prompt_languages, mock_prompt, mock_parse_dump, mock_select
    ):
        """Test start_interactive_mode with translations operation."""
        from scribe_data.cli.interactive import config, start_interactive_mode

        mock_select.return_value.ask.return_value = "translations"
        mock_prompt.side_effect = ["/dump/path", "/output/dir"]

        config.selected_languages = ["english"]

        start_interactive_mode(operation="translations")

        mock_parse_dump.assert_called_once_with(
            language=["english"],
            wikidata_dump_type=["translations"],
            data_types=None,
            type_output_dir=Path("/output/dir"),
            wikidata_dump_path=Path("/dump/path"),
            overwrite_all=False,
            interactive_mode=True,
        )


if __name__ == "__main__":
    unittest.main()
