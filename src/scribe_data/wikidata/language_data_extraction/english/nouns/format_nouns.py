"""
Formats the English nouns queried from Wikidata using query_nouns.sparql.

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

from scribe_data.utils import export_formatted_data, load_queried_data

LANGUAGE = "English"
DATA_TYPE = "nouns"

parser = argparse.ArgumentParser()
parser.add_argument("--file-path")
args = parser.parse_args()

nouns_list, data_path = load_queried_data(
    file_path=args.file_path, language=LANGUAGE, data_type=DATA_TYPE
)

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

export_formatted_data(
    file_path=args.file_path,
    formatted_data=nouns_formatted,
    language=LANGUAGE,
    data_type=DATA_TYPE,
)
