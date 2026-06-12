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
    source = tmp_path / "source_contracts"
    source.mkdir()
    (source / "en.yaml").write_text("language: english\n")
    (source / "de.yaml").write_text("language: german\n")
    return source


def test_cli_contracts_export_new(tmp_path: Path, contracts_source: Path) -> None:
    """
    Test fresh export when no existing contracts folder.
    """
    output_dir = tmp_path / "output" / "contracts"

    with patch(
        "scribe_data.cli.contracts.export.Path.__truediv__",
        return_value=contracts_source,
    ):
        export_contracts(output_dir=output_dir)

    assert output_dir.exists()
    assert (output_dir / "en.yaml").exists()
    assert (output_dir / "de.yaml").exists()


def test_cli_contracts_export_success(
    tmp_path: Path, contracts_source: Path, capsys
) -> None:
    """
    Test success message after fresh export.
    """
    output_dir = tmp_path / "output" / "contracts"

    with patch(
        "scribe_data.cli.contracts.export.Path.__truediv__",
        return_value=contracts_source,
    ):
        export_contracts(output_dir=output_dir)

    captured = capsys.readouterr()
    assert "successfully exported" in captured.out.lower()


def test_cli_contracts_export_overwrite_confirmed(
    tmp_path: Path, contracts_source: Path
) -> None:
    """
    Test overwrite when user confirms with y.
    """
    output_dir = tmp_path / "output" / "contracts"
    output_dir.mkdir(parents=True)
    (output_dir / "old.yaml").write_text("old data")

    with (
        patch(
            "scribe_data.cli.contracts.export.Path.__truediv__",
            return_value=contracts_source,
        ),
        patch("builtins.input", return_value="y"),
    ):
        export_contracts(output_dir=output_dir)

    assert (output_dir / "en.yaml").exists()
    assert not (output_dir / "old.yaml").exists()


def test_cli_contracts_export_overwrite_declined(
    tmp_path: Path, contracts_source: Path, capsys
) -> None:
    """
    Test export cancelled when user declines with n.
    """
    output_dir = tmp_path / "output" / "contracts"
    output_dir.mkdir(parents=True)
    (output_dir / "old.yaml").write_text("old data")

    with (
        patch(
            "scribe_data.cli.contracts.export.Path.__truediv__",
            return_value=contracts_source,
        ),
        patch("builtins.input", return_value="n"),
    ):
        export_contracts(output_dir=output_dir)

    captured = capsys.readouterr()
    assert "cancelled" in captured.out.lower()
    assert (output_dir / "old.yaml").exists()


def test_cli_contracts_export_source_not_found(tmp_path: Path) -> None:
    """
    Test assertion error when source directory not found.
    """
    fake_source = tmp_path / "nonexistent"
    output_dir = tmp_path / "output" / "contracts"

    with patch(
        "scribe_data.cli.contracts.export.Path.__truediv__",
        return_value=fake_source,
    ):
        with pytest.raises(AssertionError):
            export_contracts(output_dir=output_dir)


def test_cli_contracts_export_files_content(
    tmp_path: Path, contracts_source: Path
) -> None:
    """
    Test that exported files have correct content.
    """
    output_dir = tmp_path / "output" / "contracts"

    with patch(
        "scribe_data.cli.contracts.export.Path.__truediv__",
        return_value=contracts_source,
    ):
        export_contracts(output_dir=output_dir)

    assert (output_dir / "en.yaml").read_text() == "language: english\n"
    assert (output_dir / "de.yaml").read_text() == "language: german\n"


def test_cli_contracts_export_overwrite_default_declined(
    tmp_path: Path, contracts_source: Path, capsys
) -> None:
    """
    Test that default response cancels export.
    """
    output_dir = tmp_path / "output" / "contracts"
    output_dir.mkdir(parents=True)

    with (
        patch(
            "scribe_data.cli.contracts.export.Path.__truediv__",
            return_value=contracts_source,
        ),
        patch("builtins.input", return_value=""),
    ):
        export_contracts(output_dir=output_dir)

    captured = capsys.readouterr()
    assert "cancelled" in captured.out.lower()
