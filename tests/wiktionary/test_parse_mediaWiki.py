# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for parse mediawiki process.
"""

import json
from unittest.mock import patch

import pytest

from scribe_data.wiktionary.parse_mediaWiki import (
    build_json_format,
    fetch_translation_page,
    parse_wikitext_for_translations,
    parse_wiktionary_translations,
)


@pytest.fixture
def mock_mediawiki_query():
    with patch("scribe_data.wiktionary.parse_mediaWiki.mediawiki_query") as mock_query:
        yield mock_query


@pytest.fixture
def mock_get_language_from_iso():
    with patch(
        "scribe_data.wiktionary.parse_mediaWiki.get_language_from_iso"
    ) as mock_iso:
        yield mock_iso


def test_fetch_translation_page_success(mock_mediawiki_query):
    # Setup mock response
    mock_response = {
        "query": {"pages": {"123": {"revisions": [{"*": "test wikitext"}]}}}
    }
    mock_mediawiki_query.return_value = mock_response

    result = fetch_translation_page("test")
    assert result == "test wikitext"
    mock_mediawiki_query.assert_called_once_with(word="test")


def test_fetch_translation_page_no_data(mock_mediawiki_query):
    mock_mediawiki_query.return_value = {}
    result = fetch_translation_page("test")
    assert result == ""
    mock_mediawiki_query.assert_called_once_with(word="test")


def test_parse_wikitext_for_translations():
    wikitext = """
===Noun===
{{trans-top|test context}}
* English: {{t+|en|test}}
* French: {{t+|fr|essai}}
    """

    result = parse_wikitext_for_translations(wikitext)
    assert result == {
        "en": [
            {"translation": "test", "part_of_speech": "Noun", "context": "test context"}
        ],
        "fr": [
            {
                "translation": "essai",
                "part_of_speech": "Noun",
                "context": "test context",
            }
        ],
    }


def test_build_json_format(mock_get_language_from_iso):
    # Setup mock language conversion.
    mock_get_language_from_iso.side_effect = lambda x: {
        "en": "English",
        "fr": "French",
    }[x]

    translations = {
        "en": [
            {"translation": "test", "part_of_speech": "Noun", "context": "test context"}
        ],
        "fr": [
            {
                "translation": "essai",
                "part_of_speech": "Noun",
                "context": "test context",
            }
        ],
    }

    result = build_json_format("test", translations)
    expected = {
        "test": {
            "English": {
                "Noun": {"1": {"description": "test context", "translations": "test"}}
            },
            "French": {
                "Noun": {"1": {"description": "test context", "translations": "essai"}}
            },
        }
    }
    assert result == expected


def test_parse_wiktionary_translations(mock_mediawiki_query, tmp_path):
    # Setup mock responses.
    mock_mediawiki_query.return_value = {
        "query": {
            "pages": {
                "123": {
                    "revisions": [
                        {
                            "*": """
===Noun===
{{trans-top|test context}}
* English: {{t+|en|test}}
                    """
                        }
                    ]
                }
            }
        }
    }

    # Test with temporary output directory.
    output_dir = tmp_path / "output"
    parse_wiktionary_translations("test", output_dir)

    # Verify output file.
    output_file = output_dir / "test.json"
    assert output_file.exists()

    with open(output_file, "r") as f:
        data = json.load(f)
        assert "test" in data
        assert "English" in data["test"]
        assert "Noun" in data["test"]["English"]


def test_parse_wiktionary_translations_no_translations(mock_mediawiki_query, capsys):
    mock_mediawiki_query.return_value = {
        "query": {"pages": {"123": {"revisions": [{"*": ""}]}}}
    }

    parse_wiktionary_translations("test")
    captured = capsys.readouterr()
    assert "No translations found" in captured.out
