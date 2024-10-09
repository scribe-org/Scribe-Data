"""
Formats the Spanish nouns queried from Wikidata using query_nouns.sparql.

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

LANGUAGE = "Spanish"
DATA_TYPE = "nouns"

parser = argparse.ArgumentParser()
parser.add_argument("--file-path")
args = parser.parse_args()

nouns_list, data_path = load_queried_data(
    file_path=args.file_path, language=LANGUAGE, data_type=DATA_TYPE
)

nouns_formatted = {}

for noun_vals in nouns_list:
    # Check if the multiple genders of a word are being stored on the same lemma.
    if "masSingular" in noun_vals.keys():
        nouns_formatted[noun_vals["masSingular"]] = {"plural": "", "form": "M"}

        if "masPlural" in noun_vals.keys():
            nouns_formatted[noun_vals["masSingular"]]["plural"] = noun_vals["masPlural"]

            nouns_formatted[noun_vals["masPlural"]] = {
                "plural": "isPlural",
                "form": "PL",
            }

    if "femSingular" in noun_vals.keys():
        nouns_formatted[noun_vals["femSingular"]] = {"plural": "", "form": "F"}

        if "femPlural" in noun_vals.keys():
            nouns_formatted[noun_vals["femSingular"]]["plural"] = noun_vals["femPlural"]

            nouns_formatted[noun_vals["femPlural"]] = {
                "plural": "isPlural",
                "form": "PL",
            }

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
            # Another version of the word may have a different gender.
            if "gender" in noun_vals.keys() and (
                "masSingular" not in noun_vals.keys()
                or "femSingular" not in noun_vals.keys()
            ):
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
            nouns_formatted[noun_vals["plural"]] = {
                "plural": "isPlural",
                "form": "PL",
            }

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

export_formatted_data(
    file_path=args.file_path,
    formatted_data=nouns_formatted,
    language=LANGUAGE,
    data_type=DATA_TYPE,
)
