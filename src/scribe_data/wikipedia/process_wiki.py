# SPDX-License-Identifier: GPL-3.0-or-later
"""
Module for cleaning Wikipedia based corpuses for autosuggestion generation.
"""

import json
import re
import warnings
from collections import Counter, defaultdict
from itertools import chain
from pathlib import Path
from urllib.error import HTTPError

import numpy as np
import regex
from tqdm.auto import tqdm

from scribe_data.utils import DEFAULT_JSON_EXPORT_DIR, get_language_qid
from scribe_data.wikidata.wikidata_utils import sparql

warnings.filterwarnings("ignore", message=r"Passing", category=FutureWarning)


def clean(
    texts,
    language="English",
    remove_words=None,
    sample_size=1,
    verbose=True,
):
    """
    Clean text body to prepare it for analysis.

    Parameters
    ----------
    texts : str or list
        The texts to be cleaned and tokenized.

    language : str (default=en)
        The language of the texts being cleaned.

    remove_words : str or list (default=None)
        Strings that should be removed from the text body.

    sample_size : float (default=1)
        The amount of data to be randomly sampled.

    verbose : bool (default=True)
        Whether to show a tqdm progress bar for the process.

    Returns
    -------
    list
        The texts formatted for analysis.
    """
    if isinstance(texts, str):
        texts = [texts]

    language = language.lower()

    if isinstance(remove_words, str):
        words_to_remove = [remove_words]
    elif remove_words is None:
        words_to_remove = []

    # Add words that are common in Wikipedia article markdown.
    words_to_remove += [
        "nbsp",
        "ISBN",
        "Chr",
        "Nr",
        "PAGENAME",
        "REDIRECT",
        "REDIRECTION",
        "WEITERLEITUNG",
        "SORTIERUNG",
        "REDIRECIONAMENTO",
        "REDIRECCIÓN",
        "OMDIRIGERING",
        "VOLUME",
        "fontsizeS",
        "RINVIA",
        "LINEAR",
        "DateFormat",
        "pxlink",
        "ddmmyyyy",
        "TimeAxis",
        "ScaleMajor",
        "ScaleMinor",
        "PlotData",
        "PlotArea",
        "BarData",
        "BackgroundColors",
        "AlignBars",
        "TextData",
        "ImageSize",
        "LepIndex",
        "ITIS",
        "INSEE",
        "WCSP",
        "NODC",
        "colorblack",
        "colorbars",
        "alignright",
        "alignleft",
        "hmin",
        "hmax",
        "bgcolor",
        "xy",
        "centerpx",
        "px",
        "cdot",
        "UTC",
        "EuroMed",
        "msg",
        "WPProject",
        "WPProjekt",
    ]
    words_to_remove += []

    if sample_size < 1:
        idxs = range(len(texts))
        selected_idxs = np.random.choice(
            a=idxs, size=int(sample_size * len(texts)), replace=False
        )

        print(
            f"Randomly sampling {len(selected_idxs):,} {language.capitalize()} Wikipedia articles..."
        )
        texts = [texts[i] for i in selected_idxs]
        print("Random sampling finished.")

    cleaned_texts = []
    for t in tqdm(texts, desc="Articles cleaned", unit="articles", disable=not verbose):
        # Remove all websites and new line markers.
        websites = [word for word in t.split() if word[:4] == "http"]
        for w in websites:
            t = t.replace(w, "")

        # Remove all text between parentheses, brackets, braces and multiple equal signs.
        t = re.sub(r"\([^)]*\)", "", t)
        t = re.sub(r"\[.*?\]", "", t)
        t = re.sub(r"<[^>]+>", "", t)
        t = re.sub(r"===[^>]+===", "", t)
        t = re.sub(r"==[^>]+==", "", t)
        t = re.sub(r"{{[^>]+}}", "", t)
        t = re.sub(r"{[^>]+}", "", t)

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
            "–",
            # "-", we do hyphenated words later
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
            "·",
            "«",
            "»",
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
            "\n",
        ]

        wikipedia_namespaces = [
            # English
            "Talk:",
            "User:",
            "Wikipedia:",
            "File:",
            "MediaWiki:",
            "Template:",
            "Help:",
            "Category:",
            "Portal:",
            "Draft:",
            "Topic:",
            # French
            "Discussion:",
            "Utilisateur:",
            "Catégorie:",
            "Aide:",
            "Portail:",
            # German
            "Diskussion:",
            "Benutzer:",
            "Kategorie:",
            "Hilfe:",
            # Italian
            "Discussioni:",
            "Discussione:",
            "Utente:",
            "Aiuto:",
            "Categoria:",
            "Portale:",
            # Portuguese
            "Wikipédia:",
            "Discussão:",
            "Usuário(a):",
            "Ficheiro:",
            "Predefinição:",
            "Ajuda:",
            "Tópico:",
            # Russian
            "Обсуждение:",
            "Участник:",
            "Википедия:",
            "Категория:",
            "Портал:",
            # Spanish
            "Discusión:",
            "Usuario:",
            "Archivo:",
            "Plantilla:",
            "Ayuda:",
            "Categoría:",
            # Swedish
            "Diskussion:",
            "Användare:",
            "Kategori",
            "Fil:",
            "Mall:",
            "Hjälp:",
        ]

        # Remove namespaces before symbols as ":" is in the symbols.
        wikipedia_namespaces += symbols_to_remove
        for s in wikipedia_namespaces:
            t = t.replace(s, "")

        if language == "russian":
            # Remove Latin characters that aren't in Cyrillic.
            t = regex.sub(r"[+/p{Latin}]", "", t)

        # Remove all spaces that are larger than one in length.
        for i in range(
            25, 0, -1
        ):  # loop backwards to assure that smaller spaces aren't made
            large_space = str(i * " ")
            if large_space in t:
                t = t.replace(large_space, " ")

        if t not in ["", " "]:
            cleaned_texts.append(t)

    single_letter_words_dict = {
        "french": ["a", "à", "y"],
        "german": ["à"],
        "italian": ["a", "e", "è", "i", "o"],
        "portuguese": ["a", "e", "é", "o"],
        "russian": ["а", "б", "в", "ж", "и", "к", "о", "с", "у", "я"],
        "spanish": ["a", "e", "o", "u", "y"],
        "swedish": ["à", "å", "i", "ö"],
    }

    return [
        [
            w
            for w in text.split()
            if (len(w) != 1 or w in single_letter_words_dict.get(language, []))
            and w not in words_to_remove
            and "nbsp" not in w
            and "-" not in w
            and "Wikipedia" not in w
            and w != "-"
        ]
        for text in tqdm(
            cleaned_texts, desc="Articles checked", unit="articles", disable=not verbose
        )
        if text != ""
    ]


def gen_autosuggestions(
    text_corpus,
    language="English",
    num_words=500,
    ignore_words=None,
    update_local_data=False,
    verbose=True,
):
    """
    Generate a dictionary of common words (keys) and those that most commonly follow them (values).

    Parameters
    ----------
    text_corpus : list
        The Wikipedia texts formatted for word relation extraction.

    language : str (default=en)
        The language autosuggestions are being generated for.

    num_words : int (default=500)
        The number of words that autosuggestions should be generated for.

    ignore_words : str or list (default=None)
        Strings that should be removed from the text body.

    update_local_data : bool (default=False)
        Saves the created dictionaries as JSONs in the target directories.

    verbose : bool (default=True)
        Whether to show a tqdm progress bar for the process.

    Returns
    -------
    dict
        Autosuggestions dictionaries for common words are saved locally or uploaded to Scribe apps.
    """
    counter_obj = Counter(chain.from_iterable(text_corpus))

    top_words = [item[0] for item in counter_obj.most_common(num_words)]

    words_to_ignore = []
    if isinstance(ignore_words, str):
        words_to_ignore = [ignore_words]
    elif ignore_words is None:
        words_to_ignore = []

    print("Querying profanities to remove from suggestions.")
    query_path = (
        Path(__file__).parent.resolve() / ".." / "wikidata" / "query_profanity.sparql"
    )
    # First format the lines into a multi-line string and then pass this to SPARQLWrapper.
    with open(query_path, encoding="utf-8") as file:
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
        query_results = results["results"]["bindings"]  # pylint: disable=unsubscriptable-object

        for r in query_results:  # query_results is also a list
            r_dict = {k: r[k]["value"] for k in r.keys()}
            profanities.append(r_dict["lemma"])

        print(
            f"Queried {len(profanities)} words to be removed from autosuggest options."
        )

    # Precompute bigram frequencies
    print("Precomputing word relationships (bigrams)...")
    bigram_counter = defaultdict(Counter)
    for text in tqdm(
        text_corpus, desc="Building bigrams", unit="article", disable=not verbose
    ):
        for w1, w2 in zip(text, text[1:]):
            bigram_counter[w1][w2] += 1

    # Build autosuggestions
    autosuggest_dict = {}
    for w in tqdm(
        top_words, desc="Autosuggestions generated", unit="word", disable=not verbose
    ):
        candidates = bigram_counter[w].most_common()
        autosuggestions = []

        for next_word, _ in candidates:
            if (
                next_word != w
                and next_word.lower() not in w.lower()
                and next_word not in profanities
                and next_word not in words_to_ignore
                and next_word != next_word.upper()  # no upper case suggestions
                and not next_word.lower().startswith(
                    ("nazi", "наци")
                )  # Lots of detailed articles on WWII on wikipedia
            ):
                autosuggestions.append(next_word)

            if len(autosuggestions) == 3:
                break

        autosuggest_dict[w] = autosuggestions

    if not verbose:
        print(f"Autosuggestions for {language} generated.")

    if update_local_data:
        path_to_formatted_data = (
            Path(DEFAULT_JSON_EXPORT_DIR) / language / "autosuggestions.json"
        )

        # Create directory if it does not exist before attempting to write the file.
        path_to_formatted_data.parent.mkdir(parents=True, exist_ok=True)

        with open(
            path_to_formatted_data,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(autosuggest_dict, file, ensure_ascii=False, indent=0)

        print(
            f"Autosuggestions for {language} generated and saved to '{path_to_formatted_data}'."
        )

        return autosuggest_dict

    return autosuggest_dict
