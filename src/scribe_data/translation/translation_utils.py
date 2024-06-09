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

from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

from scribe_data.utils import (
    get_language_iso,
    get_target_langcodes,
)


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
        f"{os.path.dirname(sys.path[0]).split('scribe_data')[0]}/../scribe_data_export/{source_language}/translated_words.json",
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

        translations : dict
            The current dictionary of translations.

        batch_size : int
            The number of words to translate in each batch.
    """
    model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
    tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

    signal.signal(
        signal.SIGINT,
        lambda sig, frame: translation_interrupt_handler(source_language, translations),
    )

    for i in range(0, len(word_list), batch_size):
        batch_words = word_list[i : i + batch_size]
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
                if word not in translations:
                    translations[word] = {}

                translations[word][lang_code] = translation

        print(f"Batch {i//batch_size + 1} translation completed.")

        with open(
            f"{os.path.dirname(sys.path[0]).split('scribe_data')[0]}/../scribe_data_export/{source_language}/translated_words.json",
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(translations, file, ensure_ascii=False, indent=4)

    print(
        "Translation results for all words are saved to the translated_words.json file."
    )
