# SPDX-License-Identifier: GPL-3.0-or-later
"""
Updates data for Scribe by running all or desired WDQS queries and formatting scripts.
"""

import json
import os
import re
import subprocess
import sys
from http.client import IncompleteRead
from pathlib import Path
from urllib.error import HTTPError

from tqdm.auto import tqdm

from scribe_data.utils import (
    LANGUAGE_DATA_EXTRACTION_DIR,
    format_sublanguage_name,
    language_metadata,
    list_all_languages,
)
from scribe_data.wikidata.wikidata_utils import sparql


def execute_formatting_script(output_dir: str, language: str, data_type: str):
    """
    Executes a formatting script given a filepath and output directory for the process.

    Parameters
    ----------
    output_dir : str
        The output directory path for results.

    language : str
        The language for which the data is being loaded.

    data_type : str
        The type of data being loaded (e.g. 'nouns', 'verbs').

    Returns
    -------
    The results of the formatting script are saved in the given output directory.
    """
    formatting_file_path = Path(__file__).parent / "format_data.py"

    # Determine the root directory of the project.
    project_root = Path(__file__).parent.parent.parent

    # Use sys.executable to get the Python executable path.
    python_executable = sys.executable

    # Set the PYTHONPATH environment variable.
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)

    subprocess_args = [
        "--dir-path",
        output_dir,
        "--language",
        language,
        "--data_type",
        data_type,
    ]

    try:
        subprocess.run(
            [
                python_executable,
                str(formatting_file_path),
                *subprocess_args,
            ],
            env=env,
            check=True,
        )

    except subprocess.CalledProcessError as e:
        print(f"Error: The formatting script failed with exit status {e.returncode}.")


def query_data(
    languages: str = None,
    data_type: str = None,
    output_dir: str = None,
    overwrite: bool = None,
    interactive: bool = False,
):
    """
    Queries language data from the Wikidata lexicographical data.

    Parameters
    ----------
    language : str
        The language(s) to get.

    data_type : str
        The data type(s) to get.

    output_dir : str
        The output directory path for results.

    overwrite : bool (default: False)
        Whether to overwrite existing files.

    Returns
    -------
    Formatted data from Wikidata saved in the output directory.
    """
    current_languages = list_all_languages(language_metadata)
    current_data_type = ["nouns", "verbs", "prepositions"]

    # Assign current_languages and current_data_type if no arguments have been passed.
    languages_update = current_languages if languages is None else languages
    languages_update = [lang for lang in languages_update]
    data_type_update = current_data_type if data_type is None else data_type

    all_language_data_extraction_files = [
        path for path in Path(LANGUAGE_DATA_EXTRACTION_DIR).rglob("*") if path.is_file()
    ]

    language_data_extraction_files_in_use = [
        path
        for path in all_language_data_extraction_files
        if path.parent.name in data_type_update
        and path.parent.parent.name in languages_update
        and path.name != "__init__.py"
    ]

    # Derive the maximum query interval for use in looping through all queries.
    query_intervals = []
    for f in language_data_extraction_files_in_use:
        if f.name[-len(".sparql") :] == ".sparql":
            if re.findall(r".+_\d+.sparql", str(f.name)):
                query_intervals.append(int(re.search(r"_(\d+)\.", f.name).group(1)))

    if query_intervals:
        max_query_interval = max(query_intervals)

    else:
        max_query_interval = None

    queries_to_run = {
        Path(re.sub(r"_\d+.sparql", ".sparql", str(f)))
        for f in language_data_extraction_files_in_use
        if f.name[-len(".sparql") :] == ".sparql"
    }
    queries_to_run = sorted(queries_to_run)

    # MARK: Run Queries

    for q in tqdm(
        queries_to_run,
        desc="Data updated",
        unit="process",
        disable=interactive,
    ):
        lang = format_sublanguage_name(q.parent.parent.name, language_metadata)
        target_type = q.parent.name

        updated_path = output_dir[2:] if output_dir.startswith("./") else output_dir
        export_dir = Path(updated_path) / lang.replace(" ", "_")
        export_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"{target_type}.json"
        file_path = export_dir / file_name

        if existing_files := list(export_dir.glob(f"{target_type}*.json")):
            if overwrite:
                print("Overwrite is enabled. Removing existing files...")
                for file in existing_files:
                    file.unlink()

            else:
                if not interactive:
                    print(
                        f"\nExisting file(s) found for {lang.title()} {target_type} in the {output_dir} directory:\n"
                    )
                    for i, file in enumerate(existing_files, 1):
                        print(f"{i}. {file.name}")

                    # choice = input(
                    #     "\nChoose an option:\n1. Overwrite existing (press 'o')\n2. Keep all (press 'k')\n3. Skip process (press anything else)\nEnter your choice: "
                    # )

                    choice = input(
                        "\nChoose an option:\n1. Overwrite existing data (press 'o')\n2. Skip process (press anything else)\nEnter your choice: "
                    )

                    if choice.lower() == "o":
                        print("Removing existing files...")
                        for file in existing_files:
                            file.unlink()

                    # elif choice in ["k", "K"]:
                    #     timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                    #     file_name = f"{target_type}_{timestamp}.json"

                    else:
                        print(f"Skipping update for {lang.title()} {target_type}.")

        print(f"Querying and formatting {lang.title()} {target_type}")

        # Mark the query as the first in a set of queries if needed.
        if not q.exists():
            q = Path(str(q).replace(".sparql", "_1.sparql"))

        # First format the lines into a multi-line string and then pass this to SPARQLWrapper.
        with open(q, encoding="utf-8") as file:
            query_lines = file.readlines()

        sparql.setQuery("".join(query_lines))

        results = None

        try:
            results = sparql.query().convert()

        except HTTPError as http_err:
            print(f"HTTPError with {q}: {http_err}")
            return {"success": False, "skipped": False}
        except IncompleteRead as read_err:
            print(f"Incomplete read error with {q}: {read_err}")
            return {"success": False, "skipped": False}

        if results is None:
            print(f"Nothing returned by the WDQS server for {q}")

            # Allow for a query to be reran up to two times.
            if queries_to_run.count(q) < 3:
                print("The query will be retried.")
                queries_to_run.append(q)
            else:
                print("Max retries reached. Skipping this query.")
                return {"success": False, "skipped": False}

        else:
            # Subset the returned JSON and the individual results before saving.
            query_results = results["results"]["bindings"]

            results_final = []

            for r in query_results:  # query_results is also a list
                r_dict = {k: r[k]["value"] for k in r.keys()}

                results_final.append(r_dict)

            with open(
                Path(output_dir)
                / lang.replace(" ", "_")
                / f"{target_type}_queried.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(results_final, f, ensure_ascii=False, indent=0)

            if "_1" in q.name:
                # Note: Only the first query was ran, so we need to run the second and append the json.
                for i in range(max_query_interval + 1)[2:]:
                    suffix = f"_{i}"
                    q = Path(str(q).replace(f"_{i-1}", suffix))

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
                                    Path(output_dir)
                                    / lang.replace(" ", "_")
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

            # MARK: Save Results

            with open(file_path, "w", encoding="utf-8") as json_file:
                json.dump(results_final, json_file, ensure_ascii=False, indent=0)

            # Call the formatting script.
            execute_formatting_script(
                output_dir=output_dir, language=lang, data_type=target_type
            )

            print(
                f"Successfully queried and formatted data for {lang.title()} {target_type}."
            )
