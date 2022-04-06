"""
Format Verbs
------------

Formats the verbs queried from Wikidata using query_verbs.sparql.
"""

# pylint: disable=invalid-name, wrong-import-position

import collections
import json
import os
import sys

LANGUAGE = "German"
PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

from scribe_data.load.update_utils import (
    get_android_data_path,
    get_desktop_data_path,
    get_ios_data_path,
    get_path_from_format_file,
    get_path_from_update_data,
)

file_path = sys.argv[0]

update_data_in_use = False  # check if update_data.py is being used
if f"{LANGUAGE}/verbs/" not in file_path:
    with open("verbs_queried.json", encoding="utf-8") as f:
        verbs_list = json.load(f)
else:
    update_data_in_use = True
    with open(
        f"../extract_transform/{LANGUAGE}/verbs/verbs_queried.json", encoding="utf-8"
    ) as f:
        verbs_list = json.load(f)

# Get paths to load formatted data into.
path_from_file = get_path_from_format_file()
path_from_update_data = get_path_from_update_data()
ios_data_dir_from_org = get_ios_data_path(LANGUAGE, "verbs")
android_data_dir_from_org = get_android_data_path(LANGUAGE, "verbs")
desktop_data_dir_from_org = get_desktop_data_path(LANGUAGE, "verbs")

ios_output_path = f"{path_from_file}{ios_data_dir_from_org}"
android_output_path = f"{path_from_file}{android_data_dir_from_org}"
desktop_output_path = f"{path_from_file}{desktop_data_dir_from_org}"
if update_data_in_use:
    ios_output_path = f"{path_from_update_data}{ios_data_dir_from_org}"
    android_output_path = f"{path_from_update_data}{android_data_dir_from_org}"
    desktop_output_path = f"{path_from_update_data}{desktop_data_dir_from_org}"

all_output_paths = [ios_output_path, android_output_path, desktop_output_path]

# Check to make sure that Scribe application directories are present for data updates.
if not os.path.isdir(f"{PATH_TO_SCRIBE_ORG}Scribe-iOS"):
    all_output_paths = [p for p in all_output_paths if p != ios_output_path]

if not os.path.isdir(f"{PATH_TO_SCRIBE_ORG}Scribe-Android"):
    all_output_paths = [p for p in all_output_paths if p != android_output_path]

if not os.path.isdir(f"{PATH_TO_SCRIBE_ORG}Scribe-Desktop"):
    all_output_paths = [p for p in all_output_paths if p != desktop_output_path]

if not all_output_paths:
    raise OSError(
        """No Scribe project directories have been found to update.
        Scribe-Data should be in the same directory as applications that data should be updated for.
        """
    )

verbs_formatted = {}

all_keys = [
    "pastParticiple",
    "auxiliaryVerb",
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
    "perfFPS",
    "perfSPS",
    "perfTPS",
    "perfFPP",
    "perfSPP",
    "perfTPP",
]


def assign_past_participle(verb, tense):
    """
    Assigns the past participle after the auxiliary verb or by itself.
    """
    if verbs_formatted[verb["infinitive"]][tense] not in ["", verb["pastParticiple"]]:
        verbs_formatted[verb["infinitive"]][tense] += " " + verb["pastParticiple"]
    else:
        verbs_formatted[verb["infinitive"]][tense] = verb["pastParticiple"]


for verb_vals in verbs_list:
    if (
        "infinitive" in verb_vals.keys()
        and verb_vals["infinitive"] not in verbs_formatted
    ):
        non_infinitive_conjugations = {
            k: v for k, v in verb_vals.items() if k != "infinitive"
        }
        verbs_formatted[verb_vals["infinitive"]] = non_infinitive_conjugations

        for k in all_keys:
            if k not in verbs_formatted[verb_vals["infinitive"]].keys():
                verbs_formatted[verb_vals["infinitive"]][k] = ""

        if "auxiliaryVerb" in verb_vals.keys():
            # Sein
            if verb_vals["auxiliaryVerb"] == "L1761":
                verbs_formatted[verb_vals["infinitive"]]["auxiliaryVerb"] = "sein"

                verbs_formatted[verb_vals["infinitive"]]["perfFPS"] += "bin"
                verbs_formatted[verb_vals["infinitive"]]["perfSPS"] += "bist"
                verbs_formatted[verb_vals["infinitive"]]["perfTPS"] += "ist"
                verbs_formatted[verb_vals["infinitive"]]["perfFPP"] += "sind"
                verbs_formatted[verb_vals["infinitive"]]["perfSPP"] += "seid"
                verbs_formatted[verb_vals["infinitive"]]["perfTPP"] += "sind"

            # Haben
            elif verb_vals["auxiliaryVerb"] == "L4179":
                verbs_formatted[verb_vals["infinitive"]]["auxiliaryVerb"] = "haben"

                verbs_formatted[verb_vals["infinitive"]]["perfFPS"] += "habe"
                verbs_formatted[verb_vals["infinitive"]]["perfSPS"] += "hast"
                verbs_formatted[verb_vals["infinitive"]]["perfTPS"] += "hat"
                verbs_formatted[verb_vals["infinitive"]]["perfFPP"] += "haben"
                verbs_formatted[verb_vals["infinitive"]]["perfSPP"] += "habt"
                verbs_formatted[verb_vals["infinitive"]]["perfTPP"] += "haben"

    # The verb has two entries and thus has forms with both sein and haben.
    elif (
        "auxiliaryVerb" in verb_vals.keys()
        and verbs_formatted[verb_vals["infinitive"]]["auxiliaryVerb"]
        != verb_vals["auxiliaryVerb"]
    ):
        verbs_formatted[verb_vals["infinitive"]]["auxiliaryVerb"] = "sein/haben"

        verbs_formatted[verb_vals["infinitive"]]["perfFPS"] = "bin/habe"
        verbs_formatted[verb_vals["infinitive"]]["perfSPS"] = "bist/hast"
        verbs_formatted[verb_vals["infinitive"]]["perfTPS"] = "ist/hat"
        verbs_formatted[verb_vals["infinitive"]]["perfFPP"] = "sind/haben"
        verbs_formatted[verb_vals["infinitive"]]["perfSPP"] = "seid/habt"
        verbs_formatted[verb_vals["infinitive"]]["perfTPP"] = "sind/haben"

    if "pastParticiple" in verb_vals.keys():
        assign_past_participle(verb=verb_vals, tense="perfFPS")
        assign_past_participle(verb=verb_vals, tense="perfSPS")
        assign_past_participle(verb=verb_vals, tense="perfTPS")
        assign_past_participle(verb=verb_vals, tense="perfFPP")
        assign_past_participle(verb=verb_vals, tense="perfSPP")
        assign_past_participle(verb=verb_vals, tense="perfTPP")

verbs_formatted = collections.OrderedDict(sorted(verbs_formatted.items()))

for output_path in all_output_paths:
    with open(output_path, "w", encoding="utf-8",) as file:
        json.dump(verbs_formatted, file, ensure_ascii=False, indent=2)

print(f"Wrote file verbs.json with {len(verbs_formatted)} verbs.")
