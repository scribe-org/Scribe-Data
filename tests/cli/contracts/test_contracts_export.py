# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the contract export functionality in the CLI.
"""

from pathlib import Path

from scribe_data.cli.contracts.export import export_contracts
from scribe_data.cli.contracts.filter import scribe_data_contracts


def test_export_creates_contracts_folder_in_dest(tmp_path: Path):
    export_contracts(tmp_path)
    exported_folder = tmp_path / "contracts"
    assert exported_folder.exists()
    assert exported_folder.is_dir()


def test_contracts_matches_source_folder(tmp_path):
    export_contracts(tmp_path)
    source_files = list(Path(scribe_data_contracts).rglob("*"))
    exported_files = list((tmp_path / "contracts").rglob("*"))
    assert len(source_files) == len(exported_files)


def test_export_error_message(tmp_path: Path, capsys):
    (tmp_path / "contracts").mkdir()
    export_contracts(tmp_path)
    captured = capsys.readouterr()
    assert "Error exporting data contracts:" in captured.out
