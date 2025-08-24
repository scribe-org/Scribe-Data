"""
Tests functionality from check_project_metadata.py
"""

import unittest
from io import StringIO
from unittest.mock import patch

from scribe_data.check.check_project_metadata import (
    check_language_metadata,
    get_available_languages,
    get_missing_languages,
    validate_language_properties,
)


class TestCheckProjectMetadata(unittest.TestCase):
    def test_get_available_languages(self):
        """
        Tests that get_available_languages returns a dictionary with
        languages from LANGUAGE_DATA_EXTRACTION_DIR.
        """
        available_languages = get_available_languages()
        desired_dict = {
            "arabic": {},
            "estonian": {},
            "indonesian": {},
            "norwegian": {"sub_languages": ["bokmål", "nynorsk"]},
            "spanish": {},
            "basque": {},
            "finnish": {},
            "italian": {},
            "persian": {},
            "swahili": {},
            "bengali": {},
            "french": {},
            "japanese": {},
            "pidgin": {"sub_languages": ["nigerian"]},
            "swedish": {},
            "chinese": {"sub_languages": ["mandarin"]},
            "german": {},
            "korean": {},
            "polish": {},
            "tajik": {},
            "czech": {},
            "greek": {},
            "kurmanji": {},
            "portuguese": {},
            "tamil": {},
            "dagbani": {},
            "hausa": {},
            "latin": {},
            "punjabi": {"sub_languages": ["gurmukhi", "shahmukhi"]},
            "ukrainian": {},
            "danish": {},
            "hebrew": {},
            "latvian": {},
            "russian": {},
            "yoruba": {},
            "english": {},
            "hindustani": {"sub_languages": ["hindi", "urdu"]},
            "malay": {},
            "sami": {"sub_languages": ["northern"]},
            "esperanto": {},
            "igbo": {},
            "malayalam": {},
            "slovak": {},
        }
        for lang in available_languages.keys():
            self.assertIn(lang, desired_dict.keys())
            if len(available_languages[lang]) > 0:
                for sub_lang in available_languages[lang]["sub_languages"]:
                    self.assertIn(sub_lang, desired_dict[lang]["sub_languages"])

        self.assertEqual(len(available_languages), len(desired_dict))

    def test_get_missing_languages(self):
        """
        Tests that get_missing_languages returns a list of languages missing given
        a target language dictionary to check for and a reference language
        dictionary to check in.
        """
        reference_languages = {
            "estonian": {},
            "indonesian": {},
            "norwegian": {"sub_languages": ["bokmål", "nynorsk"]},
        }

        target_languages = {
            "estonian": {"iso": "et", "qid": "Q9072"},
            "indonesian": {"iso": "id", "qid": "Q9240"},
            "norwegian": {
                "sub_languages": {
                    "bokmål": {"iso": "nb", "qid": "Q25167"},
                    "nynorsk": {"iso": "nn", "qid": "Q25164"},
                }
            },
        }

        # No missing languages.
        self.assertEqual(
            get_missing_languages(reference_languages, target_languages), []
        )

        # More reference languages than target languages; should have no effect.
        reference_languages["basque"] = {}
        # Missing childless language.
        target_languages["arabic"] = {"iso": "ar", "qid": "Q13955"}
        # Missing parent language.
        target_languages["chinese"] = {
            "sub_languages": {"mandarin": {"iso": "zh", "qid": "Q727694"}}
        }
        # Missing only sub-languages.
        target_languages["estonian"] = {
            "sub_languages": {"sub_estonian": {"iso": "nb", "qid": "Q25167"}}
        }
        self.assertEqual(
            get_missing_languages(reference_languages, target_languages),
            ["estonian/sub_estonian", "arabic", "chinese/mandarin"],
        )

    def test_validate_language_properties(self):
        """
        Tests that validate_language_properties identifies languages missing an 'iso' and/or
        'qid' field from a dictionary of languages.
        """
        languages = {
            "arabic": {"iso": "ar", "qid": "Q13955"},
            "basque": {"iso": "eu", "qid": "Q8752"},
            "bengali": {"iso": "bn", "qid": "Q9610"},
            "chinese": {"sub_languages": {"mandarin": {"iso": "zh", "qid": "Q727694"}}},
        }

        # No missing "iso" or "qid".
        self.assertEqual(
            validate_language_properties(languages),
            {"missing_qids": [], "missing_isos": []},
        )

        # Childless language missing "iso".
        languages["persian"] = {"qid": "Q9168"}
        # Childless language missing "qid".
        languages["russian"] = {"iso": "ru"}
        # Childless language missing "iso" and "qid".
        languages["tajik"] = {}
        # Sub-language missing "iso" and sub-language missing "qid".
        languages["punjabi"] = {
            "sub_languages": {
                "gurmukhi": {"qid": "Q58635"},
                "shahmukhi": {"iso": "pnb"},
            }
        }
        # Sub-language missing "iso" and "qid".
        languages["chinese"]["sub_languages"]["mandarin"] = {}
        self.assertEqual(
            validate_language_properties(languages),
            {
                "missing_qids": [
                    "chinese/mandarin",
                    "russian",
                    "tajik",
                    "punjabi/shahmukhi",
                ],
                "missing_isos": [
                    "chinese/mandarin",
                    "persian",
                    "tajik",
                    "punjabi/gurmukhi",
                ],
            },
        )

    def test_check_language_metadata_success_case(self):
        """
        Tests that check_language_metadata runs successfully.
        """
        with patch("sys.stdout", new=StringIO()) as out:
            check_language_metadata()
            self.assertEqual(
                out.getvalue(),
                "All languages in language_metadata.json are included in Scribe-Data.\n"
                "Languages in language_metadata.json have the correct properties.\n",
            )

    def test_check_language_metadata_raises_error(self):
        """
        Tests that check_language_metadata prints the correct error message when
        the language metadata has languages missing from the language data extraction
        and languages without 'qid' and or 'iso' fields.
        """
        with (
            patch(
                "scribe_data.check.check_project_metadata.get_available_languages",
                return_value={
                    "indonesian": {},
                    "norwegian": {"sub_languages": ["bokmål", "nynorsk"]},
                },
            ),
            patch.dict(
                "scribe_data.utils._languages",
                {
                    "estonian": {"iso": "et", "qid": "Q9072"},
                    "indonesian": {"iso": "id", "qid": "Q9240"},
                    "norwegian": {
                        "sub_languages": {
                            "bokmål": {"qid": "Q25167"},
                            "nynorsk": {"iso": "nn"},
                        }
                    },
                },
                clear=True,
            ),
            self.assertRaises(SystemExit) as cm,
            patch("sys.stdout", new=StringIO()) as out,
        ):
            check_language_metadata()
        self.assertEqual(1, cm.exception.code)
        self.assertEqual(
            "There are missing languages or inconsistencies between language_metadata.json and language_data_extraction.\n\n"
            "\nLanguages missing from language_data_extraction:\n"
            "  - Estonian\n"
            "\nLanguages missing the `qid` property:\n"
            "  - Norwegian/Nynorsk\n"
            "\nLanguages missing the `iso` property:\n"
            "  - Norwegian/Bokmål\n",
            out.getvalue(),
        )
