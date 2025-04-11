# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the Wikipedia dump extraction functionality.
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

from scribe_data.wikipedia.extract_wiki import download_wiki, parse_to_ndjson


class TestExtractWiki(unittest.TestCase):
    @patch("os.stat")
    @patch("pathlib.Path.exists")
    @patch("subprocess.run")
    @patch("scribe_data.wikipedia.extract_wiki.requests.get")
    @patch("os.makedirs")
    def test_download_wiki(
        self, mock_makedirs, mock_get, mock_subprocess, mock_exists, mock_stat
    ):
        language = "english"
        dump_id = "20250101"
        target_dir = "./enwiki_dump/{dump_id}"
        file_limit = 1
        force_download = False

        def mock_requests_get(url, *args, **kwargs):
            if url == "https://dumps.wikimedia.org/enwiki/":
                return Mock(
                    text="""
					<html>
						<body>
							<a href="20250101/">20250101/</a>
							<a href="20250201/">20250201/</a>
							<a href="20250301/">20250301/</a>
						</body>
					</html>
				"""
                )
            elif f"/{dump_id}/" in url:
                return Mock(
                    text="""
					<html>
						<body>
							<li class="file">
								<a href="/enwiki/20250101/enwiki-20250101-pages-articles-multistream.xml-p1483662p2134111.bz2">
									enwiki-20250101-pages-articles-multistream.xml-p1483662p2134111.bz2
								</a>
							</li>
						</body>
					</html>"""
                )
            else:
                raise ValueError(f"Unexpected URL: {url}")

        mock_get.side_effect = mock_requests_get
        mock_exists.return_value = False  # simulate files not existing
        mock_stat.return_value.st_size = 10_000_000  # 10 MB

        files = download_wiki(language, target_dir, file_limit, dump_id, force_download)
        mock_makedirs.assert_called_once()
        mock_subprocess.assert_called()
        self.assertEqual(files, [("p1483662p2134111.bz2", 10.0, 650449)])

    @patch("scribe_data.wikipedia.extract_wiki.iterate_and_parse_file")
    @patch("scribe_data.wikipedia.extract_wiki.Pool")
    @patch("os.cpu_count")
    @patch("os.listdir")
    @patch("os.makedirs")
    @patch("pathlib.Path.exists")
    def test_parse_to_ndjson(
        self,
        mock_exists,
        mock_makedirs,
        mock_listdir,
        mock_cpu_count,
        mock_pool_cls,
        mock_iterate_fn,
    ):
        output_path = "./enwiki.ndjson"
        target_dir = "./enwiki_dump"
        partitions_dir = "./enwiki_partitions"
        article_limit = None
        delete_parsed_files = True
        force_download = False
        multicore = True
        verbose = True

        mock_exists.return_value = False
        mock_listdir.return_value = [
            "enwiki-20250101-pages-articles-multistream.xml-p1483662p2134111.bz2",
            "enwiki-20250101-some-other-file.txt",
        ]
        mock_cpu_count.return_value = 1
        mock_pool = MagicMock()
        mock_pool_cls.return_value.__enter__.return_value = mock_pool

        mock_pool.imap_unordered.return_value = iter(["result1", "result2"])
        mock_iterate_fn.side_effect = lambda args: f"parsed_{args[0].name}"

        parse_to_ndjson(
            output_path,
            target_dir,
            partitions_dir,
            article_limit,
            delete_parsed_files,
            force_download,
            multicore,
            verbose,
        )
        mock_exists.assert_called()
        mock_makedirs.assert_called()
        mock_pool.imap_unordered.assert_called_once()
