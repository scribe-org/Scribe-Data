# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for generating autosuggestions from wikipedia dump.
"""

import json

from tqdm.auto import tqdm

from scribe_data.utils import get_language_iso
from scribe_data.wikipedia.extract_wiki import download_wiki, parse_to_ndjson
from scribe_data.wikipedia.process_wiki import clean, gen_autosuggestions


def generate_autosuggestions(language, dump_id, force_download):
    """
    Generate autosuggestions from Wikipedia articles for a given language.

    This function downloads a Wikipedia dump, extracts and cleans article texts,
    and generates autosuggestions based on the processed text. If no matching dump is found, the function exits early.

    Parameters
    ----------
    language : str
        The language for which autosuggestions should be generated.

    dump_id : str (default=None)
        The id of an explicit Wikipedia dump that the user wants to download.

        Note: A value of None will select the third from the last (latest stable dump).

    force_download : bool (default=False)
        This argument forces re-download already existing dump_id if True.

    Returns
    -------
    None
        The function does not return anything but generates autosuggestions
        and updates local data.
    """

    language_abbr = get_language_iso(language)
    target_dir = f"./{language_abbr}wiki_dump"
    if dump_id:
        target_dir = f"./{language_abbr}wiki_dump/{dump_id[:8]}"
    files = download_wiki(
        language=language,
        target_dir=target_dir,
        file_limit=None,  # Note: Limit for autosuggestion development.
        dump_id=dump_id,
        force_download=force_download,
    )

    print(f"Number of files: {len(files)}")
    if not files:
        print(
            f"Can not generate autosuggestions for {language}. No dump matches the condition."
        )
        return

    output_path = f"./{language_abbr}wiki.ndjson"
    if dump_id:
        output_path = f"./{language_abbr}wiki-{dump_id}.ndjson"
    parse_to_ndjson(
        output_path=output_path,
        input_dir=target_dir,
        partitions_dir=f"./{language_abbr}wiki_partitions",
        article_limit=None,
        delete_parsed_files=True,
        force_download=force_download,
        multicore=True,
        verbose=True,
    )

    with open(f"./{language_abbr}wiki.ndjson", "r") as fin:
        article_texts = [
            json.loads(lang)[1]
            for lang in tqdm(fin, desc="Articles added", unit="articles")
        ]

    print(f"Number of articles: {len(article_texts)}")

    # Define sample size for up to 1 million articles.
    sample_size = 1000000 / len(article_texts)
    sample_size = min(sample_size, 1)

    text_corpus = clean(
        texts=article_texts,
        language=language,
        remove_words=None,
        sample_size=sample_size,
        verbose=True,
    )

    gen_autosuggestions(
        text_corpus,
        language=language,
        num_words=500,  # Note: Limit for autosuggestion development.
        ignore_words=None,
        update_local_data=True,
        verbose=True,
    )
