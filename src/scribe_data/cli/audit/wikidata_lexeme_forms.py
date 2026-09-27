# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to audit Wikidata lexeme forms.

This functionality creates a YAML report with the following information:
- QID combinations for Wikidata lexeme forms
- The Scribe-Data labels for each of these forms (for use in contracts)
- The number of instances of each form combination (results are ordered by decreasing number of instances)
"""

import time
from pathlib import Path
from typing import Any, cast

import yaml

from scribe_data.cli.generate.generate_utils import sort_qids_by_position
from scribe_data.utils import (
    DEFAULT_AUDIT_RESULTS_DIR,
    SCRIBE_DATA_USER_QUERIES_DIR,
    data_type_metadata,
    language_metadata,
    lexeme_form_metadata,
)
from scribe_data.wikidata.wikidata_utils import sparql

DEFAULT_COMPLEX_DATA_TYPE_FREQUENCY = 50
DEFAULT_MODERATE_DATA_TYPE_FREQUENCY = 15
DEFAULT_SIMPLE_DATA_TYPE_FREQUENCY = 5


def execute_sparql_query(query: str, max_attempts: int = 2) -> list | None:
    """
    Execute a SPARQL query against Wikidata with retry logic and rate limiting.

    Parameters
    ----------
    query : str
        The SPARQL query to execute.

    max_attempts : int, optional, default=2
        The maximum attempts of the Wikidata audit process.

    Returns
    -------
    list | None
        List of query results on success, None if query fails after all retries.
    """
    RETRY_DELAY = 2

    for attempt in range(max_attempts):
        try:
            # Add delay to avoid overwhelming the service.
            if attempt > 0:
                print(
                    f"Retry attempt {attempt}/{max_attempts} after {RETRY_DELAY}s delay..."
                )
                time.sleep(RETRY_DELAY * attempt)

            sparql.setQuery(query)
            results = sparql.query().convert()
            res_dict = cast(dict[str, Any], results)
            return res_dict.get("results", {}).get("bindings", [])

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                print(f"Rate limited (attempt {attempt + 1}/{max_attempts + 1})")
                if attempt < max_attempts:
                    time.sleep(
                        RETRY_DELAY * (attempt + 1) * 2
                    )  # longer delay for rate limits
                    continue

            elif "504" in error_msg or "Gateway Timeout" in error_msg:
                print(f"Query timeout (attempt {attempt + 1}/{max_attempts + 1})")
                if attempt < max_attempts:
                    time.sleep(RETRY_DELAY)
                    continue

            else:
                print(f"SPARQL query failed: {e}")
                if attempt < max_attempts:
                    time.sleep(RETRY_DELAY)
                    continue

    print(f"Failed after {max_attempts + 1} attempts")

    return


def generate_fallback_lexeme_query(
    language: str,
    data_type: str,
    language_qid: str,
    data_type_qid: str,
) -> None:
    """
    Generate a simple lexeme exploration query when the feature combination query fails.

    This generates a basic query that returns all lexeme IDs and lemmas for
    the given language and data type, for manual exploration when the data
    quality is too poor to generate feature combination queries.

    Parameters
    ----------
    language : str
        Human-readable language name (e.g., "arabic").

    data_type : str
        Human-readable data type name (e.g., "verbs").

    language_qid : str
        The Wikidata QID for the language (e.g., "Q13955" for Arabic).

    data_type_qid : str
        The Wikidata QID for the data type (e.g., "Q24905" for verbs).
    """
    fallback_query = f"""# tool: scribe-data
# The Scribe-Data form combination audit query failed for this language and data type combination.
# The following query returns all lexemes and their lemmas for the language and data type for further exploration.

SELECT
  (replace(str(?lexeme), "http://www.wikidata.org/entity/", "") AS ?lexemeID)
  ?lemma

WHERE {{{{
  ?lexeme a ontolex:LexicalEntry.
  ?lexeme dct:language wd:{language_qid};
    wikibase:lexicalCategory wd:{data_type_qid};
    wikibase:lemma ?lemma.
}}}}
"""
    # Save to queries directory.
    output_path = (
        SCRIBE_DATA_USER_QUERIES_DIR
        / language
        / data_type
        / f"query_{data_type}.sparql"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(fallback_query)

    print(f"Generated fallback query: {output_path}")

    return


def audit_wikidata_lexeme_forms(
    language: str,
    data_type: str,
    min_frequency: int = 0,
    max_results: int = 1000,
    max_attempts: int = 2,
) -> None:
    """
    Audit Wikidata to see the available forms for the given language and data type(s).

    Parameters
    ----------
    language : str
        The language to Audit Wikidata for.

    data_type : str
        The data type to Audit Wikidata for.

    min_frequency : int, optional, default=0
        Minimum frequency threshold for including form combinations.

    max_results : int, optional, default=1000
        Maximum number of results to return.
        Helps prevent timeout for very large datasets.

    max_attempts : int, optional, default=2
        The maximum attempts of the Wikidata audit process.
    """
    print(f"Auditing Wikidata lexeme forms for {language.capitalize()} {data_type}.")
    language_qid = language_metadata[language]["qid"]
    data_type_qid = data_type_metadata[data_type]

    template_path = Path(__file__).parent / "lexeme_form_combinations.sparql"
    with open(template_path, "r", encoding="utf-8") as f:
        lexeme_form_combinations_query = f.read()

    if min_frequency == 0:
        complex_types = ["Q1084", "Q24905"]  # nouns, verbs
        adjective_types = ["Q34698"]  # adjectives

        if data_type_qid in complex_types:
            min_frequency = DEFAULT_COMPLEX_DATA_TYPE_FREQUENCY

        elif data_type_qid in adjective_types:
            min_frequency = DEFAULT_MODERATE_DATA_TYPE_FREQUENCY

        else:
            min_frequency = DEFAULT_SIMPLE_DATA_TYPE_FREQUENCY

    else:
        min_frequency = min_frequency

    query = (
        lexeme_form_combinations_query.replace("LANGUAGE_QID", language_qid)
        .replace("DATA_TYPE_QID", data_type_qid)
        .replace("MIN_FREQUENCY", str(min_frequency))
        .replace("MAX_RESULTS", str(max_results))
    )

    results = execute_sparql_query(query=query, max_attempts=max_attempts)

    if results is None:
        print(
            f"Feature combination query failed for {language.capitalize()} {data_type}."
        )
        print(
            "This indicates data quality issues. Generating fallback lexeme listing query instead."
        )
        generate_fallback_lexeme_query(
            language=language,
            data_type=data_type,
            language_qid=language_qid,
            data_type_qid=data_type_qid,
        )

        return

    # Query succeeded but returned no results - no combinations meet threshold.
    if not results:
        print(
            f"Data quality insufficient. No combinations meet threshold {min_frequency}."
        )
        print("Generating fallback lexeme listing query for manual exploration.")
        generate_fallback_lexeme_query(
            language=language,
            data_type=data_type,
            language_qid=language_qid,
            data_type_qid=data_type_qid,
        )

        return

    form_combinations = {}
    for result in results:
        form_qids = result.get("formQIDs", {}).get("value", "").split(" ")
        sorted_form_qids = sort_qids_by_position([form_qids])[0] or []
        form_qids_label_str = "".join(sorted_form_qids)

        form_label = form_qids_label_str
        for category in lexeme_form_metadata.values():
            for element in category.values():
                form_label = form_label.replace(element["qid"], element["label"])

        total_forms = int(result.get("totalForms", {}).get("value", 0))

        form_combinations[form_label] = {
            "qids": form_qids,
            "total_forms": total_forms,
        }

    audit_file = (
        DEFAULT_AUDIT_RESULTS_DIR / language / data_type / "lexeme_forms_audit.yaml"
    )
    audit_file.parent.mkdir(parents=True, exist_ok=True)
    with open(audit_file, "w") as file:
        yaml.dump(
            dict(
                sorted(
                    form_combinations.items(),
                    key=lambda item: item[1].get("total_forms", 0),
                    reverse=True,
                )
            ),
            file,
            sort_keys=False,
        )

    print(f"Wikidata lexeme form audit results saved to {str(audit_file)}.")
