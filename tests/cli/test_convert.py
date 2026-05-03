# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI convert functionality.
"""

import json
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scribe_data.cli.convert import (
    convert_to_csv_or_tsv,
    convert_to_json,
    convert_wrapper,
)


class TestConvert(unittest.TestCase):
    # MARK: Helper Functions

    def normalize_line_endings(self, data: str) -> str:
        """
        Normalize line endings in a given string.


        Parameters
        ----------
        data: str
            The input string whose line endings are to be normalized.

        Returns
        ---------
        data: str
            The input string with normalized line endings.
        """
        return data.replace("\r\n", "\n").replace("\r", "\n")

    @pytest.fixture(autouse=True)
    def _setup_fixtures(self, tmp_path):
        self.tmp_path = tmp_path

    # MARK: JSON

    @patch("scribe_data.cli.convert.Path", autospec=True)
    def test_convert_to_json_empty_language(self, mock_path: MagicMock) -> None:
        csv_data = "key,value\na,1\nb,2"
        mock_file = StringIO(csv_data)

        mock_path_obj = MagicMock(spec=Path)
        mock_path.return_value = mock_path_obj
        mock_path_obj.suffix = ".csv"
        mock_path_obj.exists.return_value = True
        mock_path_obj.open.return_value.__enter__.return_value = mock_file

        with self.assertRaises(ValueError) as context:
            convert_to_json(
                language="",
                data_types="nouns",
                input_file=Path("input.csv"),
                output_dir=Path("/output_dir"),
                output_type="json",
                overwrite=True,
            )
        self.assertIn("Language '' is not recognized.", str(context.exception))

    @patch("scribe_data.cli.convert.Path", autospec=True)
    def test_convert_to_json_supported_file_extension_csv(
        self, mock_path_class: MagicMock
    ) -> None:
        mock_path_instance = MagicMock(spec=Path)

        mock_path_class.return_value = mock_path_instance

        mock_path_instance.suffix = ".csv"
        mock_path_instance.exists.return_value = True

        convert_to_json(
            language="English",
            data_types="nouns",
            input_file=Path("test.csv"),
            output_dir=Path("/output_dir"),
            output_type="json",
            overwrite=True,
        )

    @patch("scribe_data.cli.convert.Path", autospec=True)
    def test_convert_to_json_supported_file_extension_tsv(
        self, mock_path_class: MagicMock
    ) -> None:
        mock_path_instance = MagicMock(spec=Path)

        mock_path_class.return_value = mock_path_instance

        mock_path_instance.suffix = ".tsv"
        mock_path_instance.exists.return_value = True

        convert_to_json(
            language="English",
            data_types="nouns",
            input_file=Path("test.tsv"),
            output_dir=Path("/output_dir"),
            output_type="json",
            overwrite=True,
        )

    def test_convert_to_json_unsupported_file_extension(self) -> None:
        input_file = self.tmp_path / "test.txt"
        input_file.write_text("Hello, world!", encoding="utf-8")
        output_dir = self.tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        with self.assertRaises(ValueError) as context:
            convert_to_json(
                language="English",
                data_types="nouns",
                input_file=input_file,
                output_dir=output_dir,
                output_type="json",
                overwrite=True,
            )

        self.assertIn("Unsupported file extension", str(context.exception))
        self.assertEqual(
            str(context.exception),
            f"Unsupported file extension '.txt' for {input_file}. Please provide a '.csv' or '.tsv' file.",
        )

    # MARK: JSON

    def test_convert_to_json_standard_csv(self) -> None:
        csv_data = "key,value\na,1\nb,2"
        expected_json_output = {"a": "1", "b": "2"}

        input_file = self.tmp_path / "test.csv"
        input_file.write_text(csv_data, encoding="utf-8")
        output_dir = self.tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        convert_to_json(
            language="English",
            data_types="nouns",
            input_file=input_file,
            output_dir=output_dir,
            output_type="json",
            overwrite=True,
        )

        output_file = output_dir / "English" / "nouns.json"
        with open(output_file, "r", encoding="utf-8") as f:
            actual_content = json.load(f)

        assert actual_content == expected_json_output

    def test_convert_to_json_with_multiple_keys(self) -> None:
        csv_data = "key,value1,value2\na,1,x\nb,2,y\nc,3,z"
        expected_json_output = {
            "a": {"value1": "1", "value2": "x"},
            "b": {"value1": "2", "value2": "y"},
            "c": {"value1": "3", "value2": "z"},
        }

        input_file = self.tmp_path / "test.csv"
        input_file.write_text(csv_data, encoding="utf-8")
        output_dir = self.tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        convert_to_json(
            language="English",
            data_types="nouns",
            input_file=input_file,
            output_dir=output_dir,
            output_type="json",
            overwrite=True,
        )

        output_file = output_dir / "English" / "nouns.json"
        with open(output_file, "r", encoding="utf-8") as f:
            actual_content = json.load(f)

        assert actual_content == expected_json_output

    def test_convert_to_json_with_complex_structure(self) -> None:
        csv_data = "key,emoji,is_base,rank\na,😀,true,1\nb,😅,false,2"
        expected_json_output = {
            "a": [{"emoji": "😀", "is_base": True, "rank": 1}],
            "b": [{"emoji": "😅", "is_base": False, "rank": 2}],
        }

        input_file = self.tmp_path / "test.csv"
        input_file.write_text(csv_data, encoding="utf-8")
        output_dir = self.tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        convert_to_json(
            language="English",
            data_types="nouns",
            input_file=input_file,
            output_dir=output_dir,
            output_type="json",
            overwrite=True,
        )

        output_file = output_dir / "English" / "nouns.json"
        with open(output_file, "r", encoding="utf-8") as f:
            actual_content = json.load(f)

        assert actual_content == expected_json_output

    # MARK: CSV or TSV

    def test_convert_to_csv_or_json_empty_language(self) -> None:
        json_data = '{"key1": "value1", "key2": "value2"}'

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")
        output_dir = self.tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        with self.assertRaises(ValueError) as context:
            convert_to_csv_or_tsv(
                language="",
                data_types="nouns",
                input_file=input_file,
                output_dir=output_dir,
                output_type="csv",
                overwrite=True,
            )

        self.assertEqual(str(context.exception), "Language '' is not recognized.")

    def test_convert_to_csv_or_tsv_standard_dict_to_csv(self) -> None:
        json_data = '{"a": "1", "b": "2"}'
        expected_csv_output = "preposition,value\na,1\nb,2\n"

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")
        output_dir = self.tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        convert_to_csv_or_tsv(
            language="English",
            data_types="prepositions",
            input_file=input_file,
            output_dir=output_dir,
            output_type="csv",
            overwrite=True,
        )

        output_file = output_dir / "English" / "prepositions.csv"
        actual_content = output_file.read_text(encoding="utf-8")
        assert actual_content == expected_csv_output

    def test_convert_to_csv_or_tsv_standard_dict_to_tsv(self) -> None:
        json_data = '{"a": "1", "b": "2"}'
        expected_tsv_output = "preposition\tvalue\na\t1\nb\t2\n"

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")
        output_dir = self.tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        convert_to_csv_or_tsv(
            language="English",
            data_types="prepositions",
            input_file=input_file,
            output_dir=output_dir,
            output_type="tsv",
            overwrite=True,
        )

        output_file = output_dir / "English" / "prepositions.tsv"
        actual_content = output_file.read_text(encoding="utf-8")
        assert actual_content == expected_tsv_output

    def test_convert_to_csv_or_tsv_nested_dict_to_csv(self) -> None:
        json_data = (
            '{"a": {"value1": "1", "value2": "x"}, "b": {"value1": "2", "value2": "y"}}'
        )
        expected_csv_output = "noun,value1,value2\na,1,x\nb,2,y\n"

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")
        output_dir = self.tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        convert_to_csv_or_tsv(
            language="English",
            data_types="nouns",
            input_file=input_file,
            output_dir=output_dir,
            output_type="csv",
            overwrite=True,
        )

        output_file = output_dir / "English" / "nouns.csv"
        actual_content = output_file.read_text(encoding="utf-8")
        assert actual_content == expected_csv_output

    def test_convert_to_csv_or_tsv_nested_dict_to_tsv(self) -> None:
        json_data = (
            '{"a": {"value1": "1", "value2": "x"}, "b": {"value1": "2", "value2": "y"}}'
        )
        expected_tsv_output = "noun\tvalue1\tvalue2\na\t1\tx\nb\t2\ty\n"

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")
        output_dir = self.tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        convert_to_csv_or_tsv(
            language="English",
            data_types="nouns",
            input_file=input_file,
            output_dir=output_dir,
            output_type="tsv",
            overwrite=True,
        )

        output_file = output_dir / "English" / "nouns.tsv"
        actual_content = output_file.read_text(encoding="utf-8")
        assert actual_content == expected_tsv_output

    def test_convert_to_csv_or_tsv_list_of_dicts_to_csv(self) -> None:
        json_data = '{"a": [{"emoji": "😀", "is_base": true, "rank": 1}, {"emoji": "😅", "is_base": false, "rank": 2}]}'
        expected_csv_output = "word,emoji,is_base,rank\na,😀,True,1\na,😅,False,2\n"

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")
        output_dir = self.tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        convert_to_csv_or_tsv(
            language="English",
            data_types="emoji-keywords",
            input_file=input_file,
            output_dir=output_dir,
            output_type="csv",
            overwrite=True,
        )

        output_file = output_dir / "English" / "emoji-keywords.csv"
        actual_content = output_file.read_text(encoding="utf-8")
        assert actual_content == expected_csv_output

    def test_convert_to_csv_or_tsv_list_of_dicts_to_tsv(self) -> None:
        json_data = '{"a": [{"emoji": "😀", "is_base": true, "rank": 1}, {"emoji": "😅", "is_base": false, "rank": 2}]}'
        expected_tsv_output = (
            "word\temoji\tis_base\trank\na\t😀\tTrue\t1\na\t😅\tFalse\t2\n"
        )

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")
        output_dir = self.tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        convert_to_csv_or_tsv(
            language="English",
            data_types="emoji-keywords",
            input_file=input_file,
            output_dir=output_dir,
            output_type="tsv",
            overwrite=True,
        )

        output_file = output_dir / "English" / "emoji-keywords.tsv"
        actual_content = output_file.read_text(encoding="utf-8")
        assert actual_content == expected_tsv_output

    # MARK: SQLITE

    @patch("scribe_data.cli.convert.Path", autospec=True)
    @patch("scribe_data.cli.convert.data_to_sqlite", autospec=True)
    @patch("shutil.copy")
    def test_convert_to_sqlite(
        self,
        mock_shutil_copy: MagicMock,
        mock_data_to_sqlite: MagicMock,
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

        mock_data_to_sqlite.assert_called_with(
            languages=["english"],
            specific_tables=["nouns"],
            identifier_case="camel",
            input_file=Path("file"),
            output_file=Path("/output"),
            overwrite=True,
        )

    @patch("scribe_data.cli.convert.Path", autospec=True)
    @patch("scribe_data.cli.convert.data_to_sqlite", autospec=True)
    def test_convert_to_sqlite_no_output_dir(
        self, mock_data_to_sqlite: MagicMock, mock_path: MagicMock
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

        mock_data_to_sqlite.assert_called_with(
            languages=["english"],
            specific_tables=["nouns"],
            identifier_case="camel",
            input_file=Path(mock_input_file),
            output_file=None,
            overwrite=True,
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
