# SPDX-License-Identifier: GPL-3.0-or-later
"""
Check for missing forms in Wikidata and download Wikidata lexeme dump.

Examples
--------
>>> python3 src/scribe_data/check/check_missing_forms/check_missing_forms.py
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from get_forms import extract_dump_forms, parse_sparql_files
from normalize_forms import sort_qids_in_list
from split_query import split_group_by_identifier

from scribe_data.cli.download import wd_lexeme_dump_download_wrapper
from scribe_data.utils import (
    LANGUAGE_DATA_EXTRACTION_DIR,
    data_type_metadata,
    language_metadata,
    lexeme_form_metadata,
    sub_languages,
)
from scribe_data.wikidata.wikidata_utils import sparql


def get_all_languages():
    """
    Extract all languages and sub languages from language metadata.

    Returns
    -------
    list of str
        List of language codes for all languages and sub languages that have
        both ISO codes and QIDs defined.

    Notes
    -----
    Only includes languages and sub languages that have both 'iso' and 'qid'
    fields in their metadata.
    """
    languages = []

    for lang, lang_data in language_metadata.items():
        # Add main language if it has ISO and QID.
        if "iso" in lang_data and "qid" in lang_data:
            languages.append(lang)

        # Add sub languages.
        if "sub_languages" in lang_data:
            languages.extend(
                sublang
                for sublang, sublang_data in lang_data["sub_languages"].items()
                if "iso" in sublang_data and "qid" in sublang_data
            )

    return languages


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


def execute_sparql_query(query):
    """
    Execute a SPARQL query against Wikidata and return results.

    Parameters
    ----------
    query : str
        The SPARQL query to execute.

    Returns
    -------
    list
        List of query results, or empty list if query fails.
    """
    try:
        sparql.setQuery(query)
        results = sparql.query().convert()
        return results.get("results", {}).get("bindings", [])
    except Exception as e:
        print(f"SPARQL query failed: {e}")
        return []


def get_forms_from_sparql_service(language_qid, data_type_qid, frequency_threshold=0):
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

    Returns
    -------
    list
        List of form combinations, where each combination is a list of QIDs.
    """
    template = load_sparql_template()
    query = template.format(LANGUAGE_QID=language_qid, DATA_TYPE_QID=data_type_qid)

    results = execute_sparql_query(query)

    form_combinations = []
    for result in results:
        # Parse frequency
        frequency = int(result.get("frequency", {}).get("value", 0))

        # Skip if below threshold
        if frequency < frequency_threshold:
            continue

        # Parse feature combinations
        features_str = result.get("features", {}).get("value", "")
        if features_str:
            # Extract QIDs from feature URIs
            qids = []
            for feature_uri in features_str.split("|"):
                if feature_uri.startswith("http://www.wikidata.org/entity/"):
                    qid = feature_uri.replace("http://www.wikidata.org/entity/", "")
                    qids.append(qid)

            if qids:
                form_combinations.append(qids)

    return form_combinations


def get_forms_from_sparql_service_all_languages(frequency_threshold=0):
    """
    Get form combinations for all languages and data types from SPARQL service.

    Parameters
    ----------
    frequency_threshold : int, optional
        Minimum frequency threshold for including form combinations.
        Default is 0 (include all combinations).

    Returns
    -------
    dict
        Dictionary with structure: {language_qid: {data_type_qid: [form_combinations]}}.
    """
    result_sparql_service = defaultdict(lambda: defaultdict(list))

    # Get all language QIDs
    language_qids = {}
    for lang, lang_data in language_metadata.items():
        if "qid" in lang_data:
            language_qids[lang_data["qid"]] = lang

    # Get all data type QIDs
    data_type_qids = {}
    for data_type, data_type_data in data_type_metadata.items():
        if "qid" in data_type_data:
            data_type_qids[data_type_data["qid"]] = data_type

    # Query each language/data type combination
    total_combinations = len(language_qids) * len(data_type_qids)
    current = 0

    for lang_qid in language_qids:
        for dt_qid in data_type_qids:
            current += 1
            print(
                f"Processing {current}/{total_combinations}: {language_qids[lang_qid]} - {data_type_qids[dt_qid]}"
            )

            forms = get_forms_from_sparql_service(lang_qid, dt_qid, frequency_threshold)
            if forms:
                result_sparql_service[lang_qid][dt_qid] = forms

    return dict(result_sparql_service)


def get_features_from_sparql_service(frequency_threshold=0):
    """
    Get all form combinations from live SPARQL service (new approach).

    Parameters
    ----------
    frequency_threshold : int, optional
        Minimum frequency threshold for including form combinations.
        Default is 0 (include all combinations).

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
    print("Using new SPARQL service approach to get form combinations...")
    
    # Get all form combinations from SPARQL service
    all_features = get_forms_from_sparql_service_all_languages(frequency_threshold)
    
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


def get_missing_features(result_sparql, result_dump):
    """
    Compare features between SPARQL results and dump data to find missing ones.

    Parameters
    ----------
    result_sparql : dict
        Features extracted from SPARQL queries.
        Format: {language: {data_type: [features]}}.

    result_dump : dict
        Features extracted from Wikidata dump.
        Format: {language: {data_type: [features]}}.

    Returns
    -------
    dict or None
        Dictionary of missing features by language and data type if any found,
        otherwise None.
        Format: {language: {data_type: [missing_features]}}.

    Notes
    -----
    Only includes features that have valid QIDs present in lexeme_form_metadata.
    """
    missing_by_lang_type = defaultdict(lambda: defaultdict(list))

    # Extract all QIDs from the metadata.
    all_qids = set()
    for category, items in lexeme_form_metadata.items():
        for key, value in items.items():
            all_qids.add(value["qid"])

    # Compare features for each language and data type.
    all_languages = set(result_sparql.keys()) | set(result_dump.keys())
    for lang in all_languages:
        # Get data for the current language, with empty dict as default.
        sparql_data = result_sparql.get(lang, {})
        dump_data = result_dump.get(lang, {})

        all_data_types = set(sparql_data.keys()) | set(dump_data.keys())

        for dt in all_data_types:
            # Get values from SPARQL if available.
            sparql_values = {tuple(item) for item in sparql_data.get(dt, [])}

            # Get values from dump if available.
            dump_values = {tuple(item) for item in dump_data.get(dt, [])}

            # Get missing Forms from lexeme Dump.
            unique_dump_values = (
                set(map(tuple, sort_qids_in_list(dump_values))) - sparql_values
            )

            # Store valid missing features from dump.
            for item in unique_dump_values:
                if all(qid in all_qids for qid in item):
                    missing_by_lang_type[lang][dt].append(list(item))

    return missing_by_lang_type or None


def process_missing_features(missing_features, query_dir):
    """
    Generate SPARQL queries for missing features by language and data type.

    Parameters
    ----------
    missing_features : dict
        Dictionary of missing features by language and data type.
        Format: {language: {data_type: [features]}}.

    query_dir : str or Path
        Directory where generated query files should be saved.

    Notes
    -----
    Generates separate queries for each data type within each language.
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
    Main function to check for missing forms in Wikidata.

    Processes command line arguments and uses either the legacy dump-based approach
    or the new SPARQL service approach to identify form combinations and generate
    appropriate SPARQL queries.

    Notes
    -----
    Required command line arguments:
    - query_dir: Directory for storing generated queries

    New SPARQL service approach (recommended):
    - --use-sparql-service: Use live SPARQL service instead of dump comparison
    - --frequency-threshold: Minimum frequency for including form combinations

    Legacy dump-based approach:
    - --dump-path: Path to the Wikidata dump file or None to download
    - --process-all-keys: Flag to process all nested keys in missing features
    - --download-dump: Flag to download the dump if dump_path is not provided
    """
    parser = argparse.ArgumentParser(description="Check missing forms in Wikidata")
    
    # New SPARQL service approach arguments
    parser.add_argument(
        "--use-sparql-service",
        action="store_true",
        help="Use live SPARQL service approach (recommended, replaces dump-based method)"
    )
    parser.add_argument(
        "--frequency-threshold",
        type=int,
        default=0,
        help="Minimum frequency threshold for form combinations (default: 0 = include all)"
    )
    
    # Legacy dump-based approach arguments
    parser.add_argument(
        "--dump-path",
        type=str,
        default=None,
        help="Path to the dump file (legacy approach only)",
    )
    parser.add_argument(
        "--process-all-keys",
        action="store_true",
        help="Process all nested keys in the missing features (legacy approach only)",
    )
    parser.add_argument(
        "--download-dump",
        action="store_true",
        help="Download Wikidata lexeme dump if dump_path is not provided (legacy approach only)",
    )
    
    # Common arguments
    parser.add_argument("query_dir", type=str, help="Path to the query directory")

    args = parser.parse_args()
    query_dir = Path(args.query_dir)

    if not query_dir.exists():
        print(f"Error: Query directory does not exist: {query_dir}")
        sys.exit(1)

    # Use new SPARQL service approach if requested
    if args.use_sparql_service:
        print("Using new SPARQL service approach...")
        
        # MARK: Get Features from SPARQL Service
        form_combinations = get_features_from_sparql_service(args.frequency_threshold)
        
        if form_combinations:
            print(f"Found form combinations for {len(form_combinations)} languages")
            
            # MARK: Save Features
            with open("query_check_sparql_service_features.json", "w") as f:
                json.dump(form_combinations, f, indent=4)
            print("Form combinations saved to query_check_sparql_service_features.json")
            
            # MARK: Process Features
            process_missing_features(form_combinations, query_dir)
        else:
            print("No form combinations found from SPARQL service.")
            
        return

    # Legacy dump-based approach
    print("Using legacy dump-based approach...")
    
    # Existing dump-based logic
    if not args.dump_path and args.download_dump:
        # MARK: Download Dump
        dump_path = wd_lexeme_dump_download_wrapper(
            wikidata_dump=None, output_dir=None, default=True
        )
        if not dump_path:
            print("Failed to download Wikidata dump.")
            sys.exit(1)

    elif not args.dump_path:
        print("Error: Either provide a dump path, use --download-dump flag, or use --use-sparql-service")
        sys.exit(1)

    else:
        dump_path = args.dump_path

    dump_path = Path(dump_path)

    if not dump_path.exists():
        print(f"Error: Dump path does not exist: {dump_path}")
        sys.exit(1)

    # Get all languages including sub languages.
    languages = get_all_languages()

    # MARK: Parse SPARQL

    print("Parsing SPARQL files...")
    result_sparql = parse_sparql_files()

    # MARK: Extract Forms

    print("Extracting Wiki lexeme dump...")
    result_dump = extract_dump_forms(
        languages=languages,
        data_types=list(data_type_metadata.keys()),
        file_path=dump_path,
    )

    # MARK: Get Features

    missing_features = get_missing_features(result_sparql, result_dump)

    try:
        # MARK: Save Features

        print("Generated missing features:", missing_features)

        with open("query_check_missing_features.json", "w") as f:
            json.dump(missing_features, f, indent=4)

        print(
            "Missing features data has been saved to query_check_missing_features.json"
        )

        if missing_features:
            # Process all data types for each language.
            process_missing_features(missing_features, query_dir)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


# Note: Comment out this condition for testing.
if __name__ == "__main__":
    main()


# MARK: Testing

# Note: Please uncomment all lines except MARKs and Notes below for testing.

# MARK: Part 1

# Note: Get forms from all languages including sub languages.

# from scribe_data.utils import DEFAULT_DUMP_EXPORT_DIR

# DUMP_PATH = f"{DEFAULT_DUMP_EXPORT_DIR}/latest-lexemes.json.bz2"

# # Get all languages including sub languages.
# languages = get_all_languages()

# # Parse SPARQL

# print("Parsing SPARQL files...")
# result_sparql = parse_sparql_files()

# # Extract Forms

# print("Extracting Wiki lexeme dump...")
# result_dump = extract_dump_forms(
#     languages=languages,
#     data_types=list(data_type_metadata.keys()),
#     file_path=f"{DUMP_PATH}",  # need to give the path of the dump file.
# )
# with open("query_check_result_dump.json", "w") as f:
#     json.dump(result_dump, f, indent=4)

# with open("query_check_result_sparql.json", "w") as f:
#     json.dump(result_sparql, f, indent=4)

# MARK: Part 2

# Note: Get missing features from SPARQL and dump.

# with open("query_check_result_sparql.json", "r") as f:
#     result_sparql = json.load(f)

# with open("query_check_result_dump.json", "r") as f:
#     result_dump = json.load(f)

# missing_features = get_missing_features(result_sparql, result_dump)

# with open("query_check_missing_features.json", "w") as f:
#     json.dump(missing_features, f, indent=4)

# MARK: Part 3

# Note: Process missing features.

# with open("query_check_missing_features.json", "r") as f:
#     missing_features = json.load(f)

# process_missing_features(missing_features, query_dir=None)
