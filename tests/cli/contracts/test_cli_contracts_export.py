# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tests for the export_contracts CLI command.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from conftest import cleanup_default_directories

from scribe_data.cli.contracts.export import export_contracts
from scribe_data.utils import DEFAULT_CONTRACTS_EXPORT_DIR


@pytest.fixture
def contracts_source(tmp_path: Path) -> Path:
    """
    Create a temporary contracts source directory with sample files.
    """
    source = tmp_path / "source_contracts"
    source.mkdir()
    (source / "en.yaml").write_text("language: english\n")
    (source / "de.yaml").write_text("language: german\n")
    return source


def test_cli_contracts_export_new_dir(tmp_path: Path, contracts_source: Path) -> None:
    """
    Test export when no existing contracts folder.
    """
    with patch(
        "scribe_data.cli.contracts.export.Path.__truediv__",
        return_value=contracts_source,
    ):
        export_contracts()

    assert DEFAULT_CONTRACTS_EXPORT_DIR.exists()
    assert (DEFAULT_CONTRACTS_EXPORT_DIR / "en.yaml").exists()
    assert (DEFAULT_CONTRACTS_EXPORT_DIR / "de.yaml").exists()


def test_cli_contracts_export_success_message(
    tmp_path: Path, contracts_source: Path, capsys
) -> None:
    """
    Test success message after fresh export.
    """
    cleanup_default_directories()
    with patch(
        "scribe_data.cli.contracts.export.Path.__truediv__",
        return_value=contracts_source,
    ):
        export_contracts()

    captured = capsys.readouterr()
    assert "successfully exported" in captured.out.lower()


def test_cli_contracts_export_overwrite_confirmed(
    tmp_path: Path, contracts_source: Path
) -> None:
    """
    Test overwrite when user confirms with y.
    """
    (DEFAULT_CONTRACTS_EXPORT_DIR / "old.yaml").write_text("old data")

    with (
        patch(
            "scribe_data.cli.contracts.export.Path.__truediv__",
            return_value=contracts_source,
        ),
        patch("builtins.input", return_value="y"),
    ):
        export_contracts()

    assert (DEFAULT_CONTRACTS_EXPORT_DIR / "en.yaml").exists()
    assert not (DEFAULT_CONTRACTS_EXPORT_DIR / "old.yaml").exists()


def test_cli_contracts_export_overwrite_declined(
    tmp_path: Path, contracts_source: Path, capsys
) -> None:
    """
    Test export cancelled when user declines with n.
    """
    (DEFAULT_CONTRACTS_EXPORT_DIR / "old.yaml").write_text("old data")

    with (
        patch(
            "scribe_data.cli.contracts.export.Path.__truediv__",
            return_value=contracts_source,
        ),
        patch("builtins.input", return_value="n"),
    ):
        export_contracts()

    captured = capsys.readouterr()
    assert "cancelled" in captured.out.lower()
    assert (DEFAULT_CONTRACTS_EXPORT_DIR / "old.yaml").exists()


def test_cli_contracts_export_source_not_found(tmp_path: Path) -> None:
    """
    Test assertion error when source directory not found.
    """
    fake_source = tmp_path / "nonexistent"

    with patch(
        "scribe_data.cli.contracts.export.Path.__truediv__",
        return_value=fake_source,
    ):
        with pytest.raises(AssertionError):
            export_contracts()


def test_cli_contracts_export_files_content(
    tmp_path: Path, contracts_source: Path
) -> None:
    """
    Test that exported files have correct content.
    """
    cleanup_default_directories()
    with patch(
        "scribe_data.cli.contracts.export.Path.__truediv__",
        return_value=contracts_source,
    ):
        export_contracts()

    assert (
        DEFAULT_CONTRACTS_EXPORT_DIR / "en.yaml"
    ).read_text() == "language: english\n"
    assert (
        DEFAULT_CONTRACTS_EXPORT_DIR / "de.yaml"
    ).read_text() == "language: german\n"


def test_cli_contracts_export_overwrite_default_declined(
    tmp_path: Path, contracts_source: Path, capsys
) -> None:
    """
    Test that default response cancels export.
    """
    with (
        patch(
            "scribe_data.cli.contracts.export.Path.__truediv__",
            return_value=contracts_source,
        ),
        patch("builtins.input", return_value=""),
    ):
        export_contracts()

    captured = capsys.readouterr()
    assert "cancelled" in captured.out.lower()
