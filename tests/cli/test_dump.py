# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI dump functionality.
"""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from scribe_data.wikidata.parse_dump import LexemeProcessor, parse_dump
from scribe_data.wikidata.wikidata_utils import parse_wd_lexeme_dump

# Test line.
Sample_Lexeme_Line = """
{
    "id": "L1",
    "lemmas": {
        "en": {
            "value": "test",
            "language": "en"
        }
    },
    "lexicalCategory": "Q1084",
    "language": "Q1860",
    "forms": [
        {
            "id": "L1-F1",
            "representations": {
                "en": {
                    "value": "tests",
                    "language": "en"
                }
            },
            "grammaticalFeatures": ["Q146786"]
        }
    ],
    "senses": [
        {
            "glosses": {
                "fr": {
                    "value": "tester",
                    "language": "fr"
                }
            }
        }
    ],
    "modified": "2023-01-01T00:00:00Z"
}
"""


@pytest.fixture
def lexeme_processor() -> LexemeProcessor:
    return LexemeProcessor(
        target_lang=["english"],
        parse_type=["translations", "form"],
        data_types=["nouns"],
    )


def test_lexeme_processor_initialization(lexeme_processor: LexemeProcessor) -> None:
    """
    Test LexemeProcessor initialization with basic parameters.
    """
    assert "english" in lexeme_processor.target_lang
    assert "translations" in lexeme_processor.parse_type
    assert "form" in lexeme_processor.parse_type
    assert "nouns" in lexeme_processor.data_types


@patch("builtins.open", new_callable=mock_open, read_data=Sample_Lexeme_Line)
@patch("bz2.open")
def test_process_file(
    mock_bz2_open: MagicMock, mock_file: MagicMock, lexeme_processor: LexemeProcessor
) -> None:
    """
    Test processing a file with sample lexeme data.
    """
    mock_bz2_open.return_value.__enter__.return_value = mock_file()

    # Mock Path.stat() to return a size.
    with patch("pathlib.Path.stat") as mock_stat:
        mock_stat.return_value.st_size = 1000
        lexeme_processor.process_file("test.json.bz2")

    # Verify that stats were updated.
    assert lexeme_processor.stats["processed_entries"] > 0


@patch("scribe_data.wikidata.parse_dump.LexemeProcessor")
def test_parse_dump(mock_processor: MagicMock) -> None:
    """
    Test the parse_dump function.
    """
    parse_dump(
        language="english",
        parse_type=["translations"],
        data_types=["nouns"],
        file_path="test.json.bz2",
    )
    mock_processor.assert_called_once()


@patch("scribe_data.wikidata.wikidata_utils.Path")
@patch("scribe_data.wikidata.wikidata_utils.wd_lexeme_dump_download_wrapper")
@patch("scribe_data.wikidata.wikidata_utils.parse_dump")
def test_parse_wd_lexeme_dump(
    mock_parse_dump: MagicMock, mock_download: MagicMock, mock_path_class: MagicMock
) -> None:
    """
    Test the parse_wd_lexeme_dump function.
    """
    # Setup mock to return a valid file path and Path behavior.
    test_file_path = "test.json.bz2"
    mock_download.return_value = test_file_path

    # Setup Path mock.
    mock_path_instance = mock_path_class.return_value
    mock_path_instance.exists.return_value = True
    mock_path_class.side_effect = lambda x: mock_path_instance

    # Test with specific language.
    parse_wd_lexeme_dump(
        language="english",
        wikidata_dump_type=["translations"],
        data_types=["nouns"],
        interactive_mode=False,
    )

    # Verify parse_dump was called with correct arguments.
    mock_parse_dump.assert_called_once_with(
        language="english",
        parse_type=["translations"],
        data_types=["nouns"],
        file_path=str(test_file_path),
        output_dir=None,
        overwrite_all=False,
    )

    # Test with "all" languages.
    mock_parse_dump.reset_mock()
    mock_download.return_value = test_file_path
    mock_path_instance.exists.return_value = True

    parse_wd_lexeme_dump(
        language="all",
        wikidata_dump_type=["translations"],
        data_types=["nouns"],
        interactive_mode=False,
    )

    # Verify parse_dump was called with expanded language list.
    mock_parse_dump.assert_called_once()
    args, kwargs = mock_parse_dump.call_args
    assert isinstance(kwargs["language"], list)
    assert len(kwargs["language"]) > 0
    assert kwargs["parse_type"] == ["translations"]
    assert kwargs["data_types"] == ["nouns"]


def test_parse_wd_lexeme_dump_no_file() -> None:
    """
    Test parse_wd_lexeme_dump when no file is found.
    """
    with patch(
        "scribe_data.wikidata.wikidata_utils.wd_lexeme_dump_download_wrapper"
    ) as mock_download:
        mock_download.return_value = None

        # Should not raise an exception but return without calling parse_dump.
        result = parse_wd_lexeme_dump(
            language="english",
            wikidata_dump_type=["translations"],
            data_types=["nouns"],
        )

        assert result is None


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ({"translations": True}, True),
        ({"form": True}, True),
        ({"total": True}, True),
    ],
)
def test_parse_types(test_input: dict[str, bool], expected: bool) -> None:
    """
    Test different parse types.
    """
    processor = LexemeProcessor(
        target_lang="english", parse_type=list(test_input.keys()), data_types=["nouns"]
    )
    assert (
        any(parse_type in processor.parse_type for parse_type in test_input.keys())
        == expected
    )
