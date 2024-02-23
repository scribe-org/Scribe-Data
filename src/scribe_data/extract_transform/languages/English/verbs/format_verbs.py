"""
Format Verbs
------------

Formats the verbs queried from Wikidata using query_verbs.sparql.
"""

import collections
import json
import os
import sys

LANGUAGE = "English"
PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

from scribe_data.utils import get_path_from_et_dir  # noqa: E402

file_path = sys.argv[0]

update_data_in_use = False  # check if update_data.py is being used
if f"languages/{LANGUAGE}/verbs/" not in file_path:
    with open("verbs_queried.json", encoding="utf-8") as f:
        verbs_list = json.load(f)
else:
    update_data_in_use = True
    with open(
        f"./languages/{LANGUAGE}/verbs/verbs_queried.json", encoding="utf-8"
    ) as f:
        verbs_list = json.load(f)

verbs_formatted = {}

all_conjugations = [
    "presFPS",
    "presSPS",
    "presTPS",
    "presFPP",
    "presSPP",
    "presTPP",
    "pastFPS",
    "pastSPS",
    "pastTPS",
    "pastFPP",
    "pastSPP",
    "pastTPP",
    "pastPart",
]

for verb_vals in verbs_list:
    # If infinitive is available add to formatted verbs, else no entry created.
    if verb_vals["infinitive"] not in verbs_formatted.keys():
        verbs_formatted[verb_vals["infinitive"]] = {}

        infinitive_key = verb_vals["infinitive"]
        # presFPS
        verbs_formatted[infinitive_key]["presFPS"] = verb_vals.get("presFPS", "")
        verbs_formatted[infinitive_key]["presSPS"] = verb_vals.get("presFPS", "")

        # presTPS
        verbs_formatted[infinitive_key]["presTPS"] = verb_vals.get("presTPS", "")

        # Copying over presFPS to remaining present cases.
        verbs_formatted[infinitive_key]["presFPP"] = verb_vals.get("presFPS", "")
        verbs_formatted[infinitive_key]["presSPP"] = verb_vals.get("presFPS", "")
        verbs_formatted[infinitive_key]["presTPP"] = verb_vals.get("presFPS", "")

        # Assigning simpPast to all past keys if available.
        verbs_formatted[infinitive_key]["pastFPS"] = verb_vals.get("simpPast", "")
        verbs_formatted[infinitive_key]["pastSPS"] = verb_vals.get("simpPast", "")
        verbs_formatted[infinitive_key]["pastTPS"] = verb_vals.get("simpPast", "")
        verbs_formatted[infinitive_key]["pastFPP"] = verb_vals.get("simpPast", "")
        verbs_formatted[infinitive_key]["pastSPP"] = verb_vals.get("simpPast", "")
        verbs_formatted[infinitive_key]["pastTPP"] = verb_vals.get("simpPast", "")

        # pastParticiple
        verbs_formatted[infinitive_key]["pastPart"] = verb_vals.get("pastPart", "")

verbs_formatted = collections.OrderedDict(sorted(verbs_formatted.items()))

org_path = get_path_from_et_dir()
export_dir = "../formatted_data/"
export_path = os.path.join(export_dir, "verbs.json")
if update_data_in_use:
    export_path = f"{org_path}/Scribe-Data/src/scribe_data/extract_transform/languages/{LANGUAGE}/formatted_data/verbs.json"

if not os.path.exists(export_dir):
    os.makedirs(export_dir)

with open(
    export_path,
    "w",
    encoding="utf-8",
) as file:
    json.dump(verbs_formatted, file, ensure_ascii=False, indent=0)

print(f"Wrote file verbs.json with {len(verbs_formatted)} verbs.")
