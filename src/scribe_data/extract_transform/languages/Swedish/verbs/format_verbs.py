"""
Formats the Swedish verbs queried from Wikidata using query_verbs.sparql.
"""

import collections
import os
import sys

PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

from scribe_data.utils import export_formatted_data, load_queried_data

file_path = sys.argv[0]

verbs_list, update_data_in_use, data_path= load_queried_data(file_path, language = "Swedish", data_type = "verbs")

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

export_formatted_data(verbs_formatted, update_data_in_use, language = "Swedish", data_type = "verbs")

os.remove(data_path)
