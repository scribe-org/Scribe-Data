import unittest
from unittest.mock import mock_open, patch

import emoji

# Corrected import
from emoji_lexicon import gen_emoji_lexicon


# Rest of the test code remains unchanged
class TestEmojiLexicon(unittest.TestCase):
    # ... (rest of the code)

    def setUp(self):
        self.mock_rank_data = "Emoji\tRank\n😀\t1\n😂\t2\n"
        self.mock_annotations = {
            "annotations": {
                "😀": {"default": ["happy", "apple"]},
                "😂": {"default": ["laughing", "banana"]},
            }
        }
        self.mock_emoji_data = {
            "😀": {"status": emoji.STATUS["fully_qualified"]},
            "😂": {"status": emoji.STATUS["fully_qualified"]},
        }

    @patch(
        "builtins.open", new_callable=mock_open, read_data="Emoji\tRank\n😀\t1\n😂\t2\n"
    )
    @patch(
        "scribe_data.unicode.unicode_utils.get_emoji_codes_to_ignore",
        return_value=set(),
    )
    @patch("scribe_data.utils.get_language_iso", return_value="en")
    def test_gen_emoji_lexicon_basic(self, mock_lang, mock_ignore, mock_file):
        with patch("emoji.EMOJI_DATA", self.mock_emoji_data):
            with patch("json.load", return_value=self.mock_annotations):
                result = gen_emoji_lexicon("en", emojis_per_keyword=2)

                self.assertIn("happy", result)
                self.assertIn("laughing", result)

                self.assertEqual(result["happy"][0]["emoji"], "😀")
                self.assertEqual(result["happy"][0]["rank"], 1)
                self.assertEqual(result["laughing"][0]["emoji"], "😂")
                self.assertEqual(result["laughing"][0]["rank"], 2)

    @patch(
        "builtins.open", new_callable=mock_open, read_data="Emoji\tRank\n😀\t1\n😂\t2\n"
    )
    @patch(
        "scribe_data.unicode.unicode_utils.get_emoji_codes_to_ignore",
        return_value=set(),
    )
    @patch("scribe_data.utils.get_language_iso", return_value="en")
    def test_gen_emoji_lexicon_plural_nouns(self, mock_lang, mock_ignore, mock_file):
        plural_nouns = {
            "apple": {"singular": "apple", "plural": "apples"},
            "banana": {"singular": "banana", "plural": "bananas"},
        }

        with patch("emoji.EMOJI_DATA", self.mock_emoji_data):
            with patch("json.load", side_effect=[self.mock_annotations, plural_nouns]):
                result = gen_emoji_lexicon("en", emojis_per_keyword=2)

                self.assertIn("apples", result)
                self.assertIn("bananas", result)
                self.assertEqual(result["apples"], result["apple"])
                self.assertEqual(result["bananas"], result["banana"])

    @patch(
        "builtins.open", new_callable=mock_open, read_data="Emoji\tRank\n😀\t1\n😂\t2\n"
    )
    @patch(
        "scribe_data.unicode.unicode_utils.get_emoji_codes_to_ignore",
        return_value=set(),
    )
    @patch("scribe_data.utils.get_language_iso", return_value="en")
    def test_gen_emoji_lexicon_no_emoji_data(self, mock_lang, mock_ignore, mock_file):
        empty_emoji_data = {}

        with patch("emoji.EMOJI_DATA", empty_emoji_data):
            with patch("json.load", return_value=self.mock_annotations):
                result = gen_emoji_lexicon("en", emojis_per_keyword=2)

                # None of the emoji keywords should be included due to missing emoji status
                self.assertNotIn("happy", result)
                self.assertNotIn("laughing", result)
                self.assertNotIn("apple", result)
                self.assertNotIn("banana", result)

    # You could add more advanced tests like:
    # - test when the annotations file is missing or empty
    # - test with emojis that aren't fully qualified
    # - test filtering based on ignored emoji codes
    # - test with more than emojis_per_keyword emojis for a single keyword


if __name__ == "__main__":
    unittest.main()
