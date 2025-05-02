import pytest
import requests
from pathlib import Path
from unittest.mock import patch, Mock
from scribe_data.cli.upgrade import upgrade_cli
import os

@pytest.fixture
def temp_cwd(tmp_path):
    """Set up a temporary working directory."""
    cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        yield tmp_path
    finally:
        os.chdir(cwd)

def test_version_parsing(temp_cwd):
    """Test that invalid version formats are handled."""
    with patch("scribe_data.cli.upgrade.get_local_version", return_value="4.1.0"), \
         patch("scribe_data.cli.upgrade.get_latest_version", return_value="Scribe-Data 4.1.0"):
        with patch("sys.stdout", new=Mock()) as fake_out:
            upgrade_cli()
            assert "You already have the latest version" in fake_out.getvalue()

def test_invalid_download_url(temp_cwd):
    """Test handling of invalid download URLs."""
    with patch("scribe_data.cli.upgrade.get_local_version", return_value="4.1.0"), \
         patch("scribe_data.cli.upgrade.get_latest_version", return_value="4.2.0"), \
         patch("requests.head", return_value=Mock(status_code=404)):
        with patch("sys.stdout", new=Mock()) as fake_out:
            upgrade_cli()
            assert "Failed to find update" in fake_out.getvalue()

def test_preserve_venv(temp_cwd):
    """Test that venv and user files are preserved."""
    venv_dir = temp_cwd / "venv"
    venv_dir.mkdir()
    user_file = temp_cwd / "user.txt"
    user_file.write_text("user data")
    with patch("scribe_data.cli.upgrade.get_local_version", return_value="4.1.0"), \
         patch("scribe_data.cli.upgrade.get_latest_version", return_value="4.2.0"), \
         patch("requests.head", return_value=Mock(status_code=200)), \
         patch("requests.get", return_value=Mock(status_code=200, content=b"")), \
         patch("tarfile.open", return_value=Mock(extractall=lambda path: None)):
        class MockPath:
            def iterdir(self):
                return [Mock(is_dir=lambda: True, name="scribe_data"),
                        Mock(is_dir=lambda: False, name="setup.py"),
                        Mock(is_dir=lambda: True, name="venv")]
        with patch("pathlib.Path", return_value=MockPath()):
            upgrade_cli()
    assert venv_dir.exists()
    assert user_file.exists()