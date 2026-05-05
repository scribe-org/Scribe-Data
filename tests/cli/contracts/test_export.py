# SPDX-FileCopyrightText: 2024 Scribe-Data contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tests for the export_contracts CLI command.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from scribe_data.cli.contracts.export import export_contracts


@pytest.fixture
def contracts_source(tmp_path: Path) -> Path:
    """
    Create a temporary contracts source directory with sample files.
    """
    source = tmp_path / "data_contracts"
    source.mkdir()
    (source / "en.yaml").write_text("language: english\n")
    (source / "de.yaml").write_text("language: german\n")
    return source


def test_export_contracts_source_missing(tmp_path: Path, capsys) -> None:
    """
    Test error when source directory does not exist.
    """
    fake_source = tmp_path / "nonexistent_contracts"

    with patch(
        "scribe_data.cli.contracts.export.Path.__truediv__",
        return_value=fake_source,
    ):
        with pytest.raises(AssertionError):
            export_contracts()


def test_export_contracts_overwrite_confirmed(
    tmp_path: Path, contracts_source: Path
) -> None:
    """
    Test overwrite when user confirms with y.
    """
    with patch(
        "scribe_data.cli.contracts.export.Path.__truediv__",
        return_value=contracts_source,
    ), patch("builtins.input", return_value="y"), \
       patch("shutil.copytree") as mock_copy, \
       patch("shutil.rmtree") as mock_rmtree, \
       patch.object(Path, "exists", return_value=True):
        export_contracts()

    mock_rmtree.assert_called_once()
    mock_copy.assert_called_once()


def test_export_contracts_overwrite_declined(
    tmp_path: Path, contracts_source: Path, capsys
) -> None:
    """
    Test export cancelled when user declines with n.
    """
    with patch(
        "scribe_data.cli.contracts.export.Path.__truediv__",
        return_value=contracts_source,
    ), patch("builtins.input", return_value="n"), \
       patch.object(Path, "exists", return_value=True):
        export_contracts()

    captured = capsys.readouterr()
    assert "cancelled" in captured.out.lower()


def test_export_contracts_files_copied(
    tmp_path: Path, contracts_source: Path
) -> None:
    """
    Test that copytree is called when source exists and output does not.
    """
    with patch(
        "scribe_data.cli.contracts.export.Path.__truediv__",
        return_value=contracts_source,
    ), patch("shutil.copytree") as mock_copy, \
       patch.object(Path, "exists", side_effect=[True, False]):
        export_contracts()

    mock_copy.assert_called_once()


def test_export_contracts_success_message(
    tmp_path: Path, contracts_source: Path, capsys
) -> None:
    """
    Test success message printed after export.
    """
    with patch(
        "scribe_data.cli.contracts.export.Path.__truediv__",
        return_value=contracts_source,
    ), patch("shutil.copytree"), \
       patch.object(Path, "exists", side_effect=[True, False]):
        export_contracts()

    captured = capsys.readouterr()
    assert "successfully" in captured.out.lower()