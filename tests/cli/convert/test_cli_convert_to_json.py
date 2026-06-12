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

from scribe_data.cli.convert.to_json import convert_to_json
from scribe_data.utils import DEFAULT_JSON_DIR

# MARK: JSON


class TestCLIConvertToJSON(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def _setup_fixtures(self, tmp_path):
        self.tmp_path = tmp_path

    @patch("pathlib.Path", autospec=True)
    def test_cli_convert_to_json_empty_language(self, mock_path: MagicMock) -> None:
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
                output_type="json",
                overwrite=True,
            )
        self.assertIn("Language '' is not recognized.", str(context.exception))

    @patch("pathlib.Path", autospec=True)
    def test_cli_convert_to_json_supported_file_extension_csv(
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
            output_type="json",
            overwrite=True,
        )

    @patch("pathlib.Path", autospec=True)
    def test_cli_convert_to_json_supported_file_extension_tsv(
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
            output_type="json",
            overwrite=True,
        )

    def test_cli_convert_to_json_unsupported_file_extension(self) -> None:
        input_file = self.tmp_path / "test.txt"
        input_file.write_text("Hello, world!", encoding="utf-8")

        with self.assertRaises(ValueError) as context:
            convert_to_json(
                language="English",
                data_types="nouns",
                input_file=input_file,
                output_type="json",
                overwrite=True,
            )

        self.assertIn("Unsupported file extension", str(context.exception))
        self.assertEqual(
            str(context.exception),
            f"Unsupported file extension '.txt' for {input_file}. Please provide a '.csv' or '.tsv' file.",
        )

    def test_cli_convert_to_json_standard_csv(self) -> None:
        csv_data = "key,value\na,1\nb,2"
        expected_json_output = {"a": "1", "b": "2"}

        input_file = self.tmp_path / "test.csv"
        input_file.write_text(csv_data, encoding="utf-8")

        convert_to_json(
            language="English",
            data_types="nouns",
            input_file=input_file,
            output_type="json",
            overwrite=True,
        )

        output_file = DEFAULT_JSON_DIR / "English" / "nouns.json"
        with open(output_file, "r", encoding="utf-8") as f:
            actual_content = json.load(f)

        assert actual_content == expected_json_output

    def test_cli_convert_to_json_with_multiple_keys(self) -> None:
        csv_data = "key,value1,value2\na,1,x\nb,2,y\nc,3,z"
        expected_json_output = {
            "a": {"value1": "1", "value2": "x"},
            "b": {"value1": "2", "value2": "y"},
            "c": {"value1": "3", "value2": "z"},
        }

        input_file = self.tmp_path / "test.csv"
        input_file.write_text(csv_data, encoding="utf-8")

        convert_to_json(
            language="English",
            data_types="nouns",
            input_file=input_file,
            output_type="json",
            overwrite=True,
        )

        output_file = DEFAULT_JSON_DIR / "English" / "nouns.json"
        with open(output_file, "r", encoding="utf-8") as f:
            actual_content = json.load(f)

        assert actual_content == expected_json_output

    def test_cli_convert_to_json_with_complex_structure(self) -> None:
        csv_data = "key,emoji,is_base,rank\na,😀,true,1\nb,😅,false,2"
        expected_json_output = {
            "a": [{"emoji": "😀", "is_base": True, "rank": 1}],
            "b": [{"emoji": "😅", "is_base": False, "rank": 2}],
        }

        input_file = self.tmp_path / "test.csv"
        input_file.write_text(csv_data, encoding="utf-8")

        convert_to_json(
            language="English",
            data_types="nouns",
            input_file=input_file,
            output_type="json",
            overwrite=True,
        )

        output_file = DEFAULT_JSON_DIR / "English" / "nouns.json"
        with open(output_file, "r", encoding="utf-8") as f:
            actual_content = json.load(f)

        assert actual_content == expected_json_output
