# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the query data.
"""

import subprocess
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch, call
from io import StringIO
import tempfile
import json
from urllib.error import HTTPError

class TestQueryData(unittest.TestCase):
    @patch("subprocess.run")
    @patch("sys.executable", return_value="python")
    def test_execute_formatting_script(self, mock_executable, mock_run):
        """
        Test the execute_formatting_script function.
        """
        # Import function locally to avoid import issues during patching.
        from scribe_data.wikidata.query_data import execute_formatting_script

        # Mock Path objects correctly.
        with patch("scribe_data.wikidata.query_data.Path") as mock_path:
            # Create a mock Path object.
            mock_path_instance = MagicMock(spec=Path)
            mock_path_instance.parent.parent.parent = Path("/mock/project/root")
            mock_path_instance.parent = Path("/mock")
            mock_path.return_value = mock_path_instance

            execute_formatting_script("/output/dir", "German", "nouns")

            # Check subprocess.run was called correctly.
            mock_run.assert_called_once()

            # Get the call arguments.
            call_args = mock_run.call_args[0][0]

            # Check basic arguments match what we expect.
            self.assertIn("--dir-path", call_args)
            self.assertIn("/output/dir", call_args)
            self.assertIn("--language", call_args)
            self.assertIn("German", call_args)
            self.assertIn("--data_type", call_args)
            self.assertIn("nouns", call_args)

            # Test error case
            mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
            execute_formatting_script(
                "/output/dir", "German", "nouns"
            )  # should print error but not raise exceptions

    def test_query_data_multiple_intervals(self):
        """
        Test query_data with multiple query intervals.
        """
        with patch("sys.stdout", new=StringIO()) as out:
            # Import function locally.
            from scribe_data.wikidata.query_data import query_data

            # Setup temporary query files.
            with tempfile.TemporaryDirectory() as temp_dir:
                lang_data_extraction_dir = Path(temp_dir) / "lang_data_extraction_dir"
                german_verbs = lang_data_extraction_dir / "German" / "verbs"
                german_verbs.mkdir(parents=True)

                (german_verbs / "query_1.sparql").write_text("test query\n1")
                (german_verbs / "query_2.sparql").write_text("test query\n2")

                # Patch functions so temporary files are used.
                with patch("scribe_data.wikidata.query_data.LANGUAGE_DATA_EXTRACTION_DIR", lang_data_extraction_dir), \
                    patch("scribe_data.wikidata.query_data.list_all_languages", return_value=["German"]), \
                    patch("scribe_data.wikidata.query_data.format_sublanguage_name", return_value="German"), \
                    patch("scribe_data.wikidata.query_data.sparql.setQuery") as mock_setQuery, \
                    patch("scribe_data.wikidata.query_data.sparql.query") as mock_query, \
                    patch("scribe_data.wikidata.query_data.execute_formatting_script") as mock_exec:

                    # Simulate query responses.
                    mock_query.side_effect = [
                        MagicMock(convert=lambda: {
                            "results": {"bindings": [
                                {"item": {"value": "Q1"}, "label": {"value": "test1"}}
                            ]}
                        }),
                        MagicMock(convert=lambda: {
                            "results": {"bindings": [
                                {"item": {"value": "Q2"}, "label": {"value": "test2"}}
                            ]}
                        })
                    ]

                    output_dir = Path(temp_dir) / "output"

                    # Call query_data.
                    query_data(["German"], ["verbs"], str(output_dir))

                    # Check setQuery is called correctly.
                    mock_setQuery.assert_has_calls([call("test query\n1"), call("test query\n2")], any_order=False)

                    # Check the results JSON file exists.
                    result_file = output_dir / "German" / "verbs.json"
                    self.assertTrue(result_file.exists())

                    # Check the results.
                    data = json.loads(result_file.read_text())
                    self.assertEqual(len(data), 2)
                    self.assertEqual(data[0]["item"], "Q1")
                    self.assertEqual(data[0]["label"], "test1")
                    self.assertEqual(data[1]["item"], "Q2")
                    self.assertEqual(data[1]["label"], "test2")
                    self.assertEqual(data[1]["auxiliaryVerb"], "")

                    # Check that verbs_queried.json exists.
                    queried_file = output_dir / "German" / "verbs_queried.json"
                    self.assertTrue(queried_file.exists())

                    # Check the results of verbs_queried.json match verbs.json.
                    self.assertEqual(queried_file.read_text(), result_file.read_text())

                    # Check execute_formatting_script is called once with the correct arguments.
                    mock_exec.assert_called_once_with(output_dir=str(output_dir), language="German", data_type="verbs")

                    # Check the expected messages are printed to sys.stdout.
                    self.assertIn("Querying and formatting German verbs", out.getvalue())
                    self.assertIn("Successfully queried and formatted data for German verbs", out.getvalue())

    def test_query_data_single_query_error(self):
            """
            Test that query_data handles a single query returning None.
            """
            with patch("sys.stdout", new=StringIO()) as out:
                # Import function locally.
                from scribe_data.wikidata.query_data import query_data

                # Setup temporary query file.
                with tempfile.TemporaryDirectory() as temp_dir:
                    lang_data_extraction_dir = Path(temp_dir) / "lang_data_extraction_dir"
                    german_verbs = lang_data_extraction_dir / "German" / "verbs"
                    german_verbs.mkdir(parents=True)

                    query_file = german_verbs / "query.sparql"
                    query_file.write_text("test query")

                    # Patch functions so temporary files are used.
                    with patch("scribe_data.wikidata.query_data.LANGUAGE_DATA_EXTRACTION_DIR", lang_data_extraction_dir), \
                        patch("scribe_data.wikidata.query_data.list_all_languages", return_value=["German"]), \
                        patch("scribe_data.wikidata.query_data.format_sublanguage_name", return_value="German"), \
                        patch("scribe_data.wikidata.query_data.sparql.setQuery"), \
                        patch("scribe_data.wikidata.query_data.sparql.query") as mock_query, \
                        patch("scribe_data.wikidata.query_data.execute_formatting_script") as mock_exec:

                        # Simulate query with response of None.
                        mock_query.return_value = MagicMock(convert=lambda: None)

                        output_dir = Path(temp_dir) / "output"

                        # Call query_data.
                        error = query_data(["German"], ["verbs"], str(output_dir))

                        # Check the error return values are returned.
                        self.assertFalse(error["success"])
                        self.assertFalse(error["skipped"])

                        # Check the expected messages are printed to sys.stdout.
                        self.assertEqual(out.getvalue().count("Querying and formatting German verbs"), 3)
                        self.assertEqual(out.getvalue().count(f"Nothing returned by the WDQS server for {query_file}"), 3)
                        self.assertEqual(out.getvalue().count("The query will be retried."), 2)
                        self.assertIn("Max retries reached. Skipping this query.", out.getvalue())

                        # Check the results file is not created.
                        self.assertFalse((output_dir / "German" / "verbs.json").exists())

                        # Check that execute_formatting_script is not called.
                        mock_exec.assert_not_called()

    def test_query_data_multiple_intervals_error(self):
        """
        Test query_data with multiple query intervals where the second query throws an HTTPError
        and subsequent queries return None. 
        """
        with patch("sys.stdout", new=StringIO()) as out:
            # Import function locally.
            from scribe_data.wikidata.query_data import query_data

            # Setup temporary query files.
            with tempfile.TemporaryDirectory() as temp_dir:
                lang_data_extraction_dir = Path(temp_dir) / "lang_data_extraction_dir"
                german_verbs = lang_data_extraction_dir / "German" / "verbs"
                german_verbs.mkdir(parents=True)

                query_file_1 = german_verbs / "query_1.sparql"
                query_file_2 = german_verbs / "query_2.sparql"
                query_file_1.write_text("test query\n1")
                query_file_2.write_text("test query\n2")

                # Patch functions so temporary files are used.
                with patch("scribe_data.wikidata.query_data.LANGUAGE_DATA_EXTRACTION_DIR", lang_data_extraction_dir), \
                    patch("scribe_data.wikidata.query_data.list_all_languages", return_value=["German"]), \
                    patch("scribe_data.wikidata.query_data.format_sublanguage_name", return_value="German"), \
                    patch("scribe_data.wikidata.query_data.sparql.setQuery"), \
                    patch("scribe_data.wikidata.query_data.sparql.query") as mock_query, \
                    patch("scribe_data.wikidata.query_data.execute_formatting_script"):

                    # Simulate query responses.
                    mock_http = MagicMock()
                    mock_http.convert.side_effect = HTTPError("url", 404, "error", None, None)
                    mock_query.side_effect = [
                        MagicMock(convert=lambda: {
                            "results": {"bindings": [
                                {"item": {"value": "Q1"}, "label": {"value": "test1"}}
                            ]}
                        }),
                        mock_http,
                        MagicMock(convert=lambda: None),
                        MagicMock(convert=lambda: None),
                        MagicMock(convert=lambda: None)
                    ]

                    output_dir = Path(temp_dir) / "output"

                    # Call query_data.
                    error = query_data(["German"], ["verbs"], str(output_dir))
                    
                    # Check the error return values are returned.
                    self.assertFalse(error["success"])
                    self.assertFalse(error["skipped"])

                    # Check the results JSON file exists.
                    result_file = output_dir / "German" / "verbs.json"
                    self.assertTrue(result_file.exists())

                    # Check the results for the first query.
                    data = json.loads(result_file.read_text())
                    self.assertEqual(len(data), 1)
                    self.assertEqual(data[0]["item"], "Q1")
                    self.assertEqual(data[0]["label"], "test1")

                    # Check the expected messages are printed to sys.stdout.
                    self.assertEqual(out.getvalue().count("Querying and formatting German verbs"), 4)
                    self.assertEqual(out.getvalue().count(f"HTTPError with {query_file_2}: HTTP Error 404: error"), 1)
                    self.assertEqual(out.getvalue().count(f"Nothing returned by the WDQS server for {query_file_2}"), 4)
                    self.assertEqual(out.getvalue().count("Successfully queried and formatted data for German verbs."), 1)
                    self.assertEqual(out.getvalue().count("The query will be retried."), 2)
                    self.assertEqual(out.getvalue().count("Max retries reached. Skipping this query."), 1)
