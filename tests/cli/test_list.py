"""
Tests for the list file functions.

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
from scribe_data.cli.list import (
    list_languages,
    list_data_types,
    list_all,
    list_languages_for_data_type,
    list_wrapper,
)
from scribe_data.cli.main import main

class TestListFunctions(unittest.TestCase):
    @patch("builtins.print")
    def test_list_languages(self, mock_print):
        list_languages()
        expected_calls = [
            call(),
            call('Language     ISO  QID    '),
            call('-----------------------'),
            call('English      en   Q1860  '),
            call('French       fr   Q150   '),
            call('German       de   Q188   '),
            call('Italian      it   Q652   '),
            call('Portuguese   pt   Q5146  '),
            call('Russian      ru   Q7737  '),
            call('Spanish      es   Q1321  '),
            call('Swedish      sv   Q9027  '),
            call('-----------------------'),
            call(),
        ]
        mock_print.assert_has_calls(expected_calls)

    @patch("builtins.print")
    def test_list_data_types_all_languages(self, mock_print):
        list_data_types()
        expected_calls = [
            call(),
            call('Available data types: All languages'),
            call('-----------------------------------'),
            call('emoji-keywords'),
            call('nouns'),
            call('prepositions'),
            call('translations'),
            call('verbs'),
            call('-----------------------------------'),
            call(),
        ]
        mock_print.assert_has_calls(expected_calls)

    @patch("builtins.print")
    def test_list_data_types_specific_language(self, mock_print):
        list_data_types("English")
        expected_calls = [
            call(),
            call('Available data types: English'),
            call('-----------------------------'),
            call('emoji-keywords'),
            call('nouns'),
            call('translations'),
            call('verbs'),
            call('-----------------------------'),
            call(),
        ]
        mock_print.assert_has_calls(expected_calls)

    def test_list_data_types_invalid_language(self):
        with self.assertRaises(ValueError):
            list_data_types("InvalidLanguage")

    def test_list_data_types_no_data_types(self):
        with self.assertRaises(ValueError):
            list_data_types("Klingon")  

    @patch("scribe_data.cli.list.list_languages")
    @patch("scribe_data.cli.list.list_data_types")
    def test_list_all(self, mock_list_data_types, mock_list_languages):
        list_all()
        mock_list_languages.assert_called_once()
        mock_list_data_types.assert_called_once()

    @patch("scribe_data.cli.list.list_all")
    def test_list_wrapper_all(self, mock_list_all):
        list_wrapper(all_bool=True)
        mock_list_all.assert_called_once()

    @patch("scribe_data.cli.list.list_languages")
    def test_list_wrapper_languages(self, mock_list_languages):
        list_wrapper(language=True)
        mock_list_languages.assert_called_once()

    @patch("scribe_data.cli.list.list_data_types")
    def test_list_wrapper_data_types(self, mock_list_data_types):
        list_wrapper(data_type=True)
        mock_list_data_types.assert_called_once()

    @patch("builtins.print")
    def test_list_wrapper_language_and_data_type(self, mock_print):
        list_wrapper(language=True, data_type=True)
        mock_print.assert_called_with("Please specify either a language or a data type.")

    @patch("scribe_data.cli.list.list_languages_for_data_type")
    def test_list_wrapper_languages_for_data_type(self, mock_list_languages_for_data_type):
        list_wrapper(language=True, data_type="example_data_type")
        mock_list_languages_for_data_type.assert_called_with("example_data_type")

    @patch("scribe_data.cli.list.list_data_types")
    def test_list_wrapper_data_types_for_language(self, mock_list_data_types):
        list_wrapper(language="English", data_type=True)
        mock_list_data_types.assert_called_with("English")

    @patch("builtins.print")
    def test_list_languages_for_data_type_valid(self, mock_print):
        list_languages_for_data_type("nouns")
        expected_calls = [
            call(),
            call('Available languages: nouns'),
            call('--------------------------'),
            call('English'),
            call('French'),
            call('German'),
            call('Italian'),
            call('Portuguese'),
            call('Russian'),
            call('Spanish'),
            call('Swedish'),
            call('--------------------------'),
            call(),
        ]
        mock_print.assert_has_calls(expected_calls)

    @patch('scribe_data.cli.list.list_languages')
    def test_list_languages_command(self, mock_list_languages):
        test_args = ['main.py', 'list', '--language']
        with patch('sys.argv', test_args):
            main()
        mock_list_languages.assert_called_once()

    @patch('scribe_data.cli.list.list_data_types')
    def test_list_data_types_command(self, mock_list_data_types):
        test_args = ['main.py', 'list', '--data-type']
        with patch('sys.argv', test_args):
            main()
        mock_list_data_types.assert_called_once()

    @patch('scribe_data.cli.list.list_all')
    def test_list_all_command(self, mock_list_all):
        test_args = ['main.py', 'list', '--all']
        with patch('sys.argv', test_args):
            main()
        mock_list_all.assert_called_once()
