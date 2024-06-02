"""
Formats the Russian prepositions queried from Wikidata using query_prepositions.sparql.
"""

import collections
import os
import sys

from scribe_data.utils import (
    export_formatted_data,
    load_queried_data,
    map_cases,
    order_annotations,
)

LANGUAGE = "Russian"
DATA_TYPE = "prepositions"
file_path = sys.argv[0]

prepositions_list, update_data_in_use, data_path = load_queried_data(
    file_path=file_path, language=LANGUAGE, data_type=DATA_TYPE
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
    formatted_data=prepositions_formatted,
    update_data_in_use=update_data_in_use,
    language=LANGUAGE,
    data_type=DATA_TYPE,
)

os.remove(data_path)
