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
import os
import signal
import sys
from functools import lru_cache
from pathlib import Path

from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

from scribe_data.utils import (
    DEFAULT_JSON_EXPORT_DIR,
    get_language_iso,
    get_target_langcodes,
)
from scribe_data.wikidata.wikidata_utils import JSON, sparql

LANGUAGE_METADATA_FILE = (
    Path(__file__).parent.parent / "resources" / "language_metadata.json"
)

with LANGUAGE_METADATA_FILE.open("r", encoding="utf-8") as file:
    language_data = json.load(file)


@lru_cache(maxsize=None)
def get_language_qid(language: str) -> str:
    """
    Get the QID for a given language name.

    Parameters
    ----------
        language : str
            The language for a Wikidata QID should be returned.

    Returns
    -------
        str
            The Wikidata QID for the given language.
    """
    normalized_language = language.lower()
    return next(
        (
            lang["qid"]
            for lang in language_data["languages"]
            if lang["language"] == normalized_language
        ),
        None,
    )


@lru_cache(maxsize=None)
def get_all_articles(language: str) -> list[str]:
    """
    Get all articles for a given language.

    Parameters
    ----------
        language : str
            The language for which articles should be retrieved from Wikidata.

    Returns
    -------
        List[str]
            The articles for the given language as found on Wikidata.
    """
    qid_from_language_metadata = get_language_qid(language)
    query = f"""
    SELECT DISTINCT
        ?article

    WHERE {{
        VALUES ?language {{ wd:{qid_from_language_metadata} }}
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

    return [result["article"]["value"] for result in results["results"]["bindings"]]


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
        f"{os.path.dirname(sys.path[0]).split('scribe_data')[0]}/../{DEFAULT_JSON_EXPORT_DIR}/{source_language}/translated_words.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(translations, file, ensure_ascii=False, indent=4)

    print("The current progress is saved to the translated_words.json file.")
    exit()


def translate_to_other_languages(source_language, word_list, translations, batch_size):
    """
    Translates a list of words from the source language to other target languages using batch processing.

    Parameters
    ----------
        source_language : str
            The source language being translated from.

        word_list : list[str]
            The list of words to translate.

        translations : list
            The current list of translation dictionaries.

        batch_size : int
            The number of words to translate in each batch.
    """
    model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
    tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

    signal.signal(
        signal.SIGINT,
        lambda sig, frame: translation_interrupt_handler(source_language, translations),
    )
    articles = get_all_articles(source_language)

    for i in range(0, len(word_list), batch_size):
        batch_words = word_list[i : i + batch_size]
        batch_words = remove_articles_from_words(batch_words, articles)

        print(f"Translating batch {i//batch_size + 1}: {batch_words}")

        for lang_code in get_target_langcodes(source_language):
            tokenizer.src_lang = get_language_iso(source_language)
            encoded_words = tokenizer(batch_words, return_tensors="pt", padding=True)
            generated_tokens = model.generate(
                **encoded_words, forced_bos_token_id=tokenizer.get_lang_id(lang_code)
            )
            translated_words = tokenizer.batch_decode(
                generated_tokens, skip_special_tokens=True
            )

            for word, translation in zip(batch_words, translated_words):
                # Find if the word already exists in translations.
                existing_entry = next(
                    (item for item in translations if word in item), None
                )

                if existing_entry is None:
                    # If the word doesn't exist, create a new entry.
                    new_entry = {word: {lang_code: translation}}
                    translations.append(new_entry)

                else:
                    # If the word exists, update its translations.
                    existing_entry[word][lang_code] = translation

        print(f"Batch {i//batch_size + 1} translation completed.")

        with open(
            f"{os.path.dirname(sys.path[0]).split('scribe_data')[0]}/../{DEFAULT_JSON_EXPORT_DIR}/{source_language}/translated_words.json",
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(translations, file, ensure_ascii=False, indent=4)

    print(
        "Translation results for all words are saved to the translated_words.json file."
    )
