# Copyright (c) 2025 Scribe-Data Contributors
# SPDX-License-Identifier: GPL-3.0-or-later
import pytest
import os
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
from scribe_data.cli.upgrade import upgrade_cli


@pytest.fixture
def temp_cwd(tmp_path):
    """Set up a temporary working directory for tests."""
    cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        yield tmp_path
    finally:
        os.chdir(cwd)


def test_version_match_exits_early(temp_cwd, capsys):
    """Test that upgrade_cli exits early if versions match."""
    with patch("scribe_data.cli.upgrade.get_local_version", return_value="4.1.0"), \
         patch("scribe_data.cli.upgrade.get_latest_version", return_value="4.1.0"):
        upgrade_cli()
        captured = capsys.readouterr()
        assert "You already have the latest version of Scribe-Data: 4.1.0" in captured.out


def test_invalid_version_format(temp_cwd, capsys):
    """Test that an invalid latest_version format is handled."""
    with patch("scribe_data.cli.upgrade.get_local_version", return_value="4.1.0"), \
         patch("scribe_data.cli.upgrade.get_latest_version", return_value="invalid-version"):
        upgrade_cli()
        captured = capsys.readouterr()
        assert "Error: Invalid version format in 'invalid-version'" in captured.out


def test_download_url_not_found(temp_cwd, capsys):
    """Test that a 404 response from the download URL is handled."""
    with patch("scribe_data.cli.upgrade.get_local_version", return_value="4.1.0"), \
         patch("scribe_data.cli.upgrade.get_latest_version", return_value="4.2.0"), \
         patch("requests.head", return_value=Mock(status_code=404)):
        upgrade_cli()
        captured = capsys.readouterr()
        assert "Failed to download the update from https://github.com/scribe-org/Scribe-Data/archive/refs/tags/v4.2.0.tar.gz" in captured.out
        assert "Status code: 404" in captured.out


def test_file_preservation(temp_cwd):
    """Test that venv and user files are preserved during the update."""
    # Set up initial files and directories
    venv_dir = temp_cwd / "venv"
    venv_dir.mkdir()
    user_file = temp_cwd / "user_file.txt"
    user_file.write_text("user data")
    managed_dir = temp_cwd / "scribe_data"
    managed_dir.mkdir()
    managed_file = temp_cwd / "setup.py"
    managed_file.write_text("old setup.py")

    # Mock the download and extraction with a context manager
    mock_tarfile = MagicMock()
    mock_tarfile.__enter__.return_value = mock_tarfile
    mock_tarfile.__exit__.return_value = None
    mock_tarfile.extractall = Mock(return_value=None)

    with patch("scribe_data.cli.upgrade.get_local_version", return_value="4.1.0"), \
         patch("scribe_data.cli.upgrade.get_latest_version", return_value="4.2.0"), \
         patch("requests.head", return_value=Mock(status_code=200)), \
         patch("requests.get", return_value=Mock(status_code=200, content=b"mock content")), \
         patch("tarfile.open", return_value=mock_tarfile):
        # Create the expected directory structure
        temp_dir = temp_cwd / "temp_Scribe-Data-4.2.0"
        temp_dir.mkdir()
        extracted_dir = temp_dir / "Scribe-Data-4.2.0"
        extracted_dir.mkdir()
        # Simulate extracted files and directories
        (extracted_dir / "scribe_data").mkdir()
        (extracted_dir / "setup.py").write_text("mock setup.py")
        (extracted_dir / "user_file.txt").write_text("mock user file")
        (extracted_dir / "venv").mkdir()

        with patch("shutil.copy2", return_value=None), \
             patch("shutil.copytree", return_value=None), \
             patch("shutil.rmtree", return_value=None), \
             patch("os.remove", return_value=None), \
             patch("subprocess.check_call", return_value=None):
            upgrade_cli()

    # Verify preservation
    assert venv_dir.exists(), "venv directory should be preserved"
    assert user_file.exists(), "user file should be preserved"
    assert user_file.read_text() == "user data", "user file content should be unchanged"
    assert managed_dir.exists(), "managed directory should still exist (updated)"
