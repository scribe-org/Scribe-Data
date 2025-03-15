# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the CLI dump functionality.
"""

from unittest.mock import mock_open, patch

import orjson
import pytest

from scribe_data.check.check_query_forms import return_correct_form_label
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
def lexeme_processor():
    return LexemeProcessor(
        target_lang=["english"],
        parse_type=["translations", "form"],
        data_types=["nouns"],
    )


def test_lexeme_processor_initialization(lexeme_processor):
    """Test LexemeProcessor initialization with basic parameters."""
    assert "english" in lexeme_processor.target_lang
    assert "translations" in lexeme_processor.parse_type
    assert "form" in lexeme_processor.parse_type
    assert "nouns" in lexeme_processor.data_types


@patch("builtins.open", new_callable=mock_open, read_data=Sample_Lexeme_Line)
@patch("bz2.open")
def test_process_file(mock_bz2_open, mock_file, lexeme_processor):
    """Test processing a file with sample lexeme data."""
    mock_bz2_open.return_value.__enter__.return_value = mock_file()

    # Mock Path.stat() to return a size.
    with patch("pathlib.Path.stat") as mock_stat:
        mock_stat.return_value.st_size = 1000
        lexeme_processor.process_file("test.json.bz2")

    # Verify that stats were updated.
    assert lexeme_processor.stats["processed_entries"] > 0


@patch("scribe_data.wikidata.parse_dump.LexemeProcessor")
def test_parse_dump(mock_processor):
    """Test the parse_dump function."""
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
def test_parse_wd_lexeme_dump(mock_parse_dump, mock_download, mock_path_class):
    """Test the parse_wd_lexeme_dump function."""
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


def test_parse_wd_lexeme_dump_no_file():
    """Test parse_wd_lexeme_dump when no file is found."""
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
def test_parse_types(test_input, expected):
    """Test different parse types."""
    processor = LexemeProcessor(
        target_lang="english", parse_type=list(test_input.keys()), data_types=["nouns"]
    )
    assert (
        any(parse_type in processor.parse_type for parse_type in test_input.keys())
        == expected
    )


def test_export_translations_json(lexeme_processor, tmp_path):
    """Test exporting translations to JSON."""
    # Add some test data to the translations index.
    lexeme_processor.translations_index["en"]["nouns"]["L1"] = {
        "lastModified": "2023-01-01T00:00:00Z",
        "test": {"fr": "tester"},
    }

    # Export to temporary directory.
    output_file = tmp_path / "translations.json"
    lexeme_processor.export_translations_json(str(output_file), "en")

    assert output_file.parent.exists()


def test_export_forms_json(lexeme_processor, tmp_path):
    """Test exporting forms to JSON."""
    # Add some test data to the forms index.
    lexeme_processor.forms_index["L1"] = {
        "en": {"nouns": {"lastModified": "2023-01-01T00:00:00Z", "plural": "tests"}}
    }

    # Export to temporary directory.
    output_file = tmp_path / "nouns.json"
    lexeme_processor.export_forms_json(str(output_file), "en", "nouns")

    assert output_file.parent.exists()


@patch("scribe_data.wikidata.wikidata_utils.requests.get")
def test_mediawiki_query(mock_get):
    """Test the MediaWiki query function."""
    from scribe_data.wikidata.wikidata_utils import mediawiki_query

    mock_get.return_value.json.return_value = {"query": {"pages": {}}}

    result = mediawiki_query("test")
    assert isinstance(result, dict)
    assert "query" in result


@pytest.fixture
def mock_lexeme_data():
    return {
        "id": "L1",
        "lemmas": {"en": {"value": "test", "language": "en"}},
        "lexicalCategory": "Q1084",
        "language": "Q1860",
        "forms": [
            {
                "id": "L1-F1",
                "representations": {"en": {"value": "tests", "language": "en"}},
                "grammaticalFeatures": ["Q146786"],
            }
        ],
        "senses": [{"glosses": {"fr": {"value": "tester", "language": "fr"}}}],
        "modified": "2023-01-01T00:00:00Z",
    }


def test_process_lines_invalid_json(lexeme_processor):
    """Test handling of invalid JSON input."""
    invalid_json = "{ invalid json }"
    lexeme_processor.process_lines(invalid_json)
    assert lexeme_processor.stats["processed_entries"] == 0


def test_process_lines_invalid_category(lexeme_processor):
    """Test handling of invalid lexical category."""
    invalid_category_data = {
        "id": "L1",
        "lemmas": {"en": {"value": "test", "language": "en"}},
        "lexicalCategory": "INVALID",
        "language": "Q1860",
    }
    lexeme_processor.process_lines(orjson.dumps(invalid_category_data).decode())
    assert lexeme_processor.stats["processed_entries"] == 0


@pytest.mark.parametrize(
    "features,expected",
    [
        # Basic single feature cases
        (["Q146786"], "plural"),  # Plural
        (["Q110786"], "singular"),  # Singular
        (["Q110022"], "dual"),  # Dual
        # Multiple feature combinations
        (["Q146786", "Q146233"], "genitivePlural"),  # Plural Genitive
        (["Q146233", "Q146786"], "genitivePlural"),  # Genitive Plural (order swap)
        # Complex multi-feature cases from different categories
        (
            ["Q51929074", "Q192613", "Q146786"],  # ThirdPerson, Present, Plural
            "presentThirdPersonPlural",
        ),
        (
            [
                "Q1317831",
                "Q124351233",
                "Q51929049",
                "Q110022",
            ],  # Active, Performative, SecondPerson, Dual
            "activePerformativeSecondPersonDual",
        ),
        (
            ["Q51929074", "Q442485", "Q146786"],  # ThirdPerson, Preterite, Plural
            "preteriteThirdPersonPlural",
        ),
        (
            ["Q51929074", "Q192613", "Q146786"],  # ThirdPerson, Present, Plural
            "presentThirdPersonPlural",
        ),
        (
            [
                "Q499327",
                "Q682111",
                "Q51929074",
                "Q110022",
            ],  # Masculine, Indicative, ThirdPerson, Dual
            "masculineIndicativeThirdPersonDual",
        ),
        (
            [
                "Q1775415",
                "Q625581",
                "Q51929049",
                "Q110786",
            ],  # Feminine, Conditional, SecondPerson, Singular
            "feminineConditionalSecondPersonSingular",
        ),
        # Edge cases
        ([], ""),  # Empty features
        (["INVALID"], ""),  # Invalid feature
    ],
)
def test_form_label_variations(lexeme_processor, features, expected):
    """
    Test form label generation with diverse feature combinations.
    Covers various grammatical categories like:
    - Number (Singular, Plural, Dual)
    - Person (First, Second, Third)
    - Mood (Indicative, Conditional)
    - Tense (Present, Preterite)
    - Gender (Masculine, Feminine)
    """
    result = return_correct_form_label(features)

    # If expected is empty, check for empty or error message
    if not expected:
        assert (
            result in ["", "Invalid query formatting found"]
            or "not included in lexeme_form.metadata.json" in result
        )
    else:
        assert result.lower() == expected.lower(), f"Failed for features {features}"


def test_process_batch_empty(lexeme_processor):
    """Test processing an empty batch."""
    lexeme_processor._process_batch([])
    assert lexeme_processor.stats["processed_entries"] == 0


def test_process_forms_multiple_representations(lexeme_processor, mock_lexeme_data):
    """Test processing forms with multiple representations."""
    # Add another form with different representations.
    mock_lexeme_data["forms"].append(
        {
            "id": "L1-F2",
            "representations": {"en": {"value": "testing", "language": "en"}},
            "grammaticalFeatures": ["Q1234"],
        }
    )

    lexeme_processor.process_lines(orjson.dumps(mock_lexeme_data).decode())

    # Verify both forms were processed.
    assert "L1" in lexeme_processor.forms_index
    forms = lexeme_processor.forms_index["L1"]["en"]["nouns"]
    assert len(forms) > 1  # should have more than one form


@pytest.mark.parametrize(
    "parse_type,expected_count",
    [
        (["translations"], 1),
        (["form"], 1),
        (["total"], 1),
        (["translations", "form"], 2),
        (["translations", "form", "total"], 3),
    ],
)
def test_parse_type_combinations(parse_type, expected_count):
    """Test different combinations of parse types."""
    processor = LexemeProcessor(
        target_lang="english", parse_type=parse_type, data_types=["nouns"]
    )
    assert len(processor.parse_type) == expected_count


def test_export_translations_invalid_language(lexeme_processor, tmp_path):
    """Test exporting translations with invalid language."""
    output_file = tmp_path / "translations.json"
    lexeme_processor.export_translations_json(str(output_file), "invalid_lang")
    assert not output_file.exists()


def test_export_forms_empty_data(lexeme_processor, tmp_path):
    """Test exporting forms when no data exists."""
    output_file = tmp_path / "forms.json"
    lexeme_processor.export_forms_json(str(output_file), "en", "nouns")
    assert not output_file.exists()


def test_process_lines_unrecognized_qids(lexeme_processor):
    """
    Test processing lexeme data with unrecognized QIDs in grammatical features.
    Ensure these forms are skipped without causing errors.
    """
    unrecognized_qid_data = {
        "id": "L2",
        "lemmas": {"en": {"value": "test", "language": "en"}},
        "lexicalCategory": "Q1084",
        "language": "Q1860",
        "forms": [
            {
                "id": "L2-F1",
                "representations": {"en": {"value": "tests", "language": "en"}},
                "grammaticalFeatures": ["Q999999"],  # Unrecognized QID
            }
        ],
        "senses": [{"glosses": {"fr": {"value": "tester", "language": "fr"}}}],
        "modified": "2023-01-01T00:00:00Z",
    }

    lexeme_processor.process_lines(orjson.dumps(unrecognized_qid_data).decode())

    # Verify that forms with unrecognized QIDs don't have valid form labels
    if "L2" in lexeme_processor.forms_index:
        forms = lexeme_processor.forms_index["L2"]["en"]["nouns"]
        # Remove lastModified from the count
        form_values = [v for k, v in forms.items() if k != "lastModified"]
        assert len(form_values) == 0


def test_process_lines_mixed_qids(lexeme_processor):
    """
    Test processing lexeme data with a mix of recognized and unrecognized QIDs.
    Ensure only forms with valid QIDs are processed.
    """
    mixed_qid_data = {
        "id": "L3",
        "lemmas": {"en": {"value": "test", "language": "en"}},
        "lexicalCategory": "Q1084",
        "language": "Q1860",
        "forms": [
            {
                "id": "L3-F1",
                "representations": {"en": {"value": "tests", "language": "en"}},
                "grammaticalFeatures": ["Q146786"],  # Valid QID
            }
        ],
        "senses": [{"glosses": {"fr": {"value": "tester", "language": "fr"}}}],
        "modified": "2023-01-01T00:00:00Z",
    }

    lexeme_processor.process_lines(orjson.dumps(mixed_qid_data).decode())

    # Verify that only the form with valid QID is processed
    if "L3" in lexeme_processor.forms_index:
        forms = lexeme_processor.forms_index["L3"]["en"]["nouns"]
        # Remove lastModified from the count
        form_values = [v for k, v in forms.items() if k != "lastModified"]
        assert len(form_values) == 1


def test_form_label_cache_with_unrecognized_qids(lexeme_processor):
    """
    Test that the form label cache works correctly with unrecognized QIDs,
    ensuring repeated calls don't process invalid QIDs multiple times.
    """
    unrecognized_qid_data1 = {
        "id": "L4",
        "lemmas": {"en": {"value": "test1", "language": "en"}},
        "lexicalCategory": "Q1084",
        "language": "Q1860",
        "forms": [
            {
                "id": "L4-F1",
                "representations": {"en": {"value": "tests1", "language": "en"}},
                "grammaticalFeatures": ["Q999999"],  # Unrecognized QID
            }
        ],
        "modified": "2023-01-01T00:00:00Z",
    }

    unrecognized_qid_data2 = {
        "id": "L5",
        "lemmas": {"en": {"value": "test2", "language": "en"}},
        "lexicalCategory": "Q1084",
        "language": "Q1860",
        "forms": [
            {
                "id": "L5-F1",
                "representations": {"en": {"value": "tests2", "language": "en"}},
                "grammaticalFeatures": ["Q999999"],  # Same unrecognized QID
            }
        ],
        "modified": "2023-01-01T00:00:00Z",
    }

    # Process two lexemes with the same unrecognized QID
    lexeme_processor.process_lines(orjson.dumps(unrecognized_qid_data1).decode())
    lexeme_processor.process_lines(orjson.dumps(unrecognized_qid_data2).decode())

    # Verify that no valid forms were added
    for lexeme_id in ["L4", "L5"]:
        if lexeme_id in lexeme_processor.forms_index:
            forms = lexeme_processor.forms_index[lexeme_id]["en"]["nouns"]
            # Remove lastModified and check remaining values
            form_values = [v for k, v in forms.items() if k != "lastModified"]
            assert len(form_values) == 0

    # Verify that invalid QIDs are not cached
    assert all(
        "Q999999" not in features
        for features in lexeme_processor._form_label_cache.keys()
    )


def test_process_lines_empty_line(lexeme_processor):
    """Test processing empty lines."""
    lexeme_processor.process_lines("")
    assert lexeme_processor.stats["processed_entries"] == 0


def test_process_lines_missing_required_fields(lexeme_processor):
    """Test processing lexeme with missing required fields."""
    incomplete_data = {
        "id": "L1",
        # Missing lemmas and lexicalCategory.
        "language": "Q1860",
    }
    lexeme_processor.process_lines(orjson.dumps(incomplete_data).decode())
    assert "L1" not in lexeme_processor.forms_index


def test_process_forms_with_duplicate_values(lexeme_processor):
    """Test processing forms with duplicate values."""
    # Initialize processor with forms parse type.
    processor = LexemeProcessor(
        target_lang="english", parse_type=["form"], data_types=["nouns"]
    )

    data = {
        "id": "L1",
        "lemmas": {"en": {"value": "test"}},
        "lexicalCategory": "Q1084",
        "language": "Q1860",
        "modified": "2023-01-01T00:00:00Z",
        "forms": [
            {
                "representations": {"en": {"value": "testing"}},
                "grammaticalFeatures": ["Q146786"],  # Use valid QID
            },
            {
                "representations": {"en": {"value": "testing"}},
                "grammaticalFeatures": ["Q146786"],
            },
        ],
    }
    processor.process_lines(orjson.dumps(data).decode())
    forms = processor.forms_index["L1"]["en"]
    assert isinstance(forms, dict)
    assert "nouns" in forms
    assert len(forms["nouns"]) >= 1  # At least one form plus lastModified


def test_process_totals_with_data_type_filter(lexeme_processor):
    """Test processing totals with data type filter."""
    # Create processor with specific data types.
    processor = LexemeProcessor(
        target_lang="english", parse_type=["total"], data_types=["nouns"]
    )

    # Process verb data (should be ignored).
    verb_data = {
        "id": "L1",
        "lemmas": {"en": {"value": "test"}},
        "lexicalCategory": "Q24905",  # verb
        "language": "Q1860",
        "modified": "2023-01-01T00:00:00Z",
    }
    processor.process_lines(orjson.dumps(verb_data).decode())

    # Process noun data (should be counted).
    noun_data = {
        "id": "L2",
        "lemmas": {"en": {"value": "test"}},
        "lexicalCategory": "Q1084",  # noun
        "language": "Q1860",
        "modified": "2023-01-01T00:00:00Z",
    }
    processor.process_lines(orjson.dumps(noun_data).decode())

    assert processor.lexical_category_counts["en"]["nouns"] == 1
    assert "verbs" not in processor.lexical_category_counts["en"]
