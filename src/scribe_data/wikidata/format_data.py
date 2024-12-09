"""
Formats the data queried from Wikidata using query_verbs.sparql.

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
    remove_queried_data,
)

parser = argparse.ArgumentParser()
parser.add_argument("--dir-path")
parser.add_argument("--language")
parser.add_argument("--data_type")
args = parser.parse_args()


def format_data(
    dir_path: str = args.dir_path,
    language: str = args.language,
    data_type: str = args.data_type,
):
    """
    Formats data that has been queried from the Wikidata Query Service.

    Parameters
    ----------
        dir_path : str
            The output directory path for results.

        language : str
            The language for which the data is being loaded.

        data_type : str
            The type of data being loaded (e.g. 'nouns', 'verbs').

    Returns
    _______
        A saved and formatted data file for the given language and data type.
    """
    data_list, data_path = load_queried_data(
        dir_path=dir_path, language=language, data_type=data_type
    )

    data_formatted = {}

    for data_vals in data_list:
        lexeme_id = data_vals["lexemeID"]

        if lexeme_id not in data_formatted:
            data_formatted[lexeme_id] = {}

        # Reverse to make sure that we're getting the same order as the query.
        query_identifiers = list(reversed(data_vals.keys()))
        query_identifiers.remove("lexemeID")

        for k in query_identifiers:
            data_formatted[lexeme_id][k] = data_vals[k]

    data_formatted = collections.OrderedDict(sorted(data_formatted.items()))

    export_formatted_data(
        dir_path=dir_path,
        formatted_data=data_formatted,
        language=language,
        data_type=data_type,
    )

    remove_queried_data(dir_path=dir_path, language=language, data_type=data_type)


if __name__ == "__main__":
    format_data()
