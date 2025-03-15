# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI version functionality.
"""

import unittest
from unittest.mock import patch

import pkg_resources

from scribe_data.cli.version import (
    get_latest_version,
    get_local_version,
    get_version_message,
)


class TestVersionFunctions(unittest.TestCase):
    @patch("pkg_resources.get_distribution")
    def test_get_local_version_installed(self, mock_get_distribution):
        mock_get_distribution.return_value.version = "1.0.0"
        self.assertEqual(get_local_version(), "1.0.0")

    @patch(
        "pkg_resources.get_distribution", side_effect=pkg_resources.DistributionNotFound
    )
    def test_get_local_version_not_installed(self, mock_get_distribution):
        self.assertEqual(get_local_version(), "Unknown (Not installed via pip)")

    @patch("requests.get")
    def test_get_latest_version(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"name": "v1.0.1"}
        self.assertEqual(get_latest_version(), "v1.0.1")

    @patch("requests.get", side_effect=Exception("Unable to fetch version"))
    def test_get_latest_version_failure(self, mock_get):
        self.assertEqual(get_latest_version(), "Unknown (Unable to fetch version)")

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
        expected_message = (
            "Scribe-Data vX.Y.Y (Upgrade available: Scribe-Data vX.Y.Z)\n"
            "To update: pip install --upgrade scribe-data"
        )
        self.assertEqual(get_version_message(), expected_message)

    @patch(
        "scribe_data.cli.version.get_local_version",
        return_value="Unknown (Not installed via pip)",
    )
    @patch(
        "scribe_data.cli.version.get_latest_version", return_value="Scribe-Data X.Y.Z"
    )
    def test_local_version_unknown(self, mock_latest_version, mock_local_version):
        """
        Test case where the local version is unknown.
        """
        expected_message = "Scribe-Data Unknown (Not installed via pip)"
        self.assertEqual(get_version_message(), expected_message)

    @patch("scribe_data.cli.version.get_local_version", return_value="X.Y.Z")
    @patch(
        "scribe_data.cli.version.get_latest_version",
        return_value="Unknown (Unable to fetch version)",
    )
    def test_latest_version_unknown(self, mock_latest_version, mock_local_version):
        """
        Test case where the latest version cannot be fetched.
        """
        expected_message = "Scribe-Data Unknown (Unable to fetch version)"
        self.assertEqual(get_version_message(), expected_message)
