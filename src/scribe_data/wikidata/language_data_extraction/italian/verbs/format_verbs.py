"""
Formats the Italian verbs queried from Wikidata using query_verbs.sparql.

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

LANGUAGE = "Italian"
DATA_TYPE = "verbs"

parser = argparse.ArgumentParser()
parser.add_argument("--file-path")
args = parser.parse_args()

verbs_list, data_path = load_queried_data(
    file_path=args.file_path, language=LANGUAGE, data_type=DATA_TYPE
)

verbs_formatted = {}

all_conjugations = [
    "presFPS",
    "presSPS",
    "presTPS",
    "presFPP",
    "presSPP",
    "presTPP",
    "pretFPS",
    "pretSPS",
    "pretTPS",
    "pretFPP",
    "pretSPP",
    "pretTPP",
    "impFPS",
    "impSPS",
    "impTPS",
    "impFPP",
    "impSPP",
    "impTPP",
]

for verb_vals in verbs_list:
    if verb_vals["infinitive"] not in verbs_formatted:
        verbs_formatted[verb_vals["infinitive"]] = {}

        for conj in all_conjugations:
            if conj in verb_vals.keys():
                verbs_formatted[verb_vals["infinitive"]][conj] = verb_vals[conj]
            else:
                verbs_formatted[verb_vals["infinitive"]][conj] = ""

    else:
        for conj in all_conjugations:
            if conj in verb_vals.keys():
                verbs_formatted[verb_vals["infinitive"]][conj] = verb_vals[conj]

verbs_formatted = collections.OrderedDict(sorted(verbs_formatted.items()))

export_formatted_data(
    file_path=args.file_path,
    formatted_data=verbs_formatted,
    language=LANGUAGE,
    data_type=DATA_TYPE,
)
