import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

from cli_utils import correct_data_type, print_formatted_data, get_language_data

from main import main
from total import get_total_lexemes, get_qid_by_input
from list import (
    list_wrapper,
    list_languages,
    list_data_types,
    list_all,
    list_languages_for_data_type,
)


class TestScribeDataCLI(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    # Test CLI Utils

    def test_correct_data_type(self):
        """Test the correct_data_type function for various inputs"""
        print("Running test_correct_data_type")
        self.assertEqual(correct_data_type("noun"), "nouns")
        self.assertEqual(correct_data_type("verbs"), "verbs")
        self.assertIsNone(correct_data_type("nonexistent"))

    @patch("builtins.print")
    def test_print_formatted_data(self, mock_print):
        """Test the print_formatted_data function"""
        print("Running test_print_formatted_data")
        data = {"key1": "value1", "key2": "value2"}
        print(f"Data: {data}")
        print_formatted_data(data, "test_type")
        mock_print.assert_called()

    # Test List Command

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_languages(self, mock_stdout):
        """Test the list_languages function"""
        print("Running test_list_languages")
        list_languages()
        output = mock_stdout.getvalue()
        print(f"Output: {output}")
        self.assertIn("Language", output)
        self.assertIn("ISO", output)
        self.assertIn("QID", output)
        self.assertIn("English", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_data_types(self, mock_stdout):
        """Test the list_data_types function"""
        print("Running test_list_data_types")
        list_data_types()
        output = mock_stdout.getvalue()
        print(f"Output: {output}")
        self.assertIn("Available data types: All languages", output)
        self.assertIn("nouns", output)
        self.assertIn("verbs", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_data_types_for_language(self, mock_stdout):
        """Test the list_data_types function for a specific language"""
        print("Running test_list_data_types_for_language")
        list_data_types("English")
        output = mock_stdout.getvalue()
        print(f"Output: {output}")
        self.assertIn("Available data types: English", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_all(self, mock_stdout):
        """Test the list_all function"""
        print("Running test_list_all")
        list_all()
        output = mock_stdout.getvalue()
        print(f"Output: {output}")
        self.assertIn("Language", output)
        self.assertIn("Available data types: All languages", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_languages_for_data_type(self, mock_stdout):
        """Test the list_languages_for_data_type function"""
        print("Running test_list_languages_for_data_type")
        list_languages_for_data_type("nouns")
        output = mock_stdout.getvalue()
        print(f"Output: {output}")
        self.assertIn("Available languages: nouns", output)
        self.assertIn("English", output)

    @patch("list.list_languages")
    @patch("list.list_data_types")
    @patch("list.list_all")
    @patch("list.list_languages_for_data_type")
    def test_list_wrapper(
        self,
        mock_list_languages_for_data_type,
        mock_list_all,
        mock_list_data_types,
        mock_list_languages,
    ):
        """Test the list_wrapper function for various inputs"""
        print("Running test_list_wrapper")
        list_wrapper()
        mock_list_all.assert_called_once()

        list_wrapper(language=True)
        mock_list_languages.assert_called_once()

        list_wrapper(data_type=True)
        mock_list_data_types.assert_called_once()

        list_wrapper(language=True, data_type="nouns")
        mock_list_languages_for_data_type.assert_called_once_with("nouns")

    # Test Total Command

    def test_get_qid_by_input(self):
        """Test the get_qid_by_input function for various inputs"""
        print("Running test_get_qid_by_input")
        self.assertEqual(get_qid_by_input("English"), "Q1860")
        self.assertEqual(get_qid_by_input("french"), "Q150")
        self.assertIsNone(get_qid_by_input("NonexistentLanguage"))

    @patch("total.SPARQLWrapper")
    def test_get_total_lexemes(self, mock_sparql_wrapper):
        """Test the get_total_lexemes function"""
        print("Running test_get_total_lexemes")
        mock_sparql_wrapper.return_value.query.return_value.convert.return_value = {
            "results": {"bindings": [{"total": {"value": "100000"}}]}
        }

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            get_total_lexemes("English", "nouns")
            output = mock_stdout.getvalue()
            print(f"Output: {output}")
            self.assertIn("Language: English", output)
            self.assertIn("Data type: Nouns", output)
            self.assertIn("Total number of lexemes: 100000", output)

    # Edge Cases and Error Handling

    def test_list_data_types_nonexistent_language(self):
        """Test that list_data_types raises a ValueError for a nonexistent language"""
        print("Running test_list_data_types_nonexistent_language")
        with self.assertRaises(ValueError):
            list_data_types("NonexistentLanguage")

    def test_list_data_types_no_data_available(self):
        """Test that list_data_types raises a ValueError when no data is available"""
        print("Running test_list_data_types_no_data_available")
        with patch("pathlib.Path.iterdir", return_value=[]):
            with self.assertRaises(ValueError):
                list_data_types("English")

    @patch("total.SPARQLWrapper")
    def test_get_total_lexemes_no_results(self, mock_sparql_wrapper):
        """Test the get_total_lexemes function when no results are returned"""
        print("Running test_get_total_lexemes_no_results")
        mock_sparql_wrapper.return_value.query.return_value.convert.return_value = {
            "results": {"bindings": []}
        }

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            get_total_lexemes("English", "nouns")
            output = mock_stdout.getvalue()
            print(f"Output: {output}")
            self.assertIn("Total number of lexemes: 0", output)

    def test_get_language_data(self):
        """Test the get_language_data function for various inputs"""
        print("Running test_get_language_data")
        self.assertEqual(get_language_data("english", "language"), "English")
        self.assertEqual(get_language_data("en", "iso"), "en")
        self.assertEqual(get_language_data("Q1860", "qid"), "Q1860")
        self.assertIsNone(get_language_data("nonexistent", "language"))
        self.assertIsNone(get_language_data("english", "nonexistent_attribute"))

    @patch("argparse.ArgumentParser.parse_args")
    def test_main_with_invalid_command(self, mock_parse_args):
        """Test the main function with an invalid command"""
        print("Running test_main_with_invalid_command")
        mock_parse_args.return_value = MagicMock(command="invalid_command")

        # Capture stdout to check printed messages
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            with self.assertRaises(SystemExit) as cm:
                main()

            # Check if the program exited with status code 1
            self.assertEqual(cm.exception.code, 1)

            # Check if the usage message is printed
            self.assertIn("usage:", mock_stdout.getvalue())

    # test_scribe_data_cli.py

    @patch("total.SPARQLWrapper")
    def test_get_total_lexemes_sparql_error(self, mock_sparql_wrapper):
        print("Running test_get_total_lexemes_sparql_error")
        mock_sparql_wrapper.return_value.query.side_effect = Exception(
            "SPARQL query failed"
        )

        with self.assertRaises(Exception):
            get_total_lexemes("English", "nouns")

    @patch("argparse.ArgumentParser.parse_args")
    def test_main_invalid_command(self, mock_parse_args):
        """Test main function with invalid command"""
        print("Running test_main_invalid_command")
        mock_parse_args.return_value = MagicMock(command="invalid")
        with self.assertRaises(SystemExit):
            main()


if __name__ == "__main__":
    unittest.main()
