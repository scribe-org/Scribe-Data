"""
Tests for the CLI download functionality.

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
from unittest.mock import MagicMock, patch, mock_open
from datetime import date
from pathlib import Path

from scribe_data.cli.download import (
    parse_date,
    available_closest_lexeme_dumpfile,
    download_wd_lexeme_dump,
    wd_lexeme_dump_download_wrapper,
)
from scribe_data.utils import check_lexeme_dump_prompt_download


class TestDownloadCLI(unittest.TestCase):
    def test_parse_date_valid_formats(self):
        """Test parse_date function with valid date formats."""
        self.assertEqual(parse_date("20240101"), date(2024, 1, 1))
        self.assertEqual(parse_date("2024/01/01"), date(2024, 1, 1))
        self.assertEqual(parse_date("2024-01-01"), date(2024, 1, 1))

    def test_parse_date_invalid_format(self):
        """Test parse_date function with invalid date formats."""
        self.assertIsNone(parse_date("99-16-77"))
        self.assertIsNone(parse_date("invalid-date"))

    @patch("scribe_data.cli.download.requests.get")
    def test_available_closest_lexeme_dumpfile(self, mock_get):
        """Test finding closest available lexeme dump file.

        Tests a scenario where three dates are available: 20240101, 20240105, 20240110.
        Should return the closest date that appears first.
        """
        mock_check_func = MagicMock(
            side_effect=lambda d: True
            if d in ["20240101", "20240105", "20240110"]
            else None
        )
        target_date = "20240103"
        other_old_dumps = ["20240101", "20240105", "20240110"]
        closest = available_closest_lexeme_dumpfile(
            target_date, other_old_dumps, mock_check_func
        )
        self.assertEqual(closest, "20240101")

    @patch("scribe_data.cli.download.requests.get")
    @patch("scribe_data.cli.download.re.findall")
    def test_download_wd_lexeme_dump_latest(self, mock_findall, mock_get):
        """Test downloading latest Wikidata lexeme dump."""
        mock_get.return_value.text = 'href="latest-all.json.bz2"'
        mock_get.return_value.raise_for_status = MagicMock()
        mock_findall.return_value = ["latest-all.json.bz2"]
        url = download_wd_lexeme_dump("latest-lexemes")
        self.assertEqual(
            url,
            "https://dumps.wikimedia.org/wikidatawiki/entities/latest-lexemes.json.bz2",
        )

    @patch("scribe_data.cli.download.requests.get")
    @patch("scribe_data.cli.download.re.findall")
    def test_download_wd_lexeme_dump_by_date(self, mock_findall, mock_get):
        """Test downloading Wikidata lexeme dump for a specific date."""
        mock_get.return_value.text = 'href="wikidata-20241127-lexemes.json.bz2"'
        mock_get.return_value.raise_for_status = MagicMock()
        mock_findall.return_value = ["wikidata-20241127-lexemes.json.bz2"]
        url = download_wd_lexeme_dump("2024-11-27")
        self.assertEqual(
            url,
            "https://dumps.wikimedia.org/wikidatawiki/entities/20241127/wikidata-20241127-lexemes.json.bz2",
        )

    @patch("scribe_data.cli.download.requests.get")
    @patch("scribe_data.cli.download.input", return_value="y")
    @patch(
        "scribe_data.cli.download.check_lexeme_dump_prompt_download", return_value=None
    )
    @patch("scribe_data.cli.download.open", new_callable=mock_open)
    @patch("scribe_data.cli.download.tqdm")
    @patch("scribe_data.cli.download.DEFAULT_DUMP_EXPORT_DIR", new="test_export_dir")
    def test_wd_lexeme_dump_download_wrapper_latest(
        self, mock_tqdm, mock_file, mock_check_prompt, mock_input, mock_get
    ):
        """Test wrapper function for downloading latest Wikidata lexeme dump."""
        mock_get.return_value.text = 'href="latest-all.json.bz2"'
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.headers = {"content-length": "100"}
        mock_get.return_value.iter_content = lambda chunk_size: [b"data"] * 10

        with patch("scribe_data.cli.download.os.makedirs") as mock_makedirs:
            download_path = wd_lexeme_dump_download_wrapper()
            self.assertIn("latest-lexemes.json.bz2", download_path)
            mock_makedirs.assert_called_with("test_export_dir", exist_ok=True)

    def test_check_lexeme_dump_prompt_download_existing(self):
        """Test prompt for using existing lexeme dump files."""
        with patch(
            "scribe_data.utils.Path.glob",
            return_value=[Path("dump1.json.bz2"), Path("latest-lexemes.json.bz2")],
        ):
            with patch("builtins.input", return_value="u"):
                result = check_lexeme_dump_prompt_download(
                    "scribe_data/tests/cli/test_export_dir"
                )
                self.assertEqual(result.name, "latest-lexemes.json.bz2")

    def test_check_lexeme_dump_prompt_download_delete(self):
        """Test prompt for deleting existing lexeme dump files."""
        mock_existing_files = [Path("dump1.json.bz2"), Path("latest-lexemes.json.bz2")]
        with patch("scribe_data.utils.Path.glob", return_value=mock_existing_files):
            with patch("builtins.input", side_effect=["d", "n"]):
                with patch("scribe_data.utils.Path.unlink") as mock_unlink:
                    result = check_lexeme_dump_prompt_download(
                        "scribe_data/tests/cli/test_export_dir"
                    )
                    self.assertTrue(mock_unlink.called)
                    self.assertTrue(result)
