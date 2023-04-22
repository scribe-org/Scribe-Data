"""
Format Prepositions
-------------------

Formats the prepositions queried from Wikidata using query_prepositions.sparql.
"""

# pylint: disable=invalid-name

import collections
import json
import os
import sys

LANGUAGE = "German"
PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

from scribe_data.load.update_utils import get_path_from_et_dir

file_path = sys.argv[0]

update_data_in_use = False  # check if update_data.py is being used
if f"{LANGUAGE}/prepositions/" not in file_path:
    with open("prepositions_queried.json", encoding="utf-8") as f:
        prepositions_list = json.load(f)
else:
    update_data_in_use = True
    with open(
        f"./{LANGUAGE}/prepositions/prepositions_queried.json", encoding="utf-8",
    ) as f:
        prepositions_list = json.load(f)


def convert_cases(case):
    """
    Converts cases as found on Wikidata to more succinct versions.
    """
    case = case.split(" case")[0]
    if case in ["accusative", "Q146078"]:
        return "Acc"
    elif case in ["dative", "Q145599"]:
        return "Dat"
    elif case in ["genitive", "Q146233"]:
        return "Gen"
    else:
        return ""


def order_annotations(annotation):
    """
    Standardizes the annotations that are presented to users where more than one is applicable.

    Parameters
    ----------
        annotation : str
            The annotation to be returned to the user in the command bar.
    """
    single_annotations = ["Akk", "Dat", "Gen"]
    if annotation in single_annotations:
        return annotation

    annotation_split = sorted(annotation.split("/"))

    return "/".join(annotation_split)


prepositions_formatted = {}

for prep_vals in prepositions_list:
    if "preposition" in prep_vals.keys():
        if "case" in prep_vals.keys():
            if prep_vals["preposition"] not in prepositions_formatted:
                prepositions_formatted[prep_vals["preposition"]] = convert_cases(
                    prep_vals["case"]
                )

            else:
                prepositions_formatted[prep_vals["preposition"]] += "/" + convert_cases(
                    prep_vals["case"]
                )

        elif (
            "case" not in prep_vals.keys() and prep_vals["preposition"] != "a"
        ):  # à is the correct preposition
            prepositions_formatted[prep_vals["preposition"]] = ""

for k in prepositions_formatted:
    prepositions_formatted[k] = order_annotations(prepositions_formatted[k])

    # Contracted versions of German prepositions (ex: an + dem = am).
contractedGermanPrepositions = {
    "am": "Acc/Dat",
    "ans": "Acc/Dat",
    "aufs": "Acc/Dat",
    "beim": "Dat",
    "durchs": "Acc",
    "fürs": "Acc",
    "hinters": "Acc/Dat",
    "hinterm": "Acc/Dat",
    "ins": "Acc/Dat",
    "im": "Acc/Dat",
    "übers": "Acc/Dat",
    "überm": "Acc/Dat",
    "ums": "Acc",
    "unters": "Acc/Dat",
    "unterm": "Acc/Dat",
    "vom": "Dat",
    "vors": "Acc/Dat",
    "vorm": "Acc/Dat",
    "zum": "Dat",
    "zur": "Dat",
}

for p in contractedGermanPrepositions:
    if p not in prepositions_formatted:
        prepositions_formatted[p] = contractedGermanPrepositions[p]

prepositions_formatted = collections.OrderedDict(sorted(prepositions_formatted.items()))

org_path = get_path_from_et_dir()
export_path = "../formatted_data/prepositions.json"
if update_data_in_use:
    export_path = f"{org_path}/Scribe-Data/src/scribe_data/extract_transform/{LANGUAGE}/formatted_data/prepositions.json"

with open(export_path, "w", encoding="utf-8",) as file:
    json.dump(prepositions_formatted, file, ensure_ascii=False, indent=0)

print(f"Wrote file prepositions.json with {len(prepositions_formatted)} prepositions.")
