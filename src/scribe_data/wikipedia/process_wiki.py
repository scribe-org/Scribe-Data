"""
Module for cleaning Wikipedia based corpuses for autosuggestion generation.

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

import json
import re
import warnings
from collections import Counter
from itertools import chain
from pathlib import Path
from urllib.error import HTTPError

import numpy as np
import regex
from tqdm.auto import tqdm

from scribe_data.utils import (
    DEFAULT_JSON_EXPORT_DIR,
    get_language_qid,
)
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
    Cleans text body to prepare it for analysis.

    Parameters
    ----------
        texts : str or list
            The texts to be cleaned and tokenized.

        language : string (default=en)
            The language of the texts being cleaned.

        remove_words : str or list (default=None)
            Strings that should be removed from the text body.

        sample_size : float (default=1)
            The amount of data to be randomly sampled.

        verbose : bool (default=True)
            Whether to show a tqdm progress bar for the process.

    Returns
    -------
        cleaned_texts : list
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
            if (len(w) != 1 or w in single_letter_words_dict[language])
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
    Generates a dictionary of common words (keys) and those that most commonly follow them (values).

    Parameters
    ----------
        text_corpus : list
            The Wikipedia texts formatted for word relation extraction.

        language : string (default=en)
            The language autosuggestions are being generated for.

        num_words: int (default=500)
            The number of words that autosuggestions should be generated for.

        ignore_words : str or list (default=None)
            Strings that should be removed from the text body.

        update_local_data : bool (default=False)
            Saves the created dictionaries as JSONs in the target directories.

        verbose : bool (default=True)
            Whether to show a tqdm progress bar for the process.

    Returns
    -------
        Autosuggestions dictionaries for common words are saved locally or uploaded to Scribe apps.
    """
    counter_obj = Counter(chain.from_iterable(text_corpus))

    top_words = [item[0] for item in counter_obj.most_common()][:num_words]

    if isinstance(ignore_words, str):
        words_to_ignore = [ignore_words]
    elif ignore_words is None:
        words_to_ignore += []

    print("Querying profanities to remove from suggestions.")
    # First format the lines into a multi-line string and then pass this to SPARQLWrapper.
    with open(
        Path(__file__).parent / "query_profanity.sparql", encoding="utf-8"
    ) as file:
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

    autosuggest_dict = {}
    for w in tqdm(
        top_words, desc="Autosuggestions generated", unit="word", disable=not verbose
    ):
        words_after_w = [
            [tup[1] for tup in zip(text, text[1:]) if w == tup[0]]
            for text in text_corpus
        ]

        flat_words_after_w = [item for sublist in words_after_w for item in sublist]

        autosuggestions = []
        for tup in Counter(flat_words_after_w).most_common():
            if (
                tup[0] != w
                and tup[0].lower() not in w.lower()
                and tup[0] not in profanities
                and tup[0] not in words_to_ignore
                and tup[0] != tup[0].upper()  # no upper case suggestions
                # Lots of detailed articles on WWII on Wikipedia.
                and tup[0].lower()[:4] != "nazi"
                and tup[0].lower()[:4] != "наци"
            ):
                autosuggestions.append(tup[0])

            if len(autosuggestions) == 3:
                break

        autosuggest_dict[w] = autosuggestions

    if not verbose:
        print(f"Autosuggestions for {language} generated.")

    if update_local_data:
        path_to_formatted_data = (
            Path(DEFAULT_JSON_EXPORT_DIR) / language / "autosuggestions.json"
        )

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
