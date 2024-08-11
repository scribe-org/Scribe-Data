import unittest
from io import StringIO
from unittest.mock import patch

from scribe_data.cli.cli_utils import correct_data_type, print_formatted_data
from scribe_data.cli.list import (
    list_all,
    list_data_types,
    list_languages,
    list_languages_for_data_type,
)
from scribe_data.cli.total import get_qid_by_input


class TestScribeDataCLI(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_correct_data_type(self):
        """
        Test the correct_data_type function for various inputs.
        """
        print("Running test_correct_data_type")
        self.assertEqual(correct_data_type("noun"), "nouns")
        self.assertEqual(correct_data_type("verbs"), "verbs")
        self.assertIsNone(correct_data_type("nonexistent"))

    @patch("builtins.print")
    def test_print_formatted_data(self, mock_print):
        """
        Test the print_formatted_data function.
        """
        print("Running test_print_formatted_data")
        data = {"key1": "value1", "key2": "value2"}
        print(f"Data: {data}")
        print_formatted_data(data, "test_type")
        mock_print.assert_called()

    # Test List Command

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_languages(self, mock_stdout):
        """
        Test the list_languages function.
        """
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
        """
        Test the list_data_types function.
        """
        print("Running test_list_data_types")
        list_data_types()
        output = mock_stdout.getvalue()
        print(f"Output: {output}")
        self.assertIn("Available data types: All languages", output)
        self.assertIn("nouns", output)
        self.assertIn("verbs", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_data_types_for_language(self, mock_stdout):
        """
        Test the list_data_types function for a specific language.
        """
        print("Running test_list_data_types_for_language")
        list_data_types("English")
        output = mock_stdout.getvalue()
        print(f"Output: {output}")
        self.assertIn("Available data types: English", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_all(self, mock_stdout):
        """
        Test the list_all function.
        """
        print("Running test_list_all")
        list_all()
        output = mock_stdout.getvalue()
        print(f"Output: {output}")
        self.assertIn("Language", output)
        self.assertIn("Available data types: All languages", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_languages_for_data_type(self, mock_stdout):
        """
        Test the list_languages_for_data_type function.
        """
        print("Running test_list_languages_for_data_type")
        list_languages_for_data_type("nouns")
        output = mock_stdout.getvalue()
        print(f"Output: {output}")
        self.assertIn("Available languages: nouns", output)
        self.assertIn("English", output)

    # Test Total Command

    def test_get_qid_by_input(self):
        """
        Test the get_qid_by_input function for various inputs.
        """
        print("Running test_get_qid_by_input")
        self.assertEqual(get_qid_by_input("English"), "Q1860")
        self.assertEqual(get_qid_by_input("french"), "Q150")
        self.assertIsNone(get_qid_by_input("NonexistentLanguage"))

    # Edge Cases and Error Handling

    def test_list_data_types_nonexistent_language(self):
        """
        Test that list_data_types raises a ValueError for a nonexistent language.
        """
        print("Running test_list_data_types_nonexistent_language")
        with self.assertRaises(ValueError):
            list_data_types("NonexistentLanguage")

    def test_list_data_types_no_data_available(self):
        """
        Test that list_data_types raises a ValueError when no data is available.
        """
        print("Running test_list_data_types_no_data_available")
        with patch("pathlib.Path.iterdir", return_value=[]):
            with self.assertRaises(ValueError):
                list_data_types("English")


if __name__ == "__main__":
    unittest.main()
