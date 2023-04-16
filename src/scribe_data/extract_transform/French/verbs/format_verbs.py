"""
Format Verbs
------------

Formats the verbs queried from Wikidata using query_verbs.sparql.
"""

# pylint: disable=invalid-name

import collections
import json
import os
import sys

LANGUAGE = "French"
PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

from scribe_data.load.update_utils import get_path_from_et_dir

file_path = sys.argv[0]

update_data_in_use = False  # check if update_data.py is being used
if f"{LANGUAGE}/verbs/" not in file_path:
    with open("verbs_queried.json", encoding="utf-8") as f:
        verbs_list = json.load(f)
else:
    update_data_in_use = True
    with open(f"./{LANGUAGE}/verbs/verbs_queried.json", encoding="utf-8") as f:
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

org_path = get_path_from_et_dir()
export_path = "../formatted_data/verbs.json"
if update_data_in_use:
    export_path = f"{org_path}/Scribe-Data/src/scribe_data/extract_transform/{LANGUAGE}/formatted_data/verbs.json"

with open(export_path, "w", encoding="utf-8",) as file:
    json.dump(verbs_formatted, file, ensure_ascii=False, indent=0)

print(f"Wrote file verbs.json with {len(verbs_formatted)} verbs.")
