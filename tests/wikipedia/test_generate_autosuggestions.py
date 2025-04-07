# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the Wikipedia generate autosuggestions functionality.
"""

import unittest
from unittest.mock import mock_open, patch

from scribe_data.wikipedia.generate_autosuggestions import generate_autosuggestions


class TestGenerate(unittest.TestCase):
    @patch("scribe_data.wikipedia.generate_autosuggestions.gen_autosuggestions")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='["id1", "This is article text"]\n["id2", "Another article"]\n',
    )
    @patch(
        "scribe_data.wikipedia.generate_autosuggestions.parse_to_ndjson", autospec=True
    )
    @patch(
        "scribe_data.wikipedia.generate_autosuggestions.download_wiki", autospec=True
    )
    @patch(
        "scribe_data.wikipedia.generate_autosuggestions.get_language_iso", autospec=True
    )
    def test_generate_autosuggestions(
        self,
        mock_get_language_iso,
        mock_download_wiki,
        mock_parse_to_ndjson,
        mock_open_file,
        mock_gen_autosuggestions,
    ):
        mock_get_language_iso.return_value = "en"
        mock_download_wiki.return_value = ["dummy1.xml", "dummy2.xml"]

        language = "english"
        dump_id = "20250101"
        target_dir = f"./enwiki_dump/{dump_id}"

        generate_autosuggestions(language, dump_id, force_download=False)

        mock_get_language_iso.assert_called_once_with("english")
        mock_download_wiki.assert_called_once_with(
            language=language,
            target_dir=target_dir,
            file_limit=1,
            dump_id=dump_id,
            force_download=False,
        )
        mock_parse_to_ndjson.assert_called_once_with(
            output_path=f"./enwiki-{dump_id}.ndjson",
            input_dir=target_dir,
            partitions_dir="./enwiki_partitions",
            article_limit=None,
            delete_parsed_files=True,
            force_download=False,
            multicore=True,
            verbose=True,
        )

        mock_open_file.assert_called_once()

        text_corpus = [["This", "is", "article", "text"], ["Another", "article"]]
        mock_gen_autosuggestions.assert_called_once_with(
            text_corpus,
            language=language,
            num_words=100,  # Limiting for development purpose
            ignore_words=None,
            update_local_data=True,
            verbose=True,
        )

    @patch("scribe_data.wikipedia.generate_autosuggestions.gen_autosuggestions")
    @patch("builtins.open", new_callable=mock_open, read_data='["id1", "Text"]\n')
    @patch(
        "scribe_data.wikipedia.generate_autosuggestions.parse_to_ndjson", autospec=True
    )
    @patch(
        "scribe_data.wikipedia.generate_autosuggestions.download_wiki", autospec=True
    )
    @patch(
        "scribe_data.wikipedia.generate_autosuggestions.get_language_iso", autospec=True
    )
    def test_generate_autosuggestions_force_download_true(
        self,
        mock_get_language_iso,
        mock_download_wiki,
        mock_parse_to_ndjson,
        mock_open_file,
        mock_gen_autosuggestions,
    ):
        mock_get_language_iso.return_value = "en"
        mock_download_wiki.return_value = ["dummy1.xml"]
        language = "english"
        dump_id = "20250101"
        target_dir = f"./enwiki_dump/{dump_id}"

        generate_autosuggestions(language, dump_id, force_download=True)

        mock_get_language_iso.assert_called_once_with("english")
        mock_download_wiki.assert_called_once_with(
            language=language,
            target_dir=target_dir,
            file_limit=1,
            dump_id=dump_id,
            force_download=True,
        )

        mock_parse_to_ndjson.assert_called_once_with(
            output_path=f"./enwiki-{dump_id}.ndjson",
            input_dir=target_dir,
            partitions_dir="./enwiki_partitions",
            article_limit=None,
            delete_parsed_files=True,
            force_download=True,
            multicore=True,
            verbose=True,
        )

        mock_open_file.assert_called_once()

        text_corpus = [["Text"]]
        mock_gen_autosuggestions.assert_called_once_with(
            text_corpus,
            language=language,
            num_words=100,  # Limiting for development purpose
            ignore_words=None,
            update_local_data=True,
            verbose=True,
        )
