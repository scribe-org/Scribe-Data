"""
Format Verbs
------------

Formats the verbs queried from Wikidata using query_verbs.sparql.
"""

# pylint: disable=invalid-name

import collections
import json
import sys

from data.data_utils import (
    get_android_data_path,
    get_desktop_data_path,
    get_ios_data_path,
    get_path_from_format_file,
    get_path_from_update_data,
)

file_path = sys.argv[0]

update_data_in_use = False  # check if update_data.py is being used
if "Portuguese/verbs/" not in file_path:
    with open("verbs_queried.json", encoding="utf-8") as f:
        verbs_list = json.load(f)
else:
    with open("./Portuguese/verbs/verbs_queried.json", encoding="utf-8") as f:
        verbs_list = json.load(f)
        update_data_in_use = True

path_from_file = get_path_from_format_file()
path_from_update_data = get_path_from_update_data()
ios_data_dir_from_org = get_ios_data_path("Portuguese", "verbs")
android_data_dir_from_org = get_android_data_path("Portuguese", "verbs")
desktop_data_dir_from_org = get_desktop_data_path("Portuguese", "verbs")

ios_output_path = f"{path_from_file}{ios_data_dir_from_org}"
android_output_path = f"{path_from_file}{android_data_dir_from_org}"
desktop_output_path = f"{path_from_file}{desktop_data_dir_from_org}"
if update_data_in_use:
    ios_output_path = f"{path_from_update_data}{ios_data_dir_from_org}"
    android_output_path = f"{path_from_update_data}{android_data_dir_from_org}"
    desktop_output_path = f"{path_from_update_data}{desktop_data_dir_from_org}"

all_output_paths = [ios_output_path, android_output_path, desktop_output_path]

verbs_formatted = {}

all_keys = [
    "infinitive",
    "presFPS",
    "presSPS",
    "presTPS",
    "presFPP",
    "presSPP",
    "presTPP",
    "perfFPS",
    "perfSPS",
    "perfTPS",
    "perfFPP",
    "perfSPP",
    "perfTPP",
    "impFPS",
    "impSPS",
    "impTPS",
    "impFPP",
    "impSPP",
    "impTPP",
    "fSimpFPS",
    "fSimpSPS",
    "fSimpTPS",
    "fSimpFPP",
    "fSimpSPP",
    "fSimpTPP",
]

for verb_vals in verbs_list:
    verbs_formatted[verb_vals["infinitive"]] = {}

    for conj in [c for c in all_keys if c != "infinitive"]:
        if conj in verb_vals.keys():
            verbs_formatted[verb_vals["infinitive"]][conj] = verb_vals[conj]
        else:
            verbs_formatted[verb_vals["infinitive"]][conj] = ""

verbs_formatted = collections.OrderedDict(sorted(verbs_formatted.items()))

for output_path in all_output_paths:
    with open(output_path, "w", encoding="utf-8",) as file:
        json.dump(verbs_formatted, file, ensure_ascii=False, indent=2)

print(f"Wrote file verbs.json with {len(verbs_formatted)} verbs.")
