# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI total query functionality.
"""

import unittest
from unittest.mock import MagicMock, call, patch

import yaml

from scribe_data.cli.total.print_values import get_datatype_list
from scribe_data.cli.total.query import get_qid_by_input, query_total_lexemes
from scribe_data.utils import WIKIDATA_QIDS_PIDS_FILE, check_qid_is_language

try:
    with WIKIDATA_QIDS_PIDS_FILE.open("r", encoding="utf-8") as file:
        wikidata_qids_pids = yaml.safe_load(file)

except (IOError, yaml.YAMLError) as e:
    print(f"Error reading wikidata QIDs/PIDs metadata: {e}")

# MARK: Query


class TestCLITotalQuery(unittest.TestCase):
    @patch("scribe_data.cli.total.query.get_qid_by_input")
    @patch("scribe_data.cli.total.query.sparql.query")
    def test_cli_total_query_lexemes_valid(
        self, mock_query: MagicMock, mock_get_qid: MagicMock
    ) -> None:
        mock_get_qid.side_effect = lambda x: {"english": "Q1860", "nouns": "Q1084"}.get(
            x.lower()
        )
        mock_results = MagicMock()
        mock_results.convert.return_value = {
            "results": {"bindings": [{"total": {"value": "42"}}]}
        }
        mock_query.return_value = mock_results

        with patch("builtins.print") as mock_print:
            query_total_lexemes(language="English", data_type="nouns")

        mock_print.assert_called_once_with(
            "\nLanguage: English\nData type: nouns\nTotal number of lexemes: 42\n"
        )

    @patch("scribe_data.cli.total.query.get_qid_by_input")
    @patch("scribe_data.cli.total.query.sparql.query")
    def test_cli_total_query_lexemes_no_results(
        self, mock_query: MagicMock, mock_get_qid: MagicMock
    ) -> None:
        mock_get_qid.side_effect = lambda x: {"english": "Q1860", "nouns": "Q1084"}.get(
            x.lower()
        )
        mock_results = MagicMock()
        mock_results.convert.return_value = {"results": {"bindings": []}}
        mock_query.return_value = mock_results

        with patch("builtins.print") as mock_print:
            query_total_lexemes(language="English", data_type="nouns")

        mock_print.assert_called_once_with("Total number of lexemes: Not found")

    @patch("scribe_data.cli.total.query.get_qid_by_input")
    @patch("scribe_data.cli.total.query.sparql.query")
    def test_cli_total_query_lexemes_invalid_language(
        self, mock_query: MagicMock, mock_get_qid: MagicMock
    ) -> None:
        mock_get_qid.side_effect = lambda x: None
        mock_query.return_value = MagicMock()

        with patch("builtins.print") as mock_print:
            query_total_lexemes(language="InvalidLanguage", data_type="nouns")

        mock_print.assert_called_once_with("Total number of lexemes: Not found")

    @patch("scribe_data.cli.total.query.get_qid_by_input")
    @patch("scribe_data.cli.total.query.sparql.query")
    def test_cli_total_query_lexemes_empty_and_none_inputs(
        self, mock_query: MagicMock, mock_get_qid: MagicMock
    ) -> None:
        mock_get_qid.return_value = None
        mock_query.return_value = MagicMock()

        # Call the function with empty and None inputs.
        with patch("builtins.print") as mock_print:
            query_total_lexemes(language="", data_type="nouns")
            query_total_lexemes(language=None, data_type="verbs")

        expected_calls = [
            call("Total number of lexemes: Not found"),
            call("Total number of lexemes: Not found"),
        ]
        mock_print.assert_has_calls(expected_calls, any_order=True)

    @patch("scribe_data.cli.total.query.get_qid_by_input")
    @patch("scribe_data.cli.total.query.sparql.query")
    def test_cli_total_query_lexemes_nonexistent_language(
        self, mock_query: MagicMock, mock_get_qid: MagicMock
    ) -> None:
        mock_get_qid.return_value = None
        mock_query.return_value = MagicMock()

        with patch("builtins.print") as mock_print:
            query_total_lexemes(language="Martian", data_type="nouns")

        mock_print.assert_called_once_with("Total number of lexemes: Not found")

    @patch("scribe_data.cli.total.query.get_qid_by_input")
    @patch("scribe_data.cli.total.query.sparql.query")
    def test_cli_total_query_lexemes_various_data_types(
        self, mock_query: MagicMock, mock_get_qid: MagicMock
    ) -> None:
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

        # Call the function with different data types.
        with patch("builtins.print") as mock_print:
            query_total_lexemes(language="English", data_type="verbs")
            query_total_lexemes(language="English", data_type="nouns")

        expected_calls = [
            call(
                "\nLanguage: English\nData type: verbs\nTotal number of lexemes: 30\n"
            ),
            call(
                "\nLanguage: English\nData type: nouns\nTotal number of lexemes: 30\n"
            ),
        ]
        mock_print.assert_has_calls(expected_calls)

    @patch("scribe_data.cli.total.query.get_qid_by_input")
    @patch("scribe_data.cli.total.query.sparql.query")
    @patch("scribe_data.cli.total.print_values.WIKIDATA_QUERIES_ALL_DATA_DIR")
    def test_cli_total_query_lexemes_sub_languages(
        self, mock_dir: MagicMock, mock_query: MagicMock, mock_get_qid: MagicMock
    ) -> None:
        # Setup for sub-languages.
        mock_get_qid.side_effect = lambda x: {
            "bokmål": "Q25167",
            "nynorsk": "Q25164",
        }.get(x.lower())
        mock_results = MagicMock()
        mock_results.convert.return_value = {
            "results": {"bindings": [{"total": {"value": "30"}}]}
        }
        mock_query.return_value = mock_results

        # Mocking directory paths and contents.
        mock_dir.__truediv__.return_value.exists.return_value = True
        mock_dir.__truediv__.return_value.iterdir.return_value = [
            MagicMock(name="verbs", is_dir=lambda: True),
            MagicMock(name="nouns", is_dir=lambda: True),
        ]

        with patch("builtins.print") as mock_print:
            query_total_lexemes(language="Norwegian", data_type="verbs")
            query_total_lexemes(language="Norwegian", data_type="nouns")

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
    def setUp(self) -> None:
        self.valid_data_types = {
            "english": "Q1860",
            "nouns": "Q1084",
            "verbs": "Q24905",
        }

    @patch("scribe_data.cli.total.query.data_type_metadata", new_callable=dict)
    def test_get_qid_by_input_valid(self, mock_data_type_metadata: MagicMock) -> None:
        mock_data_type_metadata.update(self.valid_data_types)

        for data_type, expected_qid in self.valid_data_types.items():
            self.assertEqual(get_qid_by_input(data_type), expected_qid)

    @patch("scribe_data.cli.total.query.data_type_metadata", new_callable=dict)
    def test_get_qid_by_input_invalid(self, mock_data_type_metadata: MagicMock) -> None:
        mock_data_type_metadata.update(self.valid_data_types)

        self.assertIsNone(get_qid_by_input("invalid_data_type"))


class TestGetDatatypeList(unittest.TestCase):
    @patch("scribe_data.cli.total.print_values.WIKIDATA_QUERIES_ALL_DATA_DIR")
    def test_get_datatype_list_invalid_language(self, mock_dir: MagicMock) -> None:
        mock_dir.__truediv__.return_value.exists.return_value = False

        with self.assertRaises(ValueError):
            get_datatype_list("InvalidLanguage")

    @patch("scribe_data.cli.total.print_values.WIKIDATA_QUERIES_ALL_DATA_DIR")
    def test_get_datatype_list_no_data_types(self, mock_dir: MagicMock) -> None:
        mock_dir.__truediv__.return_value.exists.return_value = True
        mock_dir.__truediv__.return_value.iterdir.return_value = []

        with self.assertRaises(ValueError):
            get_datatype_list("English")


class TestCheckQidIsLanguage(unittest.TestCase):
    @patch("scribe_data.utils.requests.get")
    def test_check_qid_is_language_valid(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "statements": {
                wikidata_qids_pids["instance_of"]: [{"value": {"content": "Q34770"}}]
            },
            "labels": {"en": "English"},
        }
        mock_get.return_value = mock_response

        with patch("builtins.print") as mock_print:
            result = check_qid_is_language("Q1860")

        self.assertEqual(result, "English")
        mock_print.assert_called_once_with("English (Q1860) is a language.\n")

    @patch("scribe_data.utils.requests.get")
    def test_check_qid_is_language_invalid(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "statements": {
                wikidata_qids_pids["instance_of"]: [{"value": {"content": "Q5"}}]
            },
            "labels": {"en": "Human"},
        }
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            check_qid_is_language("Q5")
