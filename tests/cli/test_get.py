"""
Tests for the CLI get functionality.

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
from pathlib import Path
from unittest.mock import patch

from scribe_data.cli.get import get_data


class TestGetData(unittest.TestCase):
    """
    Unit tests for the get_data function.

    These tests ensure the correct behavior of the get_data function.
    """

    # MARK: Subprocess Patching

    @patch("scribe_data.cli.get.generate_emoji")
    def test_get_emoji_keywords(self, generate_emoji):
        """
        Test the generation of emoji keywords.

        This test ensures that when thee `data_type` is `emoji_keywords`, the `generate_emoji` function is called with the correct arguments.
        """
        get_data(
            language="English", data_type="emoji_keywords", output_dir="./test_output"
        )
        generate_emoji.assert_called_once_with(
            language="English",
            output_dir="./test_output",
        )

    # MARK: Invalid Arguments

    def test_invalid_arguments(self):
        """
        Test the behavior of the get_data function when invalid arguments are provided.
        """
        with self.assertRaises(ValueError):
            get_data()

    # MARK: All Data

    @patch("scribe_data.cli.get.query_data")
    @patch("builtins.input", lambda _: "N")  # don't use dump
    def test_get_all_data_types_for_language(self, mock_query_data):
        """
        Test retrieving all data types for a specific language.

        Ensures that `query_data` is called properly when `--all` flag is used with a language.
        """
        get_data(all_bool=True, language="English")
        mock_query_data.assert_called_once_with(
            languages=["English"],
            data_type=None,
            output_dir="scribe_data_json_export",
            overwrite=False,
        )

    @patch("scribe_data.cli.get.query_data")
    @patch("builtins.input", lambda _: "N")  # don't use dump
    def test_get_all_languages_for_data_type(self, mock_query_data):
        """
        Test retrieving all languages for a specific data type.

        Ensures that `query_data` is called properly when `--all` flag is used with a data type.
        """
        get_data(all_bool=True, data_type="nouns")
        mock_query_data.assert_called_once_with(
            languages=None,
            data_type=["nouns"],
            output_dir="scribe_data_json_export",
            overwrite=False,
        )

    # MARK: Language and Data Type

    @patch("scribe_data.cli.get.query_data")
    def test_get_specific_language_and_data_type(self, mock_query_data):
        """
        Test retrieving a specific language and data type.

        Ensures that `query_data` is called properly when a specific language and data type are provided.
        """
        get_data(language="german", data_type="nouns", output_dir="./test_output")
        mock_query_data.assert_called_once_with(
            languages=["german"],
            data_type=["nouns"],
            output_dir="./test_output",
            overwrite=False,
            interactive=False,
        )

    # MARK: Capitalized Language

    @patch("scribe_data.cli.get.query_data")
    def test_get_data_with_capitalized_language(self, mock_query_data):
        """
        Test retrieving data with a capitalized language.

        Ensures that `query_data` is called properly when a capitalized language is provided.
        """
        get_data(language="German", data_type="nouns")
        mock_query_data.assert_called_once_with(
            languages=["German"],
            data_type=["nouns"],
            output_dir="scribe_data_json_export",
            overwrite=False,
            interactive=False,
        )

    # MARK: Lowercase Language

    @patch("scribe_data.cli.get.query_data")
    def test_get_data_with_lowercase_language(self, mock_query_data):
        """
        Test retrieving data with a lowercase language.

        Ensures that `query_data` is called properly when a lowercase language is provided.
        """
        get_data(language="german", data_type="nouns")
        mock_query_data.assert_called_once_with(
            languages=["german"],
            data_type=["nouns"],
            output_dir="scribe_data_json_export",
            overwrite=False,
            interactive=False,
        )

    # MARK: Output Directory

    @patch("scribe_data.cli.get.query_data")
    def test_get_data_with_different_output_directory(self, mock_query_data):
        """
        Test retrieving data with a different output directory.

        Ensures that `query_data` is called properly when a different output directory is provided.
        """
        get_data(
            language="german", data_type="nouns", output_dir="./custom_output_test"
        )
        mock_query_data.assert_called_once_with(
            languages=["german"],
            data_type=["nouns"],
            output_dir="./custom_output_test",
            overwrite=False,
            interactive=False,
        )

    # MARK: Overwrite is True

    @patch("scribe_data.cli.get.query_data")
    def test_get_data_with_overwrite_true(self, mock_query_data):
        """
        Test retrieving data with the overwrite flag set to True.

        Ensures that `query_data` is called properly when the overwrite flag is set to True.
        """
        get_data(language="English", data_type="verbs", overwrite=True)
        mock_query_data.assert_called_once_with(
            languages=["English"],
            data_type=["verbs"],
            output_dir="scribe_data_json_export",
            overwrite=True,
            interactive=False,
        )

    # MARK: Overwrite is False

    @patch("scribe_data.cli.get.query_data")
    def test_get_data_with_overwrite_false(self, mock_query_data):
        get_data(
            language="English",
            data_type="verbs",
            overwrite=False,
            output_dir="./custom_output_test",
            interactive=False,
        )
        mock_query_data.assert_called_once_with(
            languages=["English"],
            data_type=["verbs"],
            output_dir="./custom_output_test",
            overwrite=False,
            interactive=False,
        )

    # MARK : User Chooses to skip

    @patch("scribe_data.cli.get.query_data")
    @patch("scribe_data.cli.get.Path.glob")
    @patch("builtins.input", return_value="s")
    def test_user_skips_existing_file(self, mock_input, mock_glob, mock_query_data):
        """
        Test the behavior when the user chooses to skip an existing file.

        Ensures that the file is not overwritten and the function returns the correct result.
        """
        mock_glob.return_value = [Path("./test_output/English/nouns.json")]
        result = get_data(
            language="English", data_type="nouns", output_dir="./test_output"
        )
        self.assertEqual(result, {"success": False, "skipped": True})
        mock_query_data.assert_not_called()

    # MARK : User Chooses to overwrite

    @patch("scribe_data.cli.get.query_data")
    @patch("scribe_data.cli.get.Path.glob")
    @patch("builtins.input", return_value="o")
    @patch("scribe_data.cli.get.Path.unlink")
    def test_user_overwrites_existing_file(
        self, mock_unlink, mock_input, mock_glob, mock_query_data
    ):
        """
        Test the behavior when the user chooses to overwrite an existing file.

        Ensures that the file is overwritten and the function returns the correct result.
        """
        mock_glob.return_value = [Path("./test_output/English/nouns.json")]
        get_data(language="English", data_type="nouns", output_dir="./test_output")
        mock_unlink.assert_called_once_with()
        mock_query_data.assert_called_once_with(
            languages=["English"],
            data_type=["nouns"],
            output_dir="./test_output",
            overwrite=False,
            interactive=False,
        )
