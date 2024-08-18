"""
Updates words to translate by running the WDQS query for the given languages.

Parameters
----------
    languages : list of strings (default=None)
        A subset of Scribe's languages that the user wants to update.

Example
-------
    python3 src/scribe_data/translation/update_words_to_translate.py '["French", "German"]'

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
import sys
import urllib
from pathlib import Path

from tqdm.auto import tqdm

from scribe_data.utils import (
    check_and_return_command_line_args,
    get_language_qid,
    get_scribe_languages,
)
from scribe_data.wikidata.wikidata_utils import sparql

PATH_TO_LANGUAGE_DATA_EXTRACTION = (
    Path(__file__).parent.parent / "language_data_extraction"
)

# Note: Check whether arguments have been passed to only update a subset of the data.
languages, _ = check_and_return_command_line_args(
    all_args=sys.argv,
    first_args_check=get_scribe_languages(),
)

if languages is None:
    languages = get_scribe_languages()

for lang in tqdm(
    languages,
    desc="Data updated",
    unit="languages",
):
    print(f"Querying words for {lang}...")
    # First format the lines into a multi-line string and then pass this to SPARQLWrapper.
    with open(
        Path(__file__).parent / "query_words_to_translate.sparql", encoding="utf-8"
    ) as file:
        query_lines = file.readlines()

    query = "".join(query_lines).replace("LANGUAGE_QID", get_language_qid(lang))
    sparql.setQuery(query)

    results = None
    try:
        results = sparql.query().convert()
    except urllib.error.HTTPError as err:
        print(f"HTTPError with query_words_to_translate.sparql for {lang}: {err}")

    if results is None:
        print(
            f"Nothing returned by the WDQS server for query_words_to_translate.sparql for {lang}"
        )

        # Allow for a query to be reran up to two times.
        if languages.count(lang) < 3:
            languages.append(lang)

    else:
        # Subset the returned JSON and the individual results before saving.
        print(f"Success! Formatting {lang} words...")
        query_results = results["results"]["bindings"]

        all_words = []
        results_formatted = []
        for r in query_results:  # query_results is also a list
            r_dict = {"word": r[k]["value"] for k in r.keys()}

            # Assure that results are unique.
            if r_dict["word"] not in all_words:
                all_words.append(r_dict["word"])
                results_formatted.append(r_dict)

        results_sorted = sorted(results_formatted, key=lambda x: x["word"])

        with open(
            PATH_TO_LANGUAGE_DATA_EXTRACTION
            / lang
            / "translations"
            / "words_to_translate.json",
            "w",
            encoding="utf-8",
        ) as file:
            file.write(json.dumps(results_sorted, ensure_ascii=False, indent=0))
            file.write("\n")
            print(
                f"Wrote the words to translate to {PATH_TO_LANGUAGE_DATA_EXTRACTION / lang / 'translations' /'words_to_translate.json'}"
            )
