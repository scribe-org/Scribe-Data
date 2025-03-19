# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the query data.
"""

import subprocess
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch


class TestQueryData(unittest.TestCase):
    @patch("subprocess.run")
    @patch("sys.executable", return_value="python")
    def test_execute_formatting_script(self, mock_executable, mock_run):
        """Test the execute_formatting_script function."""
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
            )  # should print error but not raise exception

    @patch("scribe_data.wikidata.query_data.list_all_languages")
    @patch("scribe_data.wikidata.query_data.Path")
    @patch("scribe_data.wikidata.query_data.format_sublanguage_name")
    @patch("scribe_data.wikidata.query_data.sparql")
    @patch("scribe_data.wikidata.query_data.execute_formatting_script")
    @patch(
        "builtins.open", new_callable=mock_open, read_data="SELECT * WHERE { ?s ?p ?o }"
    )
    @patch("builtins.print")
    @patch("re.findall", return_value=["query_1.sparql"])
    @patch("re.search")
    @patch("re.sub", return_value="query.sparql")
    def test_query_data_multiple_intervals(
        self,
        mock_re_sub,
        mock_re_search,
        mock_re_findall,
        mock_print,
        mock_open_file,
        mock_execute,
        mock_sparql,
        mock_format,
        mock_path,
        mock_list_langs,
    ):
        """Test query_data with multiple query intervals."""
        # Import function locally.
        from scribe_data.wikidata.query_data import query_data

        # Setup mocks.
        mock_list_langs.return_value = ["German"]
        mock_re_search.return_value = MagicMock(group=lambda x: "1" if x == 1 else None)

        # Mock paths.
        mock_file1 = MagicMock()
        mock_file1.is_file.return_value = True
        mock_file1.parent.name = "verbs"
        mock_file1.parent.parent.name = "German"
        mock_file1.name = "query_1.sparql"
        mock_file1.__str__.return_value = "query_1.sparql"

        mock_file2 = MagicMock()
        mock_file2.is_file.return_value = True
        mock_file2.parent.name = "verbs"
        mock_file2.parent.parent.name = "German"
        mock_file2.name = "query_2.sparql"
        mock_file2.__str__.return_value = "query_2.sparql"

        mock_path.return_value.rglob.return_value = [mock_file1, mock_file2]
        mock_path.return_value.exists.return_value = True

        # Setup format_sublanguage_name.
        mock_format.return_value = "German"

        # Mock sparql results.
        mock_results1 = {
            "results": {
                "bindings": [{"item": {"value": "Q1"}, "label": {"value": "test1"}}]
            }
        }

        mock_results2 = {
            "results": {
                "bindings": [{"item": {"value": "Q2"}, "label": {"value": "test2"}}]
            }
        }

        # Create mock query objects.
        mock_query1 = MagicMock()
        mock_query1.convert.return_value = mock_results1

        mock_query2 = MagicMock()
        mock_query2.convert.return_value = mock_results2

        # Set side effect for sparql.query().
        mock_sparql.query.side_effect = [mock_query1, mock_query2]

        # Run function
        query_data(languages=["German"], data_type=["verbs"], output_dir="./output")

        # Check sparql.setQuery was called.
        mock_sparql.setQuery.assert_called()
