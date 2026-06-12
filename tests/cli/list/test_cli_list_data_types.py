# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI list data types functionality.
"""

import unittest
from unittest.mock import MagicMock, call, patch

from scribe_data.cli.list.data_types import list_data_types
from scribe_data.cli.main import main


class TestCLIListDataTypes(unittest.TestCase):
    @patch("builtins.print")
    def test_cli_list_data_types_all_languages(self, mock_print: MagicMock) -> None:
        list_data_types()
        print(mock_print.mock_calls)
        expected_calls = [
            call(),
            call("Available data types: All languages"),
            call("==================================="),
            call("adjectives"),
            call("adverbs"),
            # call("articles"),
            call("conjunctions"),
            call("emoji-keywords"),
            call("nouns"),
            call("personal-pronouns"),
            call("postpositions"),
            call("prepositions"),
            call("pronouns"),
            call("proper-nouns"),
            call("verbs"),
            call(),
        ]
        mock_print.assert_has_calls(expected_calls)

    @patch("scribe_data.cli.list.data_types.os.listdir")
    @patch("builtins.print")
    def test_cli_list_data_types_specific_language(
        self, mock_print: MagicMock, mock_listdir: MagicMock
    ) -> None:
        mock_listdir.return_value = ["en"]

        list_data_types("english")

        expected_calls = [
            call(),
            call("Available data types: English"),
            call("============================="),
            call("adjectives"),
            call("adverbs"),
            call("emoji-keywords"),
            call("nouns"),
            call("personal-pronouns"),
            call("prepositions"),
            call("pronouns"),
            call("proper-nouns"),
            call("verbs"),
            call(),
        ]
        mock_print.assert_has_calls(expected_calls)

    def test_cli_list_data_types_invalid_language(self) -> None:
        with self.assertRaises(ValueError):
            list_data_types("InvalidLanguage")

    def test_cli_list_data_types_no_data_types(self) -> None:
        with self.assertRaises(ValueError):
            list_data_types("Klingon")

    @patch("scribe_data.cli.list.wrapper.list_data_types")
    def test_cli_list_data_types_command(self, mock_list_data_types: MagicMock) -> None:
        test_args = ["main.py", "list", "--data-type"]
        with patch("sys.argv", test_args):
            main()

        mock_list_data_types.assert_called_once()
