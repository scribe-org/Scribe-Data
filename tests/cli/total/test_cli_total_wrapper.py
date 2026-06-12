# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI total wrapper functionality.
"""

import unittest
from http.client import IncompleteRead
from pathlib import Path
from unittest.mock import MagicMock, call, patch
from urllib.error import HTTPError

import yaml

from scribe_data.cli.total.print_values import get_datatype_list
from scribe_data.cli.total.query import query_total_lexemes
from scribe_data.cli.total.wrapper import total_wrapper
from scribe_data.utils import DEFAULT_WIKIDATA_DUMP_EXPORT_DIR, WIKIDATA_QIDS_PIDS_FILE

try:
    with WIKIDATA_QIDS_PIDS_FILE.open("r", encoding="utf-8") as file:
        wikidata_qids_pids = yaml.safe_load(file)

except (IOError, yaml.YAMLError) as e:
    print(f"Error reading wikidata QIDs/PIDs metadata: {e}")

# MARK: Wrapper


class TestCLITotalWrapper(unittest.TestCase):
    @patch("scribe_data.cli.total.print_total_lexemes")
    def test_cli_total_wrapper_all_bool(
        self, mock_print_total_lexemes: MagicMock
    ) -> None:
        total_wrapper(all_bool=True)
        mock_print_total_lexemes.assert_called_once_with()

    @patch("scribe_data.cli.total.print_total_lexemes")
    def test_cli_total_wrapper_language_only(
        self, mock_print_total_lexemes: MagicMock
    ) -> None:
        total_wrapper(languages=["English"])
        mock_print_total_lexemes.assert_called_once_with(language="English")

    @patch("scribe_data.cli.total.query_total_lexemes")
    def test_cli_total_wrapper_language_and_data_type(
        self, mock_query_total_lexemes_lexemes: MagicMock
    ) -> None:
        total_wrapper(languages=["English"], data_types=["nouns"])
        mock_query_total_lexemes_lexemes.assert_called_once_with(
            language="English", data_type="nouns"
        )

    def test_cli_total_wrapper_invalid_input(self) -> None:
        with self.assertRaises(ValueError):
            total_wrapper()

    # MARK: Using Dump

    @patch("scribe_data.cli.total.parse_wd_lexeme_dump")
    def test_cli_total_wrapper_wikidata_dump_flag(
        self, mock_parse_dump: MagicMock
    ) -> None:
        """
        Test when wikidata_dump is True (flag without path).
        """
        total_wrapper(wikidata_dump=True)
        mock_parse_dump.assert_called_once_with(
            languages=["all"],
            data_types=["all"],
            wikidata_dump_type=["total"],
            wikidata_dump_path=DEFAULT_WIKIDATA_DUMP_EXPORT_DIR,
        )

    @patch("scribe_data.cli.total.parse_wd_lexeme_dump")
    def test_cli_total_wrapper_wikidata_dump_with_all(
        self, mock_parse_dump: MagicMock
    ) -> None:
        """
        Test when both wikidata_dump and all_bool are True.
        """
        total_wrapper(wikidata_dump=True, all_bool=True)
        mock_parse_dump.assert_called_once_with(
            languages=["all"],
            data_types=["all"],
            wikidata_dump_type=["total"],
            wikidata_dump_path=DEFAULT_WIKIDATA_DUMP_EXPORT_DIR,
        )

    @patch("scribe_data.cli.total.parse_wd_lexeme_dump")
    def test_cli_total_wrapper_wikidata_dump_with_language_and_type(
        self, mock_parse_dump: MagicMock
    ) -> None:
        """
        Test wikidata_dump with specific language and data type.
        """
        total_wrapper(
            languages=["English"],
            data_types=["nouns"],
            wikidata_dump=Path("/path/to/dump.json"),
        )
        mock_parse_dump.assert_called_once_with(
            languages=["English"],
            data_types=["nouns"],
            wikidata_dump_type=["total"],
            wikidata_dump_path=Path("/path/to/dump.json"),
        )

    # MARK: Using QID

    @patch("scribe_data.cli.total.check_qid_is_language")
    @patch("scribe_data.cli.total.print_total_lexemes")
    def test_cli_total_wrapper_with_qid(
        self, mock_print_total: MagicMock, mock_check_qid: MagicMock
    ) -> None:
        """
        Test when language is provided as a QID.
        """
        mock_check_qid.return_value = "Thai"
        total_wrapper(languages=["Q9217"])
        mock_print_total.assert_called_once_with(language="Q9217")

    @patch("scribe_data.cli.total.check_qid_is_language")
    @patch("scribe_data.cli.total.query_total_lexemes")
    def test_cli_total_wrapper_with_qid_and_datatype(
        self, mock_query_total_lexemes: MagicMock, mock_check_qid: MagicMock
    ) -> None:
        """
        Test when language QID and data type are provided.
        """
        mock_check_qid.return_value = "Thai"
        total_wrapper(languages=["Q9217"], data_types=["nouns"])
        mock_query_total_lexemes.assert_called_once_with(
            language="Q9217", data_type="nouns"
        )

    @patch("scribe_data.cli.total.parse_wd_lexeme_dump")
    def test_cli_total_wrapper_qid_with_wikidata_dump(
        self, mock_parse_dump: MagicMock
    ) -> None:
        """
        Test QID with wikidata dump.
        """
        total_wrapper(languages=["Q9217"], wikidata_dump=True, all_bool=True)
        mock_parse_dump.assert_called_once_with(
            languages=["Q9217"],
            data_types=["all"],
            wikidata_dump_type=["total"],
            wikidata_dump_path=DEFAULT_WIKIDATA_DUMP_EXPORT_DIR,
        )

    @patch("scribe_data.cli.total.query_total_lexemes")
    def test_cli_total_wrapper_query_total_lexemes_with_qid(
        self, mock_query_total_lexemes: MagicMock
    ) -> None:
        """
        Test query_total_lexemes with QID input.
        """
        total_wrapper(languages=["Q9217"], data_types=["Q1084"])  # Q1084 is noun QID
        mock_query_total_lexemes.assert_called_once_with(
            language="Q9217", data_type="Q1084"
        )

    # MARK: Multiple Languages and Data Types

    @patch("scribe_data.cli.total.query_total_lexemes")
    def test_cli_total_wrapper_multiple_languages(
        self, mock_query_total_lexemes: MagicMock
    ) -> None:
        """
        Test retrieving totals for multiple languages.
        """
        # Mock return value to avoid formatting error.
        mock_query_total_lexemes.return_value = 100

        total_wrapper(languages=["English", "German"], data_types=["nouns"])

        expected_calls = [
            call(language="English", data_type="nouns", do_print=False),
            call(language="German", data_type="nouns", do_print=False),
        ]
        mock_query_total_lexemes.assert_has_calls(expected_calls)

    @patch("scribe_data.cli.total.query_total_lexemes")
    def test_cli_total_wrapper_multiple_data_types(
        self, mock_query_total_lexemes: MagicMock
    ) -> None:
        """
        Test retrieving totals for multiple data types.
        """
        # Mock return value to avoid formatting error.
        mock_query_total_lexemes.return_value = 100

        total_wrapper(languages=["English"], data_types=["nouns", "verbs"])

        expected_calls = [
            call(language="English", data_type="nouns", do_print=False),
            call(language="English", data_type="verbs", do_print=False),
        ]
        mock_query_total_lexemes.assert_has_calls(expected_calls)

    @patch("scribe_data.cli.total.query_total_lexemes")
    def test_total_wrapper_multiple_languages_and_types(
        self, mock_query_total_lexemes: MagicMock
    ) -> None:
        """
        Test retrieving totals for multiple languages and data types.
        """
        # Mock return value to avoid formatting error.
        mock_query_total_lexemes.return_value = 100

        total_wrapper(languages=["English", "German"], data_types=["nouns", "verbs"])

        expected_calls = [
            call(language="English", data_type="nouns", do_print=False),
            call(language="English", data_type="verbs", do_print=False),
            call(language="German", data_type="nouns", do_print=False),
            call(language="German", data_type="verbs", do_print=False),
        ]
        mock_query_total_lexemes.assert_has_calls(expected_calls)

    # MARK: Error Handling

    @patch("scribe_data.cli.total.sparql.query")
    def test_cli_query_total_lexemes_http_error(self, mock_query: MagicMock) -> None:
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
            result = query_total_lexemes(language="English", data_type="nouns")

        self.assertIsNone(result)
        mock_print.assert_any_call("Query failed after retries.")

    @patch("scribe_data.cli.total.sparql.query")
    def test_cli_query_total_lexemes_incomplete_read(
        self, mock_query: MagicMock
    ) -> None:
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
            result = query_total_lexemes(language="English", data_type="nouns")

        self.assertIsNone(result)
        mock_print.assert_any_call("Query failed after retries.")

    # MARK: Sub-language Handling

    @patch("scribe_data.cli.total.get_datatype_list")
    @patch("scribe_data.cli.total.query_total_lexemes")
    def test_cli_total_wrapper_print_total_lexemes_with_sublanguages(
        self, mock_query_total_lexemes: MagicMock, mock_get_datatypes: MagicMock
    ) -> None:
        """
        Test printing totals for a language with sub-languages.
        """
        mock_get_datatypes.return_value = ["nouns", "verbs"]
        mock_query_total_lexemes.return_value = 100

        with patch("builtins.print") as mock_print:
            total_wrapper(languages=["Norwegian"], data_types=["nouns", "verbs"])

        # Verify header was printed.
        mock_print.assert_any_call(
            f"{'Language':<20} {'Data Type':<25} {'Total Wikidata Lexemes':<25}"
        )
        mock_print.assert_any_call("=" * 70)

        # Verify data was printed for each data type.
        mock_query_total_lexemes.assert_any_call(
            language="Norwegian", data_type="nouns", do_print=False
        )
        mock_query_total_lexemes.assert_any_call(
            language="Norwegian", data_type="verbs", do_print=False
        )

    # MARK: Data Type List Handling

    @patch("scribe_data.cli.total.language_metadata")
    @patch("scribe_data.cli.total.list_all_languages")
    @patch("scribe_data.utils.WIKIDATA_QUERIES_ALL_DATA_DIR")
    def test_cli_get_datatype_list_with_sublanguages(
        self,
        mock_dir: MagicMock,
        mock_list_languages: MagicMock,
        mock_metadata: MagicMock,
    ) -> None:
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
        def mock_path_handler(path: str) -> MagicMock:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path.iterdir.return_value = [mock_nouns, mock_verbs]
            return mock_path

        mock_dir.__truediv__.side_effect = mock_path_handler

        result = get_datatype_list("norwegian")  # note: lowercase
        self.assertEqual(sorted(result), ["nouns", "verbs"])

    @patch("scribe_data.cli.total.language_metadata")
    @patch("scribe_data.utils.WIKIDATA_QUERIES_ALL_DATA_DIR")
    def test_cli_get_datatype_list_empty_directory(
        self, mock_dir: MagicMock, mock_metadata: MagicMock
    ) -> None:
        """
        Test getting data type list from an empty directory.
        """
        # Mock language metadata.
        mock_metadata.get.return_value = {}

        mock_dir.__truediv__.return_value.exists.return_value = True
        mock_dir.__truediv__.return_value.iterdir.return_value = []

        with self.assertRaises(ValueError):
            get_datatype_list("English")

    @patch("scribe_data.cli.total.query_total_lexemes")
    def test_cli_total_wrapper_with_invalid_language(
        self, mock_query_total_lexemes: MagicMock
    ) -> None:
        """
        Test total wrapper with invalid language.
        """
        mock_query_total_lexemes.side_effect = ValueError("Invalid language")

        with self.assertRaises(ValueError):
            total_wrapper(languages=["invalid_lang"], data_types=["nouns"])

        mock_query_total_lexemes.assert_called_once()

    @patch("scribe_data.cli.total.query_total_lexemes")
    def test_cli_total_wrapper_with_invalid_data_type(
        self, mock_query_total_lexemes: MagicMock
    ) -> None:
        """
        Test total wrapper with invalid data type.
        """
        mock_query_total_lexemes.side_effect = ValueError("Invalid data type")

        with self.assertRaises(ValueError):
            total_wrapper(languages=["English"], data_types=["invalid_type"])

        mock_query_total_lexemes.assert_called_once()
