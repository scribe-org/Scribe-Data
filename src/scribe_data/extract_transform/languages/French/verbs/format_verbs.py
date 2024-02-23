"""
Format Verbs
------------

Formats the verbs queried from Wikidata using query_verbs.sparql.
"""

import collections
import json
import os
import sys

LANGUAGE = "French"
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

all_conjugations = [
    "presFPS",
    "presSPS",
    "presTPS",
    "presFPP",
    "presSPP",
    "presTPP",
    "pretFPS",
    "pretSPS",
    "pretTPS",
    "pretFPP",
    "pretSPP",
    "pretTPP",
    "impFPS",
    "impSPS",
    "impTPS",
    "impFPP",
    "impSPP",
    "impTPP",
    "futFPS",
    "futSPS",
    "futTPS",
    "futFPP",
    "futSPP",
    "futTPP",
]

for verb_vals in verbs_list:
    if verb_vals["infinitive"] not in verbs_formatted:
        verbs_formatted[verb_vals["infinitive"]] = {}

        for conj in all_conjugations:
            if conj in verb_vals.keys():
                verbs_formatted[verb_vals["infinitive"]][conj] = verb_vals[conj]
            else:
                verbs_formatted[verb_vals["infinitive"]][conj] = ""

    else:
        for conj in all_conjugations:
            if conj in verb_vals.keys():
                verbs_formatted[verb_vals["infinitive"]][conj] = verb_vals[conj]

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
