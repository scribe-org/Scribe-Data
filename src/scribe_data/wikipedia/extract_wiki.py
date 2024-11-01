"""
Module for downloading and creating workable files from Wikipedia dumps.

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

import gc
import json
import os
import subprocess
import time
import xml.sax
from itertools import chain
from multiprocessing import Pool
from multiprocessing.dummy import Pool as Threadpool
from pathlib import Path

import defusedxml.sax
import mwparserfromhell
import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

from scribe_data.utils import get_language_iso


def download_wiki(language="en", target_dir="wiki_dump", file_limit=None, dump_id=None):
    """
    Downloads the most recent stable dump of a language's Wikipedia if it is not already present.

    Parameters
    ----------
        language : str (default=en)
            The language of Wikipedia to download.

        target_dir : pathlib.Path (default=wiki_dump)
            The directory in the pwd into which files should be downloaded.

        file_limit : int (default=None, all files)
            The limit for the number of files to download.

        dump_id : str (default=None)
            The id of an explicit Wikipedia dump that the user wants to download.

            Note: a value of None will select the third from the last (latest stable dump).

    Returns
    -------
        file_info : list of lists
            Information on the downloaded Wikipedia dump files.
    """
    if file_limit is not None:
        assert isinstance(
            file_limit, int
        ), "The 'file_limit' argument must be 'None' or an integer to subset the available files"
    else:
        file_limit = -1

    if not target_dir.exists():
        print(f"Making {target_dir} directory")
        os.makedirs(target_dir)

    base_url = f"https://dumps.wikimedia.org/{get_language_iso(language)}wiki/"
    index = requests.get(base_url, timeout=5).text
    soup_index = BeautifulSoup(index, "html.parser")

    all_dumps = [a["href"] for a in soup_index.find_all("a") if a.has_attr("href")]
    target_dump = all_dumps[-3]
    if dump_id is not None:
        if dump_id[-1] != "/":
            dump_id += "/"

        if dump_id in all_dumps:
            target_dump = dump_id

    dump_url = base_url + target_dump
    dump_html = requests.get(dump_url, timeout=5).text
    soup_dump = BeautifulSoup(dump_html, "html.parser")

    print(f"Downloading Wikipedia dump found at {dump_url}...")

    files = []
    for file in soup_dump.find_all("li", {"class": "file"}):
        text = file.text
        if "pages-articles-multistream" in text:
            files.append((text.split()[0], text.split()[1:]))

    # Don't select the combined dump so we can check the progress.
    files_to_download = [file[0] for file in files if ".xml-p" in file[0]][:file_limit]

    file_info = []

    file_present_bools = [(target_dir / f).exists() for f in files_to_download]
    dl_files = (
        any(b != file_present_bools[0] for b in file_present_bools)
        or file_present_bools[0] is not True
    )

    if dl_files:
        for f in files_to_download:
            file_path = target_dir / f
            if not file_path.exists():
                print(f"DL file to {file_path}")
                subprocess.run(["curl", "-o", file_path, dump_url + f], check=False)

                file_size = os.stat(file_path).st_size / 1e6
                total_articles = int(f.split("p")[-1].split(".")[-2]) - int(
                    f.split("p")[-2]
                )

                file_info.append((f.split("-")[-1], file_size, total_articles))

    else:
        print(f"Files already available in the {target_dir} directory.")
        for f in files_to_download:
            file_path = Path(target_dir) / f

            file_size = os.stat(file_path).st_size / 1e6
            total_articles = int(f.split("p")[-1].split(".")[-2]) - int(
                f.split("p")[-2]
            )

            file_info.append((f.split("-")[-1], file_size, total_articles))

    return file_info


def _process_article(title, text):
    """
    Process a wikipedia article to extract the title and text.

    Parameters
    ----------
        title : str
            The title of the article.

        text : str
            The text to be processed.

    Returns
    -------
        title, text:  string, string
            The data from the article.
    """
    wikicode = mwparserfromhell.parse(text)

    title = title.strip()
    text = wikicode.strip_code().strip()

    return title, text


def iterate_and_parse_file(args):
    """
    Creates partitions of desired articles.

    Parameters
    ----------
        args : tuple
            The below arguments as a tuple for pool.imap_unordered rather than pool.starmap.

        input_path : pathlib.Path
            The path to the data file.

        partitions_dir : pathlib.Path
            The path to where output file should be stored.

        article_limit : int (default=None)
            An optional article_limit of the number of articles to find.

        verbose : bool (default=True)
            Whether to show a tqdm progress bar for the processes.

    Returns
    -------
        A parsed file Wikipedia dump file with articles.
    """
    input_path, partitions_dir, article_limit, verbose = args

    if not partitions_dir.exists():
        print(f"Making {partitions_dir} directory for the partitions")
        os.makedirs(partitions_dir)

    handler = WikiXmlHandler()
    parser = defusedxml.sax.make_parser()
    parser.setContentHandler(handler)

    file_name = input_path.split("/")[-1].split("-")[-1].split(".")[-2]
    file_name = f"{file_name}.ndjson"
    output_path = Path(partitions_dir) / file_name

    if not output_path.exists():
        if article_limit is None:
            pbar = tqdm(
                total=len(
                    [
                        i
                        for i, line in enumerate(
                            subprocess.Popen(
                                ["bzcat"],
                                stdin=open(input_path, encoding="utf-8"),
                                stdout=subprocess.PIPE,
                            ).stdout
                        )
                    ]
                ),
                desc="Lines read",
                unit="lines",
                disable=not verbose,
            )
            for line in subprocess.Popen(
                ["bzcat"],
                stdin=open(input_path, encoding="utf-8"),
                stdout=subprocess.PIPE,
            ).stdout:
                try:
                    parser.feed(line)
                except StopIteration:
                    break

                pbar.update()

        else:
            pbar = tqdm(
                total=article_limit,
                desc="Articles found",
                unit="article",
                disable=not verbose,
            )
            articles_found = 0
            for line in subprocess.Popen(
                ["bzcat"],
                stdin=open(input_path, encoding="utf-8"),
                stdout=subprocess.PIPE,
            ).stdout:
                try:
                    parser.feed(line)
                except StopIteration:
                    break

                if len(handler.target_articles) == articles_found + 1:
                    articles_found += 1
                    pbar.update()

                if len(handler.target_articles) >= article_limit:
                    break

        with open(output_path, "w", encoding="utf-8") as f_out:
            for ta in handler.target_articles:
                f_out.write(json.dumps(ta) + "\n")

        if verbose:
            n_art = len(handler.target_articles)
            print(
                f"File {file_name} with {n_art} articles processed and saved in {partitions_dir}"
            )

    elif verbose:
        print(f"File {file_name} already exists in {partitions_dir}")

    del handler
    del parser
    gc.collect()

    return None


def parse_to_ndjson(
    output_path="articles",
    input_dir="wikipedia_dump",
    partitions_dir="partitions",
    article_limit=None,
    delete_parsed_files=False,
    multicore=True,
    verbose=True,
):
    """
    Finds all Wikipedia entries and converts them to json files.

    Parameters
    ----------
        output_path : str (default=articles)
            The name of the final output ndjson file.

        input_dir : str (default=wikipedia_dump)
            The path to the directory where the data is stored.

        partitions_dir : str (default=partitions)
            The path to the directory where the output should be stored.

        article_limit : int (default=None)
            An optional limit of the number of articles per dump file to find.

        delete_parsed_files : bool (default=False)
            Whether to delete the separate parsed files after combining them.

        multicore : bool (default=True)
            Whether to use multicore processing.

        verbose : bool (default=True)
            Whether to show a tqdm progress bar for the processes.

    Returns
    -------
        Wikipedia dump files parsed and converted to json files.
    """
    output_dir = "/".join(list(output_path.split("/")[:-1]))
    if not output_dir.exists():
        print(f"Making {output_dir} directory for the output")
        os.makedirs(output_dir)

    if multicore:
        num_cores = os.cpu_count()
    elif not multicore:
        num_cores = 1
    elif isinstance(multicore, int):
        num_cores = multicore

    if output_path is None:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        output_path = f"parsed_data{timestr}"
        output_file_name = f"{output_path}.ndjson"

    else:
        if output_path[-len(".ndjson") :] != ".ndjson":
            output_file_name = f"{output_path}.ndjson"
        else:
            output_file_name = output_path

    if not output_file_name.exists():
        if not partitions_dir.exists():
            print(f"Making {partitions_dir} directory for the partitions")
            os.makedirs(partitions_dir)

        target_files = [
            Path(input_dir) / f for f in os.listdir(input_dir) if "pages-articles" in f
        ]

        parse_inputs = zip(
            target_files,
            [partitions_dir] * len(target_files),
            [article_limit] * len(target_files),
            [False] * len(target_files),
        )

        if __name__ == "scribe_data.wikipedia.extract_wiki":
            with Pool(processes=num_cores) as pool:
                for _ in tqdm(
                    pool.imap_unordered(iterate_and_parse_file, parse_inputs),
                    total=len(target_files),
                    desc="Files partitioned",
                    unit="file",
                    disable=not verbose,
                ):
                    pass

        def read_and_combine_json(file_path):
            """
            Read in json data from a file_path.
            """
            data = []

            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    data.append(json.loads(line))

            return data

        threadpool = Threadpool(processes=num_cores)
        partition_files = [
            Path(partitions_dir) / f
            for f in os.listdir(partitions_dir)
            if f[-len(".ndjson") :] == ".ndjson"
        ]

        if __name__ == "scribe_data.wikipedia.extract_wiki":
            results = threadpool.map(read_and_combine_json, partition_files)

        file_list = list(chain(*results))

        with open(output_file_name, "wt", encoding="utf-8") as f_out:
            for f in file_list:
                f_out.write(json.dumps(f) + "\n")
        print(f"File {output_file_name} with Wikipedia articles saved")

    else:
        print(f"File {output_file_name} with Wikipedia articles already exists")

    if delete_parsed_files and partitions_dir.exists():
        print(f"Deleting {partitions_dir} directory")
        os.system(f"rm -rf {partitions_dir}")

    return


class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """
    Parse through XML data using SAX.
    """

    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self.target_articles = []

    def characters(self, content):
        """
        Characters between opening and closing tags.
        """
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        """
        Opening tag of element.
        """
        if name in ("title", "text"):
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        """
        Closing tag of element.
        """
        if name == self._current_tag:
            self._values[name] = " ".join(self._buffer)

        if name == "page":
            target_article = _process_article(**self._values)
            if target_article and (
                "Wikipedia:" not in target_article[0]
                and "Draft:" not in target_article[0]
            ):  # no archive files or drafts
                self.target_articles.append(target_article)
