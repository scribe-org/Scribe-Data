# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the update_utils file functions.
"""

import sys
from pathlib import Path

import pytest

sys.path.append(Path(__file__).parent.parent.parent)

from scribe_data import utils


@pytest.mark.parametrize(
    "language, qid_code",
    [
        ("english", "Q1860"),
        ("french", "Q150"),
        ("german", "Q188"),
        ("italian", "Q652"),
        ("portuguese", "Q5146"),
        ("russian", "Q7737"),
        ("spanish", "Q1321"),
        ("swedish", "Q9027"),
        ("bokmål", "Q25167"),
    ],
)
def test_get_language_qid_positive(language: str, qid_code: str) -> None:
    assert utils.get_language_qid(language) == qid_code


def test_get_language_qid_negative() -> None:
    with pytest.raises(ValueError) as excp:
        _ = utils.get_language_qid("Newspeak")

    assert (
        str(excp.value)
        == "Newspeak is currently not a supported language for QID conversion."
    )


@pytest.mark.parametrize(
    "language, iso_code",
    [
        ("english", "en"),
        ("french", "fr"),
        ("german", "de"),
        ("italian", "it"),
        ("portuguese", "pt"),
        ("russian", "ru"),
        ("spanish", "es"),
        ("swedish", "sv"),
        ("bokmål", "nb"),
    ],
)
def test_get_language_iso_positive(language: str, iso_code: str) -> None:
    assert utils.get_language_iso(language) == iso_code


def test_get_language_iso_negative() -> None:
    with pytest.raises(ValueError) as excp:
        _ = utils.get_language_iso("Gibberish")

    assert (
        str(excp.value)
        == "Gibberish is currently not a supported language for ISO conversion."
    )


@pytest.mark.parametrize(
    "iso_code, language",
    [
        ("en", "English"),
        ("fr", "French"),
        ("de", "German"),
        ("it", "Italian"),
        ("pt", "Portuguese"),
        ("ru", "Russian"),
        ("es", "Spanish"),
        ("sv", "Swedish"),
        ("nb", "Bokmål"),
    ],
)
def test_get_language_from_iso_positive(iso_code: str, language: str) -> None:
    assert utils.get_language_from_iso(iso_code) == language


def test_get_language_from_iso_negative() -> None:
    with pytest.raises(ValueError) as excp:
        _ = utils.get_language_from_iso("ixi")

    assert str(excp.value) == "IXI is currently not a supported ISO language."


@pytest.mark.parametrize(
    "lang, expected_output",
    [
        ("nynorsk", "nynorsk norwegian"),
        ("bokmål", "bokmål norwegian"),
        ("english", "english"),
    ],
)
def test_format_sublanguage_name_positive(lang: str, expected_output: str) -> None:
    assert utils.format_sublanguage_name(lang) == expected_output


@pytest.mark.parametrize(
    "lang, expected_output",
    [
        ("Q42", "Q42"),  # test that any QID is returned
        ("Q1860", "Q1860"),
    ],
)
def test_format_sublanguage_name_qid_positive(lang: str, expected_output: str) -> None:
    assert utils.format_sublanguage_name(lang) == expected_output


def test_format_sublanguage_name_negative() -> None:
    with pytest.raises(ValueError) as excp:
        _ = utils.format_sublanguage_name("Newspeak")

    assert str(excp.value) == "Newspeak is not a valid language or sub-language."


def test_list_all_languages() -> None:
    expected_languages = [
        "arabic",
        "basque",
        "bengali",
        "bokmål norwegian",
        "czech",
        "dagbani",
        "danish",
        "english",
        "esperanto",
        "estonian",
        "finnish",
        "french",
        "german",
        "greek",
        "gurmukhi punjabi",
        "hausa",
        "hebrew",
        "hindi hindustani",
        "igbo",
        "indonesian",
        "italian",
        "japanese",
        "korean",
        "kurmanji",
        "latin",
        "latvian",
        "malay",
        "malayalam",
        "mandarin chinese",
        "nigerian pidgin",
        "northern sami",
        "nynorsk norwegian",
        "persian",
        "polish",
        "portuguese",
        "russian",
        "shahmukhi punjabi",
        "slovak",
        "spanish",
        "swahili",
        "swedish",
        "tajik",
        "tamil",
        "ukrainian",
        "urdu hindustani",
        "yoruba",
    ]

    assert utils.list_all_languages() == expected_languages
