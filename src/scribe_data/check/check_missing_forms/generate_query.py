# SPDX-License-Identifier: GPL-3.0-or-later
"""
Generate SPARQL queries for missing lexeme forms.
"""

import os
from pathlib import Path

from scribe_data.check.check_missing_forms.normalize_forms import sort_qids_by_position
from scribe_data.utils import (
    LANGUAGE_DATA_EXTRACTION_DIR as language_data_extraction,
)
from scribe_data.utils import (
    data_type_metadata,
    language_metadata,
    lexeme_form_metadata,
    sub_languages,
)


def generate_query(missing_features, query_dir=None, sub_lang_iso_code=None):
    """
    Generate SPARQL queries for missing lexeme forms.

    Parameters
    ----------
    missing_features : dict
        Dictionary containing missing features by language and data type.
        Format: {language_qid: {data_type_qid: [[form_qids]]}}

    query_dir : str or Path, optional
        Directory where query files should be saved.
        If None, uses default language_data_extraction directory.

    Returns
    -------
    str
        Path to the generated query file.

    Notes
    -----
    - Generates a single query file combining all forms for a given language and data type combination.
    - Query files are named incrementally if duplicates exist.
    - Creates necessary directories if they don't exist.
    """
    language_qid = next(iter(missing_features.keys()))
    data_type_qid = next(iter(missing_features[language_qid].keys()))

    # Find the language entry by QID.
    language_entry = None
    for name, data in language_metadata.items():
        if data.get("qid") == language_qid:
            language_entry = (name, data)
            break
        # Check sub-languages if main language not found
        if "sub_languages" in data:
            for sub_name, sub_data in data["sub_languages"].items():
                if sub_data.get("qid") == language_qid:
                    # Use main language name instead of sub_name.
                    language_entry = (
                        name,
                        sub_data,
                    )
                    break
    if language_entry is None:
        raise ValueError(f"Language with QID {language_qid} not found in metadata")

    language = language_entry[0]  # the language name

    data_type = next(
        name for name, qid in data_type_metadata.items() if qid == data_type_qid
    )

    # Create a QID to label mapping from the metadata.
    qid_to_label = {}
    for category in lexeme_form_metadata.values():
        for item in category.values():
            qid_to_label[item["qid"]] = item["label"]

    # Process all forms at once.
    forms_query = []
    all_form_combinations = sort_qids_by_position(
        nested_qids=missing_features[language_qid][data_type_qid]
    )

    # Keep track of used labels to avoid duplicates
    used_labels = set()

    for form_qids in all_form_combinations:
        # Convert QIDs to labels and join them together.
        labels = [qid_to_label.get(qid, qid) for qid in form_qids]
        concatenated_label = "".join(labels)

        # Make first letter lowercase.
        concatenated_label = concatenated_label[0].lower() + concatenated_label[1:]

        # Only add if this label hasn't been used before
        if concatenated_label not in used_labels:
            forms_query.append({"label": concatenated_label, "qids": form_qids})
            used_labels.add(concatenated_label)

    body_data_type = data_type.replace("_", "")[:-1]

    # Generate a single query for all forms.
    main_body = f"""# tool: scribe-data
# All {language.capitalize()} ({language_qid}) {data_type} ({data_type_qid}) and the given forms.
# Enter this query at https://query.wikidata.org/.

SELECT
  (REPLACE(STR(?lexeme), "http://www.wikidata.org/entity/", "") AS ?lexemeID)
  ?lastModified
  ?{body_data_type}
  """ + "\n  ".join(f'?{form["label"]}' for form in forms_query)

    where_clause = f"""

WHERE {{
  ?lexeme dct:language wd:{language_qid} ;
      wikibase:lexicalCategory wd:{data_type_qid} ;
      wikibase:lemma ?{body_data_type} ;
      schema:dateModified ?lastModified .
    """
    if sub_lang_iso_code:
        try:
            for data_type_qid in sub_languages[language]:
                if data_type_qid == sub_lang_iso_code:
                    sub_lang_name = sub_languages[language][sub_lang_iso_code]["name"]
                    break
        except (KeyError, TypeError):
            print(
                f"Warning: Could not find sub-language data for {language} - {sub_lang_iso_code}"
            )
            return None

        where_clause += f"""
  # Note: We need to filter for {sub_lang_iso_code} to remove {sub_lang_name} ({sub_lang_iso_code}) words.
  FILTER(lang(?{data_type}) = "{sub_lang_iso_code}")
    """

    # Generate OPTIONAL clauses for all forms in one query.
    optional_clauses = ""
    for form in forms_query:
        qids = ", ".join(f"wd:{qid}" for qid in form["qids"])
        optional_clauses += f"""
  OPTIONAL {{
    ?lexeme ontolex:lexicalForm ?{form['label']}Form .
    ?{form['label']}Form ontolex:representation ?{form['label']} ;
      wikibase:grammaticalFeature {qids} .
  }}
"""

    # Print the complete query.
    final_query = main_body + where_clause + optional_clauses + "}\n"

    def get_available_filename(base_path):
        """Helper function to find the next available filename"""
        if not os.path.exists(base_path):
            return base_path

        base, ext = os.path.splitext(base_path)
        counter = 1

        # If the base already ends with _N, start from that number.
        import re

        if match := re.search(r"_(\d+)$", base):
            counter = int(match.group(1)) + 1
            base = base[: match.start()]

        while True:
            new_path = f"{base}_{counter}{ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    if sub_lang_iso_code:
        base_file_name = (
            f"{query_dir}/{language}/{sub_lang_name}/{data_type}/{data_type}.sparql"
        )
        print(base_file_name)

    # Create base filename using the provided query_dir or default.
    elif query_dir:
        base_file_name = (
            Path(query_dir) / language / data_type / f"query_{data_type}.sparql"
        )

    else:
        base_file_name = f"{language_data_extraction}/{language}/{data_type}/query_{data_type}.sparql"

    # Get the next available filename.
    file_name = get_available_filename(str(base_file_name))

    # Create directory if it doesn't exist.
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    # Write the file.
    with open(file_name, "w") as file:
        file.write(final_query)

    print(f"Query file created: {file_name}")

    return file_name
