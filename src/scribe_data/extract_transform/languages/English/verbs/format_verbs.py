"""
Formats the English verbs queried from Wikidata using query_verbs.sparql.
"""

import collections
import os
import sys

PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

from scribe_data.utils import export_formatted_data, load_queried_data

file_path = sys.argv[0]

verbs_list, update_data_in_use, data_path= load_queried_data(file_path, language = "English", data_type = "verbs")

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

export_formatted_data(verbs_formatted, update_data_in_use, language = "English", data_type = "verbs")

os.remove(data_path)
