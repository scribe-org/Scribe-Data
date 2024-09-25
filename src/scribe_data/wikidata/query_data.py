"""
Updates data for Scribe by running all or desired WDQS queries and formatting scripts.

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

import json
import os
from pathlib import Path
from urllib.error import HTTPError

from tqdm.auto import tqdm

from scribe_data.utils import DEFAULT_JSON_EXPORT_DIR
from scribe_data.wikidata.wikidata_utils import sparql


def query_data(languages=None, word_types=None, overwrite=None):
    SCRIBE_DATA_SRC_PATH = Path(__file__).parent.parent
    PATH_TO_LANGUAGE_EXTRACTION_FILES = (
        SCRIBE_DATA_SRC_PATH / "language_data_extraction"
    )
    PATH_TO_UPDATE_FILES = SCRIBE_DATA_SRC_PATH / "load" / "update_files"

    with open(PATH_TO_UPDATE_FILES / "total_data.json", encoding="utf-8") as f:
        current_data = json.load(f)

    current_languages = list(current_data.keys())
    current_word_types = ["nouns", "verbs", "prepositions"]

    # Assign current_languages and current_word_types if no arguments have been passed.
    languages_update = current_languages if languages is None else languages
    word_types_update = current_word_types if word_types is None else word_types

    all_language_data_extraction_files = [
        path
        for path in Path(PATH_TO_LANGUAGE_EXTRACTION_FILES).rglob("*")
        if path.is_file()
    ]

    language_data_extraction_files_in_use = [
        path
        for path in all_language_data_extraction_files
        if path.parent.name in word_types_update
        and path.parent.parent.name in languages_update
        and path.name != "__init__.py"
    ]

    queries_to_run = [
        f
        for f in language_data_extraction_files_in_use
        if f.name[-len(".sparql") :] == ".sparql"
    ]
    queries_to_run = sorted(queries_to_run)

    # Run queries and format data.
    for q in tqdm(
        queries_to_run,
        desc="Data updated",
        unit="process",
    ):
        lang = q.parent.parent.name
        target_type = q.parent.name

        # After formatting and before saving the new data.
        export_dir = Path(DEFAULT_JSON_EXPORT_DIR) / lang.capitalize()
        export_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"{target_type}.json"

        if existing_files := list(export_dir.glob(f"{target_type}*.json")):
            if overwrite:
                print("Overwrite is enabled. Removing existing files...")
                for file in existing_files:
                    file.unlink()
            else:
                print(
                    f"Existing file(s) found for {lang} {target_type} in the outputs directory:\n"
                )
                for i, file in enumerate(existing_files, 1):
                    print(f"{i}. {file.name}")
                # choice = input(
                #     "\nChoose an option:\n1. Overwrite existing (press 'o')\n2. Keep all (press 'k')\n3. Skip process (press anything else)\nEnter your choice: "
                # )
                choice = input(
                    "\nChoose an option:\n1. Overwrite existing data (press 'o')\n2. Skip process (press anything else)\nEnter your choice: "
                )

                print(f"You entered: {choice}")

                if choice.lower() == "o":
                    print("Removing existing files...")
                    for file in existing_files:
                        file.unlink()
                # elif choice in ["k", "K"]:
                #     timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                #     file_name = f"{target_type}_{timestamp}.json"
                else:
                    print(f"Skipping update for {lang} {target_type}.")
                    continue

        file_path = export_dir / file_name
        print(f"Querying and formatting {lang} {target_type}")

        # First format the lines into a multi-line string and then pass this to SPARQLWrapper.
        with open(q, encoding="utf-8") as file:
            query_lines = file.readlines()

        sparql.setQuery("".join(query_lines))

        results = None

        try:
            results = sparql.query().convert()
        except HTTPError as err:
            print(f"HTTPError with {q}: {err}")

        if results is None:
            print(f"Nothing returned by the WDQS server for {q}")

            # Allow for a query to be reran up to two times.
            if queries_to_run.count(q) < 3:
                queries_to_run.append(q)

        else:
            # Subset the returned JSON and the individual results before saving.
            query_results = results["results"]["bindings"]

            results_final = []

            for r in query_results:  # query_results is also a list
                r_dict = {k: r[k]["value"] for k in r.keys()}

                results_final.append(r_dict)

            with open(
                Path(PATH_TO_LANGUAGE_EXTRACTION_FILES)
                / lang
                / target_type
                / f"{target_type}_queried.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(results_final, f, ensure_ascii=False, indent=0)

            if "_1" in q.name:
                # Note: Only the first query was ran, so we need to run the second and append the json.
                for suffix in ["_2", "_3"]:
                    q = Path(str(q).replace("_1", suffix).replace("_2", suffix))

                    if q.exists():
                        with open(q, encoding="utf-8") as file:
                            query_lines = file.readlines()
                            sparql.setQuery("".join(query_lines))

                            results = None
                            try:
                                results = sparql.query().convert()

                            except HTTPError as err:
                                print(f"HTTPError with {q}: {err}")

                            if results is None:
                                print(f"Nothing returned by the WDQS server for {q}")

                                # Allow for a query to be reran up to two times.
                                if queries_to_run.count(q) < 3:
                                    queries_to_run.append(q)

                            else:
                                # Subset the returned JSON and the individual results before saving.
                                query_results = results["results"]["bindings"]

                                # Note: Don't rewrite results_final as we want to extend the json and combine in formatting.
                                for r in query_results:  # query_results is also a list
                                    r_dict = {k: r[k]["value"] for k in r.keys()}

                                    # Note: The following is so we have a breakdown of queries for German later.
                                    # Note: We need auxiliary verbs to be present as we loop to get both sein and haben forms.
                                    if lang == "German":
                                        r_dict_keys = list(r_dict.keys())
                                        if "auxiliaryVerb" not in r_dict_keys:
                                            r_dict["auxiliaryVerb"] = ""

                                    results_final.append(r_dict)

                                with open(
                                    Path(PATH_TO_LANGUAGE_EXTRACTION_FILES)
                                    / lang
                                    / target_type
                                    / f"{target_type}_queried.json",
                                    "w",
                                    encoding="utf-8",
                                ) as f:
                                    json.dump(
                                        results_final,
                                        f,
                                        ensure_ascii=False,
                                        indent=0,
                                    )

            with open(file_path, "w", encoding="utf-8") as json_file:
                json.dump(results_final, json_file, ensure_ascii=False, indent=0)

            # Call the corresponding formatting file.
            os.system(
                f"python3 {PATH_TO_LANGUAGE_EXTRACTION_FILES / lang / target_type / f'format_{target_type}.py'}"
            )

            with open(
                Path("scribe_data_json_export")
                / lang.capitalize()
                / f"{target_type}.json",
                encoding="utf-8",
            ) as json_file:
                formatted_language_data = json.load(json_file)

            current_data[lang][target_type] = len(formatted_language_data)

    # Update total_data.json.
    with open(
        Path(PATH_TO_UPDATE_FILES) / "total_data.json", "w", encoding="utf-8"
    ) as file:
        file.write(json.dumps(current_data, ensure_ascii=False, indent=0))
        file.write("\n")


if __name__ == "__main__":
    query_data()
