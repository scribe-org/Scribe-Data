"""
Utility functions for the machine translation process.

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
import signal
import time
from functools import lru_cache
from pathlib import Path

from scribe_data.utils import (
    DEFAULT_JSON_EXPORT_DIR,
    get_language_iso,
    get_target_lang_codes,
)
from scribe_data.wikidata.wikidata_utils import JSON, sparql

LANGUAGE_METADATA_FILE = (
    Path(__file__).parent.parent / "resources" / "language_metadata.json"
)

with LANGUAGE_METADATA_FILE.open("r", encoding="utf-8") as file:
    language_data = json.load(file)


@lru_cache(maxsize=None)
def get_articles_dict() -> dict:
    """
    Get all articles for all languages that Scribe-Data supports.

    Returns
    -------
        dict[str: list]
            The articles for all languages as found on Wikidata.
    """
    all_scribe_lang_isos = [lang["iso"] for lang in language_data["languages"]]
    all_scribe_lang_qids = [lang["qid"] for lang in language_data["languages"]]

    articles_dict = {}

    for i, lang in enumerate(all_scribe_lang_isos):
        query = f"""
        SELECT DISTINCT
            ?article

        WHERE {{
            VALUES ?language {{ wd:{all_scribe_lang_qids[i]} }}
            ?lexeme dct:language ?language ;
            wikibase:lexicalCategory ?category ;
            wikibase:lemma ?lemma .

            # Definite, indefinite articles and Partitive Articles
            VALUES ?category {{ wd:Q2865743 wd:Q3813849 wd:Q576670 }}

            {{
                ?lexeme wikibase:lemma ?article .
            }} UNION {{
                ?lexeme ontolex:lexicalForm ?form .
                ?form ontolex:representation ?article .
            }}
        }}
        """

        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        articles_dict[lang] = [
            result["article"]["value"] for result in results["results"]["bindings"]
        ]

    return articles_dict


def remove_articles_from_words(
    batch_words: list[str], articles: list[str]
) -> list[str]:
    """
    Remove articles from a given list of words.

    Parameters
    ----------
        batch_words : List[str]
            The words derived as translations.

        articles : List[str]
            The articles to remove from translations.

    Returns
    -------
        List[str]
            Translated words without the articles for the language in question.
    """

    def remove_article(word: str) -> str:
        for article in articles:
            if word.lower().startswith(f"{article.lower()} "):
                return word[len(article) :].strip()

        return word

    return [remove_article(word) for word in batch_words]


def translation_interrupt_handler(source_language, translations):
    """
    Handles interrupt signals and saves the current translation progress.

    Parameters
    ----------
        source_language : str
            The source language being translated from.

        translations : list[dict]
            The current list of translations.
    """
    print(
        "\nThe interrupt signal has been caught and the current progress is being saved..."
    )

    with open(
        Path(DEFAULT_JSON_EXPORT_DIR) / source_language / "translations.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(translations, file, ensure_ascii=False, indent=0)

    print("The current progress is saved to the translations.json file.")
    exit()
