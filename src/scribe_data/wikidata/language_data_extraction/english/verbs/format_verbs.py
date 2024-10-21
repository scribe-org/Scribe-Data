"""
Formats the English verbs queried from Wikidata using query_verbs.sparql.

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
DATA_TYPE = "verbs"

parser = argparse.ArgumentParser()
parser.add_argument("--file-path")
args = parser.parse_args()

verbs_list, data_path = load_queried_data(
    file_path=args.file_path, language=LANGUAGE, data_type=DATA_TYPE
)

verbs_formatted = {}

all_conjugations = [
    "presSimp",
    "presTPS",
    "presPart",
    "presFPSCont",
    "prePluralCont",
    "presTPSCont",
    "presPerfSimp",
    "presPerfTPS",
    "presPerfSimpCont",
    "presPerfTPSCont",
    "pastSimp",
    "pastSimpCont",
    "pastSimpPluralCont",
    "pastPerf",
    "pastPerfCont",
    "futSimp",
    "futCont",
    "futPerf",
    "futPerfCont",
    "condSimp",
    "condCont",
    "condPerf",
    "condPerfCont",
]

for verb_vals in verbs_list:
    # If infinitive is available add to formatted verbs, else no entry created.
    infinitive_key = verb_vals["infinitive"]
    if infinitive_key not in verbs_formatted.keys():
        verbs_formatted[infinitive_key] = {}

        # Present
        verbs_formatted[infinitive_key]["presSimp"] = verb_vals.get("presSimp", "")
        verbs_formatted[infinitive_key]["presTPS"] = verb_vals.get("presTPS", "")
        verbs_formatted[infinitive_key]["presPart"] = verb_vals.get("presPart", "")
        verbs_formatted[infinitive_key]["presFPSCont"] = "am " + verb_vals.get(
            "presPart", ""
        )
        verbs_formatted[infinitive_key]["prePluralCont"] = "are " + verb_vals.get(
            "presPart", ""
        )
        verbs_formatted[infinitive_key]["presTPSCont"] = "is " + verb_vals.get(
            "presPart", ""
        )
        verbs_formatted[infinitive_key]["presPerfSimp"] = "have " + verb_vals.get(
            "pastPart", ""
        )
        verbs_formatted[infinitive_key]["presPerfTPS"] = "has " + verb_vals.get(
            "pastPart", ""
        )
        verbs_formatted[infinitive_key]["presPerfSimpCont"] = (
            "have been " + verb_vals.get("presPart", "")
        )
        verbs_formatted[infinitive_key]["presPerfTPSCont"] = (
            "has been " + verb_vals.get("presPart", "")
        )

        # Past
        verbs_formatted[infinitive_key]["pastSimp"] = verb_vals.get("pastSimp", "")
        verbs_formatted[infinitive_key]["pastSimpCont"] = "was " + verb_vals.get(
            "presPart", ""
        )
        verbs_formatted[infinitive_key]["pastSimpPluralCont"] = "were " + verb_vals.get(
            "presPart", ""
        )
        verbs_formatted[infinitive_key]["pastPerf"] = "had " + verb_vals.get(
            "pastPart", ""
        )
        verbs_formatted[infinitive_key]["pastPerfCont"] = "had been " + verb_vals.get(
            "presPart", ""
        )

        # Future
        verbs_formatted[infinitive_key]["futSimp"] = "will " + verb_vals.get(
            "presSimp", ""
        )
        verbs_formatted[infinitive_key]["futCont"] = "will be " + verb_vals.get(
            "presPart", ""
        )
        verbs_formatted[infinitive_key]["futPerf"] = "will have " + verb_vals.get(
            "pastPart", ""
        )
        verbs_formatted[infinitive_key]["futPerfCont"] = (
            "will have been " + verb_vals.get("presPart", "")
        )

        # Conditional
        verbs_formatted[infinitive_key]["condSimp"] = "would " + verb_vals.get(
            "presSimp", ""
        )
        verbs_formatted[infinitive_key]["condCont"] = "would be " + verb_vals.get(
            "presPart", ""
        )
        verbs_formatted[infinitive_key]["condPerf"] = "would have " + verb_vals.get(
            "pastPart", ""
        )
        verbs_formatted[infinitive_key]["condPerfCont"] = (
            "would have been " + verb_vals.get("presPart", "")
        )

verbs_formatted = collections.OrderedDict(sorted(verbs_formatted.items()))

export_formatted_data(
    file_path=args.file_path,
    formatted_data=verbs_formatted,
    language=LANGUAGE,
    data_type=DATA_TYPE,
)
