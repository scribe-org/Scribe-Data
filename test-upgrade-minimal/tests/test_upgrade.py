# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the upgrade functionality of Scribe-Data.
"""

import shutil
from pathlib import Path

import pytest

from src.scribe_data.upgrade import compute_file_hash, needs_update, upgrade_cli


@pytest.fixture
def setup_test_env(tmp_path):
    """Set up a test environment with mock files and directories."""
    # Create a mock current working directory
    cwd = tmp_path / "current"
    cwd.mkdir()
    (cwd / "README.md").write_text("Original content")
    (cwd / "setup.py").write_text("Setup content")
    (cwd / "venv").mkdir()
    (cwd / "user_file.txt").write_text("User content")

    # Create a mock new version directory
    new_version = tmp_path / "new-version"
    new_version.mkdir()
    (new_version / "Scribe-Data-1.0.1").mkdir()
    new_dir = new_version / "Scribe-Data-1.0.1"
    (new_dir / "README.md").write_text("Updated content")
    (new_dir / "setup.py").write_text("Setup content")  # Same as original

    return cwd, new_version


def test_upgrade_preserves_venv(setup_test_env, monkeypatch):
    """Test that the upgrade process preserves the venv directory."""
    cwd, new_version = setup_test_env
    monkeypatch.chdir(cwd)
    # Mock the version check
    monkeypatch.setattr("src.scribe_data.upgrade.get_local_version", lambda: "1.0.0")
    monkeypatch.setattr("src.scribe_data.upgrade.get_latest_version", lambda: "v1.0.1")

    # Mock the download to use the local new_version directory
    def mock_copytree(src, dst, *args, **kwargs):
        # Create the destination directory if it doesn't exist
        dest_path = Path(dst) / "Scribe-Data-1.0.1"
        dest_path.mkdir(parents=True, exist_ok=True)
        # Manually copy files from new_version to dst
        for item in (new_version / "Scribe-Data-1.0.1").iterdir():
            if item.is_file():
                shutil.copy2(item, dest_path / item.name)

    monkeypatch.setattr("shutil.copytree", mock_copytree)
    # Mock cleanup to avoid errors
    monkeypatch.setattr("shutil.rmtree", lambda x: None)
    upgrade_cli()
    assert (cwd / "venv").exists()


def test_upgrade_preserves_user_files(setup_test_env, monkeypatch):
    """Test that the upgrade process preserves user-created files."""
    cwd, new_version = setup_test_env
    monkeypatch.chdir(cwd)
    monkeypatch.setattr("src.scribe_data.upgrade.get_local_version", lambda: "1.0.0")
    monkeypatch.setattr("src.scribe_data.upgrade.get_latest_version", lambda: "v1.0.1")

    def mock_copytree(src, dst, *args, **kwargs):
        shutil.copytree(
            str(new_version / "Scribe-Data-1.0.1"), str(dst), dirs_exist_ok=True
        )

    monkeypatch.setattr("shutil.copytree", mock_copytree)
    monkeypatch.setattr("shutil.rmtree", lambda x: None)
    upgrade_cli()
    assert (cwd / "user_file.txt").exists()
    assert (cwd / "user_file.txt").read_text() == "User content"


def test_upgrade_selective_update(setup_test_env, monkeypatch):
    """Test that only changed files are updated."""
    cwd, new_version = setup_test_env
    monkeypatch.chdir(cwd)
    monkeypatch.setattr("src.scribe_data.upgrade.get_local_version", lambda: "1.0.0")
    monkeypatch.setattr("src.scribe_data.upgrade.get_latest_version", lambda: "v1.0.1")

    def mock_copytree(src, dst, *args, **kwargs):
        shutil.copytree(
            str(new_version / "Scribe-Data-1.0.1"), str(dst), dirs_exist_ok=True
        )

    monkeypatch.setattr("shutil.copytree", mock_copytree)
    monkeypatch.setattr("shutil.rmtree", lambda x: None)
    upgrade_cli()
    assert (cwd / "README.md").read_text() == "Updated content"  # Updated
    assert (cwd / "setup.py").read_text() == "Setup content"  # Unchanged


def test_compute_file_hash():
    """Test the compute_file_hash function."""
    with open("temp_file.txt", "w") as f:
        f.write("Test content")
    with open("temp_file2.txt", "w") as f:
        f.write("Test content")
    hash1 = compute_file_hash(Path("temp_file.txt"))
    hash2 = compute_file_hash(Path("temp_file2.txt"))
    assert hash1 == hash2
    with open("temp_file3.txt", "w") as f:
        f.write("Different content")
    hash3 = compute_file_hash(Path("temp_file3.txt"))
    assert hash1 != hash3
    for f in ["temp_file.txt", "temp_file2.txt", "temp_file3.txt"]:
        Path(f).unlink()


def test_needs_update():
    """Test the needs_update function."""
    with open("file1.txt", "w") as f:
        f.write("Content")
    with open("file2.txt", "w") as f:
        f.write("Content")
    with open("file3.txt", "w") as f:
        f.write("Different")
    assert not needs_update(Path("file1.txt"), Path("file2.txt"))  # Same content
    assert needs_update(Path("file1.txt"), Path("file3.txt"))  # Different content
    assert needs_update(Path("file1.txt"), Path("nonexistent.txt"))  # Nonexistent file
    for f in ["file1.txt", "file2.txt", "file3.txt"]:
        if Path(f).exists():
            Path(f).unlink()
