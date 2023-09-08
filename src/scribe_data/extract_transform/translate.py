"""
Translate
---------

Translates the words queried from Wikidata using query_words_to_translate.sparql.

Example
-------
    python translate.py '["French", "Portuguese"]' '["German"]'
"""

import collections
import json
import os
import sys

from tqdm.auto import tqdm
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

from scribe_data.utils import (
    check_and_return_command_line_args,
    get_language_iso,
    get_scribe_languages,
)

# Note: Check whether arguments have been passed to only update a subset of the data.
src_languages, target_languages = check_and_return_command_line_args(
    all_args=sys.argv,
    first_args_check=get_scribe_languages(),
    second_args_check=get_scribe_languages(),
)

# Assign current_languages and current_word_types if no arguments have been passed.
if src_languages is None:
    src_languages = get_scribe_languages()

if target_languages is None:
    target_languages = get_scribe_languages()

for src_lang in src_languages:
    for target_lang in [l for l in target_languages if l != src_lang]:
        print(
            f"Translating {get_language_iso(src_lang)} to {get_language_iso(target_lang)}"
        )

"""
Note: Before `target_lang` is defined.

with open("src_lang/words_to_translate.json", encoding="utf-8") as f:
    translations_list = json.load(f)

words_to_translate = [translation_vals["value"] for translation_vals in translations_list]
words_to_translate = list(set(words_to_translate))

translations_formatted = {}

Note: After `target_lang` is defined.

for w in tqdm(
    words_to_translate[:100],
    desc="Words translated",
    unit="word",
):
    See: https://huggingface.co/facebook/m2m100_418M
    Output:
    {
        book: {
            "es": "libro",
            "de": "Buch"
        }
    }

translations_formatted = collections.OrderedDict(sorted(translations_formatted.items()))

with open(
    "src_lang/formatted_data/translations.json",
    "w",
    encoding="utf-8",
) as f:
    json.dump(translations_formatted, f, ensure_ascii=False, indent=0)

print(f"Wrote file translations.json with {len(translations_formatted)} translations.")
"""
