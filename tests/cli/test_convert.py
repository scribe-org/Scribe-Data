"""
Tests for the CLI convert functionality.

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
from pathlib import Path
from scribe_data.cli.convert import export_json, convert_to_sqlite


class TestConvert(unittest.TestCase):
    @patch("scribe_data.cli.convert.Path")
    @patch("scribe_data.cli.convert.data_to_sqlite")
    @patch("shutil.copy")
    def test_convert_to_sqlite(self, mock_shutil_copy, mock_data_to_sqlite, mock_path):
        mock_path.return_value.exists.return_value = True

        convert_to_sqlite("english", "nouns", "/output", True)

        mock_data_to_sqlite.assert_called_with(["english"], ["nouns"])
        mock_shutil_copy.assert_called()

    @patch("scribe_data.cli.convert.Path")
    @patch("scribe_data.cli.convert.data_to_sqlite")
    def test_convert_to_sqlite_no_output_dir(self, mock_data_to_sqlite, mock_path):
        convert_to_sqlite("english", "nouns", None, True)

        mock_data_to_sqlite.assert_called_with(["english"], ["nouns"])
        mock_path.assert_not_called()

    @patch("scribe_data.cli.convert.Path")
    @patch("scribe_data.cli.convert.data_to_sqlite")
    @patch("scribe_data.cli.convert.get_language_iso")
    @patch("shutil.copy")
    def test_convert_to_sqlite_with_language_iso(
        self, mock_copy, mock_get_language_iso, mock_data_to_sqlite, mock_path
    ):
        mock_get_language_iso.return_value = "en"
        mock_path.return_value.exists.return_value = True

        convert_to_sqlite("English", "data_type", "/output", True)

        mock_data_to_sqlite.assert_called_with(["English"], ["data_type"])
        mock_copy.assert_called()

    @patch("scribe_data.cli.convert.language_map")
    def test_export_json_invalid_language(self, mock_language_map):
        mock_language_map.get.return_value = None

        with self.assertRaises(ValueError):
            export_json("invalid", "data_type", Path("/output"), True)

    def test_convert_to_sqlite_no_language(self):
        with self.assertRaises(ValueError):
            convert_to_sqlite(None, "data_type", "/output", True)
