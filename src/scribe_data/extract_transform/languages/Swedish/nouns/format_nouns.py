"""
Format Nouns
------------

Formats the nouns queried from Wikidata using query_nouns.sparql.
"""

import collections
import os
import sys

PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

from scribe_data.utils import export_formatted_data, load_queried_data

file_path = sys.argv[0]

nouns_list, update_data_in_use, data_path= load_queried_data(file_path, language = "Swedish", data_type = "nouns")


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
                    nouns_formatted[noun_vals["nominativeSingular"]]["form"] += (
                        "/" + map_genders(noun_vals["gender"])
                    )

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
                    nouns_formatted[noun_vals["genitiveSingular"]]["form"] += (
                        "/" + map_genders(noun_vals["gender"])
                    )

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

export_formatted_data(nouns_formatted, update_data_in_use, language = "Swedish", data_type = "nouns")

os.remove(data_path)
