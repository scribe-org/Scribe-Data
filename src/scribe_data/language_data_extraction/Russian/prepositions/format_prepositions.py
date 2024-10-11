"""
Formats the Russian prepositions queried from Wikidata using query_prepositions.sparql.

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
    map_cases,
    order_annotations,
)

LANGUAGE = "Russian"
DATA_TYPE = "prepositions"

parser = argparse.ArgumentParser()
parser.add_argument("--file-path")
args = parser.parse_args()

prepositions_list, data_path = load_queried_data(
    file_path=args.file_path, language=LANGUAGE, data_type=DATA_TYPE
)

prepositions_formatted = {}

for prep_vals in prepositions_list:
    if "preposition" in prep_vals.keys() and "case" in prep_vals.keys():
        if prep_vals["preposition"] not in prepositions_formatted:
            prepositions_formatted[prep_vals["preposition"]] = map_cases(
                prep_vals["case"]
            )

        else:
            prepositions_formatted[prep_vals["preposition"]] += "/" + map_cases(
                prep_vals["case"]
            )

for k in prepositions_formatted:
    prepositions_formatted[k] = order_annotations(prepositions_formatted[k])

prepositions_formatted = collections.OrderedDict(sorted(prepositions_formatted.items()))

export_formatted_data(
    file_path=args.file_path,
    formatted_data=prepositions_formatted,
    language=LANGUAGE,
    data_type=DATA_TYPE,
)
