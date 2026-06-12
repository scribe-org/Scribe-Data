# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI convert functionality.
"""

import unittest

import pytest

from scribe_data.cli.convert.to_csv_or_tsv import convert_to_csv_or_tsv
from scribe_data.utils import DEFAULT_CSV_DIR, DEFAULT_TSV_DIR

# MARK: CSV or TSV


class TestCLIConvertToCSVorTSV(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def _setup_fixtures(self, tmp_path):
        self.tmp_path = tmp_path

    def test_cli_convert_to_csv_or_json_empty_language(self) -> None:
        json_data = '{"key1": "value1", "key2": "value2"}'

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")

        with self.assertRaises(ValueError) as context:
            convert_to_csv_or_tsv(
                language="",
                data_types="nouns",
                input_file=input_file,
                output_type="csv",
                overwrite=True,
            )

        self.assertEqual(str(context.exception), "Language '' is not recognized.")

    def test_cli_convert_to_csv_or_tsv_standard_dict_to_csv(self) -> None:
        json_data = '{"a": "1", "b": "2"}'
        expected_csv_output = "preposition,value\na,1\nb,2\n"

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")

        convert_to_csv_or_tsv(
            language="English",
            data_types="prepositions",
            input_file=input_file,
            output_type="csv",
            overwrite=True,
        )

        output_file = DEFAULT_CSV_DIR / "English" / "prepositions.csv"
        actual_content = output_file.read_text(encoding="utf-8")
        assert actual_content == expected_csv_output

    def test_cli_convert_to_csv_or_tsv_standard_dict_to_tsv(self) -> None:
        json_data = '{"a": "1", "b": "2"}'
        expected_tsv_output = "preposition\tvalue\na\t1\nb\t2\n"

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")

        convert_to_csv_or_tsv(
            language="English",
            data_types="prepositions",
            input_file=input_file,
            output_type="tsv",
            overwrite=True,
        )

        output_file = DEFAULT_TSV_DIR / "English" / "prepositions.tsv"
        actual_content = output_file.read_text(encoding="utf-8")
        assert actual_content == expected_tsv_output

    def test_cli_convert_to_csv_or_tsv_nested_dict_to_csv(self) -> None:
        json_data = (
            '{"a": {"value1": "1", "value2": "x"}, "b": {"value1": "2", "value2": "y"}}'
        )
        expected_csv_output = "noun,value1,value2\na,1,x\nb,2,y\n"

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")

        convert_to_csv_or_tsv(
            language="English",
            data_types="nouns",
            input_file=input_file,
            output_type="csv",
            overwrite=True,
        )

        output_file = DEFAULT_CSV_DIR / "English" / "nouns.csv"
        actual_content = output_file.read_text(encoding="utf-8")
        assert actual_content == expected_csv_output

    def test_cli_convert_to_csv_or_tsv_nested_dict_to_tsv(self) -> None:
        json_data = (
            '{"a": {"value1": "1", "value2": "x"}, "b": {"value1": "2", "value2": "y"}}'
        )
        expected_tsv_output = "noun\tvalue1\tvalue2\na\t1\tx\nb\t2\ty\n"

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")

        convert_to_csv_or_tsv(
            language="English",
            data_types="nouns",
            input_file=input_file,
            output_type="tsv",
            overwrite=True,
        )

        output_file = DEFAULT_TSV_DIR / "English" / "nouns.tsv"
        actual_content = output_file.read_text(encoding="utf-8")
        assert actual_content == expected_tsv_output

    def test_cli_convert_to_csv_or_tsv_list_of_dicts_to_csv(self) -> None:
        json_data = '{"a": [{"emoji": "😀", "is_base": true, "rank": 1}, {"emoji": "😅", "is_base": false, "rank": 2}]}'
        expected_csv_output = "word,emoji,is_base,rank\na,😀,True,1\na,😅,False,2\n"

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")

        convert_to_csv_or_tsv(
            language="English",
            data_types="emoji-keywords",
            input_file=input_file,
            output_type="csv",
            overwrite=True,
        )

        output_file = DEFAULT_CSV_DIR / "English" / "emoji-keywords.csv"
        actual_content = output_file.read_text(encoding="utf-8")
        assert actual_content == expected_csv_output

    def test_cli_convert_to_csv_or_tsv_list_of_dicts_to_tsv(self) -> None:
        json_data = '{"a": [{"emoji": "😀", "is_base": true, "rank": 1}, {"emoji": "😅", "is_base": false, "rank": 2}]}'
        expected_tsv_output = (
            "word\temoji\tis_base\trank\na\t😀\tTrue\t1\na\t😅\tFalse\t2\n"
        )

        input_file = self.tmp_path / "test.json"
        input_file.write_text(json_data, encoding="utf-8")

        convert_to_csv_or_tsv(
            language="English",
            data_types="emoji-keywords",
            input_file=input_file,
            output_type="tsv",
            overwrite=True,
        )

        output_file = DEFAULT_TSV_DIR / "English" / "emoji-keywords.tsv"
        actual_content = output_file.read_text(encoding="utf-8")
        assert actual_content == expected_tsv_output
