# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the contract checking functionality in the CLI.
"""

import json
from unittest.mock import patch

import pytest

from scribe_data.cli.contracts.check import (
    check_contract_data_completeness,
    check_contracts,
    print_missing_forms,
)


@pytest.fixture
def mock_export_dir(tmp_path):
    """
    Create a mock export directory structure for testing.
    """
    # Create language directories.
    en_dir = tmp_path / "english"
    es_dir = tmp_path / "spanish"
    en_dir.mkdir()
    es_dir.mkdir()

    en_nouns = {
        "word1": {"singular": "word1", "plural": "words1"},
        "word2": {"singular": "word2", "plural": "words2"},
    }
    en_verbs = {
        "verb1": {"infinitive": "verb1", "present": "verbs1", "past": "verbed1"},
        "verb2": {"infinitive": "verb2", "present": "verbs2", "past": "verbed2"},
    }
    es_nouns = {
        "palabra1": {
            "singular": "palabra1",
            "plural": "palabras1",
            "masculine": "m",
            "feminine": "f",
        },
        "palabra2": {
            "singular": "palabra2",
            "plural": "palabras2",
            "masculine": "m",
            "feminine": "f",
        },
    }

    with open(en_dir / "nouns.json", "w") as f:
        json.dump(en_nouns, f)
    with open(en_dir / "verbs.json", "w") as f:
        json.dump(en_verbs, f)
    with open(es_dir / "nouns.json", "w") as f:
        json.dump(es_nouns, f)

    return tmp_path


@pytest.fixture
def mock_contract_metadata():
    """
    Mock contract metadata with proper structure.
    """
    return {
        "nouns": {"numbers": ["singular", "plural"], "genders": []},
        "verbs": {"conjugations": ["infinitive", "present", "past", "future"]},
    }


@patch("scribe_data.cli.contracts.check.check_contract_data_completeness")
@patch("scribe_data.cli.contracts.check.print_missing_forms")
def test_check_contracts_with_dir(mock_print, mock_check, mock_export_dir):
    """
    Test check_contracts with a specified directory.
    """
    mock_check.return_value = {"English": {"verbs": ["future"]}}

    check_contracts(output_dir=str(mock_export_dir))

    mock_check.assert_called_once_with(mock_export_dir)
    mock_print.assert_called_once_with({"English": {"verbs": ["future"]}})


@patch("scribe_data.cli.contracts.check.check_contract_data_completeness")
@patch("scribe_data.cli.contracts.check.print_missing_forms")
def test_check_contracts_default_dir(mock_print, mock_check):
    """
    Test check_contracts with default directory.
    """
    mock_check.return_value = {}

    with patch("scribe_data.cli.contracts.check.Path") as mock_path:
        mock_path.return_value.exists.return_value = True

        check_contracts()

        mock_check.assert_called_once()
        mock_print.assert_called_once_with({})


@patch("scribe_data.cli.contracts.check.Path")
def test_check_contracts_nonexistent_dir(mock_path):
    """
    Test check_contracts with a nonexistent directory.
    """
    mock_path.return_value.exists.return_value = False

    with patch("builtins.print") as mock_print:
        check_contracts(output_dir="nonexistent_dir")

        mock_print.assert_called_once()
        assert "Error: Directory" in mock_print.call_args[0][0]
        assert "does not exist" in mock_print.call_args[0][0]


@patch("scribe_data.utils.get_language_iso")
@patch("scribe_data.cli.contracts.export.filter_contract_metadata")
def test_check_contract_data_completeness_json_error(
    mock_filter_metadata, mock_get_iso, mock_export_dir, mock_contract_metadata
):
    """
    Test handling of JSON errors in data files.
    """
    mock_get_iso.return_value = "en"
    mock_filter_metadata.return_value = mock_contract_metadata

    # Execute with patched open to cause JSON error.
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True  # make paths exist
        with patch("builtins.open", side_effect=json.JSONDecodeError("Error", "", 0)):
            with patch("builtins.print") as mock_print:
                check_contract_data_completeness(mock_export_dir)

                mock_print.assert_called()
                assert "Error reading" in mock_print.call_args[0][0]


def test_print_missing_forms_none():
    """
    Test print_missing_forms with no missing forms.
    """
    # Execute with mock print to capture output.
    with patch("builtins.print") as mock_print:
        print_missing_forms({})

        mock_print.assert_called_once_with(
            "All languages have complete data contracts!"
        )


def test_print_missing_forms_with_missing():
    """
    Test print_missing_forms with missing forms.
    """
    missing_forms = {
        "English": {
            "nouns": ["genitive", "dative"],
            "verbs": ["future", "conditional"],
        },
        "Spanish": {"verbs": ["subjunctive"]},
    }

    # Execute with mock print to capture output.
    with patch("builtins.print") as mock_print:
        print_missing_forms(missing_forms)

        # Get all print calls without examining specific order.
        call_strings = [call[0][0] for call in mock_print.call_args_list]
        assert "Missing Forms:" in call_strings
        assert any("English:" in s for s in call_strings)
        assert any("  Nouns:" in s for s in call_strings)
        assert any("    - genitive" in s for s in call_strings)
        assert any("    - dative" in s for s in call_strings)
        assert any("  Verbs:" in s for s in call_strings)
        assert any("    - future" in s for s in call_strings)
        assert any("    - conditional" in s for s in call_strings)
        assert any("Spanish:" in s for s in call_strings)
        assert any("  Verbs:" in s for s in call_strings)
        assert any("    - subjunctive" in s for s in call_strings)
