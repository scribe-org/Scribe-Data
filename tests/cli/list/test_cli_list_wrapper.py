# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI list wrapper functionality.
"""

import unittest
from unittest.mock import MagicMock, patch

from scribe_data.cli.list.wrapper import list_all, list_wrapper
from scribe_data.cli.main import main


class TestCLIListWrapper(unittest.TestCase):
    @patch("scribe_data.cli.list.languages.list_languages")
    @patch("scribe_data.cli.list.data_types.list_data_types")
    def test_cli_list_wrapper_list_all(
        self, mock_list_data_types: MagicMock, mock_list_languages: MagicMock
    ) -> None:
        list_all()
        mock_list_languages.assert_called_once()
        mock_list_data_types.assert_called_once()

    @patch("scribe_data.cli.list.list_all")
    def test_cli_list_wrapper_all(self, mock_list_all: MagicMock) -> None:
        list_wrapper(all_bool=True)
        mock_list_all.assert_called_once()

    @patch("scribe_data.cli.list.languages.list_languages")
    def test_cli_list_wrapper_languages(self, mock_list_languages: MagicMock) -> None:
        list_wrapper(language=True)
        mock_list_languages.assert_called_once()

    @patch("scribe_data.cli.list.data_types.list_data_types")
    def test_cli_list_wrapper_data_types(self, mock_list_data_types: MagicMock) -> None:
        list_wrapper(data_type=True)
        mock_list_data_types.assert_called_once()

    @patch("builtins.print")
    def test_cli_list_wrapper_language_and_data_type(
        self, mock_print: MagicMock
    ) -> None:
        list_wrapper(language=True, data_type=True)
        mock_print.assert_called_with(
            "Please specify either a language or a data type."
        )

    @patch("scribe_data.cli.list.languages.list_languages_for_data_type")
    def test_cli_list_wrapper_languages_for_data_type(
        self, mock_list_languages_for_data_type: MagicMock
    ) -> None:
        list_wrapper(language=True, data_type="example_data_type")
        mock_list_languages_for_data_type.assert_called_with("example_data_type")

    @patch("scribe_data.cli.list.data_types.list_data_types")
    def test_cli_list_wrapper_data_types_for_language(
        self, mock_list_data_types: MagicMock
    ) -> None:
        list_wrapper(language="English", data_type=True)
        mock_list_data_types.assert_called_with("English")

    @patch("scribe_data.cli.list.list_all")
    def test_cli_list_wrapper_list_all_command(self, mock_list_all: MagicMock) -> None:
        test_cli_list_wrapper_args = ["main.py", "list", "--all"]
        with patch("sys.argv", test_cli_list_wrapper_args):
            main()

        mock_list_all.assert_called_once()
