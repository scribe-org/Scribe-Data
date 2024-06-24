"""
Setup and commands for the Scribe-Data command line interface.

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
import itertools
import json
import os
from pathlib import Path
from typing import List, Optional
from urllib.error import HTTPError
import datetime

import pandas as pd
from SPARQLWrapper import JSON, POST, SPARQLWrapper
from tqdm.auto import tqdm
import importlib.util

SCRIBE_DATA_SRC_PATH = Path("src/scribe_data")
PATH_TO_LANGUAGE_EXTRACTION_FILES = SCRIBE_DATA_SRC_PATH / "language_data_extraction"
PATH_TO_UPDATE_FILES = SCRIBE_DATA_SRC_PATH / "load/update_files"

# Set SPARQLWrapper query conditions.
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)
sparql.setMethod(POST)

def update_data(languages: Optional[List[str]] = None, word_types: Optional[List[str]] = None):
    with open(PATH_TO_UPDATE_FILES / "total_data.json", encoding="utf-8") as f:
        current_data = json.load(f)

    current_languages = list(current_data.keys())
    current_word_types = ["nouns", "verbs", "prepositions"]

    # Assign current_languages and current_word_types if no arguments have been passed.
    languages_update = current_languages if languages is None else languages
    word_types_update = current_word_types if word_types is None else word_types

    # Add new languages to current_data if they don't exist
    new_language_list = []
    for lang in languages_update:
        if lang not in current_data:
            print(f"Adding new language: {lang}")
            current_data[lang] = {wt: 0 for wt in current_word_types}
            new_language_list.append(lang)

    # Derive queries to be ran.
    queries_to_run = []
    for lang in languages_update:
        for wt in word_types_update:
            query_path = PATH_TO_LANGUAGE_EXTRACTION_FILES / lang / wt / f"query_{wt}.sparql"
            if query_path.exists():
                queries_to_run.append((lang, wt, query_path))

    # Run queries and format data.
    data_added_dict = {}
    for lang, wt, query_path in tqdm(queries_to_run, desc="Data updated", unit="process"):
        print(f"Querying and formatting {lang} {wt}")
        
        with open(query_path, encoding="utf-8") as file:
            query_lines = file.read()
        sparql.setQuery(query_lines)

        try:
            results = sparql.query().convert()
        except HTTPError as err:
            print(f"HTTPError with {query_path}: {err}")
            continue

        if results is None:
            print(f"Nothing returned by the WDQS server for {query_path}")
            continue

        query_results = results["results"]["bindings"]
        results_formatted = [
            {k: r[k]["value"] for k in r.keys()}
            for r in query_results
        ]

        output_path = Path(generate_filename(lang, wt))
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results_formatted, f, ensure_ascii=False, indent=0)

        # Call the corresponding formatting file and update data changes.
        format_data(lang, wt)
        
        # Check current data within formatted data directories.
        json_export_path = Path(f"scribe_data_json_export/{lang.capitalize()}/{wt}.json")
        if json_export_path.exists():
            with open(json_export_path, encoding="utf-8") as json_file:
                new_keyboard_data = json.load(json_file)

            if lang not in data_added_dict:
                data_added_dict[lang] = {}
            data_added_dict[lang][wt] = len(new_keyboard_data) - current_data[lang][wt]

            current_data[lang][wt] = len(new_keyboard_data)
        else:
            print(f"Warning: No data file found for {lang} {wt}")

       # Update total_data.json.
    with open(PATH_TO_UPDATE_FILES / "total_data.json", "w", encoding="utf-8") as f:
        json.dump(current_data, f, ensure_ascii=False, indent=0)

    # Update data_table.txt
    update_data_table(current_data)

# Update data_updates.txt.
    update_data_updates(data_added_dict, new_language_list)

def update_data_updates(data_added_dict, new_language_list):
    data_added_string = ""
    language_keys = sorted([lang for lang in data_added_dict.keys() if any(v > 0 for v in data_added_dict[lang].values())])

    for lang in language_keys:
        prefix = "- {}{}: ".format(lang, " (New)" if lang in new_language_list else "")
        updates = []
        for wt in data_added_dict[lang]:
            if data_added_dict[lang][wt] > 0:
                label = wt[:-1] if data_added_dict[lang][wt] == 1 else wt
                updates.append(f"{data_added_dict[lang][wt]:,} {label}")
        data_added_string += prefix + ", ".join(updates) + "\n"

    with open(PATH_TO_UPDATE_FILES / "data_updates.txt", "w", encoding="utf-8") as f:
        f.write(data_added_string)

def generate_filename(language, word_type):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"scribe_data_json_export/{language}/{word_type}_{timestamp}.json"
    
    # Create the directory if it doesn't exist
    file_path = Path(filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    return str(file_path)

def format_data(lang, target_type):
    format_script_path = PATH_TO_LANGUAGE_EXTRACTION_FILES / lang / target_type / f"format_{target_type}.py"
    # queried_data_path = PATH_TO_LANGUAGE_EXTRACTION_FILES / lang / target_type / f"{target_type}_queried.json"
    
    if not format_script_path.exists():
        print(f"Warning: Format script not found for {lang} {target_type}")
        return

    # if not queried_data_path.exists():
    #     print(f"Warning: Queried data file not found: {queried_data_path}")
    #     return

    try:
        # Change working directory to ensure relative paths work correctly
        original_dir = os.getcwd()
        os.chdir(format_script_path.parent)

        spec = importlib.util.spec_from_file_location("format_module", format_script_path)
        format_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(format_module)

        if hasattr(format_module, 'main'):
            format_module.main()
        else:
            print(f"Warning: main() function not found in {format_script_path}")
    except Exception as e:
        print(f"Error occurred while formatting {lang} {target_type}: {str(e)}")
    finally:
        # Change back to the original directory
        os.chdir(original_dir)


def update_data_table(current_data):
    current_data_df = pd.DataFrame(
        index=sorted(list(current_data.keys())),
        columns=["nouns", "verbs", "translations", "prepositions"],
    )
    for lang, wt in itertools.product(current_data_df.index, current_data_df.columns):
        if wt in current_data[lang]:
            current_data_df.loc[lang, wt] = f"{current_data[lang][wt]:,}"
        elif wt == "translations":
            current_data_df.loc[lang, wt] = f"{67652:,}"

    current_data_df.index.name = "Languages"
    current_data_df.columns = [c.capitalize() for c in current_data_df.columns]

    # Get the current emoji data
    with open(PATH_TO_UPDATE_FILES / "data_table.txt", encoding="utf-8") as f:
        old_table_values = f.read()
    current_emoji_data_strings = [line.split("|")[-2] + "|" for line in old_table_values.splitlines()]

    # Write the new values to the table
    table_string = str(current_data_df.to_markdown()).replace(" nan ", "   - ")
    table_string = table_string.replace("-|-", ":|-").replace("-|:", ":|-").replace(":|-", "-|-", 1)

    new_table_value_strings = []
    for line in table_string.splitlines():
        line = line.replace("Translations  ", "Translations*")
        line = line.replace("Prepositions ", "Prepositions†")
        new_table_value_strings.append(line)

    with open(PATH_TO_UPDATE_FILES / "data_table.txt", "w", encoding="utf-8") as f:
        for i, line in enumerate(new_table_value_strings):
            if i < len(current_emoji_data_strings):
                f.write(line + current_emoji_data_strings[i] + "\n")
            else:
                f.write(line + "   |\n")  # Add an empty emoji column if we run out of emoji data

def update_data_updates(data_added_dict, new_language_list):
    data_added_string = ""
    language_keys = sorted([lang for lang in data_added_dict.keys() if any(v > 0 for v in data_added_dict[lang].values())])

    for lang in language_keys:
        prefix = "- {}{}: ".format(lang, " (New)" if lang in new_language_list else "")
        updates = []
        for wt in data_added_dict[lang]:
            if data_added_dict[lang][wt] > 0:
                label = wt[:-1] if data_added_dict[lang][wt] == 1 else wt
                updates.append(f"{data_added_dict[lang][wt]:,} {label}")
        data_added_string += prefix + ", ".join(updates) + "\n"

    with open(PATH_TO_UPDATE_FILES / "data_updates.txt", "w", encoding="utf-8") as f:
        f.write(data_added_string)

if __name__ == "__main__":
    update_data()