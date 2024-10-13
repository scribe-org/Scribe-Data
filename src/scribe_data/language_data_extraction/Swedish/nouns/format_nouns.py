"""
Formats the Swedish nouns queried from Wikidata using query_nouns.sparql.

.. raw:: html
    <!--
    * Copyright (C) 2024 Scribe
    *
    * This program is free software: you can redistribute it and/or modify
    * it under the terms of the GNU General Public License as published by
    * the Free Software Foundation, either version 3 of the License, or
    * (at your option) any later version.
    *
    * This program is distributed in the hope that it will be useful,
    * but WITHOUT ANY WARRANTY; without even the implied warranty of
    * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    * GNU General Public License for more details.
    *
    * You should have received a copy of the GNU General Public License
    * along with this program.  If not, see <https://www.gnu.org/licenses/>.
    -->
"""

import argparse
import collections

from scribe_data.utils import (
    export_formatted_data,
    load_queried_data,
    map_genders,
    order_annotations,
)

LANGUAGE = "Swedish"
DATA_TYPE = "nouns"

parser = argparse.ArgumentParser()
parser.add_argument("--file-path")
args = parser.parse_args()

nouns_list, data_path = load_queried_data(
    file_path=args.file_path, language=LANGUAGE, data_type=DATA_TYPE
)

nouns_formatted = {}

for noun_vals in nouns_list:
    if "nomIndefSingular" in noun_vals.keys():
        if noun_vals["nomIndefSingular"] not in nouns_formatted:
            nouns_formatted[noun_vals["nomIndefSingular"]] = {
                "plural": "",
                "form": "",
            }

            if "gender" in noun_vals.keys():
                nouns_formatted[noun_vals["nomIndefSingular"]]["form"] = map_genders(
                    noun_vals["gender"]
                )

            if "nomIndefPlural" in noun_vals.keys():
                nouns_formatted[noun_vals["nomIndefSingular"]]["plural"] = noun_vals[
                    "nomIndefPlural"
                ]

                if noun_vals["nomIndefPlural"] not in nouns_formatted:
                    nouns_formatted[noun_vals["nomIndefPlural"]] = {
                        "plural": "isPlural",
                        "form": "PL",
                    }

                # Plural is same as singular.
                else:
                    nouns_formatted[noun_vals["nomIndefSingular"]]["plural"] = (
                        noun_vals["nomIndefPlural"]
                    )
                    nouns_formatted[noun_vals["nomIndefSingular"]]["form"] = (
                        nouns_formatted[noun_vals["nomIndefSingular"]]["form"] + "/PL"
                    )

        else:
            if "gender" in noun_vals.keys():
                if (
                    nouns_formatted[noun_vals["nomIndefSingular"]]["form"]
                    != noun_vals["gender"]
                ):
                    nouns_formatted[noun_vals["nomIndefSingular"]]["form"] += (
                        "/" + map_genders(noun_vals["gender"])
                    )

                elif nouns_formatted[noun_vals["nomIndefSingular"]]["gender"] == "":
                    nouns_formatted[noun_vals["nomIndefSingular"]]["gender"] = (
                        map_genders(noun_vals["gender"])
                    )

    elif "genIndefSingular" in noun_vals.keys():
        if noun_vals["genIndefSingular"] not in nouns_formatted:
            nouns_formatted[noun_vals["genIndefSingular"]] = {
                "plural": "",
                "form": "",
            }

            if "gender" in noun_vals.keys():
                nouns_formatted[noun_vals["genIndefSingular"]]["form"] = map_genders(
                    noun_vals["gender"]
                )

            if "genIndefPlural" in noun_vals.keys():
                nouns_formatted[noun_vals["genIndefSingular"]]["plural"] = noun_vals[
                    "genIndefPlural"
                ]

                if noun_vals["genIndefPlural"] not in nouns_formatted:
                    nouns_formatted[noun_vals["genIndefPlural"]] = {
                        "plural": "isPlural",
                        "form": "PL",
                    }

                # Plural is same as singular.
                else:
                    nouns_formatted[noun_vals["genIndefSingular"]]["plural"] = (
                        noun_vals["genIndefPlural"]
                    )
                    nouns_formatted[noun_vals["genIndefSingular"]]["form"] = (
                        nouns_formatted[noun_vals["genIndefSingular"]]["form"] + "/PL"
                    )

        else:
            if "gender" in noun_vals.keys():
                if (
                    nouns_formatted[noun_vals["genIndefSingular"]]["form"]
                    != noun_vals["gender"]
                ):
                    nouns_formatted[noun_vals["genIndefSingular"]]["form"] += (
                        "/" + map_genders(noun_vals["gender"])
                    )

                elif nouns_formatted[noun_vals["genIndefSingular"]]["gender"] == "":
                    nouns_formatted[noun_vals["genIndefSingular"]]["gender"] = (
                        map_genders(noun_vals["gender"])
                    )

    # Plural only noun.
    elif "nomIndefPlural" in noun_vals.keys():
        if noun_vals["nomIndefPlural"] not in nouns_formatted:
            nouns_formatted[noun_vals["nomIndefPlural"]] = {
                "plural": "isPlural",
                "form": "PL",
            }

        # Plural is same as singular.
        else:
            nouns_formatted[noun_vals["nomIndefSingular"]]["nomIndefPlural"] = (
                noun_vals["nomIndefPlural"]
            )
            nouns_formatted[noun_vals["nomIndefSingular"]]["form"] = (
                nouns_formatted[noun_vals["nomIndefSingular"]]["form"] + "/PL"
            )

    # Plural only noun.
    elif "genIndefPlural" in noun_vals.keys():
        if noun_vals["genIndefPlural"] not in nouns_formatted:
            nouns_formatted[noun_vals["genIndefPlural"]] = {
                "plural": "isPlural",
                "form": "PL",
            }

        # Plural is same as singular.
        else:
            nouns_formatted[noun_vals["genIndefSingular"]]["genIndefPlural"] = (
                noun_vals["genIndefPlural"]
            )
            nouns_formatted[noun_vals["genIndefSingular"]]["form"] = (
                nouns_formatted[noun_vals["genIndefSingular"]]["form"] + "/PL"
            )

for k in nouns_formatted:
    nouns_formatted[k]["form"] = order_annotations(nouns_formatted[k]["form"])

nouns_formatted = collections.OrderedDict(sorted(nouns_formatted.items()))

export_formatted_data(
    file_path=args.file_path,
    formatted_data=nouns_formatted,
    language=LANGUAGE,
    data_type=DATA_TYPE,
)
