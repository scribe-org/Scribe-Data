"""
Check the queries within Scribe-Data to make sure the accessed forms are correct.

Example
-------
    python3 src/scribe_data/check/check_query_forms.py

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

import re
from pathlib import Path

from scribe_data.cli.cli_utils import (
    LANGUAGE_DATA_EXTRACTION_DIR,
    lexeme_form_metadata,
)

lexeme_form_qid_order = []
for key, value in lexeme_form_metadata.items():
    lexeme_form_qid_order.extend(
        sub_value["qid"] for sub_key, sub_value in value.items() if "qid" in sub_value
    )


def extract_forms_from_sparql(file_path: Path) -> str:
    """
    Extracts the QID from a SPARQL query file based on the provided pattern.

    Parameters
    ----------
        file_path : Path
            The path to the SPARQL query file from which to extract forms.

    Returns
    -------
        query_form_dict : dict
            The file path with form labels of the query and their respective QIDs.

    Raises
    ------
        FileNotFoundError
            If the specified file does not exist.
    """
    optional_pattern = r"\s\sOPTIONAL\s*\{([^}]*)\}"
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            query_text = file.read()

            return [
                match[1]
                for match in re.finditer(pattern=optional_pattern, string=query_text)
            ]

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return None


def check_form_label(form_text: str):
    """
    Checks that the label of the form matches the representation label.

    Parameters
    ----------
        form_text : str
            The text that defines the form within the query.

    Returns
    -------
        bool
            Whether the form and its current representation label match (repForm and rep).
    """
    form_label_line_pattern = r"\?lexeme ontolex:lexicalForm .* \."

    if line_match := re.search(pattern=form_label_line_pattern, string=form_text):
        form_label_pattern = r".*\?(.*)\."
        if label_match := re.search(pattern=form_label_pattern, string=line_match[0]):
            form_label = label_match[1].strip()
            current_form_rep_label = form_label.split("Form")[0]

    onto_rep_pattern = r"{form_label} ontolex:representation .* ;".format(
        form_label=form_label
    )

    if not (line_match := re.search(pattern=onto_rep_pattern, string=form_text)):
        return False

    rep_label_pattern = r".*\?(.*);"
    if label_match := re.search(pattern=rep_label_pattern, string=line_match[0]):
        form_rep_label = label_match[1].strip()

    return form_rep_label == current_form_rep_label


def extract_form_rep_label(form_text: str):
    """
    Extracts the representation label from an optional query form.

    Parameters
    ----------
        form_text : str
            The text that defines the form within the query.

    Returns
    -------
        str
            The label of the form representation.
    """
    onto_rep_pattern = r"ontolex:representation .* ;"
    if line_match := re.search(pattern=onto_rep_pattern, string=form_text):
        rep_label_pattern = r".*\?(.*);"
        if label_match := re.search(pattern=rep_label_pattern, string=line_match[0]):
            return label_match[1].strip()


def extract_form_qids(form_text: str):
    """
    Extracts all QIDs from an optional query form.

    Parameters
    ----------
        form_text : str
            The text that defines the form within the query.

    Returns
    -------
        list[str]
            All QIDS that make up the form.
    """
    qids_pattern = r"wikibase:grammaticalFeature .+ \."
    if match := re.search(pattern=qids_pattern, string=form_text):
        return [q.split("wd:")[1].split(" .")[0] for q in match[0].split(", ")]


def return_correct_form_label(qids: list):
    """
    Returns the correct label for a lexeme form representation given the QIDs that compose it.

    Parameters
    ----------
        qids : list[str]
            All QIDS that make up the form.

    Returns
    -------
        correct_label : str
            The label for the representation given the QIDs.
    """
    if not qids:
        return "Invalid query formatting found"

    if not set(qids) <= set(lexeme_form_qid_order):
        not_included_qids = sorted(set(qids) - set(lexeme_form_qid_order))
        qid_label = "QIDs" if len(not_included_qids) > 1 else "QID"
        return f"{qid_label} {', '.join(not_included_qids)} not included in metadata"

    qids_ordered = [q for q in lexeme_form_qid_order if q in qids]
    correct_label = ""
    for q in qids_ordered:
        for category_vals in lexeme_form_metadata.values():
            for qid_label in category_vals.values():
                if q == qid_label["qid"]:
                    correct_label += qid_label["label"]

    return correct_label[:1].lower() + correct_label[1:]


def check_query_forms() -> None:
    """
    Validates SPARQL queries in the language data directory to check for correct form QIDs.
    """
    error_output = ""
    index = 0
    for query_file in LANGUAGE_DATA_EXTRACTION_DIR.glob("**/*.sparql"):
        query_file_str = str(query_file)
        if extract_forms_from_sparql(query_file):
            query_form_check_dict = {}
            for form_text in extract_forms_from_sparql(query_file):
                if (
                    "ontolex:lexicalForm" in form_text
                    and "ontolex:representation" in form_text
                ):
                    form_rep_label = extract_form_rep_label(form_text=form_text)
                    check = check_form_label(form_text=form_text)
                    qids = extract_form_qids(form_text=form_text)
                    correct_form_rep_label = return_correct_form_label(qids=qids)

                    query_form_check_dict[form_rep_label] = {
                        "form_rep_match": check,
                        "qids": qids,
                        "correct_form_rep_label": correct_form_rep_label,
                    }

            if query_form_check_dict:
                incorrect_query_labels = []
                for k in query_form_check_dict:
                    if k != query_form_check_dict[k]["correct_form_rep_label"]:
                        incorrect_query_labels.append(
                            (k, query_form_check_dict[k]["correct_form_rep_label"])
                        )

                    elif query_form_check_dict[k]["form_rep_match"] is False:
                        incorrect_query_labels.append(
                            (k, "Form and representation labels don't match")
                        )

                if incorrect_query_labels:
                    current_rep_label_to_correct_label_str = [
                        f"{incorrect_query_labels[i][0]}: {incorrect_query_labels[i][1]}"
                        for i in range(len(incorrect_query_labels))
                    ]
                    incorrect_query_form_rep_labels_str = "\n  - ".join(
                        current_rep_label_to_correct_label_str
                    )

                    error_output += f"\n{index}. {query_file_str}:\n  - {incorrect_query_form_rep_labels_str}\n"
                    index += 1

    if error_output:
        print(
            "There are query forms that have invalid representation labels given their forms:"
        )
        print(error_output)
        print("Please correct the above lexeme form representation labels.")
        exit(1)


if __name__ == "__main__":
    check_query_forms()
