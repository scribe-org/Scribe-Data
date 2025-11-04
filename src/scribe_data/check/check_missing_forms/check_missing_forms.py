# SPDX-License-Identifier: GPL-3.0-or-later
"""
Check for missing forms in Wikidata using live SPARQL service.
"""

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

from scribe_data.check.check_missing_forms.split_query import split_group_by_identifier

from scribe_data.utils import (
    LANGUAGE_DATA_EXTRACTION_DIR,
    data_type_metadata,
    language_metadata,
    lexeme_form_metadata,
    sub_languages,
)
from scribe_data.wikidata.wikidata_utils import sparql


def load_sparql_template():
    """
    Load the universal SPARQL query template from file.

    Returns
    -------
    str
        The template string with placeholders for LANGUAGE_QID and DATA_TYPE_QID.
    """
    template_path = Path(__file__).parent / "query_form_combinations.sparql"
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def execute_sparql_query(query, max_retries=3):
    """
    Execute a SPARQL query against Wikidata with retry logic and rate limiting.

    Parameters
    ----------
    query : str
        The SPARQL query to execute.
    max_retries : int, optional
        Maximum number of retry attempts (default: 3).

    Returns
    -------
    list or None
        List of query results on success, None if query fails after all retries.
    """
    RETRY_DELAY = 2  # Fixed delay in seconds between retry attempts
    
    for attempt in range(max_retries + 1):
        try:
            # Add delay to avoid overwhelming the service
            if attempt > 0:
                print(f"Retry attempt {attempt}/{max_retries} after {RETRY_DELAY}s delay...")
                time.sleep(RETRY_DELAY * attempt)

            sparql.setQuery(query)
            results = sparql.query().convert()
            return results.get("results", {}).get("bindings", [])

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                print(f"Rate limited (attempt {attempt + 1}/{max_retries + 1})")
                if attempt < max_retries:
                    time.sleep(
                        RETRY_DELAY * (attempt + 1) * 2
                    )  # Longer delay for rate limits
                    continue
            elif "504" in error_msg or "Gateway Timeout" in error_msg:
                print(f"Query timeout (attempt {attempt + 1}/{max_retries + 1})")
                if attempt < max_retries:
                    time.sleep(RETRY_DELAY)
                    continue
            else:
                print(f"SPARQL query failed: {e}")
                if attempt < max_retries:
                    time.sleep(RETRY_DELAY)
                    continue

    print(f"Failed after {max_retries + 1} attempts")
    return None


def generate_fallback_lexeme_query(language_qid, data_type_qid, language_name, data_type_name):
    """
    Generate a simple lexeme listing query when feature combination query fails.
    
    This generates a basic query that returns all lexeme IDs and lemmas for 
    the given language and data type, for manual exploration when the data 
    quality is too poor to generate feature combination queries.
    
    Parameters
    ----------
    language_qid : str
        The Wikidata QID for the language (e.g., "Q13955" for Arabic).
    
    data_type_qid : str
        The Wikidata QID for the data type (e.g., "Q24905" for verbs).
    
    language_name : str
        Human-readable language name (e.g., "arabic").
    
    data_type_name : str
        Human-readable data type name (e.g., "verbs").
    
    Returns
    -------
    Path
        Path to the generated fallback query file.
    """
    fallback_query = f'''# tool: scribe-data
# Note: The Scribe-Data form combination derivation query failed for this language and data type combination.
# Note: The following query returns all lexemes and their lemmas for the language and data type for further exploration.

SELECT
  (REPLACE(STR(?lexeme), "http://www.wikidata.org/entity/", "") AS ?lexemeID)
  ?lemma

WHERE {{{{
  ?lexeme a ontolex:LexicalEntry .
  ?lexeme dct:language wd:{language_qid} ;
    wikibase:lexicalCategory wd:{data_type_qid} ;
    wikibase:lemma ?lemma .
}}}}
'''
    # Save to language_data_extraction directory
    output_path = LANGUAGE_DATA_EXTRACTION_DIR / language_name / data_type_name / f"query_{data_type_name}.sparql"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(fallback_query)
    
    return output_path

def get_forms_from_sparql_service(language_qid, data_type_qid, frequency_threshold=0, max_results=1000, language_name=None, data_type_name=None):
    """
    Get form combinations for a language/data type pair from live SPARQL service.

    Parameters
    ----------
    language_qid : str
        The Wikidata QID for the language (e.g., "Q1860" for English).

    data_type_qid : str
        The Wikidata QID for the data type (e.g., "Q1084" for nouns).

    frequency_threshold : int, optional
        Minimum frequency threshold for including form combinations.
        Default is 0 (include all combinations).

    max_results : int, optional
        Maximum number of results to return (default: 1000).
        Helps prevent timeout for very large datasets.
    
    language_name : str, optional
        Human-readable language name for fallback query generation.
    
    data_type_name : str, optional
        Human-readable data type name for fallback query generation.

    Returns
    -------
    list or str
        List of form combinations (each is a list of QIDs) on success,
        or "FALLBACK_GENERATED" string if fallback query was generated due to data quality issues.
    """
    template = load_sparql_template()

    if frequency_threshold == 0:
        complex_types = ["Q1084", "Q24905"]  # nouns, verbs
        adjective_types = ["Q34698"]  # adjectives

        if data_type_qid in complex_types:
            min_frequency = 50
        elif data_type_qid in adjective_types:
            min_frequency = 15
        else:
            min_frequency = 5
    else:
        min_frequency = frequency_threshold

    query = template.format(
        LANGUAGE_QID=language_qid,
        DATA_TYPE_QID=data_type_qid,
        MIN_FREQUENCY=min_frequency,
        MAX_RESULTS=max_results,
    )

    results = execute_sparql_query(query)
    
    if results is None:
        print(f"Feature combination query failed for {language_name or language_qid} - {data_type_name or data_type_qid}")
        print(f"This indicates data quality issues - generating fallback lexeme listing query instead")
        
        if language_name and data_type_name:
            fallback_path = generate_fallback_lexeme_query(
                language_qid, data_type_qid, language_name, data_type_name
            )
            print(f"Generated fallback query: {fallback_path}")
        else:
            print(f"Cannot generate fallback query - missing language/data type names")
        
        return "FALLBACK_GENERATED"
    
    # Query succeeded but returned no results - no combinations meet threshold
    if not results:
        print(f"Data quality insufficient - no combinations meet threshold {min_frequency}")
        print(f"Generating fallback lexeme listing query for manual exploration")
        
        if language_name and data_type_name:
            fallback_path = generate_fallback_lexeme_query(
                language_qid, data_type_qid, language_name, data_type_name
            )
            print(f"Generated fallback query: {fallback_path}")
        else:
            print(f"Cannot generate fallback query - missing language/data type names")
        
        return "FALLBACK_GENERATED"

    form_combinations = []
    for result in results:
        frequency = int(result.get("formsWithThisCombo", {}).get("value", 0))

        combo_qids_str = result.get("comboQIDs", {}).get("value", "")
        if combo_qids_str:
            qids = [qid.strip() for qid in combo_qids_str.split() if qid.strip()]

            if qids and frequency >= min_frequency:
                form_combinations.append(qids)

    return form_combinations


def get_forms_from_sparql_service_all_languages(
    frequency_threshold=0, max_results=1000
):
    """
    Get form combinations for all languages and data types from SPARQL service.

    Parameters
    ----------
    frequency_threshold : int, optional
        Minimum frequency threshold for including form combinations.
        Default is 0 (include all combinations).

    max_results : int, optional
        Maximum results per query to prevent timeouts (default: 1000).

    Returns
    -------
    dict
        Dictionary with structure: {language_qid: {data_type_qid: [form_combinations]}}.
    """
    result_sparql_service = defaultdict(lambda: defaultdict(list))

    # Get all language QIDs and track parent QIDs for sub-languages
    language_qids = {}
    parent_qids = {}  # Maps sub-language QID to parent QID for fallback
    
    for lang, lang_data in language_metadata.items():
        if "qid" in lang_data:
            language_qids[lang_data["qid"]] = lang
        if "sub_languages" in lang_data:
            parent_qid = lang_data.get("qid")  # Get parent QID if exists
            for sub_lang, sub_data in lang_data["sub_languages"].items():
                if "qid" in sub_data:
                    sub_lang_qid = sub_data["qid"]
                    language_qids[sub_lang_qid] = sub_lang
                    # Store parent QID for fallback (only if parent exists and differs from sub-language)
                    if parent_qid and parent_qid != sub_lang_qid:
                        parent_qids[sub_lang_qid] = parent_qid

    data_type_qids = {}
    for data_type, qid in data_type_metadata.items():
        if qid and qid.startswith("Q"):  # Skip empty values and ensure it's a QID
            data_type_qids[qid] = data_type

    # Query each language/data type combination
    total_combinations = len(language_qids) * len(data_type_qids)
    current = 0

    print(f"Processing {len(language_qids)} languages * {len(data_type_qids)} data types = {total_combinations} combinations")

    for lang_qid in language_qids:
        for dt_qid in data_type_qids:
            current += 1
            lang_name = language_qids[lang_qid]
            dt_name = data_type_qids[dt_qid]
            
            print(f"Processing {current}/{total_combinations}: {lang_name} - {dt_name} ({lang_qid}, {dt_qid})")

            forms = get_forms_from_sparql_service(lang_qid, dt_qid, frequency_threshold, max_results, lang_name, dt_name)
            
            if not forms and lang_qid in parent_qids:
                parent_qid = parent_qids[lang_qid]
                print(f"No data for sub-language, trying parent QID {parent_qid} with threshold=10...")
                forms = get_forms_from_sparql_service(parent_qid, dt_qid, frequency_threshold=10, max_results=max_results, language_name=lang_name, data_type_name=dt_name)
                if forms and forms != "FALLBACK_GENERATED":
                    print(f"Found {len(forms)} form combinations from parent language")
            
            if forms == "FALLBACK_GENERATED":
                result_sparql_service[lang_qid][dt_qid] = "FALLBACK_GENERATED"
            elif forms:
                result_sparql_service[lang_qid][dt_qid] = forms
                print(f"Found {len(forms)} form combinations")
            else:
                print("No combinations found")
            if current < total_combinations:
                time.sleep(1)

    return dict(result_sparql_service)


def get_features_from_sparql_service(frequency_threshold=0, max_results=1000):
    """
    Get all form combinations from live SPARQL service (new approach).

    Parameters
    ----------
    frequency_threshold : int, optional
        Minimum frequency threshold for including form combinations.
        Default is 0 (include all combinations).

    max_results : int, optional
        Maximum results per query to prevent timeouts (default: 1000).

    Returns
    -------
    dict or None
        Dictionary of form combinations by language and data type if any found,
        otherwise None.
        Format: {language_qid: {data_type_qid: [form_combinations]}}.

    Notes
    -----
    This function replaces the dump-based approach with live SPARQL queries.
    It directly queries Wikidata for all form combinations available for each
    language/data type pair.
    """
    print("Using SPARQL service approach to get form combinations...")

    # Get all form combinations from SPARQL service
    all_features = get_forms_from_sparql_service_all_languages(frequency_threshold, max_results)

    if not all_features:
        print("No form combinations found from SPARQL service.")
        return None

    # Apply additional filtering based on valid QIDs from metadata
    all_qids = set()
    for category, items in lexeme_form_metadata.items():
        for key, value in items.items():
            if "qid" in value:
                all_qids.add(value["qid"])

    # Filter to only include combinations with valid QIDs
    filtered_features = defaultdict(lambda: defaultdict(list))
    for lang_qid, data_types in all_features.items():
        for dt_qid, combinations in data_types.items():
            for combination in combinations:
                if all(qid in all_qids for qid in combination):
                    filtered_features[lang_qid][dt_qid].append(combination)

    return dict(filtered_features) if filtered_features else None


def process_missing_features(missing_features, query_dir):
    """
    Generate SPARQL queries for missing features by language and data type.

    Parameters
    ----------
    missing_features : dict
        Dictionary of missing features by language and data type.
        Format: {language: {data_type: [features] or "FALLBACK_GENERATED"}}.

    query_dir : str or Path
        Directory where generated query files should be saved.

    Notes
    -----
    Generates separate queries for each data type within each language.
    Skips combinations where fallback queries were already generated.
    """
    if not missing_features:
        return
    sub_languages_iso_codes = {}
    for language, sub_langs in sub_languages.items():
        # Get all unique QIDs and their ISO codes for this language.
        qid_to_isos = {}
        for iso_code, sub_lang_data in sub_langs.items():
            qid = sub_lang_data["qid"]
            if qid not in qid_to_isos:
                qid_to_isos[qid] = set()
            qid_to_isos[qid].add(iso_code)

        # Add to main dictionary.
        sub_languages_iso_codes |= qid_to_isos

    for language_qid, data_types_qid in missing_features.items():
        try:
            print(f"Processing language: {language_qid}")
            print(f"Data types: {list(data_types_qid.keys())}")

            # Create a separate entry for each data type.
            for data_type_qid, features in data_types_qid.items():
                # Skip if fallback was generated (data quality issue)
                if features == "FALLBACK_GENERATED":
                    print(f"Skipping {language_qid} - {data_type_qid} (fallback query already generated due to data quality)")
                    continue
                
                # Skip if no features found
                if not features:
                    print(f"Skipping {language_qid} - {data_type_qid} (no features found)")
                    continue
                
                language_entry = {language_qid: {data_type_qid: features}}
                if language_qid in sub_languages_iso_codes:
                    # For macro-languages, generate a separate set of files
                    # for each sub-language, each with a specific filter.
                    for sub_lang_iso_code in sub_languages_iso_codes[language_qid]:
                        print(
                            f"Generating query for {language_qid} - {data_type_qid} - {sub_lang_iso_code}"
                        )
                        split_group_by_identifier(
                            language_entry,
                            LANGUAGE_DATA_EXTRACTION_DIR,
                            sub_lang_iso_code,
                        )
                else:
                    print(f"Generating query for {language_qid} - {data_type_qid}")
                    split_group_by_identifier(
                        language_entry,
                        LANGUAGE_DATA_EXTRACTION_DIR,
                        sub_lang_iso_code=None,
                    )

        except (ValueError, KeyError) as e:
            print(f"Skipping language {language_qid} due to error: {e}")
            continue


def main():
    """
    Main function to check for missing forms in Wikidata using SPARQL service.

    Processes command line arguments and uses the SPARQL service approach to 
    identify form combinations and generate appropriate SPARQL queries.

    Notes
    -----
    Command line arguments:
    - query_dir: Directory for storing generated queries (optional)
    - --frequency-threshold: Minimum frequency for including form combinations
    - --request-delay: Delay in seconds between SPARQL requests
    - --max-retries: Maximum retry attempts for failed queries
    - --max-results: Maximum results per query to prevent timeouts
    """
    parser = argparse.ArgumentParser(description="Check missing forms in Wikidata using SPARQL service")

    parser.add_argument(
        "--frequency-threshold",
        type=int,
        default=0,
        help="Minimum frequency threshold for form combinations (default: 0 = use adaptive thresholds)",
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=1.0,
        help="Delay in seconds between SPARQL requests (default: 1.0, increase if getting rate limited)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts for failed queries (default: 3)",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=1000,
        help="Maximum results per query to prevent timeouts (default: 1000, decrease for complex languages)",
    )
    parser.add_argument(
        "query_dir", 
        type=str, 
        nargs='?',
        default=None,
        help="Path to the query directory (optional, defaults to language_data_extraction in wikidata folder)"
    )

    args = parser.parse_args()
    
    # Use language_data_extraction directory by default
    if args.query_dir:
        query_dir = Path(args.query_dir)
        if not query_dir.exists():
            print(f"Error: Query directory does not exist: {query_dir}")
            sys.exit(1)
    else:
        query_dir = LANGUAGE_DATA_EXTRACTION_DIR
        query_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Query output directory: {query_dir}")
    print("Using SPARQL service approach...")
    print(f"Frequency threshold: {args.frequency_threshold} (0 = use adaptive thresholds)")
    print(f"Request delay: {args.request_delay}s (increase if getting rate limited)")
    print(f"Max retries: {args.max_retries}")
    print(f"Max results per query: {args.max_results}")

    # Get form combinations from SPARQL service
    form_combinations = get_features_from_sparql_service(
        args.frequency_threshold, args.max_results
    )

    if form_combinations:
        print(f"Found form combinations for {len(form_combinations)} languages")
        with open("query_check_sparql_service_features.json", "w") as f:
            json.dump(form_combinations, f, indent=4)
        print("Form combinations saved to query_check_sparql_service_features.json")

        process_missing_features(form_combinations, query_dir)
        print("Query generation complete!")
    else:
        print("No form combinations found from SPARQL service.")


if __name__ == "__main__":
    main()
