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

from scribe_data.utils import LANGUAGE_DATA_EXTRACTION_DIR, lexeme_form_metadata

lexeme_form_qid_order = []
for key, value in lexeme_form_metadata.items():
    lexeme_form_qid_order.extend(
        sub_value["qid"] for sub_key, sub_value in value.items() if "qid" in sub_value
    )


# MARK: Extract Forms


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


# MARK: Check Label


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

    if not line_match:
        return False

    onto_rep_pattern = r"{form_label} ontolex:representation .* ;".format(
        form_label=form_label
    )

    if not (line_match := re.search(pattern=onto_rep_pattern, string=form_text)):
        return False

    rep_label_pattern = r".*\?(.*);"
    if label_match := re.search(pattern=rep_label_pattern, string=line_match[0]):
        form_rep_label = label_match[1].strip()

    return form_rep_label == current_form_rep_label


# MARK: Get Label


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


# MARK: Get QIDs


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


# MARK: Correct Label


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
        return f"{qid_label} {', '.join(not_included_qids)} not included in lexeme_form.metadata.json"

    qids_ordered = [q for q in lexeme_form_qid_order if q in qids]
    correct_label = ""
    for q in qids_ordered:
        for category_vals in lexeme_form_metadata.values():
            for qid_label in category_vals.values():
                if q == qid_label["qid"]:
                    correct_label += qid_label["label"]

    return correct_label[:1].lower() + correct_label[1:]


# MARK: Return Forms


def check_unique_return_forms(query_text: str) -> bool:
    """
    Checks that each form returned by the SELECT statement is unique.

    Parameters
    ----------
        query_text : str
            The full text of the SPARQL query.

    Returns
    -------
        bool
            True if all returned forms are unique, False otherwise.
    """

    error_output = ""
    select_pattern = r"SELECT\s*(.*?)\s*WHERE"
    if match := re.search(pattern=select_pattern, string=query_text, flags=re.DOTALL):
        # Extracting forms after '?' and handling cases where 'AS' is used for aliasing.
        return_forms = []
        for part in match[1].split():
            if "?" in part:
                form = part.split("?")[-1]
                if "AS" in form:
                    form = form.split("AS")[0].strip()
                return_forms.append(form)

        unique_forms = set(return_forms)
        if len(return_forms) != len(unique_forms):
            error_output += f"\nDuplicate forms found: {', '.join([form for form in return_forms if return_forms.count(form) > 1])}"
            return error_output

        return True

    return True


# MARK: Unreturned Forms


def check_unreturned_optional_forms(query_text: str) -> str:
    """
    Checks if there are any optional forms in the query that aren't returned in the SELECT statement.

    Parameters
    ----------
    query_text : str
        The full text of the SPARQL query.

    Returns
    -------
    str
        Error message listing any unreturned forms, or empty string if all forms are returned.
    """
    # Extract forms from SELECT statement.
    select_pattern = r"SELECT\s*(.*?)\s*WHERE"
    select_forms = set()
    if select_match := re.search(
        pattern=select_pattern, string=query_text, flags=re.DOTALL
    ):
        for part in select_match[1].split():
            if "?" in part:
                form = part.split("?")[-1]
                if "AS" in form:
                    form = form.split("AS")[0].strip()
                select_forms.add(form)

    # Extract forms from OPTIONAL blocks
    optional_forms = set()
    optional_pattern = r"OPTIONAL\s*\{([^}]*)\}"
    for match in re.finditer(optional_pattern, query_text):
        form_text = match.group(1)
        rep_pattern = r"ontolex:representation\s+\?([\w]+)\s*;"
        if rep_match := re.search(rep_pattern, form_text):
            optional_forms.add(rep_match[1])

    # Find forms that appear in OPTIONAL blocks but not in SELECT
    unreturned_forms = optional_forms - select_forms

    if unreturned_forms:
        return f"Unreturned optional forms: {', '.join(sorted(unreturned_forms))}"

    return ""


# MARK: Undefined Return Forms
def check_undefined_return_forms(query_text: str) -> str:
    """
    Checks if the query is trying to return forms that aren't defined in the WHERE clause
    when there are no OPTIONAL blocks.

    Parameters
    ----------
        query_text : str
            The full text of the SPARQL query.

    Returns
    -------
        str
            Error message listing any undefined forms being returned, or empty string if all
            returned forms are properly defined.
    """

    # Check if query has any OPTIONAL blocks
    optional_pattern = r"OPTIONAL\s*\{"
    has_optional_blocks = bool(re.search(optional_pattern, query_text))

    if has_optional_blocks:
        return ""  # Skip check for queries with OPTIONAL blocks

    # Extract forms from SELECT statement and track aliases
    select_pattern = r"SELECT\s*(.*?)\s*WHERE"
    select_forms = set()
    aliases = set()

    if select_match := re.search(
        pattern=select_pattern, string=query_text, flags=re.DOTALL
    ):
        select_clause = select_match[1]

        # Process each SELECT item
        items = select_clause.split("\n")
        for item in items:
            item = item.strip()
            if not item:
                continue

            # Handle REPLACE...AS statements
            if "AS ?" in item:
                if alias_match := re.search(r"AS \?(\w+)", item):
                    aliases.add(alias_match[1])

                if var_match := re.findall(r"\?(\w+)", item):
                    select_forms.update(v for v in var_match if v not in aliases)

            elif "?" in item:
                var_match = re.findall(r"\?(\w+)", item)
                select_forms.update(var_match)

    # Extract defined variables from WHERE clause
    where_pattern = r"WHERE\s*\{(.*?)\}(?:\s*ORDER BY|\s*$)"
    defined_vars = set()
    if where_match := re.search(
        pattern=where_pattern, string=query_text, flags=re.DOTALL
    ):
        where_clause = where_match[1]
        var_pattern = r"\?(\w+)"
        defined_vars = set(re.findall(var_pattern, where_clause))

    if undefined_forms := {
        form for form in select_forms - defined_vars if form not in aliases
    }:
        return f"Undefined forms in SELECT: {', '.join(sorted(undefined_forms))}"

    return ""


# MARK: Defined Return Forms


def check_defined_return_forms(query_text: str) -> str:
    """
    Ensures that all variables defined in the WHERE clause are returned in the SELECT clause.

    Parameters
    ----------
        query_text : str
            The full text of the SPARQL query.

    Returns
    -------
        str
            Error message listing any defined but unreturned forms, or empty string if all forms are returned.
    """
    # Check if query has any OPTIONAL blocks.
    optional_pattern = r"OPTIONAL\s*\{"
    has_optional_blocks = bool(re.search(optional_pattern, query_text))

    if has_optional_blocks:
        return ""  # Skip check for queries with OPTIONAL blocks

    # Extract forms from WHERE clause
    where_pattern = r"WHERE\s*\{(.*?)\}"
    where_forms = set()
    if where_match := re.search(
        pattern=where_pattern, string=query_text, flags=re.DOTALL
    ):
        where_clause = where_match[1]
        where_forms = set(re.findall(r"\?(\w+)", where_clause))

    # Extract forms from SELECT statement.
    select_pattern = r"SELECT\s*(.*?)\s*WHERE"
    select_forms = set()
    if select_match := re.search(
        pattern=select_pattern, string=query_text, flags=re.DOTALL
    ):
        select_clause = select_match[1]
        select_forms = set(re.findall(r"\?(\w+)", select_clause))

    # Find forms that are defined but not returned, excluding allowed unreturned variables.
    unreturned_forms = where_forms - select_forms

    if unreturned_forms:
        return f"Defined but unreturned forms: {', '.join(sorted(unreturned_forms))}"
    return ""


# MARK: Main Query Forms Validation
def check_query_forms() -> None:
    """
    Validates SPARQL queries in the language data directory to check for correct form QIDs.
    """

    error_output = ""
    index = 0
    for query_file in LANGUAGE_DATA_EXTRACTION_DIR.glob("**/*.sparql"):
        query_file_str = str(query_file)
        with open(query_file, "r", encoding="utf-8") as file:
            query_text = file.read()

        # Check for unique return forms and handle the error message if any
        unique_check_result = check_unique_return_forms(query_text)
        if unique_check_result is not True:
            error_output += f"\n{index}. {query_file_str}: {unique_check_result}\n"
            index += 1

        if undefined_forms := check_undefined_return_forms(query_text):
            error_output += f"\n{index}. {query_file_str}: {undefined_forms}\n"
            index += 1

        if unreturned_optional_forms := check_unreturned_optional_forms(query_text):
            error_output += (
                f"\n{index}. {query_file_str}: {unreturned_optional_forms}\n"
            )
            index += 1

        if defined_unreturned_forms := check_defined_return_forms(query_text):
            error_output += f"\n{index}. {query_file_str}: {defined_unreturned_forms}\n"
            index += 1
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
                        f"{incorrect_query_labels[i][0]} : {incorrect_query_labels[i][1]}"
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

    else:
        print("All query forms are labeled and formatted correctly.")


if __name__ == "__main__":
    check_query_forms()
