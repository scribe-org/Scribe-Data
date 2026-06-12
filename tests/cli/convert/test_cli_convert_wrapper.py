# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI convert functionality.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scribe_data.cli.convert.wrapper import convert_wrapper

# MARK: Wrapper


class TestCLIConvertWrapper(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def _setup_fixtures(self, tmp_path):
        self.tmp_path = tmp_path

    @patch("scribe_data.cli.convert.Path", autospec=True)
    @patch("scribe_data.cli.convert.to_sqlite.convert_to_sqlite", autospec=True)
    @patch("shutil.copy")
    def test_convert_to_sqlite(
        self,
        mock_shutil_copy: MagicMock,
        mock_convert_to_sqlite: MagicMock,
        mock_path: MagicMock,
    ) -> None:
        mock_path.return_value.exists.return_value = True

        convert_wrapper(
            languages=["english"],
            data_types=["nouns"],
            input_path=Path("file"),
            output_dir=Path("/output"),
            output_type="sqlite",
            overwrite=True,
            identifier_case="camel",
        )

        mock_convert_to_sqlite.assert_called_with(
            languages=["english"],
            specific_tables=["nouns"],
            identifier_case="camel",
            input_file=Path("file"),
            output_file=Path("/output"),
            overwrite=True,
        )

    @patch("scribe_data.cli.convert.Path", autospec=True)
    @patch("scribe_data.cli.convert.to_sqlite.convert_to_sqlite", autospec=True)
    def test_convert_to_sqlite_no_output_dir(
        self, mock_convert_to_sqlite: MagicMock, mock_path: MagicMock
    ) -> None:
        mock_input_file = MagicMock()
        mock_input_file.exists.return_value = True

        mock_path.return_value = mock_input_file

        mock_input_file.parent = MagicMock()
        mock_input_file.parent.__truediv__.return_value = MagicMock()
        mock_input_file.parent.__truediv__.return_value.exists.return_value = False

        convert_wrapper(
            languages=["english"],
            data_types=["nouns"],
            input_path=Path(mock_input_file),
            output_dir=None,
            output_type="sqlite",
            overwrite=True,
            identifier_case="camel",
        )

        mock_convert_to_sqlite.assert_called_with(
            languages=["english"],
            specific_tables=["nouns"],
            identifier_case="camel",
            input_file=Path(mock_input_file),
            output_file=Path("scribe_data_sqlite_export"),
            overwrite=True,
        )

    @patch("scribe_data.cli.convert.to_sqlite.convert_to_sqlite", autospec=True)
    def test_convert_wrapper_german_wiktionary_translations_sqlite(
        self, mock_convert_to_sqlite: MagicMock
    ) -> None:
        convert_wrapper(
            languages=["german"],
            data_types=["wiktionary_translations"],
            input_path=Path("/input"),
            output_dir=Path("/output"),
            output_type="sqlite",
            overwrite=False,
            identifier_case="camel",
        )

        mock_convert_to_sqlite.assert_called_once_with(
            languages=["german"],
            specific_tables=["wiktionary_translations"],
            identifier_case="camel",
            input_file=Path("/input"),
            output_file=Path("/output"),
            overwrite=False,
        )

    @patch(
        "scribe_data.cli.convert.DEFAULT_WIKTIONARY_JSON_EXPORT_DIR",
        new=Path("/mock_wiktionary_dir"),
    )
    @patch("scribe_data.cli.convert.to_sqlite.convert_to_sqlite", autospec=True)
    def test_convert_wrapper_wiktionary_no_input_path_uses_wiktionary_default(
        self, mock_convert_to_sqlite: MagicMock
    ) -> None:
        convert_wrapper(
            languages=["german"],
            data_types=["wiktionary_translations"],
            input_path=None,
            output_dir=Path("/output"),
            output_type="sqlite",
            overwrite=False,
        )

        mock_convert_to_sqlite.assert_called_once_with(
            languages=["german"],
            specific_tables=["wiktionary_translations"],
            identifier_case="camel",
            input_file=Path("/mock_wiktionary_dir"),
            output_file=Path("/output"),
            overwrite=False,
        )

    def test_convert(self) -> None:
        with self.assertRaises(ValueError) as context:
            convert_wrapper(
                languages=["English"],
                data_types=["nouns"],
                input_path=Path("Data/ecode.csv"),
                output_dir=Path("/output_dir"),
                output_type="parquet",
                overwrite=True,
            )

        self.assertEqual(
            str(context.exception),
            "Unsupported output type 'parquet'. Must be 'json', 'csv', 'tsv' or 'sqlite'.",
        )
