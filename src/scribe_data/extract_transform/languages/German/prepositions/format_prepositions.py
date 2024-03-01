"""
Format Prepositions
-------------------

Formats the prepositions queried from Wikidata using query_prepositions.sparql.
"""

import collections
import os
import sys

PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)
from scribe_data.utils import export_formatted_data, load_queried_data

LANGUAGE = "German"
QUERIED_DATA_TYPE = "prepositions"

file_path = sys.argv[0]

prepositions_list, update_data_in_use, data_path= load_queried_data(LANGUAGE, QUERIED_DATA_TYPE, file_path)


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

export_formatted_data(LANGUAGE, QUERIED_DATA_TYPE, prepositions_formatted, update_data_in_use)
os.remove(data_path)
