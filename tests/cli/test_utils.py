"""
Tests for the CLI utils functionality.

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
from unittest.mock import patch

from scribe_data.cli.cli_utils import (
    correct_data_type,
    print_formatted_data,
    validate_language_and_data_type,
)

# MARK: Utils


class TestCLIUtils(unittest.TestCase):
    def test_correct_data_type(self):
        self.assertEqual(correct_data_type("autosuggestion"), "autosuggestions")
        self.assertEqual(correct_data_type("emoji_keyword"), "emoji_keywords")
        self.assertEqual(correct_data_type("preposition"), "prepositions")
        self.assertEqual(correct_data_type("invalid"), None)

    def test_correct_data_type_with_trailing_s(self):
        self.assertEqual(correct_data_type("autosuggestions"), "autosuggestions")
        self.assertEqual(correct_data_type("emoji_keywords"), "emoji_keywords")
        self.assertEqual(correct_data_type("prepositions"), "prepositions")

    def test_correct_data_type_invalid_input(self):
        self.assertIsNone(correct_data_type("invalid_data_type"))
        self.assertIsNone(correct_data_type(""))
        self.assertIsNone(correct_data_type(None))

    @patch("builtins.print")
    def test_print_formatted_data_autosuggestions(self, mock_print):
        data = {"key1": ["value1", "value2"], "key2": ["value3"]}
        print_formatted_data(data, "autosuggestions")
        mock_print.assert_any_call("key1 : value1, value2")
        mock_print.assert_any_call("key2 : value3")

    @patch("builtins.print")
    def test_print_formatted_data_emoji_keywords(self, mock_print):
        data = {"key1": [{"emoji": "😀"}, {"emoji": "😁"}], "key2": [{"emoji": "😂"}]}
        print_formatted_data(data, "emoji_keywords")
        mock_print.assert_any_call("key1 : 😀 😁")
        mock_print.assert_any_call("key2 : 😂")

    @patch("builtins.print")
    def test_print_formatted_data_dict(self, mock_print):
        data = {
            "key1": {"subkey1": "value1", "subkey2": "value2"},
            "key2": ["item1", "item2"],
        }
        print_formatted_data(data, "dict_data")
        mock_print.assert_any_call("key1 : ")
        mock_print.assert_any_call("  subkey1 : value1")
        mock_print.assert_any_call("  subkey2 : value2")
        mock_print.assert_any_call("key2 : ")
        mock_print.assert_any_call("  item1")
        mock_print.assert_any_call("  item2")

    @patch("builtins.print")
    def test_print_formatted_data_empty_data(self, mock_print):
        print_formatted_data({}, "autosuggestions")
        mock_print.assert_called_once_with(
            "No data available for data type 'autosuggestions'."
        )

    @patch("builtins.print")
    def test_print_formatted_data_invalid_data_type(self, mock_print):
        data = {"key1": "value1", "key2": "value2"}
        print_formatted_data(data, "invalid_data_type")
        mock_print.assert_any_call("key1 : value1")
        mock_print.assert_any_call("key2 : value2")

    @patch("builtins.print")
    def test_print_formatted_data_list(self, mock_print):
        data = ["item1", "item2", "item3"]
        print_formatted_data(data, "list_data")
        mock_print.assert_any_call("item1")
        mock_print.assert_any_call("item2")
        mock_print.assert_any_call("item3")

    @patch("builtins.print")
    def test_print_formatted_data_list_of_dicts(self, mock_print):
        data = [{"key1": "value1"}, {"key2": "value2"}]
        print_formatted_data(data, "list_of_dicts")
        mock_print.assert_any_call("key1 : value1")
        mock_print.assert_any_call("key2 : value2")

    @patch("builtins.print")
    def test_print_formatted_data_autosuggestions_redefined(self, mock_print):
        data = {"key1": ["value1", "value2"], "key2": ["value3"]}
        print_formatted_data(data, "autosuggestions")

    def test_print_formatted_data_autosuggestions_with_patch(self):
        data = {"key1": ["value1", "value2"], "key2": ["value3", "value4"]}
        with patch("builtins.print") as mock_print:
            print_formatted_data(data, "autosuggestions")
            mock_print.assert_any_call("key1 : value1, value2")
            mock_print.assert_any_call("key2 : value3, value4")

    def test_print_formatted_data_prepositions(self):
        data = {"key1": "value1", "key2": "value2"}
        with patch("builtins.print") as mock_print:
            print_formatted_data(data, "prepositions")
            mock_print.assert_any_call("key1 : value1")
            mock_print.assert_any_call("key2 : value2")

    def test_print_formatted_data_nested_dict(self):
        data = {"key1": {"subkey1": "subvalue1", "subkey2": "subvalue2"}}
        with patch("builtins.print") as mock_print:
            print_formatted_data(data, "nested_dict")
            mock_print.assert_any_call("key1 : ")
            mock_print.assert_any_call("  subkey1 : subvalue1")
            mock_print.assert_any_call("  subkey2 : subvalue2")

    def test_print_formatted_data_list_of_dicts_with_different_keys(self):
        data = [{"key1": "value1"}, {"key2": "value2"}]
        with patch("builtins.print") as mock_print:
            print_formatted_data(data, "list_of_dicts_different_keys")
            mock_print.assert_any_call("key1 : value1")
            mock_print.assert_any_call("key2 : value2")

    def test_print_formatted_data_unknown_type(self):
        data = "unknown data type"
        with patch("builtins.print") as mock_print:
            print_formatted_data(data, "unknown")
            mock_print.assert_called_once_with("unknown data type")


# MARK: Validate


class TestValidateLanguageAndDataType(unittest.TestCase):
    def setUp(self):
        self.qid_mapping = {
            "english": "Q1860",
            "nouns": "Q1084",
            "verbs": "Q24905",
        }

    def mock_get_qid(self, input_value):
        """Returns QID based on the input language or data type."""
        return self.qid_mapping.get(input_value.lower())

    @patch("scribe_data.cli.total.get_qid_by_input")
    def test_validate_language_and_data_type_valid(self, mock_get_qid):
        mock_get_qid.side_effect = self.mock_get_qid

        language_qid = mock_get_qid("English")
        data_type_qid = mock_get_qid("nouns")

        try:
            validate_language_and_data_type(language_qid, data_type_qid)

        except ValueError:
            self.fail("validate_language_and_data_type raised ValueError unexpectedly!")

    @patch("scribe_data.cli.total.get_qid_by_input")
    def test_validate_language_and_data_type_invalid_language(self, mock_get_qid):
        mock_get_qid.side_effect = self.mock_get_qid

        language_qid = "InvalidLanguage"
        data_type_qid = "nouns"

        with self.assertRaises(ValueError) as context:
            validate_language_and_data_type(
                language=language_qid, data_type=data_type_qid
            )

        self.assertEqual(str(context.exception), "Invalid language 'InvalidLanguage'.")

    @patch("scribe_data.cli.total.get_qid_by_input")
    def test_validate_language_and_data_type_invalid_data_type(self, mock_get_qid):
        mock_get_qid.side_effect = self.mock_get_qid

        language_qid = "English"
        data_type_qid = "InvalidDataType"

        with self.assertRaises(ValueError) as context:
            validate_language_and_data_type(
                language=language_qid, data_type=data_type_qid
            )

        self.assertEqual(str(context.exception), "Invalid data-type 'InvalidDataType'.")

    @patch("scribe_data.cli.total.get_qid_by_input")
    def test_validate_language_and_data_type_both_invalid(self, mock_get_qid):
        mock_get_qid.side_effect = lambda x: None  # Simulate invalid inputs

        language_qid = "InvalidLanguage"
        data_type_qid = "InvalidDataType"

        with self.assertRaises(ValueError) as context:
            validate_language_and_data_type(
                language=language_qid, data_type=data_type_qid
            )

        self.assertEqual(
            str(context.exception),
            "Invalid language 'InvalidLanguage'.\nInvalid data-type 'InvalidDataType'.",
        )

    def test_validate_language_and_data_type_with_list(self):
        """Test validation with lists of languages and data types."""
        languages = ["English", "Spanish"]
        data_types = ["nouns", "verbs"]
        try:
            validate_language_and_data_type(languages, data_types)
        except ValueError:
            self.fail(
                "validate_language_and_data_type raised ValueError unexpectedly with valid lists!"
            )

    def test_validate_language_and_data_type_with_qids(self):
        """Test validation directly with QIDs."""
        language_qid = "Q1860"  # QID for English
        data_type_qid = "Q1084"  # QID for nouns
        try:
            validate_language_and_data_type(language_qid, data_type_qid)
        except ValueError:
            self.fail(
                "validate_language_and_data_type raised ValueError unexpectedly with valid QIDs!"
            )

    def test_validate_language_and_data_type_mixed_validity_in_lists(self):
        """Test validation with mixed valid and invalid entries in lists."""
        languages = ["English", "InvalidLanguage"]
        data_types = ["nouns", "InvalidDataType"]
        with self.assertRaises(ValueError) as context:
            validate_language_and_data_type(languages, data_types)
        self.assertIn("Invalid language 'InvalidLanguage'", str(context.exception))
        self.assertIn("Invalid data-type 'InvalidDataType'", str(context.exception))
