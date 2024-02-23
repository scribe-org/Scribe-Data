"""
Format Nouns
------------

Formats the nouns queried from Wikidata using query_nouns.sparql.
"""

import collections
import json
import os
import sys

LANGUAGE = "English"
PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
LANGUAGES_DIR_PATH = (
    f"{PATH_TO_SCRIBE_ORG}/Scribe-Data/src/scribe_data/extract_transform/languages"
)

file_path = sys.argv[0]

update_data_in_use = False  # check if update_data.py is being used
if f"languages/{LANGUAGE}/nouns/" not in file_path:
    with open("nouns_queried.json", encoding="utf-8") as f:
        nouns_list = json.load(f)
else:
    update_data_in_use = True
    with open(
        f"{LANGUAGES_DIR_PATH}/{LANGUAGE}/nouns/nouns_queried.json",
        encoding="utf-8",
    ) as f:
        nouns_list = json.load(f)

nouns_formatted = {}

for noun_vals in nouns_list:
    if "singular" in noun_vals.keys():
        if noun_vals["singular"] not in nouns_formatted:
            if "plural" in noun_vals.keys():
                nouns_formatted[noun_vals["singular"]] = {
                    "plural": noun_vals["plural"],
                    "form": "",
                }

                # Assign plural as a new entry after checking if it's its own plural.
                if noun_vals["plural"] not in nouns_formatted:
                    if noun_vals["singular"] != noun_vals["plural"]:
                        nouns_formatted[noun_vals["plural"]] = {
                            "plural": "isPlural",
                            "form": "PL",
                        }

                    else:
                        nouns_formatted[noun_vals["plural"]] = {
                            "plural": noun_vals["plural"],
                            "form": "PL",
                        }
                else:
                    # Mark plural as a possible form if it isn't already.
                    if nouns_formatted[noun_vals["plural"]]["form"] == "":
                        nouns_formatted[noun_vals["plural"]]["form"] = "PL"

                    # Assign itself as a plural if possible (maybe wasn't for prior versions).
                    if noun_vals["singular"] == noun_vals["plural"]:
                        nouns_formatted[noun_vals["plural"]]["plural"] = noun_vals[
                            "plural"
                        ]
            else:
                nouns_formatted[noun_vals["singular"]] = {
                    "plural": "",
                    "form": "",
                }

    elif "plural" in noun_vals.keys():
        if noun_vals["plural"] not in nouns_formatted:
            nouns_formatted[noun_vals["plural"]] = {
                "plural": "isPlural",
                "form": "PL",
            }

        else:
            # Mark plural as a possible form if it isn't already.
            if (
                "PL" not in nouns_formatted[noun_vals["plural"]]["form"]
                and nouns_formatted[noun_vals["plural"]]["form"] != ""
            ):
                nouns_formatted[noun_vals["plural"]]["form"] = (
                    nouns_formatted[noun_vals["plural"]]["form"] + "/PL"
                )

            elif nouns_formatted[noun_vals["plural"]]["form"] == "":
                nouns_formatted[noun_vals["plural"]]["form"] = "PL"

nouns_formatted = collections.OrderedDict(sorted(nouns_formatted.items()))

export_dir = "../formatted_data/"
export_path = os.path.join(export_dir, "nouns.json")
if update_data_in_use:
    export_path = f"{LANGUAGES_DIR_PATH}/{LANGUAGE}/formatted_data/nouns.json"

if not os.path.exists(export_dir):
    os.makedirs(export_dir)

with open(
    export_path,
    "w",
    encoding="utf-8",
) as file:
    json.dump(nouns_formatted, file, ensure_ascii=False, indent=0)

print(f"Wrote file nouns.json with {len(nouns_formatted)} nouns.")
