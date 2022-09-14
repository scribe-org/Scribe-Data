"""
Process Wiki
------------

Module for cleaning Wikipedia based corpuses for autosuggestion generation.

Contents:
    clean,
    gen_autosuggestions
"""

import json
import re
import warnings
from collections import Counter
from itertools import chain
from urllib.error import HTTPError

import numpy as np
from scribe_data.load.update_utils import (
    get_android_data_path,
    get_desktop_data_path,
    get_ios_data_path,
    get_language_qid,
    get_path_from_update_data,
)
from SPARQLWrapper import JSON, POST, SPARQLWrapper
from tqdm.auto import tqdm

warnings.filterwarnings("ignore", message=r"Passing", category=FutureWarning)

# Set SPARQLWrapper query conditions.
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)
sparql.setMethod(POST)


def clean(
    texts, ignore_words=None, sample_size=1, verbose=True,
):
    """
    Cleans text body to prepare it for analysis.

    Parameters
    ----------
        texts : str or list
            The texts to be cleaned and tokenized.

        ignore_words : str or list (default=None)
            Strings that should be removed from the text body.

        sample_size : float (default=1)
            The amount of data to be randomly sampled.

        verbose : bool (default=True)
            Whether to show a tqdm progress bar for the query.

    Returns
    -------
        cleaned_texts : list
            The texts formatted for analysis.
    """
    if isinstance(texts, str):
        texts = [texts]

    if isinstance(ignore_words, str):
        words_to_ignore = [ignore_words]
    elif ignore_words is None:
        words_to_ignore = []

    cleaned_texts = []
    for t in tqdm(texts, desc="Articles cleaned", unit="article", disable=not verbose):
        # Remove words that should be ignored.
        for w in words_to_ignore:
            t = t.replace(w, "")

        # Remove all websites and new line markers.
        websites = [word for word in t.split() if word[:4] == "http"]
        for w in websites:
            t = t.replace(w, "")

        t = t.replace("\n", "")

        # Remove all text between parentheses, brackets and braces.
        t = re.sub(r"\([^)]*\)", "", t)
        t = re.sub(r"\[.*?\]", "", t)
        t = re.sub(r"<[^>]+>", "", t)

        # Remove numbers and symbols.
        t = "".join(c for c in t if not c.isdigit())

        symbols_to_remove = [
            "!",
            "@",
            "#",
            "$",
            "%",
            "^",
            "&",
            "*",
            "",
            "_",
            "+",
            "=",
            "`",
            "~",
            "|",
            "\\",
            ";",
            ":",
            '"',
            "„",
            "“",
            "?",
            "/",
            ",",
            ".",
        ]
        for s in symbols_to_remove:
            t = t.replace(s, "")

        # Remove all spaces that are larger than one in length.
        for i in range(
            25, 0, -1
        ):  # loop backwards to assure that smaller spaces aren't made
            large_space = str(i * " ")
            if large_space in t:
                t = t.replace(large_space, " ")

        if t not in ["", " "]:
            cleaned_texts.append(t)

    # Randomly sample texts if necessary.
    original_len = len(texts)
    if sample_size == 1 or len(cleaned_texts) <= int(sample_size * original_len):
        return [t.split() for t in cleaned_texts]

    idxs = range(len(cleaned_texts))
    selected_idxs = np.random.choice(
        a=idxs, size=int(sample_size * original_len), replace=False
    )

    return [cleaned_texts[i].split() for i in selected_idxs]


def gen_autosuggestions(
    text_corpus, language="English", num_words=500, update_scribe_apps=False
):
    """
    Generates a dictionary of common words (keys) and those that most commonly follow them (values).

    Parameters
    ----------
        text_corpus : list
            The Wikipedia texts formatted for word relation extraction.

        language : string (default=en)
            The language autosuggestions are being generated for.

        num_words: int (default=500)
            The number of words that autosuggestions should be generated for.

        update_scribe : bool (default=False)
            Saves the created dictionaries as JSONs in Scribe app directories.

    Returns
    -------
        Autosuggestions dictionaries for common words are saved locally or uploaded to Scribe apps.
    """
    counter_obj = Counter(chain.from_iterable(text_corpus))

    top_words = [item[0] for item in counter_obj.most_common()][:num_words]

    print("Querying profanities to remove from suggestions.")
    # First format the lines into a multi-line string and then pass this to SPARQLWrapper.
    with open("../extract_transform/query_profanity.sparql", encoding="utf-8") as file:
        query_lines = file.readlines()

    query = "".join(query_lines).replace(
        "LANGUAGE_QID", get_language_qid(language=language)
    )
    sparql.setQuery(query)

    results = None
    try:
        results = sparql.query().convert()
    except HTTPError as err:
        print(f"HTTPError with query_profanity.sparql: {err}")

    profanities = []

    if results is None:
        print("Nothing returned by the WDQS server for query_profanity.sparql")
    else:
        # Subset the returned JSON and the individual results before saving.
        query_results = results["results"][  # pylint: disable=unsubscriptable-object
            "bindings"
        ]

        for r in query_results:  # query_results is also a list
            r_dict = {k: r[k]["value"] for k in r.keys()}
            profanities.append(r_dict["lemma"])

        print(
            f"Queried {len(profanities)} words to be removed from autosuggest options."
        )

    print("Generating autosuggestions.")
    autosuggest_dict = {}
    for w in top_words:
        words_after_w = [
            [tup[1] for tup in zip(text, text[1:]) if w == tup[0]]
            for text in text_corpus
        ]

        flat_words_after_w = [item for sublist in words_after_w for item in sublist]

        autosuggestions = []
        for tup in Counter(flat_words_after_w).most_common():
            if tup[0] not in profanities:
                autosuggestions.append(tup[0])

            if len(autosuggestions) == 3:
                break

        autosuggest_dict[w] = autosuggestions

    if update_scribe_apps:
        # Get paths to load formatted data into.
        path_to_scribe_org = get_path_from_update_data()
        ios_data_dir_from_org = get_ios_data_path(language, "autosuggestions")
        android_data_dir_from_org = get_android_data_path(language, "autosuggestions")
        desktop_data_dir_from_org = get_desktop_data_path(language, "autosuggestions")

        ios_output_path = f"{path_to_scribe_org}{ios_data_dir_from_org}"
        android_output_path = f"{path_to_scribe_org}{android_data_dir_from_org}"
        desktop_output_path = f"{path_to_scribe_org}{desktop_data_dir_from_org}"

        all_output_paths = [ios_output_path, android_output_path, desktop_output_path]

        for output_path in all_output_paths:
            with open(output_path, "w", encoding="utf-8",) as file:
                json.dump(autosuggest_dict, file, ensure_ascii=False, indent=2)

        print(f"Autosuggestions for {language} saved to Scribe app directories.")

        return

    return autosuggest_dict
