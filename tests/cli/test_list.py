# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI list functionality.
"""

import unittest
from unittest.mock import call, patch

from scribe_data.cli.list import (
    get_language_iso,
    get_language_qid,
    list_all,
    list_all_languages,
    list_data_types,
    list_languages,
    list_languages_for_data_type,
    list_languages_with_metadata_for_data_type,
    list_wrapper,
)
from scribe_data.cli.main import main


class TestListFunctions(unittest.TestCase):
    @patch("builtins.print")
    def test_list_languages(self, mock_print):
        list_languages()

        # Verify the headers
        mock_print.assert_any_call("Language            ISO   QID      ")
        mock_print.assert_any_call("=================================")

        # Dynamically get the first language from the metadata.
        languages = list_all_languages()
        first_language = languages[0]
        first_iso = get_language_iso(first_language)
        first_qid = get_language_qid(first_language)

        # Verify the first language entry.
        # Calculate column widths as in the actual function.
        language_col_width = max(len(lang) for lang in languages) + 2
        iso_col_width = max(len(get_language_iso(lang)) for lang in languages) + 2
        qid_col_width = max(len(get_language_qid(lang)) for lang in languages) + 2

        # Verify the first language entry with dynamic spacing.
        mock_print.assert_any_call(
            f"{first_language.capitalize():<{language_col_width}} {first_iso:<{iso_col_width}} {first_qid:<{qid_col_width}}"
        )
        # Total print calls: N (languages) + 5 (initial line, header, one separator, final line).
        self.assertEqual(mock_print.call_count, len(languages) + 4)

    @patch("builtins.print")
    def test_list_data_types_all_languages(self, mock_print):
        list_data_types()
        print(mock_print.mock_calls)
        expected_calls = [
            call(),
            call("Available data types: All languages"),
            call("==================================="),
            call("adjectives"),
            call("adverbs"),
            call("emoji-keywords"),
            call("nouns"),
            call("personal-pronouns"),
            call("postpositions"),
            call("prepositions"),
            call("proper-nouns"),
            call("verbs"),
            call(),
        ]
        mock_print.assert_has_calls(expected_calls)

    @patch("builtins.print")
    def test_list_data_types_specific_language(self, mock_print):
        list_data_types("english")

        expected_calls = [
            call(),
            call("Available data types: English"),
            call("============================="),
            call("adjectives"),
            call("adverbs"),
            call("emoji-keywords"),
            call("nouns"),
            call("prepositions"),
            call("proper-nouns"),
            call("verbs"),
            call(),
        ]
        mock_print.assert_has_calls(expected_calls)

    def test_list_data_types_invalid_language(self):
        with self.assertRaises(ValueError):
            list_data_types("InvalidLanguage")

    def test_list_data_types_no_data_types(self):
        with self.assertRaises(ValueError):
            list_data_types("Klingon")

    @patch("scribe_data.cli.list.list_languages")
    @patch("scribe_data.cli.list.list_data_types")
    def test_list_all(self, mock_list_data_types, mock_list_languages):
        list_all()
        mock_list_languages.assert_called_once()
        mock_list_data_types.assert_called_once()

    @patch("scribe_data.cli.list.list_all")
    def test_list_wrapper_all(self, mock_list_all):
        list_wrapper(all_bool=True)
        mock_list_all.assert_called_once()

    @patch("scribe_data.cli.list.list_languages")
    def test_list_wrapper_languages(self, mock_list_languages):
        list_wrapper(language=True)
        mock_list_languages.assert_called_once()

    @patch("scribe_data.cli.list.list_data_types")
    def test_list_wrapper_data_types(self, mock_list_data_types):
        list_wrapper(data_type=True)
        mock_list_data_types.assert_called_once()

    @patch("builtins.print")
    def test_list_wrapper_language_and_data_type(self, mock_print):
        list_wrapper(language=True, data_type=True)
        mock_print.assert_called_with(
            "Please specify either a language or a data type."
        )

    @patch("scribe_data.cli.list.list_languages_for_data_type")
    def test_list_wrapper_languages_for_data_type(
        self, mock_list_languages_for_data_type
    ):
        list_wrapper(language=True, data_type="example_data_type")
        mock_list_languages_for_data_type.assert_called_with("example_data_type")

    @patch("scribe_data.cli.list.list_data_types")
    def test_list_wrapper_data_types_for_language(self, mock_list_data_types):
        list_wrapper(language="English", data_type=True)
        mock_list_data_types.assert_called_with("English")

    @patch("builtins.print")
    def test_list_languages_for_data_type_valid(self, mock_print):
        # Call the function with a specific data type.
        list_languages_for_data_type("nouns")

        # Dynamically create the header based on column widths.
        all_languages = list_languages_with_metadata_for_data_type()

        # Calculate column widths as in the actual function.
        language_col_width = max(len(lang["name"]) for lang in all_languages) + 2
        iso_col_width = max(len(lang["iso"]) for lang in all_languages) + 2
        qid_col_width = max(len(lang["qid"]) for lang in all_languages) + 2

        # Dynamically generate the expected header string.
        expected_header = f"{'Language':<{language_col_width}} {'ISO':<{iso_col_width}} {'QID':<{qid_col_width}}"

        # Verify the headers dynamically
        mock_print.assert_any_call(expected_header)
        mock_print.assert_any_call(
            "=" * (language_col_width + iso_col_width + qid_col_width)
        )

        # Verify the first language entry if there are any languages.

        first_language = all_languages[0]["name"].capitalize()
        first_iso = all_languages[0]["iso"]
        first_qid = all_languages[0]["qid"]

        # Verify the first language entry with dynamic spacing.
        mock_print.assert_any_call(
            f"{first_language:<{language_col_width}} {first_iso:<{iso_col_width}} {first_qid:<{qid_col_width}}"
        )

        # Check the total number of calls.
        # Total calls = N (languages) + 5 (initial line, header, one separator, final line)
        expected_calls = len(all_languages) + 4
        self.assertEqual(mock_print.call_count, expected_calls)

    @patch("scribe_data.cli.list.list_languages")
    def test_list_languages_command(self, mock_list_languages):
        test_args = ["main.py", "list", "--language"]
        with patch("sys.argv", test_args):
            main()
        mock_list_languages.assert_called_once()

    @patch("scribe_data.cli.list.list_data_types")
    def test_list_data_types_command(self, mock_list_data_types):
        test_args = ["main.py", "list", "--data-type"]
        with patch("sys.argv", test_args):
            main()
        mock_list_data_types.assert_called_once()

    @patch("scribe_data.cli.list.list_all")
    def test_list_all_command(self, mock_list_all):
        test_args = ["main.py", "list", "--all"]
        with patch("sys.argv", test_args):
            main()
        mock_list_all.assert_called_once()
