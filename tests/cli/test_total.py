# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI total functionality.
"""

import json
import unittest
from http.client import IncompleteRead
from unittest.mock import MagicMock, call, patch
from urllib.error import HTTPError

from scribe_data.cli.total import (
    get_datatype_list,
    get_qid_by_input,
    get_total_lexemes,
    total_wrapper,
)
from scribe_data.utils import WIKIDATA_QIDS_PIDS_FILE, check_qid_is_language

try:
    with WIKIDATA_QIDS_PIDS_FILE.open("r", encoding="utf-8") as file:
        wikidata_qids_pids = json.load(file)

except (IOError, json.JSONDecodeError) as e:
    print(f"Error reading language metadata: {e}")


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
            get_total_lexemes(language="English", data_type="nouns")

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
            get_total_lexemes(language="English", data_type="nouns")

        mock_print.assert_called_once_with("Total number of lexemes: Not found")

    @patch("scribe_data.cli.total.get_qid_by_input")
    @patch("scribe_data.cli.total.sparql.query")
    def test_get_total_lexemes_invalid_language(self, mock_query, mock_get_qid):
        mock_get_qid.side_effect = lambda x: None
        mock_query.return_value = MagicMock()

        with patch("builtins.print") as mock_print:
            get_total_lexemes(language="InvalidLanguage", data_type="nouns")

        mock_print.assert_called_once_with("Total number of lexemes: Not found")

    @patch("scribe_data.cli.total.get_qid_by_input")
    @patch("scribe_data.cli.total.sparql.query")
    def test_get_total_lexemes_empty_and_none_inputs(self, mock_query, mock_get_qid):
        mock_get_qid.return_value = None
        mock_query.return_value = MagicMock()

        # Call the function with empty and None inputs.
        with patch("builtins.print") as mock_print:
            get_total_lexemes(language="", data_type="nouns")
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
            get_total_lexemes(language="Martian", data_type="nouns")

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

        # Call the function with different data types.
        with patch("builtins.print") as mock_print:
            get_total_lexemes(language="English", data_type="verbs")
            get_total_lexemes(language="English", data_type="nouns")

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
            get_total_lexemes(language="Norwegian", data_type="verbs")
            get_total_lexemes(language="Norwegian", data_type="nouns")

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
    @patch("scribe_data.utils.requests.get")
    def test_check_qid_is_language_valid(self, mock_get):
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
    def test_check_qid_is_language_invalid(self, mock_get):
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


class TestTotalWrapper(unittest.TestCase):
    @patch("scribe_data.cli.total.print_total_lexemes")
    def test_total_wrapper_all_bool(self, mock_print_total_lexemes):
        total_wrapper(all_bool=True)
        mock_print_total_lexemes.assert_called_once_with()

    @patch("scribe_data.cli.total.print_total_lexemes")
    def test_total_wrapper_language_only(self, mock_print_total_lexemes):
        total_wrapper(language="English")
        mock_print_total_lexemes.assert_called_once_with(language="English")

    @patch("scribe_data.cli.total.get_total_lexemes")
    def test_total_wrapper_language_and_data_type(self, mock_get_total_lexemes):
        total_wrapper(language="English", data_type="nouns")
        mock_get_total_lexemes.assert_called_once_with(
            language="English", data_type="nouns"
        )

    def test_total_wrapper_invalid_input(self):
        with self.assertRaises(ValueError):
            total_wrapper()

    # MARK: Using Dump

    @patch("scribe_data.cli.total.parse_wd_lexeme_dump")
    def test_total_wrapper_wikidata_dump_flag(self, mock_parse_dump):
        """Test when wikidata_dump is True (flag without path)"""
        total_wrapper(wikidata_dump=True)
        mock_parse_dump.assert_called_once_with(
            language=None,
            data_types=None,
            wikidata_dump_type=["total"],
            wikidata_dump_path=None,
        )

    @patch("scribe_data.cli.total.parse_wd_lexeme_dump")
    def test_total_wrapper_wikidata_dump_path(self, mock_parse_dump):
        """Test when wikidata_dump is a file path"""
        dump_path = "/path/to/dump.json"
        total_wrapper(wikidata_dump=dump_path)
        mock_parse_dump.assert_called_once_with(
            language=None,
            data_types=[None],
            wikidata_dump_type=["total"],
            wikidata_dump_path=dump_path,
        )

    @patch("scribe_data.cli.total.parse_wd_lexeme_dump")
    def test_total_wrapper_wikidata_dump_with_all(self, mock_parse_dump):
        """Test when both wikidata_dump and all_bool are True"""
        total_wrapper(wikidata_dump=True, all_bool=True)
        mock_parse_dump.assert_called_once_with(
            language="all",
            data_types="all",
            wikidata_dump_type=["total"],
            wikidata_dump_path=None,
        )

    @patch("scribe_data.cli.total.parse_wd_lexeme_dump")
    def test_total_wrapper_wikidata_dump_with_language_and_type(self, mock_parse_dump):
        """Test wikidata_dump with specific language and data type"""
        total_wrapper(
            language="English", data_type="nouns", wikidata_dump="/path/to/dump.json"
        )
        mock_parse_dump.assert_called_once_with(
            language="English",
            data_types=["nouns"],
            wikidata_dump_type=["total"],
            wikidata_dump_path="/path/to/dump.json",
        )

    # MARK: Using QID

    @patch("scribe_data.cli.total.check_qid_is_language")
    @patch("scribe_data.cli.total.print_total_lexemes")
    def test_total_wrapper_with_qid(self, mock_print_total, mock_check_qid):
        """
        Test when language is provided as a QID
        """
        mock_check_qid.return_value = "Thai"
        total_wrapper(language="Q9217")
        mock_print_total.assert_called_once_with(language="Q9217")

    @patch("scribe_data.cli.total.check_qid_is_language")
    @patch("scribe_data.cli.total.get_total_lexemes")
    def test_total_wrapper_with_qid_and_datatype(self, mock_get_total, mock_check_qid):
        """
        Test when language QID and data type are provided
        """
        mock_check_qid.return_value = "Thai"
        total_wrapper(language="Q9217", data_type="nouns")
        mock_get_total.assert_called_once_with(language="Q9217", data_type="nouns")

    @patch("scribe_data.cli.total.parse_wd_lexeme_dump")
    def test_total_wrapper_qid_with_wikidata_dump(self, mock_parse_dump):
        """
        Test QID with wikidata dump
        """
        total_wrapper(language="Q9217", wikidata_dump=True, all_bool=True)
        mock_parse_dump.assert_called_once_with(
            language="Q9217",
            data_types="all",
            wikidata_dump_type=["total"],
            wikidata_dump_path=None,
        )

    @patch("scribe_data.cli.total.get_total_lexemes")
    def test_get_total_lexemes_with_qid(self, mock_get_total):
        """
        Test get_total_lexemes with QID input
        """
        total_wrapper(language="Q9217", data_type="Q1084")  # Q1084 is noun QID
        mock_get_total.assert_called_once_with(language="Q9217", data_type="Q1084")

    # MARK: Multiple Languages and Data Types

    @patch("scribe_data.cli.total.get_total_lexemes")
    def test_total_wrapper_multiple_languages(self, mock_get_total):
        """
        Test retrieving totals for multiple languages.
        """
        # Mock return value to avoid formatting error.
        mock_get_total.return_value = 100

        total_wrapper(language=["English", "German"], data_type="nouns")

        expected_calls = [
            call(language="English", data_type="nouns", do_print=False),
            call(language="German", data_type="nouns", do_print=False),
        ]
        mock_get_total.assert_has_calls(expected_calls)

    @patch("scribe_data.cli.total.get_total_lexemes")
    def test_total_wrapper_multiple_data_types(self, mock_get_total):
        """
        Test retrieving totals for multiple data types.
        """
        # Mock return value to avoid formatting error.
        mock_get_total.return_value = 100

        total_wrapper(language="English", data_type=["nouns", "verbs"])

        expected_calls = [
            call(language="English", data_type="nouns", do_print=False),
            call(language="English", data_type="verbs", do_print=False),
        ]
        mock_get_total.assert_has_calls(expected_calls)

    @patch("scribe_data.cli.total.get_total_lexemes")
    def test_total_wrapper_multiple_languages_and_types(self, mock_get_total):
        """
        Test retrieving totals for multiple languages and data types.
        """
        # Mock return value to avoid formatting error.
        mock_get_total.return_value = 100

        total_wrapper(language=["English", "German"], data_type=["nouns", "verbs"])

        expected_calls = [
            call(language="English", data_type="nouns", do_print=False),
            call(language="English", data_type="verbs", do_print=False),
            call(language="German", data_type="nouns", do_print=False),
            call(language="German", data_type="verbs", do_print=False),
        ]
        mock_get_total.assert_has_calls(expected_calls)

    # MARK: Error Handling

    @patch("scribe_data.cli.total.sparql.query")
    def test_get_total_lexemes_http_error(self, mock_query):
        """
        Test handling of HTTPError when querying totals.
        """
        # Set up mock to return None for results after max retries.
        mock_query.side_effect = [
            HTTPError(url="test", code=500, msg="error", hdrs={}, fp=None),
            HTTPError(url="test", code=500, msg="error", hdrs={}, fp=None),
            HTTPError(url="test", code=500, msg="error", hdrs={}, fp=None),
        ]

        with patch("builtins.print") as mock_print:
            result = get_total_lexemes(language="English", data_type="nouns")

        self.assertIsNone(result)
        mock_print.assert_any_call("Query failed after retries.")

    @patch("scribe_data.cli.total.sparql.query")
    def test_get_total_lexemes_incomplete_read(self, mock_query):
        """
        Test handling of IncompleteRead error when querying totals.
        """
        # Set up mock to return None for results after max retries.
        mock_query.side_effect = [
            IncompleteRead(partial=b""),
            IncompleteRead(partial=b""),
            IncompleteRead(partial=b""),
        ]

        with patch("builtins.print") as mock_print:
            result = get_total_lexemes(language="English", data_type="nouns")

        self.assertIsNone(result)
        mock_print.assert_any_call("Query failed after retries.")

    # MARK: Sub-language Handling

    @patch("scribe_data.cli.total.get_datatype_list")
    @patch("scribe_data.cli.total.get_total_lexemes")
    def test_print_total_lexemes_with_sublanguages(
        self, mock_get_total, mock_get_datatypes
    ):
        """
        Test printing totals for a language with sub-languages.
        """
        mock_get_datatypes.return_value = ["nouns", "verbs"]
        mock_get_total.return_value = 100

        with patch("builtins.print") as mock_print:
            total_wrapper(language="Norwegian")

        # Verify header was printed.
        mock_print.assert_any_call(
            f"{'Language':<20} {'Data Type':<25} {'Total Wikidata Lexemes':<25}"
        )
        mock_print.assert_any_call("=" * 70)

        # Verify data was printed for each data type.
        mock_get_total.assert_any_call(
            language="Norwegian", data_type="nouns", do_print=False
        )
        mock_get_total.assert_any_call(
            language="Norwegian", data_type="verbs", do_print=False
        )

    # MARK: Data Type List Handling

    @patch("scribe_data.cli.total.language_metadata")
    @patch("scribe_data.cli.total.list_all_languages")
    @patch("scribe_data.cli.total.LANGUAGE_DATA_EXTRACTION_DIR")
    def test_get_datatype_list_with_sublanguages(
        self, mock_dir, mock_list_languages, mock_metadata
    ):
        """
        Test getting data type list for a language with sub-languages.
        """
        # Mock language metadata and list_all_languages.
        mock_metadata_dict = {
            "norwegian": {
                "sub_languages": {"bokmal": {"iso": "nb"}, "nynorsk": {"iso": "nn"}}
            }
        }

        # Mock dictionary-like behavior for language_metadata.
        mock_metadata.__iter__.return_value = mock_metadata_dict.items()
        mock_metadata.items.return_value = mock_metadata_dict.items()
        mock_metadata.get.return_value = mock_metadata_dict["norwegian"]
        mock_metadata.__getitem__.return_value = mock_metadata_dict["norwegian"]

        mock_list_languages.return_value = ["norwegian"]

        # Create mock directory entries with proper string names.
        mock_nouns = MagicMock()
        mock_nouns.name = "nouns"
        mock_nouns.is_dir.return_value = True

        mock_verbs = MagicMock()
        mock_verbs.name = "verbs"
        mock_verbs.is_dir.return_value = True

        # Mock directory structure for both sub-languages.
        def mock_path_handler(path):
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path.iterdir.return_value = [mock_nouns, mock_verbs]
            return mock_path

        mock_dir.__truediv__.side_effect = mock_path_handler

        result = get_datatype_list("norwegian")  # note: lowercase
        self.assertEqual(sorted(result), ["nouns", "verbs"])

    @patch("scribe_data.cli.total.language_metadata")
    @patch("scribe_data.cli.total.LANGUAGE_DATA_EXTRACTION_DIR")
    def test_get_datatype_list_empty_directory(self, mock_dir, mock_metadata):
        """
        Test getting data type list from an empty directory.
        """
        # Mock language metadata.
        mock_metadata.get.return_value = {}

        mock_dir.__truediv__.return_value.exists.return_value = True
        mock_dir.__truediv__.return_value.iterdir.return_value = []

        with self.assertRaises(ValueError):
            get_datatype_list("English")
