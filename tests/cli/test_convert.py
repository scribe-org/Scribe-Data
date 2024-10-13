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
from unittest.mock import MagicMock, patch

from scribe_data.cli.convert import (
    convert_to_sqlite,
)


class TestConvert(unittest.TestCase):
    @patch("scribe_data.cli.convert.Path")
    @patch("scribe_data.cli.convert.data_to_sqlite")
    @patch("shutil.copy")
    def test_convert_to_sqlite(self, mock_shutil_copy, mock_data_to_sqlite, mock_path):
        mock_path.return_value.exists.return_value = True

        convert_to_sqlite(
            language="english",
            data_type="nouns",
            input_file="file",
            output_type="sqlite",
            output_dir="/output",
            overwrite=True,
        )

        mock_data_to_sqlite.assert_called_with(["english"], ["nouns"])
        mock_shutil_copy.assert_called()

    @patch("scribe_data.cli.convert.Path")
    @patch("scribe_data.cli.convert.data_to_sqlite")
    def test_convert_to_sqlite_no_output_dir(self, mock_data_to_sqlite, mock_path):
        # Create a mock for input file
        mock_input_file = MagicMock()
        mock_input_file.exists.return_value = True

        mock_path.return_value = mock_input_file

        # source and destination paths
        mock_input_file.parent = MagicMock()
        mock_input_file.parent.__truediv__.return_value = MagicMock()
        mock_input_file.parent.__truediv__.return_value.exists.return_value = False

        convert_to_sqlite(
            language="english",
            data_type="nouns",
            input_file=mock_input_file,
            output_type="sqlite",
            output_dir=None,
            overwrite=True,
        )

        mock_data_to_sqlite.assert_called_with(["english"], ["nouns"])

    @patch("scribe_data.cli.convert.Path")
    @patch("scribe_data.cli.convert.data_to_sqlite")
    @patch("scribe_data.cli.convert.get_language_iso")
    @patch("shutil.copy")
    def test_convert_to_sqlite_with_language_iso(
        self, mock_copy, mock_get_language_iso, mock_data_to_sqlite, mock_path
    ):
        mock_get_language_iso.return_value = "en"
        mock_path.return_value.exists.return_value = True

        convert_to_sqlite(
            language="English",
            data_type="data_type",
            input_file="file",
            output_type="sqlite",
            output_dir="/output",
            overwrite=True,
        )

        mock_data_to_sqlite.assert_called_with(["English"], ["data_type"])
        mock_copy.assert_called()

    def test_convert_to_sqlite_no_language(self):
        with self.assertRaises(ValueError):
            convert_to_sqlite(
                language=None,
                data_type="data_type",
                output_type="sqlite",
                output_dir="/output",
                overwrite=True,
            )
