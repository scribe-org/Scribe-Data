"""
Updates data for Scribe by running all or desired WDQS queries and formatting scripts.

Parameters
----------
    languages : list of strings (default=None)
        A subset of Scribe's languages that the user wants to update.

    word_types : list of strings (default=None)
        A subset of nouns, verbs, and prepositions that currently can be updated with this fie.

Example
-------
    python3 src/scribe_data/extract_transform/wikidata/update_data.py '["French", "German"]' '["nouns", "verbs"]'
"""

import itertools
import json
import os
import sys
from urllib.error import HTTPError

import pandas as pd
from SPARQLWrapper import JSON, POST, SPARQLWrapper
from tqdm.auto import tqdm

from scribe_data.utils import (
    check_and_return_command_line_args,
    extract_language_id,
)

from scribe_data.total_nouns import get_total_nouns
from scribe_data.query_results import process_query_results
import math 


SCRIBE_DATA_SRC_PATH = "src/scribe_data"
PATH_TO_ET_LANGUAGE_FILES = f"{SCRIBE_DATA_SRC_PATH}/extract_transform/languages"
PATH_TO_UPDATE_FILES = f"{SCRIBE_DATA_SRC_PATH}/load/update_files"

# Set SPARQLWrapper query conditions.
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)
sparql.setMethod(POST)

with open(f"{PATH_TO_UPDATE_FILES}/total_data.json", encoding="utf-8") as f:
    current_data = json.load(f)

current_languages = list(current_data.keys())
current_word_types = ["nouns", "verbs", "prepositions"]

# Check whether arguments have been passed to only update a subset of the data.
languages, word_types = check_and_return_command_line_args(
    all_args=sys.argv,
    first_args_check=current_languages,
    second_args_check=current_word_types,
)

# Assign current_languages and current_word_types if no arguments have been passed.
languages_update = []
if languages is None:
    languages_update = current_languages
else:
    languages_update = languages

word_types_update = []
if word_types is None:
    word_types_update = current_word_types
else:
    word_types_update = word_types

# Derive Data directory elements for potential queries.
languages_dir_files = []

for path, _, files in os.walk(PATH_TO_ET_LANGUAGE_FILES):
    languages_dir_files.extend(os.path.join(path, name) for name in files)

language_dir_files = list(
    {
        f.split(PATH_TO_ET_LANGUAGE_FILES + "/")[1].split("/")[0]
        for f in languages_dir_files
        if f.split(PATH_TO_ET_LANGUAGE_FILES + "/")[1][0] != "_"
    }
)

# Data paths to run scripts and format outputs.
# Check to see if the language has all zeroes for its data, meaning it's been added.
new_language_list = []
for lang in languages_update:
    # Prepositions not needed for all languages.
    check_current_data = [current_data[lang][k] for k in current_data[lang].keys()]
    if len(set(check_current_data)) == 1 and check_current_data[0] == 0:
        new_language_list.append(lang)

# Derive queries to be ran.
possible_queries = []
for d in language_dir_files:
    possible_queries.extend(
        f"{PATH_TO_ET_LANGUAGE_FILES}/{d}/{target_type}"
        for target_type in word_types_update
        if f"{PATH_TO_ET_LANGUAGE_FILES}/{d}/{target_type}"
        in [
            e[: len(f"{PATH_TO_ET_LANGUAGE_FILES}/{d}/{target_type}")]
            for e in languages_dir_files
        ]
    )

queries_to_run_lists = [
    [
        q
        for q in possible_queries
        if q.split(PATH_TO_ET_LANGUAGE_FILES + "/")[1].split("/")[0] in languages_update
    ]
    for lang in languages_update
]

queries_to_run = list({q for sub in queries_to_run_lists for q in sub})

# Run queries and format data.
data_added_dict = {}
for q in tqdm(
    queries_to_run,
    desc="Data updated",
    unit="dirs",
):
    lang = q.split("/")[-2]
    target_type = q.split("/")[-1]
    query_name = f"query_{target_type}.sparql"
    query_path = f"{q}/{query_name}"

    if not os.path.exists(query_path):
        # There are multiple queries for a given target_type, so start by running the first.
        query_path = query_path[: -len(".sparql")] + "_1" + ".sparql"

    print(f"Querying and formatting {lang} {target_type}")
    # First format the lines into a multi-line string and then pass this to SPARQLWrapper.
    with open(query_path, encoding="utf-8") as file:
        query_lines = file.readlines()
    
    
    if any("OFFSET" in line for line in query_lines):
        
        language_id = extract_language_id(query_lines)
        Total_nouns = get_total_nouns(language_id)

        batch_size = 10000  #adjust as needed {{Same as limit}}
     
        # Calculate the number of iterations needed
        num_iterations = math.ceil(Total_nouns / batch_size)

        for iteration in range(num_iterations):
            # Calculate the offset for the current iteration
            offset = iteration * batch_size

            modified_query = [line.replace("OFFSET OFFSET_BY", f"OFFSET {offset}") for line in query_lines]
            
            sparql.setQuery("".join(modified_query))
    
            results = None
            try:
                results = sparql.query().convert()
            except HTTPError as err:
                print(f"HTTPError with {query_path}: {err}")
            
            process_query_results(results, lang, target_type, PATH_TO_ET_LANGUAGE_FILES, query_path, data_added_dict, current_data, sparql, queries_to_run, q)


    else:

        sparql.setQuery("".join(query_lines))

        results = None
        try:
            results = sparql.query().convert()
        except HTTPError as err:
            print(f"HTTPError with {query_path}: {err}")

        process_query_results(results, lang, target_type, PATH_TO_ET_LANGUAGE_FILES, query_path, data_added_dict, current_data, sparql, queries_to_run, q)

# Update total_data.json.
with open(f"{PATH_TO_UPDATE_FILES}/total_data.json", "w", encoding="utf-8") as f:
    json.dump(current_data, f, ensure_ascii=False, indent=0)


# Update data_table.txt
current_data_df = pd.DataFrame(
    #current_data
    index=sorted(list(current_data.keys())),
    columns=["nouns", "verbs", "translations", "prepositions"],
)
for lang, wt in itertools.product(
    list(current_data_df.index), list(current_data_df.columns)
):
    if wt in current_data[lang].keys():
        current_data_df.loc[lang, wt] = f"{current_data[lang][wt]:,}"
    elif wt == "translations":
        current_data_df.loc[lang, wt] = f"{67652:,}"

current_data_df.index.name = "Languages"
current_data_df.columns = [c.capitalize() for c in current_data_df.columns]

# Get the current emoji data so that it can be appended at the end of the table.
current_emoji_data_strings = []
with open(f"{PATH_TO_UPDATE_FILES}/data_table.txt", encoding="utf-8") as f:
    old_table_values = f.read()

for line in old_table_values.splitlines():
    current_emoji_data_strings.append(line.split("|")[-2] + "|")

# Write the new values to the table, which overwrites the emoji keyword values.
with open(f"{PATH_TO_UPDATE_FILES}/data_table.txt", "w+", encoding="utf-8") as f:
    table_string = str(current_data_df.to_markdown()).replace(" nan ", "   - ")
    # Right justify the data and left justify the language indexes.
    table_string = (
        table_string.replace("-|-", ":|-")
        .replace("-|:", ":|-")
        .replace(":|-", "-|-", 1)
    )
    f.writelines(table_string)

# Get the new table values and then rewrite the file with the full table.
new_table_value_strings = []
with open(f"{PATH_TO_UPDATE_FILES}/data_table.txt", encoding="utf-8") as f:
    new_table_values = f.read()

for line in new_table_values.splitlines():
    # Replace headers while translation is still in beta and always for prepositions to annotate missing values.
    line = line.replace("Translations", "Translations\*")
    line = line.replace("Prepositions", "Prepositions†")
    new_table_value_strings.append(line)

with open(f"{PATH_TO_UPDATE_FILES}/data_table.txt", "w+", encoding="utf-8") as f:
    for i in range(len(new_table_value_strings)):
        f.writelines(new_table_value_strings[i] + current_emoji_data_strings[i] + "\n")

# Update data_updates.txt.
data_added_string = ""
language_keys = sorted(list(data_added_dict.keys()))

# Check if all data added values are 0 and remove if so.
for lang in language_keys:
    if all(v <= 0 for v in data_added_dict[lang].values()):
        language_keys.remove(lang)

for lang in language_keys:
    if lang == language_keys[0]:
        data_added_string += (
            f"- {lang} (New):" if lang in new_language_list else f"- {lang}:"
        )
    else:
        data_added_string += (
            f"\n- {lang} (New):" if lang in new_language_list else f"\n- {lang}:"
        )

    for wt in word_types_update:
        if wt in data_added_dict[lang].keys():
            if data_added_dict[lang][wt] <= 0:
                pass
            elif data_added_dict[lang][wt] == 1:  # remove the s for label
                data_added_string += f" {data_added_dict[lang][wt]} {wt[:-1]},"
            else:
                data_added_string += f" {data_added_dict[lang][wt]:,} {wt},"

    data_added_string = data_added_string[:-1]  # remove the last comma

with open(f"{PATH_TO_UPDATE_FILES}/data_updates.txt", "w+", encoding="utf-8") as f:
    f.writelines(data_added_string)
