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
if "Swedish/nouns/" not in file_path:
    with open("nouns_queried.json", encoding="utf-8") as f:
        nouns_list = json.load(f)
else:
    with open("./Swedish/nouns/nouns_queried.json", encoding="utf-8") as f:
        nouns_list = json.load(f)
        update_data_in_use = True

path_from_file = get_path_from_format_file()
path_from_update_data = get_path_from_update_data()
ios_data_dir_from_org = get_ios_data_path("Swedish", "nouns")
android_data_dir_from_org = get_android_data_path("Swedish", "nouns")
desktop_data_dir_from_org = get_desktop_data_path("Swedish", "nouns")

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
    if wikidata_gender in ["common gender", "Q1305037"]:
        return "C"
    elif wikidata_gender in ["neuter", "Q1775461"]:
        return "N"
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
    single_annotations = ["C", "N", "PL"]
    if annotation in single_annotations:
        return annotation

    annotation_split = sorted([a for a in set(annotation.split("/")) if a != ""])

    return "/".join(annotation_split)


nouns_formatted = {}

for noun_vals in nouns_list:
    if "nominativeSingular" in noun_vals.keys():
        if noun_vals["nominativeSingular"] not in nouns_formatted:
            nouns_formatted[noun_vals["nominativeSingular"]] = {
                "plural": "",
                "form": "",
            }

            if "gender" in noun_vals.keys():
                nouns_formatted[noun_vals["nominativeSingular"]]["form"] = map_genders(
                    noun_vals["gender"]
                )

            if "nominativePlural" in noun_vals.keys():
                nouns_formatted[noun_vals["nominativeSingular"]]["plural"] = noun_vals[
                    "nominativePlural"
                ]

                if noun_vals["nominativePlural"] not in nouns_formatted:
                    nouns_formatted[noun_vals["nominativePlural"]] = {
                        "plural": "isPlural",
                        "form": "PL",
                    }

                # Plural is same as singular.
                else:
                    nouns_formatted[noun_vals["nominativeSingular"]][
                        "plural"
                    ] = noun_vals["nominativePlural"]
                    nouns_formatted[noun_vals["nominativeSingular"]]["form"] = (
                        nouns_formatted[noun_vals["nominativeSingular"]]["form"] + "/PL"
                    )

        else:
            if "gender" in noun_vals.keys():
                if (
                    nouns_formatted[noun_vals["nominativeSingular"]]["form"]
                    != noun_vals["gender"]
                ):
                    nouns_formatted[noun_vals["nominativeSingular"]][
                        "form"
                    ] += "/" + map_genders(noun_vals["gender"])

                elif nouns_formatted[noun_vals["nominativeSingular"]]["gender"] == "":
                    nouns_formatted[noun_vals["nominativeSingular"]][
                        "gender"
                    ] = map_genders(noun_vals["gender"])

    elif "genitiveSingular" in noun_vals.keys():
        if noun_vals["genitiveSingular"] not in nouns_formatted:
            nouns_formatted[noun_vals["genitiveSingular"]] = {
                "plural": "",
                "form": "",
            }

            if "gender" in noun_vals.keys():
                nouns_formatted[noun_vals["genitiveSingular"]]["form"] = map_genders(
                    noun_vals["gender"]
                )

            if "genitivePlural" in noun_vals.keys():
                nouns_formatted[noun_vals["genitiveSingular"]]["plural"] = noun_vals[
                    "genitivePlural"
                ]

                if noun_vals["genitivePlural"] not in nouns_formatted:
                    nouns_formatted[noun_vals["genitivePlural"]] = {
                        "plural": "isPlural",
                        "form": "PL",
                    }

                # Plural is same as singular.
                else:
                    nouns_formatted[noun_vals["genitiveSingular"]][
                        "plural"
                    ] = noun_vals["genitivePlural"]
                    nouns_formatted[noun_vals["genitiveSingular"]]["form"] = (
                        nouns_formatted[noun_vals["genitiveSingular"]]["form"] + "/PL"
                    )

        else:
            if "gender" in noun_vals.keys():
                if (
                    nouns_formatted[noun_vals["genitiveSingular"]]["form"]
                    != noun_vals["gender"]
                ):
                    nouns_formatted[noun_vals["genitiveSingular"]][
                        "form"
                    ] += "/" + map_genders(noun_vals["gender"])

                elif nouns_formatted[noun_vals["genitiveSingular"]]["gender"] == "":
                    nouns_formatted[noun_vals["genitiveSingular"]][
                        "gender"
                    ] = map_genders(noun_vals["gender"])

    # Plural only noun.
    elif "nominativePlural" in noun_vals.keys():
        if noun_vals["nominativePlural"] not in nouns_formatted:
            nouns_formatted[noun_vals["nominativePlural"]] = {
                "plural": "isPlural",
                "form": "PL",
            }

        # Plural is same as singular.
        else:
            nouns_formatted[noun_vals["nominativeSingular"]][
                "nominativePlural"
            ] = noun_vals["nominativePlural"]
            nouns_formatted[noun_vals["nominativeSingular"]]["form"] = (
                nouns_formatted[noun_vals["nominativeSingular"]]["form"] + "/PL"
            )

    # Plural only noun.
    elif "genitivePlural" in noun_vals.keys():
        if noun_vals["genitivePlural"] not in nouns_formatted:
            nouns_formatted[noun_vals["genitivePlural"]] = {
                "plural": "isPlural",
                "form": "PL",
            }

        # Plural is same as singular.
        else:
            nouns_formatted[noun_vals["genitiveSingular"]][
                "genitivePlural"
            ] = noun_vals["genitivePlural"]
            nouns_formatted[noun_vals["genitiveSingular"]]["form"] = (
                nouns_formatted[noun_vals["genitiveSingular"]]["form"] + "/PL"
            )

for k in nouns_formatted:
    nouns_formatted[k]["form"] = order_annotations(nouns_formatted[k]["form"])

nouns_formatted = collections.OrderedDict(sorted(nouns_formatted.items()))

for output_path in all_output_paths:
    with open(output_path, "w", encoding="utf-8",) as file:
        json.dump(nouns_formatted, file, ensure_ascii=False, indent=2)

print(f"Wrote file nouns.json with {len(nouns_formatted)} nouns.")
