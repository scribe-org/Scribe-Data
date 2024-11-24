"""
Tests for the update_utils file functions.

.. raw:: html
    <!--
    * Copyright (C) 2024 Scribe
    *
    * This program is free software: you can redistribute it and/or modify
    * it under the terms of the GNU General Public License as published by
    * the Free Software Foundation, either version 3 of the License, or
    * (at your option) any later version.
    *
    * This program is distributed in the hope that it will be useful,
    * but WITHOUT ANY WARRANTY; without even the implied warranty of
    * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    * GNU General Public License for more details.
    *
    * You should have received a copy of the GNU General Public License
    * along with this program.  If not, see <https://www.gnu.org/licenses/>.
    -->
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
def test_get_language_qid_positive(language, qid_code):
    assert utils.get_language_qid(language) == qid_code


def test_get_language_qid_negative():
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
def test_get_language_iso_positive(language, iso_code):
    assert utils.get_language_iso(language) == iso_code


def test_get_language_iso_negative():
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
def test_get_language_from_iso_positive(iso_code, language):
    assert utils.get_language_from_iso(iso_code) == language


def test_get_language_from_iso_negative():
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
def test_format_sublanguage_name_positive(lang, expected_output):
    assert utils.format_sublanguage_name(lang) == expected_output


def test_format_sublanguage_name_negative():
    with pytest.raises(ValueError) as excp:
        _ = utils.format_sublanguage_name("Silence")

    assert str(excp.value) == "Silence is not a valid language or sub-language."


def test_list_all_languages():
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


def test_get_ios_data_path():
    assert (
        utils.get_ios_data_path("suomi")
        == Path("Scribe-iOS") / "Keyboards" / "LanguageKeyboards" / "suomi"
    )


@pytest.mark.parametrize(
    "passed_values, values_to_check, expected",
    [
        ("['1', '2', '3']", ["1", "2", "3"], ["1", "2", "3"]),
        ("['1', '3', '2']", ["1", "2", "3"], ["1", "3", "2"]),
        ("['1', '2']", ["1", "2", "3"], ["1", "2"]),
        ("['abc']", ["def", "abc", "ghi"], ["abc"]),
        ("[]", ["1", "2", "3"], []),
    ],
)
def test_check_command_line_args_positive(passed_values, values_to_check, expected):
    assert (
        utils.check_command_line_args("pass.txt", passed_values, values_to_check)
        == expected
    )


def test_check_command_line_args_fail_not_subset():
    with pytest.raises(ValueError):
        _ = utils.check_command_line_args("Fail.txt", "['1', '2', '3']", ["1", "2"])


def test_check_command_line_args_passed_values_not_list():
    with pytest.raises(ValueError):
        _ = utils.check_command_line_args("Fail.txt", "('1', '2', '3')", ["1", "2"])


def test_check_command_line_args_passed_values_invalid_arg():
    with pytest.raises(ValueError):
        _ = utils.check_command_line_args("Fail.txt", 3, ["3"])


def test_check_and_return_command_line_args_one_arg():
    assert utils.check_and_return_command_line_args(["1"]) == (None, None)


def test_check_and_return_command_line_args_two_args():
    assert utils.check_and_return_command_line_args(
        ["a.txt", '["1","2"]'], ["1", "2", "3"], ["1", "2", "3"]
    ) == (["1", "2"], None)


def test_check_and_return_command_line_args_three_args():
    assert utils.check_and_return_command_line_args(
        ["a.txt", '["1","2"]', '["3"]'], ["1", "2", "3"], ["1", "2", "3"]
    ) == (["1", "2"], ["3"])


def test_check_and_return_command_line_args_too_many_args():
    with pytest.raises(ValueError):
        _ = utils.check_and_return_command_line_args(["a", "b", "c", "d"])
