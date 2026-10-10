# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from pathlib import Path 
import tempfile

from scribe_data.check.check_project_structure import (
    check_for_sparql_files,
    check_data_type_folders,
    check_project_structure,
)


class TestCheckProjectStructure(unittest.TestCase):
    def test_check_for_sparql_files_true(self) -> None:
        """
        Test to check for sparql files. Creates a temporary directory. Returns True if a sparql file is found.
        """
        missing_queries = []
        data_type = "sparql"
        language = "sv"
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            (tmp_path / "query_test.sparql").touch()
            
            self.assertTrue(check_for_sparql_files(tmp_path, data_type, language, None, missing_queries))
            
    def test_check_for_sparql_files_false(self) -> None:
        """
        Test to check for sparql files. Creates a temporary directory. No sparql file exists, should return false.
        """
        missing_queries = []
        data_type = "sparql"
        language = "sv"
        with tempfile.TemporaryDirectory() as temp_dir:
                tmp_path = Path(temp_dir)
                self.assertFalse(check_for_sparql_files(tmp_path, data_type, language, None, missing_queries))
    
    def test_check_data_type_folders(self) -> None:
        errors = []
        missing_folders = []
        missing_queries = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            (path / "unexpected_folder").mkdir()
            
            check_data_type_folders(
                str(path),
                "sv",
                None,
                errors,
                missing_folders,
                missing_queries
            )
        
        self.assertTrue(any("unexpected_folder" in error for error in errors))