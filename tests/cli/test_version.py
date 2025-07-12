# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI version functionality.
"""

import importlib.metadata
import unittest
from unittest.mock import patch

from scribe_data.cli.version import (
    UNKNOWN_VERSION_NOT_FETCHED,
    UNKNOWN_VERSION_NOT_PIP,
    get_latest_version,
    get_local_version,
    get_version_message,
)


class TestVersionFunctions(unittest.TestCase):
    @patch("scribe_data.cli.version.importlib.metadata.version")
    def test_get_local_version_installed(self, mock_version):
        mock_version.return_value = "1.0.0"
        self.assertEqual(get_local_version(), "1.0.0")

    @patch(
        "scribe_data.cli.version.importlib.metadata.version",
        side_effect=importlib.metadata.PackageNotFoundError,
    )
    def test_get_local_version_not_installed(self, mock_version):
        self.assertEqual(get_local_version(), UNKNOWN_VERSION_NOT_PIP)

    @patch("requests.get")
    def test_get_latest_version(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"name": "v1.0.1"}
        self.assertEqual(get_latest_version(), "v1.0.1")

    @patch("requests.get", side_effect=Exception("Unable to fetch version"))
    def test_get_latest_version_failure(self, mock_get):
        self.assertEqual(get_latest_version(), UNKNOWN_VERSION_NOT_FETCHED)

    @patch("scribe_data.cli.version.get_local_version", return_value="X.Y.Z")
    @patch(
        "scribe_data.cli.version.get_latest_version", return_value="Scribe-Data X.Y.Z"
    )
    def test_get_version_message_up_to_date(
        self, mock_latest_version, mock_local_version
    ):
        """
        Tests the scenario where the local version is up to date with the latest version.
        """
        expected_message = "Scribe-Data vX.Y.Z"
        self.assertEqual(get_version_message(), expected_message)

    @patch("scribe_data.cli.version.get_local_version", return_value="X.Y.Y")
    @patch(
        "scribe_data.cli.version.get_latest_version", return_value="Scribe-Data X.Y.Z"
    )
    def test_upgrade_available(self, mock_latest_version, mock_local_version):
        """
        Test case where a newer version is available.
        """
        expected_message = "Scribe-Data vX.Y.Y (Upgrade available: Scribe-Data vX.Y.Z). To upgrade: scribe-data -u"
        self.assertEqual(get_version_message(), expected_message)

    @patch(
        "scribe_data.cli.version.get_local_version",
        return_value=UNKNOWN_VERSION_NOT_PIP,
    )
    @patch(
        "scribe_data.cli.version.get_latest_version", return_value="Scribe-Data X.Y.Z"
    )
    def test_local_version_unknown(self, mock_latest_version, mock_local_version):
        """
        Test case where the local version is unknown.
        """
        self.assertEqual(get_version_message(), UNKNOWN_VERSION_NOT_PIP)

    @patch("scribe_data.cli.version.get_local_version", return_value="X.Y.Z")
    @patch(
        "scribe_data.cli.version.get_latest_version",
        return_value=UNKNOWN_VERSION_NOT_FETCHED,
    )
    def test_latest_version_unknown(self, mock_latest_version, mock_local_version):
        """
        Test case where the latest version cannot be fetched.
        """
        self.assertEqual(get_version_message(), UNKNOWN_VERSION_NOT_FETCHED)


if __name__ == "__main__":
    unittest.main()
