import sys
import unittest

import pytest

sys.path.append("../../src")

from scribe_data import utils


def test_get_scribe_languages():
    test_case = unittest.TestCase()

    # test for content, not order
    test_case.assertCountEqual(
        utils.get_scribe_languages(),
        [
            "English",
            "French",
            "German",
            "Italian",
            "Portuguese",
            "Russian",
            "Spanish",
            "Swedish",
        ],
    )


@pytest.mark.parametrize(
    "language, qid_code",
    [
        ("English", "Q1860"),
        ("french", "Q150"),
        ("GERMAN", "Q188"),
        ("iTalian", "Q652"),
        ("poRTUGuese", "Q5146"),
        ("russian", "Q7737"),
        ("spanish", "Q1321"),
        ("swedish", "Q9027"),
    ],
)
def test_get_language_qid_positive(language, qid_code):
    assert utils.get_language_qid(language) == qid_code


def test_get_language_qid_negative():
    with pytest.raises(ValueError) as excp:
        _ = utils.get_language_qid("Newspeak")

    assert (
        str(excp.value)
        == "NEWSPEAK is currently not a supported language for QID conversion."
    )


@pytest.mark.parametrize(
    "language, iso_code",
    [
        ("English", "en"),
        ("french", "fr"),
        ("GERMAN", "de"),
        ("iTalian", "it"),
        ("poRTUGuese", "pt"),
        ("russian", "ru"),
        ("spanish", "es"),
        ("SwedisH", "sv"),
    ],
)
def test_get_language_iso_positive(language, iso_code):
    assert utils.get_language_iso(language) == iso_code


def test_get_language_iso_negative():
    with pytest.raises(ValueError) as excp:
        _ = utils.get_language_iso("gibberish")

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
    ],
)
def test_get_language_from_iso_positive(iso_code, language):
    assert utils.get_language_from_iso(iso_code) == language


def test_get_language_from_iso_negative():
    with pytest.raises(ValueError) as excp:
        _ = utils.get_language_from_iso("ixi")

    assert str(excp.value) == "IXI is currently not a supported ISO language."


@pytest.mark.parametrize(
    "language, remove_words",
    [
        (
            "english",
            [
                "of",
                "the",
                "The",
                "and",
            ],
        ),
        (
            "french",
            [
                "of",
                "the",
                "The",
                "and",
            ],
        ),
        ("german", ["of", "the", "The", "and", "NeinJa", "et", "redirect"]),
        ("italian", ["of", "the", "The", "and", "text", "from"]),
        ("portuguese", ["of", "the", "The", "and", "jbutadptflora"]),
        (
            "russian",
            [
                "of",
                "the",
                "The",
                "and",
            ],
        ),
        ("spanish", ["of", "the", "The", "and"]),
        ("swedish", ["of", "the", "The", "and", "Checklist", "Catalogue"]),
    ],
)
def test_get_language_words_to_remove(language, remove_words):
    test_case = unittest.TestCase()

    # ignore order, only content matters
    test_case.assertCountEqual(
        utils.get_language_words_to_remove(language), remove_words
    )


def test_get_language_words_to_remove_negative():
    with pytest.raises(ValueError) as excp:
        _ = utils.get_language_words_to_remove("python")

    assert str(excp.value) == "Python is currently not a supported language."


@pytest.mark.parametrize(
    "language, ignore_words",
    [
        (
            "french",
            [
                "XXe",
            ],
        ),
        ("german", ["Gemeinde", "Familienname"]),
        ("italian", ["The", "ATP"]),
        ("portuguese", []),
        ("russian", []),
        ("spanish", []),
        ("swedish", ["databasdump"]),
    ],
)
def test_get_language_words_to_ignore(language, ignore_words):
    test_case = unittest.TestCase()

    # ignore order, only content matters
    test_case.assertCountEqual(
        utils.get_language_words_to_ignore(language), ignore_words
    )


def test_get_language_words_to_ignore_negative():
    with pytest.raises(ValueError) as excp:
        _ = utils.get_language_words_to_ignore("JAVA")

    assert str(excp.value) == "Java is currently not a supported language."


def test_get_path_from_format_file():
    assert utils.get_path_from_format_file() == "../../../../../.."


def test_get_path_from_load_dir():
    assert utils.get_path_from_load_dir() == "../../../.."


def test_get_path_from_wikidata_dir():
    assert utils.get_path_from_wikidata_dir() == "../../../.."


def test_get_ios_data_path():
    assert (
        utils.get_ios_data_path("suomi")
        == "/Scribe-iOS/Keyboards/LanguageKeyboards/suomi"
    )


def test_get_android_data_path():
    assert (
        utils.get_android_data_path("Robbie")
        == "/Scribe-Android/app/src/main/LanguageKeyboards/Robbie"
    )


def test_get_desktop_data_path():
    assert (
        utils.get_desktop_data_path("PAVEMENT")
        == "/Scribe-Desktop/scribe/language_guis/PAVEMENT"
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
