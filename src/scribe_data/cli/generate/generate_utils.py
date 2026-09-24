# SPDX-License-Identifier: GPL-3.0-or-later
"""
Utility functions for generating Wikidata lexeme queries.
"""

import os
import re
import string
from collections import defaultdict
from pathlib import Path

from scribe_data.utils import lexeme_form_metadata

MAX_FORMS_PER_QUERY = 6

# MARK: Extract Contract Values


def _has_key(data: dict | list, target_key: str) -> bool:
    """
    Recursively checks if a target key exists anywhere in the dictionary/list.

    Parameters
    ----------
    data : dict | list
        The data to check for the target key.

    target_key : str
        The string to check for dictionary for.

    Returns
    -------
    bool
        Whether the target key appears in the data.
    """
    if isinstance(data, dict):
        if target_key in data:
            return True
        return any(_has_key(v, target_key) for v in data.values())

    elif isinstance(data, list):
        return any(_has_key(item, target_key) for item in data)

    return False


def _extract_specific_key_values(data: dict | list, target_key: str) -> list:
    """
    Walks the structure and only extracts values assigned to the target_key.

    Parameters
    ----------
    data : dict | list
        The data to extract all values for a target key.

    target_key : str
        The string to extract values from the dictionary for.

    Returns
    -------
    list
        The values in the data that match the target key.
    """
    values = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == target_key:
                # If the value itself is a list/dict, extract its end values.
                if isinstance(v, (dict, list)):
                    values.extend(_extract_all_leaves(v))

                else:
                    values.append(v)

            else:
                values.extend(_extract_specific_key_values(v, target_key))

    elif isinstance(data, list):
        for item in data:
            values.extend(_extract_specific_key_values(item, target_key))

    return values


def _extract_all_leaves(data: dict | list) -> list:
    """
    Walks the structure and extracts all end values (leaf nodes).

    Parameters
    ----------
    data : dict | list
        The data to extract all leaf node values for.
    """
    values = []
    if isinstance(data, dict):
        for v in data.values():
            values.extend(_extract_all_leaves(v))

    elif isinstance(data, list):
        for item in data:
            values.extend(_extract_all_leaves(item))

    else:
        values.append(data)

    return values


def extract_data_contract_values(contract_entry: dict) -> list:
    """
    Extract the end values from a Scribe-Data data contract.

    Parameters
    ----------
    contract_entry : dict
        A dictionary found within a data contract.

    Returns
    -------
    list
        The end values of the data contract.
    """
    # If "value" exists anywhere in this contract entry tree, then only get these values.
    if _has_key(contract_entry, "value"):
        contract_values = _extract_specific_key_values(contract_entry, "value")

    # Get all the end values.
    else:
        contract_values = _extract_all_leaves(contract_entry)

    final_contract_values = set()
    for cv in contract_values:
        cv_split_and_no_punctuation = [
            v.translate(str.maketrans("", "", string.punctuation))
            for v in cv.split(" ")
        ]
        for v in cv_split_and_no_punctuation:
            final_contract_values.add(v)

    return sorted(list(final_contract_values))


# MARK: Query Filename


def get_next_query_filename(base_path: str) -> str:
    """
    Get the next available filename by incrementing a counter if file exists.

    Parameters
    ----------
    base_path : str
        Base path for the query file.

    Returns
    -------
    str
        Available filename that doesn't conflict with existing files.

    Examples
    --------
    If no files exist:
        - Returns query_{data_type}.sparql
    If query_{data_type}.sparql exists:
        - Renames existing query_{data_type}.sparql to query_{data_type}_1.sparql
        - Returns query_{data_type}_2.sparql
    If last file is query_{data_type}_N.sparql:
        - Returns query_{data_type}_(N+1).sparql
    """
    base_dir = os.path.dirname(base_path)
    base_name = os.path.basename(base_path)
    name, ext = os.path.splitext(base_name)  # ext : ".sparql"

    # If directory doesn't exist, return base name.
    if not os.path.exists(base_dir):
        return base_path

    # Check for existing files.
    existing_files = [
        f for f in os.listdir(base_dir) if f.startswith(name) and f.endswith(ext)
    ]

    # If no files exist, use base name.
    if not existing_files:
        return base_path

    # Check if base file exists (query_{data_type}.sparql).
    if base_name in existing_files:
        # Rename base file to query_{data_type}_1.sparql.
        old_path = os.path.join(base_dir, base_name)
        new_path = os.path.join(base_dir, f"{name}_1{ext}")
        os.rename(old_path, new_path)

        # Return query_{data_type}_2.sparql for new file.
        return os.path.join(base_dir, f"{name}_2{ext}")

    # Find highest number in existing files.
    max_num = 0
    for f in existing_files:
        if match := re.search(rf"{name}_(\d+){ext}$", f):
            num = int(match[1])
            max_num = max(max_num, num)

    # Return next number in sequence.
    return os.path.join(base_dir, f"{name}_{max_num + 1}{ext}")


# MARK: Split Forms


def split_lexeme_forms_by_identifier(
    language_entry: dict,
    output_dir: Path,
    sub_lang_iso_code: str | None = None,
) -> None:
    """
    Split forms into groups of up to six forms per query based on identifiers.

    Parameters
    ----------
    language_entry : dict
        Dictionary containing language data with missing features.
        Format: {language_qid: {data_type_qid: [features]}}.

    output_dir : Path
        Directory where generated query files should be saved.

    sub_lang_iso_code : str, optional
        ISO code for sub-language if applicable.

    Notes
    -----
    Groups forms based on their identifiers to avoid generating too many queries.
    Combines small groups when possible to reduce the number of query files.
    """
    for data in language_entry.values():
        for data_type, missing_features_list in data.items():
            # Group features by their first identifier.
            identifier_groups: defaultdict[str, list] = defaultdict(list)

            # First try to group by the first identifier in each feature list.
            for feature_list in missing_features_list:
                if feature_list:  # skip empty lists
                    # Use the first identifier as the grouping key.
                    key = feature_list[0]
                    identifier_groups[key].append(feature_list)

            # Now check if any groups have more than 6 features.
            final_groups: list[list] = []

            for features in identifier_groups.values():
                if len(features) <= MAX_FORMS_PER_QUERY:
                    # This group is small enough so keep it as is.
                    final_groups.append(features)

                else:
                    # This group is too large so it needs to split further by the second identifier.
                    second_level_groups: defaultdict[str, list] = defaultdict(list)

                    for feature_list in features:
                        if len(feature_list) > 1:
                            # Use the second identifier for further grouping.
                            second_key = feature_list[1]
                            second_level_groups[second_key].append(feature_list)

                        else:
                            # If there's only one identifier, make it its own group.
                            second_level_groups["single_identifier"].append(
                                feature_list
                            )

                    # Further split if necessary and add to final groups.
                    for second_features in second_level_groups.values():
                        # Split into chunks of 6.
                        for i in range(0, len(second_features), MAX_FORMS_PER_QUERY):
                            chunk = second_features[i : i + MAX_FORMS_PER_QUERY]
                            final_groups.append(chunk)

            # Now combine small groups if possible to reduce query files.
            optimized_groups: list[list] = []
            current_group: list = []

            # Sort groups by size to try combining smaller ones first.
            final_groups.sort(key=len)

            for group in final_groups:
                if len(current_group) + len(group) <= MAX_FORMS_PER_QUERY:
                    # Can add this group to the current one.
                    current_group.extend(group)

                else:
                    # Current group is full, so start a new one.
                    if current_group:
                        optimized_groups.append(current_group)
                    current_group = group

            # Add the last group if not empty.
            if current_group:
                optimized_groups.append(current_group)


# MARK: Sort QIDs


def sort_qids_by_position(nested_qids: list[list[str]]) -> list[list[str]]:
    """
    Sort lists of QIDs based on their predefined positions and sublist length.

    This function sorts the sub-lists within `nested_qids` based on two criteria:
    1. The length of the sublist (shorter lists come first).
    2. The positions of the QIDs within each sublist, as defined in `lexeme_form_metadata`.

    Parameters
    ----------
    nested_qids : List[List[str]]
        A list of lists, where each sublist contains QIDs.

    Returns
    -------
    list
        A new list of lists, sorted according to the defined criteria.
    """
    qid_positions = {}
    for category_index, (category_name, category) in enumerate(
        lexeme_form_metadata.items()
    ):
        for item in category.values():
            if "qid" in item:
                # Category index * 1000 ensures different categories don't overlap
                qid_positions[item["qid"]] = category_index * 1000 + len(qid_positions)

    def get_sort_key(sublist: list) -> list:
        """
        Get a key to sort the forms list.

        Parameters
        ----------
        sublist : list
            A sublist of keys.

        Returns
        -------
        list
            A list of keys by which sorting will occur.
        """
        # First priority: length of sublist.
        length_priority = len(sublist) * 1000000

        # Sort QIDs within the sublist by their positions.
        sorted_positions = sorted(
            qid_positions.get(qid, float("inf")) for qid in sublist
        )

        # Pad with infinity for consistent comparison.
        while len(sorted_positions) < 5:
            sorted_positions.append(float("inf"))

        return [length_priority] + sorted_positions

    return sorted(nested_qids, key=get_sort_key)
