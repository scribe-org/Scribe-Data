"""
Format Verbs
------------

Formats the verbs queried from Wikidata using query_verbs.sparql.
"""

import collections
import json
import os
import sys

LANGUAGE = "Swedish"
QUERIED_DATA_TYPE = "verbs"
QUERIED_DATA_FILE = f"{QUERIED_DATA_TYPE}_queried.json"
PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
LANGUAGES_DIR_PATH = (
    f"{PATH_TO_SCRIBE_ORG}/Scribe-Data/src/scribe_data/extract_transform/languages"
)

file_path = sys.argv[0]

update_data_in_use = False  # check if update_data.py is being used
if f"languages/{LANGUAGE}/{QUERIED_DATA_TYPE}/" not in file_path:
    data_path = QUERIED_DATA_FILE
else:
    update_data_in_use = True
    data_path = (
        f"{LANGUAGES_DIR_PATH}/{LANGUAGE}/{QUERIED_DATA_TYPE}/{QUERIED_DATA_FILE}"
    )

with open(data_path, encoding="utf-8") as f:
    verbs_list = json.load(f)

verbs_formatted = {}

# Any verbs occurring more than once will for now be deleted.
verbs_not_included = []

all_conjugations = [
    "activeInfinitive",
    "imperative",
    "activeSupine",
    "activePresent",
    "activePreterite",
    "passiveInfinitive",
    "passiveSupine",
    "passivePresent",
    "passivePreterite",
]

for verb_vals in verbs_list:
    if (
        verb_vals["activeInfinitive"] not in verbs_formatted
        and verb_vals["activeInfinitive"] not in verbs_not_included
    ):
        verbs_formatted[verb_vals["activeInfinitive"]] = {
            conj: verb_vals[conj] if conj in verb_vals.keys() else ""
            for conj in [c for c in all_conjugations if c != "activeInfinitive"]
        }

    elif verb_vals["activeInfinitive"] in verbs_formatted:
        verbs_not_included.append(verb_vals["activeInfinitive"])
        del verbs_formatted[verb_vals["activeInfinitive"]]

verbs_formatted = collections.OrderedDict(sorted(verbs_formatted.items()))

export_path = f"../formatted_data/{QUERIED_DATA_TYPE}.json"
if update_data_in_use:
    export_path = (
        f"{LANGUAGES_DIR_PATH}/{LANGUAGE}/formatted_data/{QUERIED_DATA_TYPE}.json"
    )

with open(
    export_path,
    "w",
    encoding="utf-8",
) as file:
    json.dump(verbs_formatted, file, ensure_ascii=False, indent=0)

print(
    f"Wrote file {QUERIED_DATA_TYPE}.json with {len(verbs_formatted):,} {QUERIED_DATA_TYPE}."
)

os.remove(data_path)
