# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI interactive mode prompt functionality.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from prompt_toolkit.completion import WordCompleter

from scribe_data.cli.interactive.config import ScribeDataConfig
from scribe_data.cli.interactive.prompt import (
    create_word_completer,
    prompt_for_data_types,
    prompt_for_languages,
    resolve_wiktionary_dump_path,
)


class TestScribeDataCLIInteractivePrompt(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        """
        self.config = ScribeDataConfig()
        # Mock the language_metadata and data_type_metadata.
        self.config.languages = ["english", "spanish", "french"]
        self.config.data_types = ["nouns", "verbs"]

    @patch("scribe_data.cli.interactive.prompt")
    @patch("scribe_data.cli.interactive.rprint")
    def test_cli_interactive_request_total_lexeme(
        self, mock_rprint: MagicMock, mock_prompt: MagicMock
    ) -> None:
        """
        Test request_total_lexeme functionality.
        """
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

    def test_resolve_wiktionary_dump_path_from_subdirectory(self) -> None:
        """
        Find dumps when cwd is not the project root.
        """
        with patch("os.getcwd") as mock_getcwd:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                dump_dir = root / "scribe_data_wiktionary_dumps_export"
                json_dir = root / "scribe_data_json_export"
                dump_dir.mkdir()
                json_dir.mkdir()
                dump_file = dump_dir / "dewiktionary-pages-articles.xml.bz2"
                dump_file.write_bytes(b"x")

                mock_getcwd.return_value = str(json_dir)
                resolved = resolve_wiktionary_dump_path(
                    "german",
                    "scribe_data_wiktionary_dumps_export",
                )

                self.assertEqual(resolved, dump_file.resolve())

    def test_cli_interactive_create_word_completer(self) -> None:
        """
        Test create_word_completer functionality.
        """
        # Test without 'All' option.
        options = ["english", "spanish", "french"]
        completer = create_word_completer(options, include_all=False)
        self.assertIsInstance(completer, WordCompleter)
        self.assertEqual(completer.words, options)

        # Test with 'All' option.
        completer_with_all = create_word_completer(options, include_all=True)
        self.assertEqual(completer_with_all.words, ["All"] + options)
