# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the upgrade CLI functionality.
"""

import subprocess
import sys
from unittest.mock import call, patch

from scribe_data.cli.upgrade import upgrade_cli
from scribe_data.cli.version import UNKNOWN_VERSION_NOT_FETCHED


class TestUpgradeCLI:
    """Test cases for the upgrade_cli function."""

    @patch("scribe_data.cli.upgrade.get_local_version")
    @patch("scribe_data.cli.upgrade.get_latest_version")
    @patch("builtins.print")
    def test_upgrade_cli_unable_to_fetch_latest_version(
        self, mock_print, mock_get_latest, mock_get_local
    ):
        """Test upgrade_cli when unable to fetch latest version from GitHub."""
        mock_get_latest.return_value = UNKNOWN_VERSION_NOT_FETCHED
        mock_get_local.return_value = "5.0.0"

        upgrade_cli()

        mock_print.assert_called_once_with(
            "Unable to fetch the latest version from GitHub. Please check the GitHub repository or your internet connection."
        )

    @patch("scribe_data.cli.upgrade.get_local_version")
    @patch("scribe_data.cli.upgrade.get_latest_version")
    @patch("builtins.print")
    def test_upgrade_cli_already_latest_version(
        self, mock_print, mock_get_latest, mock_get_local
    ):
        """Test upgrade_cli when already on latest version."""
        mock_get_local.return_value = "5.1.0"
        mock_get_latest.return_value = "Scribe-Data v5.1.0"

        upgrade_cli()

        mock_print.assert_called_once_with(
            "You already have the latest version of Scribe-Data."
        )

    @patch("scribe_data.cli.upgrade.get_local_version")
    @patch("scribe_data.cli.upgrade.get_latest_version")
    @patch("builtins.print")
    def test_upgrade_cli_local_version_higher(
        self, mock_print, mock_get_latest, mock_get_local
    ):
        """Test upgrade_cli when local version is higher than released version."""
        mock_get_local.return_value = "5.2.0"
        mock_get_latest.return_value = "Scribe-Data v5.1.0"

        upgrade_cli()

        expected_message = (
            "Scribe-Data v5.2.0 is higher than the currently released version Scribe-Data v5.1.0. "
            "Hopefully this is a development build, and if so, thanks for your work on Scribe-Data! "
            "If not, please report this to the team at https://github.com/scribe-org/Scribe-Data/issues."
        )
        mock_print.assert_called_once_with(expected_message)

    @patch("scribe_data.cli.upgrade.subprocess.check_call")
    @patch("scribe_data.cli.upgrade.get_local_version")
    @patch("scribe_data.cli.upgrade.get_latest_version")
    @patch("builtins.print")
    def test_upgrade_cli_successful_upgrade(
        self, mock_print, mock_get_latest, mock_get_local, mock_check_call
    ):
        """Test upgrade_cli when upgrade is needed and successful."""
        mock_get_local.return_value = "5.0.0"
        mock_get_latest.return_value = "Scribe-Data v5.1.0"
        mock_check_call.return_value = None

        upgrade_cli()

        expected_calls = [
            call("Current version: 5.0.0"),
            call("Latest version: 5.1.0"),
            call("Updating Scribe-Data with pip..."),
        ]
        mock_print.assert_has_calls(expected_calls)

        mock_check_call.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "--upgrade", "scribe-data"]
        )

    @patch("scribe_data.cli.upgrade.subprocess.check_call")
    @patch("scribe_data.cli.upgrade.get_local_version")
    @patch("scribe_data.cli.upgrade.get_latest_version")
    @patch("builtins.print")
    def test_upgrade_cli_subprocess_error(
        self, mock_print, mock_get_latest, mock_get_local, mock_check_call
    ):
        """Test upgrade_cli when subprocess.check_call fails."""
        mock_get_local.return_value = "5.0.0"
        mock_get_latest.return_value = "Scribe-Data v5.1.0"

        error = subprocess.CalledProcessError(1, "pip")
        mock_check_call.side_effect = error

        upgrade_cli()

        # Verify error message is printed
        error_calls = [
            call
            for call in mock_print.call_args_list
            if "Failed to install" in str(call)
        ]
        assert len(error_calls) == 1
        assert "Failed to install the latest version of Scribe-Data" in str(
            error_calls[0]
        )

    @patch("scribe_data.cli.upgrade.get_local_version")
    @patch("scribe_data.cli.upgrade.get_latest_version")
    @patch("builtins.print")
    def test_upgrade_cli_version_parsing_edge_cases(
        self, mock_print, mock_get_latest, mock_get_local
    ):
        """Test upgrade_cli with version strings containing whitespace."""
        mock_get_local.return_value = "  5.1.0  "
        mock_get_latest.return_value = "v5.1.0"

        upgrade_cli()

        mock_print.assert_called_once_with(
            "You already have the latest version of Scribe-Data."
        )

    @patch("scribe_data.cli.upgrade.get_local_version")
    @patch("scribe_data.cli.upgrade.get_latest_version")
    @patch("builtins.print")
    def test_upgrade_cli_string_comparison_edge_case(
        self, mock_print, mock_get_latest, mock_get_local
    ):
        """Test version comparison edge case where semantic versioning works correctly."""
        # This tests proper semantic version comparison
        # Semantically: 5.10.0 > 5.2.0 (5.10.0 is the 10th minor version)
        mock_get_local.return_value = "5.10.0"
        mock_get_latest.return_value = "Scribe-Data v5.2.0"

        upgrade_cli()

        # With proper semantic versioning, 5.10.0 > 5.2.0 so it shows higher version message
        expected_message = (
            "Scribe-Data v5.10.0 is higher than the currently released version Scribe-Data v5.2.0. "
            "Hopefully this is a development build, and if so, thanks for your work on Scribe-Data! "
            "If not, please report this to the team at https://github.com/scribe-org/Scribe-Data/issues."
        )
        mock_print.assert_called_once_with(expected_message)

    @patch("scribe_data.cli.upgrade.get_local_version")
    @patch("scribe_data.cli.upgrade.get_latest_version")
    @patch("builtins.print")
    def test_upgrade_cli_proper_higher_version_scenario(
        self, mock_print, mock_get_latest, mock_get_local
    ):
        """Test upgrade_cli when local version is legitimately higher than released version."""
        # Test with a version that's clearly higher to trigger the "higher version" message
        mock_get_local.return_value = "6.0.0"
        mock_get_latest.return_value = "Scribe-Data v5.1.0"

        upgrade_cli()

        expected_message = (
            "Scribe-Data v6.0.0 is higher than the currently released version Scribe-Data v5.1.0. "
            "Hopefully this is a development build, and if so, thanks for your work on Scribe-Data! "
            "If not, please report this to the team at https://github.com/scribe-org/Scribe-Data/issues."
        )
        mock_print.assert_called_once_with(expected_message)

    @patch("scribe_data.cli.upgrade.get_local_version")
    @patch("scribe_data.cli.upgrade.get_latest_version")
    @patch("builtins.print")
    def test_upgrade_cli_different_version_formats(
        self, mock_print, mock_get_latest, mock_get_local
    ):
        """Test upgrade_cli with different version string formats."""
        mock_get_local.return_value = "5.1.0"
        mock_get_latest.return_value = "Scribe-Data v5.1.0"

        upgrade_cli()

        mock_print.assert_called_once_with(
            "You already have the latest version of Scribe-Data."
        )

    @patch("scribe_data.cli.upgrade.get_local_version")
    @patch("scribe_data.cli.upgrade.get_latest_version")
    @patch("builtins.print")
    def test_upgrade_cli_semantic_version_upgrade_needed(
        self, mock_print, mock_get_latest, mock_get_local
    ):
        """Test upgrade_cli when semantic version upgrade is needed."""
        mock_get_local.return_value = "5.0.9"
        mock_get_latest.return_value = "Scribe-Data v5.1.0"

        with patch("scribe_data.cli.upgrade.subprocess.check_call") as mock_check_call:
            mock_check_call.return_value = None
            upgrade_cli()

            expected_calls = [
                call("Current version: 5.0.9"),
                call("Latest version: 5.1.0"),
                call("Updating Scribe-Data with pip..."),
            ]
            mock_print.assert_has_calls(expected_calls)
            mock_check_call.assert_called_once()

    @patch("scribe_data.cli.upgrade.get_local_version")
    @patch("scribe_data.cli.upgrade.get_latest_version")
    @patch("builtins.print")
    def test_upgrade_cli_with_empty_version_strings(
        self, mock_print, mock_get_latest, mock_get_local
    ):
        """Test upgrade_cli with edge case of empty version strings."""
        mock_get_local.return_value = ""
        mock_get_latest.return_value = "Scribe-Data v5.1.0"

        with patch("scribe_data.cli.upgrade.subprocess.check_call") as mock_check_call:
            mock_check_call.return_value = None
            upgrade_cli()

            # Should attempt upgrade with empty local version
            expected_calls = [
                call("Current version: "),
                call("Latest version: 5.1.0"),
                call("Updating Scribe-Data with pip..."),
            ]
            mock_print.assert_has_calls(expected_calls)

            # Verify subprocess was called
            mock_check_call.assert_called_once_with(
                [sys.executable, "-m", "pip", "install", "--upgrade", "scribe-data"]
            )
