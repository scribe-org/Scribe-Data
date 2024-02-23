"""
Format Verbs
------------

Formats the verbs queried from Wikidata using query_verbs.sparql.

Attn: The formatting in the file is significantly more complex than for other verbs.
    - We have two queries: query_verbs_1 and query_verbs_2.
    - For the second query we could get two different auxiliary verbs (could be sein and haben).
    - We thus need to get the results for the first and then check if we need to combine the second.
"""

import collections
import json
import os
import sys

LANGUAGE = "German"
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

# Note: The following are combined later: perfFPS, perfSPS, perfTPS, perfFPP, perfSPP, perfTPP
all_query_1_conjugations = [
    "presFPS",
    "presSPS",
    "presTPS",
    "presFPP",
    "presSPP",
    "presTPP",
]

all_query_2_conjugations = [
    "pastParticiple",
    "auxiliaryVerb",
    "pretFPS",
    "pretSPS",
    "pretTPS",
    "pretFPP",
    "pretSPP",
    "pretTPP",
]


def assign_past_participle(verb, tense):
    """
    Assigns the past participle after the auxiliary verb or by itself.
    """
    if verbs_formatted[verb][tense] == "":
        verbs_formatted[verb][tense] = verbs_formatted[verb]["pastParticiple"]
    else:
        verbs_formatted[verb][tense] += f" {verbs_formatted[verb]['pastParticiple']}"


for verb_vals in verbs_list:
    if verb_vals["infinitive"] not in verbs_formatted.keys():
        verbs_formatted[verb_vals["infinitive"]] = {}

    # Note: query_verbs_1 result - we want all values.
    if "auxiliaryVerb" not in verb_vals.keys():
        for k in all_query_1_conjugations:
            if k in verb_vals.keys():
                verbs_formatted[verb_vals["infinitive"]][k] = verb_vals[k]
            else:
                verbs_formatted[verb_vals["infinitive"]][k] = ""

    # Note: query_verbs_2 first time seeing verb - we want all values.
    elif (
        "auxiliaryVerb" in verb_vals.keys()
        and "auxiliaryVerb" not in verbs_formatted[verb_vals["infinitive"]].keys()
    ):
        for k in all_query_2_conjugations:
            if k in verb_vals.keys():
                verbs_formatted[verb_vals["infinitive"]][k] = verb_vals[k]
            else:
                verbs_formatted[verb_vals["infinitive"]][k] = ""

        # Note: Sein
        if verb_vals["auxiliaryVerb"] == "L1761":
            verbs_formatted[verb_vals["infinitive"]]["auxiliaryVerb"] = "sein"

            verbs_formatted[verb_vals["infinitive"]]["perfFPS"] = "bin"
            verbs_formatted[verb_vals["infinitive"]]["perfSPS"] = "bist"
            verbs_formatted[verb_vals["infinitive"]]["perfTPS"] = "ist"
            verbs_formatted[verb_vals["infinitive"]]["perfFPP"] = "sind"
            verbs_formatted[verb_vals["infinitive"]]["perfSPP"] = "seid"
            verbs_formatted[verb_vals["infinitive"]]["perfTPP"] = "sind"

        # Note: Haben
        elif verb_vals["auxiliaryVerb"] == "L4179":
            verbs_formatted[verb_vals["infinitive"]]["auxiliaryVerb"] = "haben"

            verbs_formatted[verb_vals["infinitive"]]["perfFPS"] = "habe"
            verbs_formatted[verb_vals["infinitive"]]["perfSPS"] = "hast"
            verbs_formatted[verb_vals["infinitive"]]["perfTPS"] = "hat"
            verbs_formatted[verb_vals["infinitive"]]["perfFPP"] = "haben"
            verbs_formatted[verb_vals["infinitive"]]["perfSPP"] = "habt"
            verbs_formatted[verb_vals["infinitive"]]["perfTPP"] = "haben"

        # Note: No auxiliaryVerb for this verb.
        elif verb_vals["auxiliaryVerb"] == "":
            verbs_formatted[verb_vals["infinitive"]]["perfFPS"] = ""
            verbs_formatted[verb_vals["infinitive"]]["perfSPS"] = ""
            verbs_formatted[verb_vals["infinitive"]]["perfTPS"] = ""
            verbs_formatted[verb_vals["infinitive"]]["perfFPP"] = ""
            verbs_formatted[verb_vals["infinitive"]]["perfSPP"] = ""
            verbs_formatted[verb_vals["infinitive"]]["perfTPP"] = ""

    # Note: query_verbs_2 second time seeing verb.
    elif (
        "auxiliaryVerb" in verb_vals.keys()
        and "auxiliaryVerb" in verbs_formatted[verb_vals["infinitive"]].keys()
    ):
        # Note: Neither is "" and they're not the same, so we have the same verb with two different auxiliaries.
        if (
            verbs_formatted[verb_vals["infinitive"]]["auxiliaryVerb"] != ""
            and verb_vals["auxiliaryVerb"] != ""
        ) and (
            verbs_formatted[verb_vals["infinitive"]]["auxiliaryVerb"]
            != verb_vals["auxiliaryVerb"]
        ):
            verbs_formatted[verb_vals["infinitive"]]["auxiliaryVerb"] = "sein/haben"

            verbs_formatted[verb_vals["infinitive"]]["perfFPS"] = "bin/habe"
            verbs_formatted[verb_vals["infinitive"]]["perfSPS"] = "bist/hast"
            verbs_formatted[verb_vals["infinitive"]]["perfTPS"] = "ist/hat"
            verbs_formatted[verb_vals["infinitive"]]["perfFPP"] = "sind/haben"
            verbs_formatted[verb_vals["infinitive"]]["perfSPP"] = "seid/habt"
            verbs_formatted[verb_vals["infinitive"]]["perfTPP"] = "sind/haben"

for k in verbs_formatted.keys():
    assign_past_participle(verb=k, tense="perfFPS")
    assign_past_participle(verb=k, tense="perfSPS")
    assign_past_participle(verb=k, tense="perfTPS")
    assign_past_participle(verb=k, tense="perfFPP")
    assign_past_participle(verb=k, tense="perfSPP")
    assign_past_participle(verb=k, tense="perfTPP")

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
