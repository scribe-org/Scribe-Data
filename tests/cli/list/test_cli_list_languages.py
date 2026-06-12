# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI list languages functionality.
"""

import unittest
from unittest.mock import MagicMock, patch

from scribe_data.cli.list.languages import list_languages, list_languages_for_data_type
from scribe_data.cli.main import main
from scribe_data.utils import (
    get_language_iso,
    get_language_qid,
    list_all_languages,
    list_languages_with_metadata_for_data_type,
)


class TestCLIListLanguages(unittest.TestCase):
    @patch("builtins.print")
    def test_cli_list_languages(self, mock_print: MagicMock) -> None:
        list_languages()

        # Verify the headers.
        mock_print.assert_any_call("\nLanguage           ISO   QID      ")
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
        # Total print calls: N (languages) + 3 (header, one separator, final line).
        self.assertEqual(mock_print.call_count, len(languages) + 3)

    @patch("builtins.print")
    def test_cli_list_languages_for_data_type_valid(
        self, mock_print: MagicMock
    ) -> None:
        # Call the function with a specific data type.
        list_languages_for_data_type("nouns")

        # Dynamically create the header based on column widths.
        all_languages = list_languages_with_metadata_for_data_type()

        # Calculate column widths as in the actual function.
        language_col_width = max(len(lang["name"]) for lang in all_languages) + 2
        iso_col_width = max(len(lang["iso"]) for lang in all_languages) + 2
        qid_col_width = max(len(lang["qid"]) for lang in all_languages) + 2

        # Dynamically generate the expected header string.
        expected_header = f"{'\nLanguage':<{language_col_width}} {'ISO':<{iso_col_width}} {'QID':<{qid_col_width}}"

        # Verify the headers dynamically.
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
        # Total calls = N (languages) + 3 (header, one separator, final line)
        expected_calls = len(all_languages) + 3
        self.assertEqual(mock_print.call_count, expected_calls)

    @patch("scribe_data.cli.list.languages.list_languages")
    def test_cli_list_languages_command(self, mock_list_languages: MagicMock) -> None:
        test_args = ["main.py", "list", "--language"]
        with patch("sys.argv", test_args):
            main()

        mock_list_languages.assert_called_once()
