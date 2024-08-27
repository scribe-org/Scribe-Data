"""
Tests for the CLI total functionality.

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
from unittest.mock import patch, MagicMock, call
from scribe_data.cli.total import get_total_lexemes

class TestTotalLexemes(unittest.TestCase):
    @patch('scribe_data.cli.total.get_qid_by_input')
    @patch('scribe_data.cli.total.sparql.query')
    def test_get_total_lexemes_valid(self, mock_query, mock_get_qid):
        mock_get_qid.side_effect = lambda x: {'english': 'Q1860', 'nouns': 'Q1084'}.get(x.lower(), None)
        mock_results = MagicMock()
        mock_results.convert.return_value = {
            "results": {
                "bindings": [
                    {"total": {"value": "42"}}
                ]
            }
        }
        mock_query.return_value = mock_results

        with patch('builtins.print') as mock_print:
            get_total_lexemes('English', 'nouns')

        mock_print.assert_called_once_with('Language: English\nData type: nouns\nTotal number of lexemes: 42')

    @patch('scribe_data.cli.total.get_qid_by_input')
    @patch('scribe_data.cli.total.sparql.query')
    def test_get_total_lexemes_no_results(self, mock_query, mock_get_qid):
        mock_get_qid.side_effect = lambda x: {'english': 'Q1860', 'nouns': 'Q1084'}.get(x.lower(), None)
        mock_results = MagicMock()
        mock_results.convert.return_value = {
            "results": {
                "bindings": []
            }
        }
        mock_query.return_value = mock_results

        with patch('builtins.print') as mock_print:
            get_total_lexemes('English', 'nouns')

        mock_print.assert_called_once_with('Total number of lexemes: Not found')

    @patch('scribe_data.cli.total.get_qid_by_input')
    @patch('scribe_data.cli.total.sparql.query')
    def test_get_total_lexemes_invalid_language(self, mock_query, mock_get_qid):
        mock_get_qid.side_effect = lambda x: None
        mock_query.return_value = MagicMock()

        with patch('builtins.print') as mock_print:
            get_total_lexemes('InvalidLanguage', 'nouns')

        mock_print.assert_called_once_with('Total number of lexemes: Not found')

    @patch('scribe_data.cli.total.get_qid_by_input')
    @patch('scribe_data.cli.total.sparql.query')
    def test_get_total_lexemes_empty_and_none_inputs(self, mock_query, mock_get_qid):
        mock_get_qid.return_value = None
        mock_query.return_value = MagicMock()

        # Call the function with empty and None inputs
        with patch('builtins.print') as mock_print:
            get_total_lexemes('', 'nouns')
            get_total_lexemes(None, 'verbs')

        expected_calls = [
            call('Total number of lexemes: Not found'),
            call('Total number of lexemes: Not found')
        ]
        mock_print.assert_has_calls(expected_calls, any_order=True)

    @patch('scribe_data.cli.total.get_qid_by_input')
    @patch('scribe_data.cli.total.sparql.query')
    def test_get_total_lexemes_nonexistent_language(self, mock_query, mock_get_qid):
        mock_get_qid.return_value = None
        mock_query.return_value = MagicMock()

        with patch('builtins.print') as mock_print:
            get_total_lexemes('Martian', 'nouns')

        mock_print.assert_called_once_with('Total number of lexemes: Not found')
    
    @patch('scribe_data.cli.total.get_qid_by_input')
    @patch('scribe_data.cli.total.sparql.query')
    def test_get_total_lexemes_various_data_types(self, mock_query, mock_get_qid):
        mock_get_qid.side_effect = lambda x: {'english': 'Q1860', 'verbs': 'Q24905', 'nouns': 'Q1084'}.get(x.lower(), None)
        mock_results = MagicMock()
        mock_results.convert.return_value = {
            "results": {
                "bindings": [
                    {"total": {"value": "30"}}
                ]
            }
        }

        mock_query.return_value = mock_results

        # Call the function with different data types
        with patch('builtins.print') as mock_print:
            get_total_lexemes('English', 'verbs')
            get_total_lexemes('English', 'nouns')

        expected_calls = [
            call('Language: English\nData type: verbs\nTotal number of lexemes: 30'),
            call('Language: English\nData type: nouns\nTotal number of lexemes: 30')
        ]
        mock_print.assert_has_calls(expected_calls)
