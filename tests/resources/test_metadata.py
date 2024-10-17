"""
Tests for the accessibility of resources.

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

from unittest import TestCase
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
LANGUAGE_METADATA_PATH = (
    BASE_DIR / "src" / "scribe_data" / "resources" / "language_metadata.json"
)
DATA_TYPE_METADATA_PATH = (
    BASE_DIR / "src" / "scribe_data" / "resources" / "data_type_metadata.json"
)


class TestFileAccessibility(TestCase):
    def check_file_exists(self, file_path):
        """Helper method to check if a file exists."""
        if not file_path.is_file():
            self.fail(f"Error: {file_path} is missing. Check the file location.")

    def check_file_readable(self, file_path):
        """Helper method to check if a file is readable."""
        if not file_path.is_file():
            self.fail(f"Error: {file_path} is missing.")

        try:
            with open(file_path, "r") as f:
                content = f.read()
            if not content:
                self.fail(f"Error: {file_path} is empty.")
        except Exception as e:
            # Catching any other file reading error
            self.fail(f"Failed to read {file_path}: {str(e)}")

    def test_language_metadata_file_exists(self):
        """Check if the language_metadata.json file exists."""
        self.check_file_exists(LANGUAGE_METADATA_PATH)

    def test_language_metadata_file_readable(self):
        """Check if the language_metadata.json file is readable."""
        self.check_file_readable(LANGUAGE_METADATA_PATH)

    def test_data_type_metadata_file_exists(self):
        """Check if the data_type_metadata.json file exists."""
        self.check_file_exists(DATA_TYPE_METADATA_PATH)

    def test_data_type_metadata_file_readable(self):
        """Check if the data_type_metadata.json file is readable."""
        self.check_file_readable(DATA_TYPE_METADATA_PATH)
