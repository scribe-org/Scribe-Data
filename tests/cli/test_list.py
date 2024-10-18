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
from unittest.mock import call, patch

from scribe_data.cli.list import (
    list_all,
    list_data_types,
    list_languages,
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
            call("Language     ISO   QID      "),
            call("--------------------------"),
            call("Arabic       ar    Q13955   "),
            call("Basque       eu    Q8752    "),
            call("Bengali      bn    Q9610    "),
            call("Bokmål       nb    Q25167   "),
            call("Czech        cs    Q9056    "),
            call("Danish       da    Q9035    "),
            call("English      en    Q1860    "),
            call("Esperanto    eo    Q143     "),
            call("Estonian     et    Q9072    "),
            call("Finnish      fi    Q1412    "),
            call("French       fr    Q150     "),
            call("German       de    Q188     "),
            call("Greek        el    Q36510   "),
            call("Gurmukhi     pa    Q58635   "),
            call("Hausa        ha    Q56475   "),
            call("Hebrew       he    Q9288    "),
            call("Hindi        hi    Q11051   "),
            call("Indonesian   id    Q9240    "),
            call("Italian      it    Q652     "),
            call("Japanese     ja    Q5287    "),
            call("Kurmanji     kmr   Q36163   "),
            call("Latin        la    Q397     "),
            call("Malay        ms    Q9237    "),
            call("Malayalam    ml    Q36236   "),
            call("Mandarin     zh    Q727694  "),
            call("Nigerian     pi    Q33655   "),
            call("Nynorsk      nn    Q25164   "),
            call("Polish       pl    Q809     "),
            call("Portuguese   pt    Q5146    "),
            call("Russian      ru    Q7737    "),
            call("Shahmukhi    pnb   Q58635   "),
            call("Slovak       sk    Q9058    "),
            call("Spanish      es    Q1321    "),
            call("Swahili      sw    Q7838    "),
            call("Swedish      sv    Q9027    "),
            call("Tajik        tg    Q9260    "),
            call("Tamil        ta    Q5885    "),
            call("Ukrainian    ua    Q8798    "),
            call("Urdu         ur    Q11051   "),
            call("Yoruba       yo    Q34311   "),
            call("--------------------------"),
            call(),
        ]
        mock_print.assert_has_calls(expected_calls)

    @patch("builtins.print")
    def test_list_data_types_all_languages(self, mock_print):
        list_data_types()
        print(mock_print.mock_calls)
        expected_calls = [
            call(),
            call("Available data types: All languages"),
            call("-----------------------------------"),
            call("adjectives"),
            call("adverbs"),
            call("emoji-keywords"),
            call("nouns"),
            call("personal-pronouns"),
            call("postpositions"),
            call("prepositions"),
            call("proper-nouns"),
            call("verbs"),
            call("-----------------------------------"),
            call(),
        ]
        mock_print.assert_has_calls(expected_calls)

    @patch("builtins.print")
    def test_list_data_types_specific_language(self, mock_print):
        list_data_types("English")

        expected_calls = [
            call(),
            call("Available data types: English"),
            call("-----------------------------"),
            call("adjectives"),
            call("adverbs"),
            call("emoji-keywords"),
            call("nouns"),
            call("proper-nouns"),
            call("verbs"),
            call("-----------------------------"),
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
        mock_print.assert_called_with(
            "Please specify either a language or a data type."
        )

    @patch("scribe_data.cli.list.list_languages_for_data_type")
    def test_list_wrapper_languages_for_data_type(
        self, mock_list_languages_for_data_type
    ):
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
            call("Language     ISO   QID      "),
            call("--------------------------"),
            call("Arabic       ar    Q13955   "),
            call("Basque       eu    Q8752    "),
            call("Bengali      bn    Q9610    "),
            call("Bokmål       nb    Q25167   "),
            call("Czech        cs    Q9056    "),
            call("Danish       da    Q9035    "),
            call("English      en    Q1860    "),
            call("Esperanto    eo    Q143     "),
            call("Estonian     et    Q9072    "),
            call("Finnish      fi    Q1412    "),
            call("French       fr    Q150     "),
            call("German       de    Q188     "),
            call("Greek        el    Q36510   "),
            call("Gurmukhi     pa    Q58635   "),
            call("Hausa        ha    Q56475   "),
            call("Hebrew       he    Q9288    "),
            call("Hindi        hi    Q11051   "),
            call("Indonesian   id    Q9240    "),
            call("Italian      it    Q652     "),
            call("Japanese     ja    Q5287    "),
            call("Kurmanji     kmr   Q36163   "),
            call("Latin        la    Q397     "),
            call("Malay        ms    Q9237    "),
            call("Malayalam    ml    Q36236   "),
            call("Mandarin     zh    Q727694  "),
            call("Nigerian     pi    Q33655   "),
            call("Nynorsk      nn    Q25164   "),
            call("Polish       pl    Q809     "),
            call("Portuguese   pt    Q5146    "),
            call("Russian      ru    Q7737    "),
            call("Shahmukhi    pnb   Q58635   "),
            call("Slovak       sk    Q9058    "),
            call("Spanish      es    Q1321    "),
            call("Swahili      sw    Q7838    "),
            call("Swedish      sv    Q9027    "),
            call("Tajik        tg    Q9260    "),
            call("Tamil        ta    Q5885    "),
            call("Ukrainian    ua    Q8798    "),
            call("Urdu         ur    Q11051   "),
            call("Yoruba       yo    Q34311   "),
            call("--------------------------"),
            call(),
        ]
        mock_print.assert_has_calls(expected_calls)

    @patch("scribe_data.cli.list.list_languages")
    def test_list_languages_command(self, mock_list_languages):
        test_args = ["main.py", "list", "--language"]
        with patch("sys.argv", test_args):
            main()
        mock_list_languages.assert_called_once()

    @patch("scribe_data.cli.list.list_data_types")
    def test_list_data_types_command(self, mock_list_data_types):
        test_args = ["main.py", "list", "--data-type"]
        with patch("sys.argv", test_args):
            main()
        mock_list_data_types.assert_called_once()

    @patch("scribe_data.cli.list.list_all")
    def test_list_all_command(self, mock_list_all):
        test_args = ["main.py", "list", "--all"]
        with patch("sys.argv", test_args):
            main()
        mock_list_all.assert_called_once()
