"""
Tests for the CLI get functionality.

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
from unittest.mock import patch, call
from scribe_data.cli.get import get_data

class TestCLIGetCommand(unittest.TestCase):
    @patch('scribe_data.cli.get.query_data')
    @patch('scribe_data.cli.get.export_json')
    @patch('scribe_data.cli.get.convert_to_csv_or_tsv')
    @patch('os.system')  
    def test_get_command(self, mock_system, mock_convert, mock_export_json, mock_query_data):
        expected_calls = [
            call(['English'], ['nouns']),
            call(['English'], ['nouns']),
            call()
        ]

        # Execute the test
        get_data(language='English', data_type='nouns', output_dir='outputs', output_type='json')
        get_data(language='English', data_type='nouns', output_dir='outputs', output_type='csv')
        get_data(all=True)

        # Validate the calls
        mock_query_data.assert_has_calls(expected_calls, any_order=True)
