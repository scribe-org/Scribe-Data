"""
Format Nouns
------------

Formats the nouns queried from Wikidata using query_nouns.sparql.
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
if "Spanish/nouns/" not in file_path:
    with open("nounsQueried.json", encoding="utf-8") as f:
        nouns_list = json.load(f)
else:
    with open("./Spanish/nouns/nounsQueried.json", encoding="utf-8") as f:
        nouns_list = json.load(f)
        update_data_in_use = True

path_from_file = get_path_from_format_file()
path_from_update_data = get_path_from_update_data()
ios_data_dir_from_org = get_ios_data_path("Spanish", "nouns")
android_data_dir_from_org = get_android_data_path("Spanish", "nouns")
desktop_data_dir_from_org = get_desktop_data_path("Spanish", "nouns")

ios_output_path = f"{path_from_file}{ios_data_dir_from_org}"
android_output_path = f"{path_from_file}{android_data_dir_from_org}"
desktop_output_path = f"{path_from_file}{desktop_data_dir_from_org}"
if update_data_in_use:
    ios_output_path = f"{path_from_update_data}{ios_data_dir_from_org}"
    android_output_path = f"{path_from_update_data}{android_data_dir_from_org}"
    desktop_output_path = f"{path_from_update_data}{desktop_data_dir_from_org}"

all_output_paths = [ios_output_path, android_output_path, desktop_output_path]


def map_genders(wikidata_gender):
    """
    Maps those genders from Wikidata to succinct versions.
    """
    if wikidata_gender in ["masculine", "Q499327"]:
        return "M"
    elif wikidata_gender in ["feminine", "Q1775415"]:
        return "F"
    else:
        return ""  # nouns could have a gender that is not valid as an attribute


def order_annotations(annotation):
    """
    Standardizes the annotations that are presented to users where more than one is applicable.

    Parameters
    ----------
        annotation : str
            The annotation to be returned to the user in the command bar.
    """
    single_annotations = ["F", "M", "PL"]
    if annotation in single_annotations:
        return annotation

    annotation_split = sorted([a for a in set(annotation.split("/")) if a != ""])

    return "/".join(annotation_split)


nouns_formatted = {}

for noun_vals in nouns_list:
    if "singular" in noun_vals.keys():
        if noun_vals["singular"] not in nouns_formatted:
            nouns_formatted[noun_vals["singular"]] = {"plural": "", "form": ""}

            if "gender" in noun_vals.keys():
                nouns_formatted[noun_vals["singular"]]["form"] = map_genders(
                    noun_vals["gender"]
                )

            if "plural" in noun_vals.keys():
                nouns_formatted[noun_vals["singular"]]["plural"] = noun_vals["plural"]

                if noun_vals["plural"] not in nouns_formatted:
                    nouns_formatted[noun_vals["plural"]] = {
                        "plural": "isPlural",
                        "form": "PL",
                    }

                # Plural is same as singular.
                else:
                    nouns_formatted[noun_vals["singular"]]["plural"] = noun_vals[
                        "plural"
                    ]
                    nouns_formatted[noun_vals["singular"]]["form"] = (
                        nouns_formatted[noun_vals["singular"]]["form"] + "/PL"
                    )

        else:
            if "gender" in noun_vals.keys():
                if (
                    nouns_formatted[noun_vals["singular"]]["form"]
                    != noun_vals["gender"]
                ):
                    nouns_formatted[noun_vals["singular"]]["form"] += "/" + map_genders(
                        noun_vals["gender"]
                    )

                elif nouns_formatted[noun_vals["singular"]]["gender"] == "":
                    nouns_formatted[noun_vals["singular"]]["gender"] = map_genders(
                        noun_vals["gender"]
                    )

    # Plural only noun.
    elif "plural" in noun_vals.keys():
        if noun_vals["plural"] not in nouns_formatted:
            nouns_formatted[noun_vals["plural"]] = {"plural": "isPlural", "form": "PL"}

        # Plural is same as singular.
        else:
            if "singular" in noun_vals.keys():
                nouns_formatted[noun_vals["singular"]]["plural"] = noun_vals["plural"]
                nouns_formatted[noun_vals["singular"]]["form"] = (
                    nouns_formatted[noun_vals["singular"]]["form"] + "/PL"
                )

for k in nouns_formatted:
    nouns_formatted[k]["form"] = order_annotations(nouns_formatted[k]["form"])

nouns_formatted = collections.OrderedDict(sorted(nouns_formatted.items()))

for output_path in all_output_paths:
    with open(output_path, "w", encoding="utf-8",) as file:
        json.dump(nouns_formatted, file, ensure_ascii=False, indent=2)

print(f"Wrote file nouns.json with {len(nouns_formatted)} nouns.")
