# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for generate emoji keywords process.
"""

from unittest.mock import patch

import pytest

from scribe_data.unicode.generate_emoji_keywords import generate_emoji


@pytest.fixture
def mock_pyicu():
    with (
        patch(
            "scribe_data.unicode.generate_emoji_keywords.check_and_install_pyicu"
        ) as mock_check_install,
        patch(
            "scribe_data.unicode.generate_emoji_keywords.check_if_pyicu_installed"
        ) as mock_check_installed,
    ):
        yield mock_check_install, mock_check_installed


@pytest.fixture
def mock_utils():
    with (
        patch(
            "scribe_data.unicode.generate_emoji_keywords.get_language_iso"
        ) as mock_iso,
        patch(
            "scribe_data.unicode.generate_emoji_keywords.export_formatted_data"
        ) as mock_export,
    ):
        yield mock_iso, mock_export


@pytest.fixture
def mock_process_unicode():
    with patch(
        "scribe_data.unicode.generate_emoji_keywords.gen_emoji_lexicon"
    ) as mock_lexicon:
        yield mock_lexicon


def test_generate_emoji_success(mock_pyicu, mock_utils, mock_process_unicode, tmp_path):
    mock_check_install, mock_check_installed = mock_pyicu
    mock_iso, mock_export = mock_utils
    mock_lexicon = mock_process_unicode

    mock_check_install.return_value = True
    mock_check_installed.return_value = True
    mock_iso.return_value = "en"
    mock_lexicon.return_value = {"smile": ["😊"]}

    generate_emoji("en", str(tmp_path))

    mock_check_install.assert_called_once()
    mock_check_installed.assert_called()
    mock_iso.assert_called_once_with(language="en")
    mock_lexicon.assert_called_once_with(language="en", emojis_per_keyword=3)
    mock_export.assert_called_once()


def test_generate_emoji_pyicu_not_installed(mock_pyicu):
    mock_check_install, mock_check_installed = mock_pyicu
    mock_check_install.return_value = False
    mock_check_installed.return_value = False

    generate_emoji("en")

    mock_check_install.assert_called_once()
    mock_check_installed.assert_called_once()


def test_generate_emoji_unsupported_language(mock_pyicu, mock_utils, tmp_path):
    mock_check_install, mock_check_installed = mock_pyicu
    mock_iso, _ = mock_utils

    mock_check_install.return_value = True
    mock_check_installed.return_value = True
    mock_iso.return_value = "xx"  # unsupported language

    generate_emoji("xx", str(tmp_path))

    mock_check_install.assert_called_once()
    mock_check_installed.assert_called()
    mock_iso.assert_called_once_with(language="xx")


def test_generate_emoji_output_dir_handling(
    mock_pyicu, mock_utils, mock_process_unicode, tmp_path
):
    mock_check_install, mock_check_installed = mock_pyicu
    mock_iso, mock_export = mock_utils
    mock_lexicon = mock_process_unicode

    mock_check_install.return_value = True
    mock_check_installed.return_value = True
    mock_iso.return_value = "en"
    mock_lexicon.return_value = {"smile": ["😊"]}

    # Test with different output dir formats.
    for output_dir in [str(tmp_path), "./test", "test"]:
        generate_emoji("en", output_dir)
        mock_export.assert_called()
        mock_export.reset_mock()
