"""
Update Words to Translate
-------------------------

Updates words to translate by running the WDQS query for the given languages.

Parameters
----------
    languages : list of strings (default=None)
        A subset of Scribe's languages that the user wants to update.

Example
-------
    python update_words_to_translate.py '["French", "German"]'
"""

import json
import os
import sys

from SPARQLWrapper import JSON, POST, SPARQLWrapper
from tqdm.auto import tqdm

PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

from scribe_data.utils import (
    check_and_return_command_line_args,
    get_language_qid,
    get_scribe_languages,
)

PATH_TO_ET_FILES = "./"

# Set SPARQLWrapper query conditions.
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)
sparql.setMethod(POST)

# Note: Check whether arguments have been passed to only update a subset of the data.
languages, _ = check_and_return_command_line_args(
    all_args=sys.argv,
    first_args_check=get_scribe_languages(),
)

if languages is None:
    languages = get_scribe_languages()

for l in tqdm(
    languages,
    desc="Data updated",
    unit="languages",
):
    print(f"Querying words for {l}...")
    # First format the lines into a multi-line string and then pass this to SPARQLWrapper.
    with open("query_words_to_translate.sparql", encoding="utf-8") as file:
        query_lines = file.readlines()

    query = "".join(query_lines).replace("LANGUAGE_QID", get_language_qid(l))
    sparql.setQuery(query)

    results = None
    try:
        results = sparql.query().convert()
    except HTTPError as err:
        print(f"HTTPError with query_words_to_translate.sparql for {l}: {err}")

    if results is None:
        print(
            f"Nothing returned by the WDQS server for query_words_to_translate.sparql for {l}"
        )

        # Allow for a query to be reran up to two times.
        if languages.count(l) < 3:
            languages.append(l)

    else:
        # Subset the returned JSON and the individual results before saving.
        print(f"Success! Formatting {l} words...")
        query_results = results["results"]["bindings"]

        results_formatted = []
        for r in query_results:  # query_results is also a list
            r_dict = {k: r[k]["value"] for k in r.keys()}

            results_formatted.append(r_dict)

        with open(
            f"{PATH_TO_ET_FILES}{l}/translations/words_to_translate.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(results_formatted, f, ensure_ascii=False, indent=0)
            print(
                f"Wrote the words to translate to {PATH_TO_ET_FILES}{l}/translations/words_to_translate.json"
            )
