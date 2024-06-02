"""
Formats the Italian verbs queried from Wikidata using query_verbs.sparql.
"""

import collections
import os
import sys

from scribe_data.utils import export_formatted_data, load_queried_data

LANGUAGE = "Italian"
DATA_TYPE = "verbs"
file_path = sys.argv[0]

verbs_list, update_data_in_use, data_path = load_queried_data(
    file_path=file_path, language=LANGUAGE, data_type=DATA_TYPE
)

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

export_formatted_data(
    formatted_data=verbs_formatted,
    update_data_in_use=update_data_in_use,
    language=LANGUAGE,
    data_type=DATA_TYPE,
)

os.remove(data_path)
