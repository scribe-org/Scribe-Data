# SPDX-License-Identifier: GPL-3.0-or-later
"""
Module for downloading and creating workable files from Wikipedia dumps.
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
import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

from scribe_data.utils import get_language_iso


def download_wiki(language="en", target_dir="wiki_dump", file_limit=None, dump_id=None):
    """
    Download the most recent stable dump of a language's Wikipedia if it is not already present.

    Parameters
    ----------
    language : str, optional
        The language of Wikipedia to download. Default is "en".
    target_dir : str or pathlib.Path, optional
        The directory in the current working directory where files should be downloaded. Default is "wiki_dump".
    file_limit : int, optional
        The maximum number of files to download. Default is None (all files).
    dump_id : str, optional
        The ID of a specific Wikipedia dump to download. Default is None (latest stable dump).

    Returns
    -------
    list
        A list of lists containing information on the downloaded Wikipedia dump files (filename, size, article count).
    """
    if file_limit is not None:
        assert isinstance(
            file_limit, int
        ), "The 'file_limit' argument must be 'None' or an integer to subset the available files"
    else:
        file_limit = -1

    target_dir = Path(target_dir)  # Ensure Path object
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


def iterate_and_parse_file(args):
    """
    Iterate over a Wikipedia dump file and parse it into partitions.

    Parameters
    ----------
    args : tuple
        A tuple of (input_path, partitions_dir, article_limit, verbose) for multiprocessing.

    Returns
    -------
    None
        Indicates successful completion of parsing.
    """
    input_path, partitions_dir, article_limit, verbose = args

    partitions_dir = Path(partitions_dir)  # Ensure Path object
    if not partitions_dir.exists():
        print(f"Making {partitions_dir} directory for the partitions")
        os.makedirs(partitions_dir)

    handler = WikiXmlHandler()
    parser = defusedxml.sax.make_parser()
    parser.setContentHandler(handler)

    file_name = input_path.split("/")[-1].split("-")[-1].split(".")[-2]
    file_name = f"{file_name}.ndjson"
    output_path = partitions_dir / file_name

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
    Parse Wikipedia entries and convert them to NDJSON files.

    Parameters
    ----------
    output_path : str or pathlib.Path, optional
        The name of the final output NDJSON file. Default is "articles".
    input_dir : str or pathlib.Path, optional
        The path to the directory where the data is stored. Default is "wikipedia_dump".
    partitions_dir : str or pathlib.Path, optional
        The path to the directory where the output should be stored. Default is "partitions".
    article_limit : int, optional
        An optional limit of the number of articles per dump file to find. Default is None.
    delete_parsed_files : bool, optional
        Whether to delete the separate parsed files after combining them. Default is False.
    multicore : bool or int, optional
        Whether to use multicore processing (True), single-core (False), or specify cores (int). Default is True.
    verbose : bool, optional
        Whether to show a tqdm progress bar for the processes. Default is True.

    Returns
    -------
    None
        Indicates successful conversion of Wikipedia dump files to NDJSON format.
    """

    output_dir = Path("/".join(str(output_path).split("/")[:-1]))
    if not output_dir.exists():
        print(f"Making {output_dir} directory for the output")
        os.makedirs(output_dir)

    if multicore is True:
        num_cores = os.cpu_count()
    elif multicore is False:
        num_cores = 1
    elif isinstance(multicore, int):
        num_cores = multicore

    if output_path is None:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        output_path = f"parsed_data{timestr}"
        output_file_name = f"{output_path}.ndjson"
    else:
        output_path = Path(output_path)
        if output_path.suffix != ".ndjson":
            output_file_name = f"{output_path}.ndjson"
        else:
            output_file_name = output_path

    if not output_file_name.exists():
        partitions_dir = Path(partitions_dir)
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
            [verbose] * len(target_files),  # Fixed: was [False], now respects verbose
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
            if f.endswith(".ndjson")
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


# ... (imports and other functions unchanged) ...


def _process_article(title, text):
    """
    Extract title and text from a Wikipedia article.

    Parameters
    ----------
    title : str
        The title of the article.
    text : str
        The text to be processed.

    Returns
    -------
    tuple
        A tuple of (title, text) extracted from the article.
    """


class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """
    Parse XML data using SAX for Wikipedia articles.

    Attributes
    ----------
    _buffer : list
        Temporary storage for tag content.
    _values : dict
        Collected tag values (title, text).
    _current_tag : str
        The current XML tag being processed.
    target_articles : list
        List of parsed (title, text) tuples.
    """

    def __init__(self):
        """
        Initialize the WikiXmlHandler with empty buffers and storage.
        """
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self.target_articles = []

    def startElement(self, name, attrs):
        """
        Opening tag of element.

        Parameters
        ----------
        name : str
            The name of the XML tag.
        attrs : dict
            Attributes of the XML tag.
        """
        if name in ("title", "text"):
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        """
        Closing tag of element.

        Parameters
        ----------
        name : str
            The name of the XML tag.
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
