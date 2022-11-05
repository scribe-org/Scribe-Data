"""
Update Data
-----------

Updates data for Scribe by running all or desired WDQS queries and formatting scripts.

Parameters
----------
    languages : list of strings (default=None)
        A subset of Scribe's languages that the user wants to update.

    word_types : list of strings (default=None)
        A subset of nouns, verbs, and prepositions that currently can be updated with this fie.

Example
-------
    python update_data.py '["French", "German"]' '["nouns", "verbs"]'
"""


# pylint: disable=invalid-name, wrong-import-position

import ast
import itertools
import json
import os
import sys
from urllib.error import HTTPError

import pandas as pd
from SPARQLWrapper import JSON, POST, SPARQLWrapper
from tqdm.auto import tqdm

PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

from scribe_data.load.update_utils import (  # isort:skip
    get_ios_data_path,
    get_path_from_update_data,
)

# Set SPARQLWrapper query conditions.
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)
sparql.setMethod(POST)

PATH_TO_ET_FILES = "../extract_transform/"

with open("_update_files/total_data.json", encoding="utf-8") as f:
    current_data = json.load(f)

current_languages = list(current_data.keys())
word_types_to_update = ["nouns", "verbs", "prepositions"]

# Check whether arguments have been passed to only update a subset of the data.
languages = None
word_types = None
if len(sys.argv) == 2:
    arg = sys.argv[1]
    if isinstance(arg, str):
        raise ValueError(
            f"""The argument type of '{arg}' passed to update_data.py is invalid.
            Only lists are allowed, and can be passed via:
            python update_data.py '[comma_separated_args_in_quotes]'
            """
        )

    try:
        arg = ast.literal_eval(arg)
    except ValueError as invalid_arg:
        raise ValueError(
            f"""The argument type of '{arg}' passed to update_data.py is invalid.
            Only lists are allowed, and can be passed via:
            python update_data.py '[comma_separated_args_in_quotes]'
            """
        ) from invalid_arg

    if not isinstance(arg, list):
        raise ValueError(
            f"""The argument type of '{arg}' passed to update_data.py is invalid.
            Only lists are allowed, and can be passed via:
            python update_data.py '[comma_separated_args_in_quotes]'
            """
        )

    if set(arg).issubset(current_languages):
        languages = arg
    elif set(arg).issubset(word_types_to_update):
        word_types = arg
    else:
        raise ValueError(
            f"""An invalid argument '{arg}' was specified.
                For languages, please choose from those found as keys in total_data.json.
                For grammatical types, please choose from nouns, verbs or prepositions.
                """
        )

elif len(sys.argv) == 3:
    languages = sys.argv[1]
    word_types = sys.argv[2]

# Derive Data directory elements for potential queries.
data_dir_elements = []

for path, _, files in os.walk(PATH_TO_ET_FILES):
    data_dir_elements.extend(os.path.join(path, name) for name in files)
data_dir_files = [
    f
    for f in os.listdir(PATH_TO_ET_FILES)
    if os.path.isfile(os.path.join(PATH_TO_ET_FILES, f))
]

data_dir_directories = list(
    {
        f.split(PATH_TO_ET_FILES)[1].split("/")[0]
        for f in data_dir_elements
        if f.split(PATH_TO_ET_FILES)[1] not in data_dir_files
        and f.split(PATH_TO_ET_FILES)[1][0] != "_"
    }
)

# Subset current_languages and word_types_to_update if arguments have been passed.
languages_update = []
if languages is None:
    languages_update = current_languages

elif (
    not isinstance(ast.literal_eval(languages), str)
    and isinstance(ast.literal_eval(languages), list)
    and set(ast.literal_eval(languages)).issubset(current_languages)
):
    languages_update = ast.literal_eval(languages)
else:
    raise ValueError(
        f"""Invalid languages '{languages}' were specified.
            Please choose from those found as keys in total_data.json.
            Pass arguments via: python update_data.py '[languages_in_quotes]'
            """
    )

word_types_update = []
if word_types is None:
    word_types_update = word_types_to_update

elif (
    not isinstance(ast.literal_eval(word_types), str)
    and isinstance(ast.literal_eval(word_types), list)
    and set(ast.literal_eval(word_types)).issubset(word_types_to_update)
):
    word_types_update = ast.literal_eval(word_types)
else:
    raise ValueError(
        f"""Invalid grammatical types '{word_types}' were specified.
            Please choose from nouns, verbs or prepositions.
            Pass arguments via: python update_data.py '[word_types_in_quotes]'
            """
    )

# Check to see if the language has all zeroes for its data, meaning it's been added.
new_language_list = []
for lang in languages_update:
    # Prepositions not needed for all languages.
    check_current_data = [current_data[lang][k] for k in current_data[lang].keys()]
    if len(set(check_current_data)) == 1 and check_current_data[0] == 0:
        new_language_list.append(lang)

# Derive queries to be ran.
possible_queries = []
for d in data_dir_directories:
    possible_queries.extend(
        f"{PATH_TO_ET_FILES}{d}/{target_type}"
        for target_type in word_types_update
        if f"{PATH_TO_ET_FILES}{d}/{target_type}"
        in [e[: len(f"{PATH_TO_ET_FILES}{d}/{target_type}")] for e in data_dir_elements]
    )

queries_to_run_lists = [
    [
        q
        for q in possible_queries
        if q[len(PATH_TO_ET_FILES) : len(PATH_TO_ET_FILES) + len(lang)]
        in languages_update
    ]
    for lang in languages_update
]

queries_to_run = list({q for sub in queries_to_run_lists for q in sub})

data_added_dict = {}

for q in tqdm(queries_to_run, desc="Data updated", unit="dirs",):
    lang = q.split("/")[2]
    target_type = q.split("/")[3]
    query_name = f"query_{target_type}.sparql"
    query_path = f"{q}/{query_name}"

    if not os.path.exists(query_path):
        # There are multiple queries for a given target_type, so start by running the first.
        query_path = query_path[: -len(".sparql")] + "_1" + ".sparql"

    print(f"Querying {lang} {target_type}")
    # First format the lines into a multi-line string and then pass this to SPARQLWrapper.
    with open(query_path, encoding="utf-8") as file:
        query_lines = file.readlines()
    sparql.setQuery("".join(query_lines))

    results = None
    try:
        results = sparql.query().convert()
    except HTTPError as err:
        print(f"HTTPError with {query_path}: {err}")

    if results is None:
        print(f"Nothing returned by the WDQS server for {query_path}")

        # Allow for a query to be reran up to two times.
        if queries_to_run.count(q) < 3:
            queries_to_run.append(q)

    else:
        # Subset the returned JSON and the individual results before saving.
        query_results = results["results"]["bindings"]

        results_formatted = []
        for r in query_results:  # query_results is also a list
            r_dict = {k: r[k]["value"] for k in r.keys()}

            results_formatted.append(r_dict)

        with open(
            f"{PATH_TO_ET_FILES}{lang}/{target_type}/{target_type}_queried.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(results_formatted, f, ensure_ascii=False, indent=0)

        if "_1" in query_path:
            # note: Only the first query was ran, so we need to run the second and append the json.

            query_path = query_path.replace("_1", "_2")
            with open(query_path, encoding="utf-8") as file:
                query_lines = file.readlines()
                sparql.setQuery("".join(query_lines))

                results = None
                try:
                    results = sparql.query().convert()
                except HTTPError as err:
                    print(f"HTTPError with {query_path}: {err}")

                if results is None:
                    print(f"Nothing returned by the WDQS server for {query_path}")

                    # Allow for a query to be reran up to two times.
                    if queries_to_run.count(q) < 3:
                        queries_to_run.append(q)

                else:
                    # Subset the returned JSON and the individual results before saving.
                    query_results = results["results"]["bindings"]

                    # note: Don't rewrite results_formatted as we want to extend the json and combine in formatting.
                    for r in query_results:  # query_results is also a list
                        r_dict = {k: r[k]["value"] for k in r.keys()}

                        results_formatted.append(r_dict)

                    with open(
                        f"{PATH_TO_ET_FILES}{lang}/{target_type}/{target_type}_queried.json",
                        "w",
                        encoding="utf-8",
                    ) as f:
                        json.dump(results_formatted, f, ensure_ascii=False, indent=0)

        # Call the corresponding formatting file and update data changes.
        os.system(
            f"python {PATH_TO_ET_FILES}{lang}/{target_type}/format_{target_type}.py"
        )

        # Use Scribe-iOS as the basis of checking the new data.
        PATH_TO_SCRIBE_ORG = get_path_from_update_data()
        PATH_TO_DATA_JSON = get_ios_data_path(lang, target_type)
        with open(
            f"{PATH_TO_SCRIBE_ORG}{PATH_TO_DATA_JSON}", encoding="utf-8",
        ) as json_file:
            new_keyboard_data = json.load(json_file)

        if lang not in data_added_dict:
            data_added_dict[lang] = {}
        data_added_dict[lang][target_type] = (
            len(new_keyboard_data) - current_data[lang][target_type]
        )

        current_data[lang][target_type] = len(new_keyboard_data)

# Update total_data.json.
with open("./_update_files/total_data.json", "w", encoding="utf-8") as f:
    json.dump(current_data, f, ensure_ascii=False, indent=0)


def num_add_commas(num):
    """
    Adds commas to a numeric string for readability.

    Parameters
    ----------
        num : int
            An int to have commas added to.

    Returns
    -------
        str_with_commas : str
            The original number with commas to make it more readable.
    """
    num_str = str(num)

    str_list = list(num_str)
    str_list = str_list[::-1]

    str_list_with_commas = [
        f"{s}," if i % 3 == 0 and i != 0 else s for i, s in enumerate(str_list)
    ]

    str_list_with_commas = str_list_with_commas[::-1]

    return "".join(str_list_with_commas)


# Update data_table.txt
current_data_df = pd.DataFrame(
    index=sorted(list(current_data.keys())),
    columns=["nouns", "verbs", "translations", "prepositions"],
)
for lang, wt in itertools.product(
    list(current_data_df.index), list(current_data_df.columns)
):
    if wt in current_data[lang].keys():
        current_data_df.loc[lang, wt] = num_add_commas(current_data[lang][wt])
    elif wt == "translations":
        current_data_df.loc[lang, wt] = num_add_commas(67652)

current_data_df.index.name = "Languages"
current_data_df.columns = [c.capitalize() for c in current_data_df.columns]
with open("./_update_files/data_table.txt", "w+", encoding="utf-8") as f:
    table_string = str(current_data_df.to_markdown()).replace(" nan ", "   - ")
    # Right justify the data and left justify the language indexes.
    table_string = (
        table_string.replace("-|-", ":|-")
        .replace("-|:", ":|-")
        .replace(":|-", "-|-", 1)
    )
    f.writelines(table_string)

# Update data_updates.txt.
data_added_string = ""
language_keys = sorted(list(data_added_dict.keys()))

# Check if all data added values are 0 and remove if so.
for l in language_keys:
    if all(v <= 0 for v in data_added_dict[l].values()):
        language_keys.remove(l)

for l in language_keys:
    if l == language_keys[0]:
        data_added_string += f"- {l} (New):" if l in new_language_list else f"- {l}:"
    else:
        data_added_string += (
            f"\n- {l} (New):" if l in new_language_list else f"\n- {l}:"
        )

    for wt in word_types_update:
        if wt in data_added_dict[l].keys():
            if data_added_dict[l][wt] <= 0:
                pass
            elif data_added_dict[l][wt] == 1:  # remove the s for label
                data_added_string += f" {data_added_dict[l][wt]} {wt[:-1]},"
            else:
                data_added_string += f" {data_added_dict[l][wt]} {wt},"

    data_added_string = data_added_string[:-1]  # remove the last comma

with open("./_update_files/data_updates.txt", "w+", encoding="utf-8") as f:
    f.writelines(data_added_string)
