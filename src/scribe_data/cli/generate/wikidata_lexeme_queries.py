# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to generate Wikidata lexeme queries based on Scribe-Data data contracts.
"""

import os
import re
from pathlib import Path

import yaml

from scribe_data.cli.generate.generate_utils import (
    extract_data_contract_values,
    get_next_query_filename,
    sort_qids_by_position,
    split_lexeme_forms_by_identifier,
)
from scribe_data.utils import (
    DATA_CONTRACTS_DIR,
    WIKIDATA_QUERIES_DIR,
    data_type_metadata,
    get_language_from_iso,
    get_language_iso,
    language_metadata,
    lexeme_form_metadata,
    sub_languages,
)


def generate_wikidata_lexeme_queries(
    language: str | None = None,
    data_type: str | None = None,
    contracts_dir: Path | None = DATA_CONTRACTS_DIR,
    output_dir: Path | None = WIKIDATA_QUERIES_DIR,
) -> str | None:
    """
    Generate Wikidata SPARQL queries to derive data based on Scribe-Data data contract values.

    Parameters
    ----------
    language : str | None, optional
        The language to generate Wikidata queries for.

    data_type : str | None, optional
        The type of data to generate queries for (e.g. 'nouns', 'verbs').

    contracts_dir : Path, optional, default=DATA_CONTRACTS_DIR
        Directory containing the contracts to generate queries from.

    output_dir : Path, optional, default=WIKIDATA_QUERIES_DIR
        The directory to save the downloaded file.

    Returns
    -------
    str | None
        Path to the generated query file.

    Notes
    -----
    - Generates query files combining all forms for a given language depending on contract values.
    - Query files are named incrementally if duplicates exist.
    - Creates necessary directories if they don't exist.
    """
    # MARK: Resolve Arguments

    if language:
        language_isos = [get_language_iso(language=language)]

    else:
        language_isos = sorted(
            [
                f.stem
                for f in DATA_CONTRACTS_DIR.iterdir()
                if f.is_file() and str(f).endswith(".yaml")
            ]
        )

    print(language_isos)

    sub_language_isos = []
    for v in sub_languages.values():
        sub_language_isos.extend(iter(v.keys()))

    # Filter for those data types that we get from Wikidata and thus have a QID.
    all_data_types = [dt for dt in data_type_metadata.keys() if data_type_metadata[dt]]

    contract_values_dict = {}
    for lang_iso in language_isos:
        # MARK: Load Contracts

        with open(DATA_CONTRACTS_DIR / f"{lang_iso}.yaml", "r") as file:
            contract_text = yaml.safe_load(file)

        if data_type:
            all_data_types = [data_type]  # replace for now
            assert data_type in all_data_types, (
                f"{data_type} is not a valid Scribe-Data data type."
            )
            contract_values_dict[data_type] = extract_data_contract_values(
                contract_entry=contract_text[data_type]
            )

        else:
            for d in all_data_types:
                if not data_type and d in contract_text:
                    contract_values_dict[d] = extract_data_contract_values(
                        contract_entry=contract_text[d]
                    )

        # MARK: Language Fields

        lang_name = get_language_from_iso(iso=lang_iso).lower()
        sub_lang_name = ""
        sub_lang_qid = ""
        if lang_name in language_metadata:
            lang_qid = language_metadata[lang_name]["qid"]

        elif lang_iso in sub_language_isos:
            for parent_language in sub_languages.keys():
                if lang_iso in sub_languages[parent_language].keys():
                    lang_name = parent_language
                    lang_qid = language_metadata[parent_language]["qid"]
                    sub_lang_name = sub_languages[parent_language][lang_iso]["name"]
                    sub_lang_qid = sub_languages[parent_language][lang_iso]["qid"]

        else:
            raise ValueError(f"{language} is not a valid Scribe-Data language.")

        # Determine which language name and QID to use in comments.
        if sub_lang_name:
            comment_language_name = sub_lang_name.capitalize() if sub_lang_name else ""
            comment_language_qid = sub_lang_qid

        else:
            comment_language_name = language.capitalize() if language else ""
            comment_language_qid = lang_qid

        for dt, contract_values in contract_values_dict.items():
            dt_qid = data_type_metadata[dt]
            query_dt_label = dt.replace("_", "")[:-1]

            # MARK: Get QIDs

            # Create a label to QID mappings from the metadata.
            label_to_qid = {}
            for category in lexeme_form_metadata.values():
                for element in category.values():
                    label_to_qid[element["label"]] = element["qid"]

            grouped_form_labels = split_lexeme_forms_by_identifier(
                language_entry={lang_qid: {dt_qid: contract_values}}
            )

            # Convert contracts to their Wikidata QIDs.
            contract_values_to_qids = []
            grouped_and_ordered_form_labels = []
            for lbls in grouped_form_labels:
                sub_list = []
                for cv in lbls:
                    cv = cv[0].upper() + cv[1:]
                    for lbl, qid in label_to_qid.items():
                        cv = cv.replace(lbl, qid)

                    sub_list.append(re.findall(r"Q[^Q]+", cv))

                sorted_qids = sort_qids_by_position(nested_qids=sub_list)
                contract_values_to_qids.append(sorted_qids)
                grouped_and_ordered_form_labels.append(
                    [lbls[i] for i in [sub_list.index(q) for q in sorted_qids]]
                )

            for j in range(len(grouped_and_ordered_form_labels)):
                forms_for_query = [
                    {
                        "label": grouped_and_ordered_form_labels[j][k],
                        "qids": contract_values_to_qids[j][k],
                    }
                    for k in range(len(grouped_and_ordered_form_labels[j]))
                ]

                # MARK: Generate Query

                main_body = f"""# tool: scribe-data
# All {comment_language_name} ({comment_language_qid}) {dt} ({dt_qid}) and the given forms.
# Enter this query at https://query.wikidata.org/.

SELECT
  (replace(str(?lexeme), "http://www.wikidata.org/entity/", "") AS ?lexemeID)
  ?lastModified
  ?{query_dt_label}
  """ + "\n  ".join(f"?{form}" for form in grouped_and_ordered_form_labels[j])

                where_clause = f"""\n
WHERE {{
  ?lexeme dct:language wd:{lang_qid};
    wikibase:lexicalCategory wd:{dt_qid};
    wikibase:lemma ?{query_dt_label};
    schema:dateModified ?lastModified.
"""

                if sub_lang_name:
                    where_clause += f"""
# Note: We need to filter for {lang_iso} to remove {sub_lang_name} ({lang_iso}) words.
FILTER(lang(?{query_dt_label}) = "{lang_iso}")
"""

                # Generate OPTIONAL clauses for all forms in one query.
                optional_clauses = ""

                # Note: We add gender explicitly for nouns as it's a property (PID).
                if "gender" in contract_values:
                    forms_for_query = [
                        f for f in forms_for_query if "gender" not in f.values()
                    ]
                    optional_clauses += """
  OPTIONAL {
    ?lexeme wdt:P5185 ?nounGender.
  }
"""

                for form in forms_for_query:
                    qids = ", ".join(f"wd:{qid}" for qid in form["qids"])
                    optional_clauses += f"""
  OPTIONAL {{
    ?lexeme ontolex:lexicalForm ?{form["label"]}Form.
    ?{form["label"]}Form ontolex:representation ?{form["label"]};
    wikibase:grammaticalFeature {qids}.
  }}
"""

                if "gender" in contract_values:
                    optional_clauses += """
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en".
    ?nounGender rdfs:label ?gender.
  }
"""

                # Concatenate the complete query.
                final_query = main_body + where_clause + optional_clauses + "}\n"
                # print(final_query)

                # MARK: Save Query

                # Create base filename.
                # If this is a sub-language, place it under parent_language/sub_language/data_type/.
                # Otherwise, place it directly under language/data_type/.
                if sub_lang_name:
                    if output_dir:
                        base_file_name = (
                            output_dir
                            / parent_language.lower()
                            / sub_lang_name.lower()
                            / dt
                            / f"query_{dt}.sparql"
                        )

                    else:
                        base_file_name = (
                            Path(WIKIDATA_QUERIES_DIR)
                            / parent_language.lower()
                            / sub_lang_name.lower()
                            / dt
                            / f"query_{dt}.sparql"
                        )

                else:
                    if output_dir:
                        # Regular language with query_dir specified.
                        base_file_name = (
                            output_dir / lang_name / dt / f"query_{dt}.sparql"
                        )

                    else:
                        # Regular language with default directory.
                        base_file_name = (
                            Path(WIKIDATA_QUERIES_DIR)
                            / lang_name
                            / dt
                            / f"query_{dt}.sparql"
                        )

                # Get the next available filename.
                file_to_save_name = get_next_query_filename(str(base_file_name))

                # Create directory if it doesn't exist.
                os.makedirs(os.path.dirname(file_to_save_name), exist_ok=True)

                # Write query to file.
                with open(file_to_save_name, "w") as file:
                    file.write(final_query)

                print(f"Query file created: {file_to_save_name}")
