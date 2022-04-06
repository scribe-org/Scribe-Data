"""
Format Prepositions
-------------------

Formats the prepositions queried from Wikidata using query_prepositions.sparql.
"""

# pylint: disable=invalid-name, wrong-import-position

import collections
import json
import os
import sys

LANGUAGE = "Russian"
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
if f"{LANGUAGE}/prepositions/" not in file_path:
    with open("prepositions_queried.json", encoding="utf-8") as f:
        prepositions_list = json.load(f)
else:
    update_data_in_use = True
    with open(
        f"../extract_transform/{LANGUAGE}/prepositions/prepositions_queried.json",
        encoding="utf-8",
    ) as f:
        prepositions_list = json.load(f)

# Get paths to load formatted data into.
path_from_file = get_path_from_format_file()
path_from_update_data = get_path_from_update_data()
ios_data_dir_from_org = get_ios_data_path(LANGUAGE, "prepositions")
android_data_dir_from_org = get_android_data_path(LANGUAGE, "prepositions")
desktop_data_dir_from_org = get_desktop_data_path(LANGUAGE, "prepositions")

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
    elif case in ["instrumental", "Q192997"]:
        return "Ins"
    elif case in ["prepositional", "Q2114906"]:
        return "Pre"
    elif case in ["locative", "Q202142"]:
        return "Loc"
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
    single_annotations = ["Akk", "Dat", "Gen", "Ins", "Pre", "Loc", "Nom"]
    if annotation in single_annotations:
        return annotation

    annotation_split = sorted(annotation.split("/"))

    return "/".join(annotation_split)


prepositions_formatted = {}

for prep_vals in prepositions_list:
    if "preposition" in prep_vals.keys() and "case" in prep_vals.keys():
        if prep_vals["preposition"] not in prepositions_formatted:
            prepositions_formatted[prep_vals["preposition"]] = convert_cases(
                prep_vals["case"]
            )

        else:
            prepositions_formatted[prep_vals["preposition"]] += "/" + convert_cases(
                prep_vals["case"]
            )

for k in prepositions_formatted:
    prepositions_formatted[k] = order_annotations(prepositions_formatted[k])

prepositions_formatted = collections.OrderedDict(sorted(prepositions_formatted.items()))

for output_path in all_output_paths:
    with open(output_path, "w", encoding="utf-8",) as file:
        json.dump(prepositions_formatted, file, ensure_ascii=False, indent=2)

print(f"Wrote file prepositions.json with {len(prepositions_formatted)} prepositions.")
