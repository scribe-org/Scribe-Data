# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI get functionality.
"""

import json
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from SPARQLWrapper.SPARQLExceptions import EndPointInternalError

from scribe_data.cli.get import get_data
from scribe_data.utils import (
    DEFAULT_CSV_EXPORT_DIR,
    DEFAULT_JSON_EXPORT_DIR,
    DEFAULT_SQLITE_EXPORT_DIR,
    DEFAULT_TSV_EXPORT_DIR,
    DEFAULT_WIKTIONARY_JSON_EXPORT_DIR,
)


class TestGetData(unittest.TestCase):
    """
    Unit tests for the get_data function.

    These tests ensure the correct behavior of the get_data function.
    """

    # MARK: Subprocess Patching

    @patch("scribe_data.cli.get.generate_emoji")
    def test_cli_get_emoji_keywords(self, generate_emoji: MagicMock) -> None:
        """
        Test the generation of emoji keywords.

        This test ensures that when thee `data_type` is `emoji_keywords`, the `generate_emoji` function is called with the correct arguments.
        """
        get_data(
            languages=["English"],
            data_types=["emoji_keywords"],
            output_dir=Path("./test_output"),
        )
        generate_emoji.assert_called_once_with(
            language="English",
            output_dir=Path("./test_output"),
        )

    # MARK: Invalid Arguments

    def test_invalid_arguments(self) -> None:
        """
        Test the behavior of the get_data function when invalid arguments are provided.
        """
        with self.assertRaises(ValueError):
            get_data()

    # MARK: All Data

    @patch("scribe_data.cli.get.query_data")
    @patch("scribe_data.cli.get.parse_wd_lexeme_dump")
    @patch("scribe_data.cli.get.questionary.confirm")
    def test_cli_get_all_data_types_for_language_user_says_no(
        self,
        mock_questionary_confirm: MagicMock,
        mock_parse: MagicMock,
        mock_query_data: MagicMock,
    ) -> None:
        """
        Test the behavior when the user agrees to use Wikidata lexeme dumps.

        This test checks that `parse_wd_lexeme_dump` is called with the correct parameters
        when the user confirms they don't want to query Wikidata.
        """
        mock_questionary_confirm.return_value.ask.return_value = False

        get_data(all_bool=True, languages=["English"])

        mock_parse.assert_called_once_with(
            languages=["English"],
            data_types=["all"],
            wikidata_dump_type=["form"],
            output_dir=DEFAULT_JSON_EXPORT_DIR,
            wikidata_dump_path=None,  # explicitly set to None
            overwrite_all=False,
        )
        mock_query_data.assert_not_called()

    @patch("scribe_data.cli.get.parse_wd_lexeme_dump")
    def test_cli_get_all_languages_and_data_types(self, mock_parse: MagicMock) -> None:
        """
        Test retrieving all languages for a specific data type.

        Ensures that `query_data` is called properly when `--all` flag is used with a data type.
        """
        get_data(all_bool=True)

        mock_parse.assert_called_once_with(
            languages=["all"],
            data_types=["all"],
            wikidata_dump_type=["form", "translations"],
            output_dir=DEFAULT_JSON_EXPORT_DIR,
            wikidata_dump_path=None,
            overwrite_all=False,
        )

    # MARK: Language and Data Type

    @patch("scribe_data.cli.get.query_data")
    def test_cli_get_specific_language_and_data_type(
        self, mock_query_data: MagicMock
    ) -> None:
        """
        Test retrieving a specific language and data type.

        Ensures that `query_data` is called properly when a specific language and data type are provided.
        """
        get_data(
            languages=["german"], data_types=["nouns"], output_dir=Path("./test_output")
        )
        mock_query_data.assert_called_once_with(
            languages=["german"],
            data_types=["nouns"],
            output_dir=Path("./test_output"),
            overwrite=False,
            interactive=False,
        )

    # MARK: Capitalized Language

    @patch("scribe_data.cli.get.query_data")
    @patch("scribe_data.cli.get.Path.glob", return_value=[])
    @patch("scribe_data.cli.get.check_index_exists")
    def test_cli_get_data_with_capitalized_language(
        self,
        mock_check_index: MagicMock,
        mock_glob: MagicMock,
        mock_query_data: MagicMock,
    ) -> None:
        """
        Test retrieving data with a capitalized language.

        Ensures that `query_data` is called properly when a capitalized language is provided.
        """
        mock_check_index.return_value = False
        get_data(languages=["German"], data_types=["nouns"])
        mock_query_data.assert_called_once_with(
            languages=["German"],
            data_types=["nouns"],
            output_dir=DEFAULT_JSON_EXPORT_DIR,
            overwrite=False,
            interactive=False,
        )

    # MARK: Lowercase Language

    @patch("scribe_data.cli.get.query_data")
    @patch("scribe_data.cli.get.Path.glob", return_value=[])
    @patch("scribe_data.cli.get.check_index_exists", return_value=False)
    def test_cli_get_data_with_lowercase_language(
        self,
        mock_check_index: MagicMock,
        mock_glob: MagicMock,
        mock_query_data: MagicMock,
    ) -> None:
        """
        Test retrieving data with a lowercase language.

        Ensures that `query_data` is called properly when a lowercase language is provided.
        """
        get_data(languages=["german"], data_types=["nouns"])
        mock_query_data.assert_called_once_with(
            languages=["german"],
            data_types=["nouns"],
            output_dir=DEFAULT_JSON_EXPORT_DIR,
            overwrite=False,
            interactive=False,
        )

    # MARK: Output Directory

    @patch("scribe_data.cli.get.query_data")
    def test_cli_get_data_with_different_output_directory(
        self, mock_query_data: MagicMock
    ) -> None:
        """
        Test retrieving data with a different output directory.

        Ensures that `query_data` is called properly when a different output directory is provided.
        """
        get_data(
            languages=["german"],
            data_types=["nouns"],
            output_dir=Path("./custom_output_test"),
        )
        mock_query_data.assert_called_once_with(
            languages=["german"],
            data_types=["nouns"],
            output_dir=Path("./custom_output_test"),
            overwrite=False,
            interactive=False,
        )

    # MARK: Overwrite is True

    @patch("scribe_data.cli.get.query_data")
    @patch("scribe_data.cli.get.Path.glob", return_value=[])
    def test_cli_get_data_with_overwrite_true(
        self, mock_glob: MagicMock, mock_query_data: MagicMock
    ) -> None:
        """
        Test retrieving data with the overwrite flag set to True.

        Ensures that `query_data` is called properly when the overwrite flag is set to True.
        """
        get_data(languages=["English"], data_types=["verbs"], overwrite=True)
        mock_query_data.assert_called_once_with(
            languages=["English"],
            data_types=["verbs"],
            output_dir=DEFAULT_JSON_EXPORT_DIR,
            overwrite=True,
            interactive=False,
        )

    # MARK: Overwrite is False

    @patch("scribe_data.cli.get.query_data")
    def test_cli_get_data_with_overwrite_false(
        self, mock_query_data: MagicMock
    ) -> None:
        get_data(
            languages=["English"],
            data_types=["verbs"],
            overwrite=False,
            output_dir=Path("./custom_output_test"),
            interactive=False,
        )
        mock_query_data.assert_called_once_with(
            languages=["English"],
            data_types=["verbs"],
            output_dir=Path("./custom_output_test"),
            overwrite=False,
            interactive=False,
        )

    # MARK: User Chooses Skip

    @patch("scribe_data.cli.get.query_data")
    @patch(
        "scribe_data.cli.get.Path.glob",
        return_value=[Path("./test_output/English/nouns.json")],
    )
    @patch("scribe_data.cli.get.questionary.confirm")
    @patch("scribe_data.cli.get.check_index_exists")
    def test_user_skips_existing_file(
        self,
        mock_check_index: MagicMock,
        mock_questionary_confirm: MagicMock,
        mock_glob: MagicMock,
        mock_query_data: MagicMock,
    ) -> None:
        """
        Test the behavior when the user chooses to skip an existing file.

        Ensures that the file is not overwritten and the function returns the correct result.
        """
        mock_questionary_confirm.return_value.ask.return_value = False
        mock_check_index.return_value = True

        result = get_data(
            languages=["English"],
            data_types=["nouns"],
            output_dir=Path("./test_output"),
        )

        # Validate the skip result.
        self.assertEqual(result, {"success": False, "skipped": True})
        mock_query_data.assert_not_called()

    # MARK: User Chooses Overwrite

    @patch("scribe_data.cli.get.query_data")
    @patch(
        "scribe_data.cli.get.Path.glob",
        return_value=[Path("./test_output/English/nouns.json")],
    )
    @patch("scribe_data.cli.get.questionary.confirm")
    def test_user_overwrites_existing_file(
        self,
        mock_questionary_confirm: MagicMock,
        mock_glob: MagicMock,
        mock_query_data: MagicMock,
    ) -> None:
        """
        Test the behavior when the user chooses to overwrite an existing file.

        Ensures that the file is overwritten and the function returns the correct result.
        """
        mock_questionary_confirm.return_value.ask.return_value = True
        get_data(
            languages=["English"],
            data_types=["nouns"],
            output_dir=Path("./test_output"),
        )
        mock_query_data.assert_called_once_with(
            languages=["English"],
            data_types=["nouns"],
            output_dir=Path("./test_output"),
            overwrite=False,
            interactive=False,
        )

    # MARK: Translations

    @patch("scribe_data.wiktionary.parse_translations.parse_wiktionary_translations")
    def test_cli_get_translations_no_language_specified(self, mock_parse):
        get_data(data_types=["translations"])
        mock_parse.assert_called_once_with(
            target_languages=None,
            wiktionary_dump_path=None,
            output_dir=DEFAULT_WIKTIONARY_JSON_EXPORT_DIR,
            overwrite=False,
        )

    @patch("scribe_data.wiktionary.parse_translations.parse_wiktionary_translations")
    def test_cli_get_translations_with_specific_language(self, mock_parse):
        get_data(
            languages=["Spanish"],
            data_types=["translations"],
            output_dir=Path("./test_output"),
        )
        mock_parse.assert_called_once_with(
            target_languages=["Spanish"],
            wiktionary_dump_path=None,
            output_dir=Path("./test_output"),
            overwrite=False,
        )

    @patch("scribe_data.wiktionary.parse_translations.parse_wiktionary_translations")
    def test_cli_get_translations_with_dump(self, mock_parse):
        get_data(
            languages=["German"],
            data_types=["translations"],
            wiktionary_dump=Path("./wikidump.json"),
        )
        mock_parse.assert_called_once_with(
            target_languages=["German"],
            wiktionary_dump_path=Path("./wikidump.json"),
            output_dir=DEFAULT_WIKTIONARY_JSON_EXPORT_DIR,
            overwrite=False,
        )

    # MARK: Use QID as language

    @patch("scribe_data.cli.get.parse_wd_lexeme_dump")
    @patch("scribe_data.cli.get.questionary.confirm")
    def test_cli_get_data_with_wikidata_identifier(
        self, mock_questionary_confirm: MagicMock, mock_parse: MagicMock
    ) -> None:
        """
        Test retrieving data with a Wikidata identifier as language.

        Ensures that `parse_wd_lexeme_dump` is called with the correct parameters
        when a Wikidata identifier is used.
        """
        # Mock the user confirmation to return True (query Wikidata directly).
        mock_questionary_confirm.return_value.ask.return_value = False

        get_data(
            languages=["Q9217"],
            output_dir=Path("exported_json"),
            wikidata_dump_path=Path("scribe"),
            all_bool=True,
        )
        mock_parse.assert_called_once_with(
            languages=["Q9217"],
            data_types=["all"],
            wikidata_dump_type=["form"],
            output_dir=Path("exported_json"),
            wikidata_dump_path=Path("scribe"),
            overwrite_all=False,
        )

    @patch("scribe_data.cli.get.parse_wd_lexeme_dump")
    def test_cli_get_data_with_wikidata_identifier_and_data_type(
        self, mock_parse: MagicMock
    ) -> None:
        """
        Test retrieving a specific data type with a Wikidata identifier.

        Ensures that `parse_wd_lexeme_dump` is called with the correct parameters
        when a Wikidata identifier and specific data type are used.
        """
        get_data(
            languages=["Q9217"],
            data_types=["nouns"],
            output_dir=Path("exported_json"),
            wikidata_dump_path=Path("scribe"),
        )
        mock_parse.assert_called_once_with(
            languages=["Q9217"],
            wikidata_dump_type=["form"],
            data_types=["nouns"],
            output_dir=Path("exported_json"),
            wikidata_dump_path=Path("scribe"),
            overwrite_all=False,
        )

    # MARK: All Languages for Data Type
    @patch("scribe_data.cli.get.parse_wd_lexeme_dump")
    @patch("scribe_data.cli.get.questionary.confirm")
    def test_cli_get_all_languages_for_data_type_user_says_no(
        self, mock_questionary_confirm: MagicMock, mock_parse: MagicMock
    ) -> None:
        """
        Test retrieving all languages for a specific data type when user chooses to use lexeme dump.

        This tests the behavior when using --all (-a) with --data-type (-dt) and the user
        chooses not to query Wikidata directly.
        """
        # Mock user choosing to use lexeme dump instead of querying Wikidata.
        mock_questionary_confirm.return_value.ask.return_value = False

        get_data(all_bool=True, data_types=["verbs"], output_dir=Path("test"))
        mock_parse.assert_called_once_with(
            languages=["all"],
            data_types=["verbs"],
            wikidata_dump_type=["form"],
            output_dir=Path("test"),
            wikidata_dump_path=None,
            overwrite_all=False,
        )

    @patch("scribe_data.cli.get.query_data")
    @patch("scribe_data.cli.get.questionary.confirm")
    def test_cli_get_all_languages_for_data_type_user_says_yes(
        self, mock_questionary_confirm: MagicMock, mock_query_data: MagicMock
    ) -> None:
        """
        Test retrieving all languages for a specific data type when user chooses to query Wikidata.

        This tests the behavior when using --all (-a) with --data-type (-dt) and the user
        chooses to query Wikidata directly.
        """
        # Mock user choosing to query Wikidata directly.
        mock_questionary_confirm.return_value.ask.return_value = True

        get_data(all_bool=True, data_types=["verbs"], output_dir=Path("test"))
        mock_query_data.assert_called_once_with(
            languages=["all"],
            data_types=["verbs"],
            output_dir=Path("test"),
            overwrite=False,
        )

    # MARK: Error Handling

    @patch("scribe_data.cli.get.query_data")
    @patch("scribe_data.cli.get.check_index_exists")
    def test_json_decode_error_handling(
        self, mock_check_index: MagicMock, mock_query_data: MagicMock
    ) -> None:
        """
        Test handling of JSONDecodeError when querying data.
        """
        mock_check_index.return_value = False
        mock_query_data.side_effect = json.decoder.JSONDecodeError("Msg", "Doc", 0)

        get_data(languages=["German"], data_types=["verbs"])

    @patch("scribe_data.cli.get.query_data")
    @patch("scribe_data.cli.get.check_index_exists")
    def test_http_error_handling(
        self, mock_check_index: MagicMock, mock_query_data: MagicMock
    ) -> None:
        """
        Test handling of HTTPError when querying data.
        """
        mock_check_index.return_value = False
        mock_query_data.side_effect = urllib.error.HTTPError(
            url="test", code=500, msg="error", hdrs={}, fp=None
        )

        get_data(languages=["German"], data_types=["verbs"])

    @patch("scribe_data.cli.get.query_data")
    @patch("scribe_data.cli.get.check_index_exists")
    def test_endpoint_error_handling(
        self, mock_check_index: MagicMock, mock_query_data: MagicMock
    ) -> None:
        """
        Test handling of EndPointInternalError when querying data.
        """
        mock_check_index.return_value = False
        mock_query_data.side_effect = EndPointInternalError

        get_data(languages=["German"], data_types=["verbs"])

    # MARK: Output Type Handling

    @patch("scribe_data.cli.get.query_data")
    @patch("scribe_data.cli.get.convert_wrapper")
    @patch("scribe_data.cli.get.Path.exists")
    @patch("scribe_data.cli.get.os.remove")
    @patch("scribe_data.cli.get.check_index_exists")
    def test_output_type_conversion(
        self,
        mock_check_index: MagicMock,
        mock_remove: MagicMock,
        mock_exists: MagicMock,
        mock_convert: MagicMock,
        mock_query_data: MagicMock,
    ) -> None:
        """
        Test conversion of output to different file types.
        """
        mock_exists.return_value = True
        mock_check_index.return_value = False

        get_data(
            languages=["German"],
            data_types=["verbs"],
            output_type="csv",
            output_dir=Path("test_dir"),
            identifier_case="snake",
        )

        # Use Path to create platform-appropriate path.
        expected_input_file = Path("test_dir/German/verbs.json")

        mock_convert.assert_called_once_with(
            languages=["German"],
            data_types=["verbs"],
            input_path=expected_input_file,
            output_dir=Path("test_dir"),
            output_type="csv",
            overwrite=False,
            identifier_case="snake",
        )
        mock_remove.assert_called_once()

    # MARK: Default Output Directory

    @patch("scribe_data.cli.get.check_index_exists")
    def test_default_output_directory_selection(
        self, mock_check_index: MagicMock
    ) -> None:
        """
        Test that correct default output directory is selected based on output type.
        """
        mock_check_index.return_value = False
        test_cases = [
            ("csv", DEFAULT_CSV_EXPORT_DIR),
            ("json", DEFAULT_JSON_EXPORT_DIR),
            ("sqlite", DEFAULT_SQLITE_EXPORT_DIR),
            ("tsv", DEFAULT_TSV_EXPORT_DIR),
        ]

        for output_type, expected_dir in test_cases:
            with patch("scribe_data.cli.get.query_data") as mock_query:
                get_data(
                    languages=["German"], data_types=["verbs"], output_type=output_type
                )
                mock_query.assert_called_with(
                    languages=["German"],
                    data_types=["verbs"],
                    output_dir=expected_dir,
                    overwrite=False,
                    interactive=False,
                )

    @patch("scribe_data.cli.get.query_data")
    @patch("scribe_data.cli.get.check_index_exists")
    def test_cli_get_data_with_interactive_mode(
        self, mock_check_exists: MagicMock, mock_query_data: MagicMock
    ) -> None:
        """
        Test retrieving data in interactive mode.
        """
        mock_check_exists.return_value = False

        get_data(languages=["English"], data_types=["nouns"], interactive=True)
        mock_query_data.assert_called_once_with(
            languages=["English"],
            data_types=["nouns"],
            output_dir=DEFAULT_JSON_EXPORT_DIR,
            overwrite=False,
            interactive=True,
        )

    @patch("scribe_data.cli.get.parse_wd_lexeme_dump")
    def test_cli_get_data_with_custom_dump_path(self, mock_parse: MagicMock) -> None:
        """
        Test retrieving data with a custom Wikidata dump path.
        """
        custom_path = Path("./custom/dump/path.json")
        get_data(
            languages=["English"], data_types=["nouns"], wikidata_dump_path=custom_path
        )
        mock_parse.assert_called_once_with(
            languages=["English"],
            wikidata_dump_type=["form"],
            data_types=["nouns"],
            output_dir=DEFAULT_JSON_EXPORT_DIR,
            wikidata_dump_path=custom_path,
            overwrite_all=False,
        )

    @patch("scribe_data.cli.get.query_data")
    def test_cli_get_data_with_multiple_languages(
        self, mock_query_data: MagicMock
    ) -> None:
        """
        Test retrieving data for multiple languages.
        """
        # Mock the query_data response.
        mock_query_data.return_value = True

        # Test with a single string containing multiple languages.
        get_data(
            languages=["English Spanish"],  # Space-separated languages
            data_types=["nouns"],
        )

        # Verify query_data was called with first language only (per get.py implementation).
        mock_query_data.assert_called_once_with(
            languages=["English"],  # only first language is used
            data_types=["nouns"],
            output_dir=DEFAULT_JSON_EXPORT_DIR,
            overwrite=False,
            interactive=False,
        )

    @patch("scribe_data.cli.get.query_data")
    def test_error_handling_value_error(self, mock_query_data: MagicMock) -> None:
        """
        Test handling of ValueError during data retrieval.
        """
        mock_query_data.side_effect = ValueError("Invalid parameter")

        with pytest.raises(ValueError):
            get_data(languages=["Invalid"], data_types=["nouns"])

    @patch("scribe_data.cli.get.parse_wd_lexeme_dump")
    @patch("scribe_data.cli.get.questionary.confirm")
    def test_cli_get_data_with_all_and_specific_type(
        self, mock_questionary: MagicMock, mock_parse: MagicMock
    ) -> None:
        """
        Test retrieving all languages for a specific data type.
        """
        mock_questionary.return_value.ask.return_value = False

        get_data(all_bool=True, data_types=["nouns"])
        mock_parse.assert_called_once_with(
            languages=["all"],
            wikidata_dump_type=["form"],
            data_types=["nouns"],
            output_dir=DEFAULT_JSON_EXPORT_DIR,
            wikidata_dump_path=None,
            overwrite_all=False,
        )

    @patch("scribe_data.cli.get.query_data")
    @patch("scribe_data.cli.get.check_index_exists")
    def test_cli_get_data_case_insensitive_type(
        self, mock_check_exists: MagicMock, mock_query_data: MagicMock
    ) -> None:
        """
        Test that data type is case insensitive.
        """
        mock_check_exists.return_value = False

        get_data(languages=["English"], data_types=["NOUNS"])
        mock_query_data.assert_called_once_with(
            languages=["English"],
            data_types=["NOUNS"],
            output_dir=DEFAULT_JSON_EXPORT_DIR,
            overwrite=False,
            interactive=False,
        )
