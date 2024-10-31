"""
Tests for the CLI total functionality.

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
from unittest.mock import MagicMock, call, patch

from scribe_data.cli.total import (
    get_qid_by_input,
    get_total_lexemes,
    get_datatype_list,
    check_qid_is_language,
    total_wrapper,
)


class TestTotalLexemes(unittest.TestCase):
    @patch("scribe_data.cli.total.get_qid_by_input")
    @patch("scribe_data.cli.total.sparql.query")
    def test_get_total_lexemes_valid(self, mock_query, mock_get_qid):
        mock_get_qid.side_effect = lambda x: {"english": "Q1860", "nouns": "Q1084"}.get(
            x.lower()
        )
        mock_results = MagicMock()
        mock_results.convert.return_value = {
            "results": {"bindings": [{"total": {"value": "42"}}]}
        }
        mock_query.return_value = mock_results

        with patch("builtins.print") as mock_print:
            get_total_lexemes("English", "nouns")

        mock_print.assert_called_once_with(
            "\nLanguage: English\nData type: nouns\nTotal number of lexemes: 42\n"
        )

    @patch("scribe_data.cli.total.get_qid_by_input")
    @patch("scribe_data.cli.total.sparql.query")
    def test_get_total_lexemes_no_results(self, mock_query, mock_get_qid):
        mock_get_qid.side_effect = lambda x: {"english": "Q1860", "nouns": "Q1084"}.get(
            x.lower()
        )
        mock_results = MagicMock()
        mock_results.convert.return_value = {"results": {"bindings": []}}
        mock_query.return_value = mock_results

        with patch("builtins.print") as mock_print:
            get_total_lexemes("English", "nouns")

        mock_print.assert_called_once_with("Total number of lexemes: Not found")

    @patch("scribe_data.cli.total.get_qid_by_input")
    @patch("scribe_data.cli.total.sparql.query")
    def test_get_total_lexemes_invalid_language(self, mock_query, mock_get_qid):
        mock_get_qid.side_effect = lambda x: None
        mock_query.return_value = MagicMock()

        with patch("builtins.print") as mock_print:
            get_total_lexemes("InvalidLanguage", "nouns")

        mock_print.assert_called_once_with("Total number of lexemes: Not found")

    @patch("scribe_data.cli.total.get_qid_by_input")
    @patch("scribe_data.cli.total.sparql.query")
    def test_get_total_lexemes_empty_and_none_inputs(self, mock_query, mock_get_qid):
        mock_get_qid.return_value = None
        mock_query.return_value = MagicMock()

        # Call the function with empty and None inputs
        with patch("builtins.print") as mock_print:
            get_total_lexemes("", "nouns")
            get_total_lexemes(None, "verbs")

        expected_calls = [
            call("Total number of lexemes: Not found"),
            call("Total number of lexemes: Not found"),
        ]
        mock_print.assert_has_calls(expected_calls, any_order=True)

    @patch("scribe_data.cli.total.get_qid_by_input")
    @patch("scribe_data.cli.total.sparql.query")
    def test_get_total_lexemes_nonexistent_language(self, mock_query, mock_get_qid):
        mock_get_qid.return_value = None
        mock_query.return_value = MagicMock()

        with patch("builtins.print") as mock_print:
            get_total_lexemes("Martian", "nouns")

        mock_print.assert_called_once_with("Total number of lexemes: Not found")

    @patch("scribe_data.cli.total.get_qid_by_input")
    @patch("scribe_data.cli.total.sparql.query")
    def test_get_total_lexemes_various_data_types(self, mock_query, mock_get_qid):
        mock_get_qid.side_effect = lambda x: {
            "english": "Q1860",
            "verbs": "Q24905",
            "nouns": "Q1084",
        }.get(x.lower())
        mock_results = MagicMock()
        mock_results.convert.return_value = {
            "results": {"bindings": [{"total": {"value": "30"}}]}
        }

        mock_query.return_value = mock_results

        # Call the function with different data types
        with patch("builtins.print") as mock_print:
            get_total_lexemes("English", "verbs")
            get_total_lexemes("English", "nouns")

        expected_calls = [
            call(
                "\nLanguage: English\nData type: verbs\nTotal number of lexemes: 30\n"
            ),
            call(
                "\nLanguage: English\nData type: nouns\nTotal number of lexemes: 30\n"
            ),
        ]
        mock_print.assert_has_calls(expected_calls)

    @patch("scribe_data.cli.total.get_qid_by_input")
    @patch("scribe_data.cli.total.sparql.query")
    @patch("scribe_data.cli.total.LANGUAGE_DATA_EXTRACTION_DIR")
    def test_get_total_lexemes_sub_languages(self, mock_dir, mock_query, mock_get_qid):
        # Setup for sub-languages
        mock_get_qid.side_effect = lambda x: {
            "bokmål": "Q25167",
            "nynorsk": "Q25164",
        }.get(x.lower())
        mock_results = MagicMock()
        mock_results.convert.return_value = {
            "results": {"bindings": [{"total": {"value": "30"}}]}
        }
        mock_query.return_value = mock_results

        # Mocking directory paths and contents
        mock_dir.__truediv__.return_value.exists.return_value = True
        mock_dir.__truediv__.return_value.iterdir.return_value = [
            MagicMock(name="verbs", is_dir=lambda: True),
            MagicMock(name="nouns", is_dir=lambda: True),
        ]

        with patch("builtins.print") as mock_print:
            get_total_lexemes("Norwegian", "verbs")
            get_total_lexemes("Norwegian", "nouns")

        expected_calls = [
            call(
                "\nLanguage: Norwegian\nData type: verbs\nTotal number of lexemes: 30\n"
            ),
            call(
                "\nLanguage: Norwegian\nData type: nouns\nTotal number of lexemes: 30\n"
            ),
        ]
        mock_print.assert_has_calls(expected_calls)


class TestGetQidByInput(unittest.TestCase):
    def setUp(self):
        self.valid_data_types = {
            "english": "Q1860",
            "nouns": "Q1084",
            "verbs": "Q24905",
        }

    @patch("scribe_data.cli.total.data_type_metadata", new_callable=dict)
    def test_get_qid_by_input_valid(self, mock_data_type_metadata):
        mock_data_type_metadata.update(self.valid_data_types)

        for data_type, expected_qid in self.valid_data_types.items():
            self.assertEqual(get_qid_by_input(data_type), expected_qid)

    @patch("scribe_data.cli.total.data_type_metadata", new_callable=dict)
    def test_get_qid_by_input_invalid(self, mock_data_type_metadata):
        mock_data_type_metadata.update(self.valid_data_types)

        self.assertIsNone(get_qid_by_input("invalid_data_type"))


class TestGetDatatypeList(unittest.TestCase):
    @patch("scribe_data.cli.total.LANGUAGE_DATA_EXTRACTION_DIR")
    def test_get_datatype_list_invalid_language(self, mock_dir):
        mock_dir.__truediv__.return_value.exists.return_value = False

        with self.assertRaises(ValueError):
            get_datatype_list("InvalidLanguage")

    @patch("scribe_data.cli.total.LANGUAGE_DATA_EXTRACTION_DIR")
    def test_get_datatype_list_no_data_types(self, mock_dir):
        mock_dir.__truediv__.return_value.exists.return_value = True
        mock_dir.__truediv__.return_value.iterdir.return_value = []

        with self.assertRaises(ValueError):
            get_datatype_list("English")


class TestCheckQidIsLanguage(unittest.TestCase):
    @patch("scribe_data.cli.total.requests.get")
    def test_check_qid_is_language_valid(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "statements": {"P31": [{"value": {"content": "Q34770"}}]},
            "labels": {"en": "English"},
        }
        mock_get.return_value = mock_response

        with patch("builtins.print") as mock_print:
            result = check_qid_is_language("Q1860")

        self.assertEqual(result, "English")
        mock_print.assert_called_once_with("English (Q1860) is a language.\n")

    @patch("scribe_data.cli.total.requests.get")
    def test_check_qid_is_language_invalid(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "statements": {"P31": [{"value": {"content": "Q5"}}]},
            "labels": {"en": "Human"},
        }
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            check_qid_is_language("Q5")


class TestTotalWrapper(unittest.TestCase):
    @patch("scribe_data.cli.total.print_total_lexemes")
    def test_total_wrapper_all_bool(self, mock_print_total_lexemes):
        total_wrapper(all_bool=True)
        mock_print_total_lexemes.assert_called_once_with()

    @patch("scribe_data.cli.total.print_total_lexemes")
    def test_total_wrapper_language_only(self, mock_print_total_lexemes):
        total_wrapper(language="English")
        mock_print_total_lexemes.assert_called_once_with("English")

    @patch("scribe_data.cli.total.get_total_lexemes")
    def test_total_wrapper_language_and_data_type(self, mock_get_total_lexemes):
        total_wrapper(language="English", data_type="nouns")
        mock_get_total_lexemes.assert_called_once_with("English", "nouns")

    def test_total_wrapper_invalid_input(self):
        with self.assertRaises(ValueError):
            total_wrapper()
