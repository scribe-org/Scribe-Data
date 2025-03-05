# SPDX-License-Identifier: GPL-3.0-or-later
"""
Order QID from a missing_unique_forms based on lexeme_form_metadata.json.
"""

from collections import defaultdict

from scribe_data.check.check_missing_forms.generate_query import generate_query
from scribe_data.utils import lexeme_form_metadata


# Precompute QID positions mapping only once when the module is imported.
def sort_qids_in_list(qids_lists):
    """
    Sort QIDs within each sublist based on their predefined positions.

    This function sorts the QIDs in each sublist of `qids_lists` according to their position
    defined in `lexeme_form_metadata`. QIDs not found in the metadata are placed at the end.

    Parameters
    ----------
    qids_lists : list[list[str]]
        A list of lists, where each sublist contains QIDs.

    Returns
    -------
    A new list of lists, with QIDs in each sublist sorted by position.
    """
    qid_positions = {}
    for category in lexeme_form_metadata.values():
        for item in category.values():
            if "qid" in item:
                qid_positions[item["qid"]] = len(qid_positions)

    # Sort each sublist based on position.
    return [
        sorted(qids, key=lambda x: qid_positions.get(x, float("inf")))
        for qids in qids_lists
    ]


def sort_qids_by_position(nested_qids):
    """
    Sort lists of QIDs based on their predefined positions and sublist length.

    This function sorts the sublists within `nested_qids` based on two criteria:
    1. The length of the sublist (shorter lists come first).
    2. The positions of the QIDs within each sublist, as defined in `lexeme_form_metadata`.

    Parameters
    ----------
    nested_qids : list[list[str]]
        A list of lists, where each sublist contains QIDs.

    Returns
    -------
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

    def get_sort_key(sublist):
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


def split_group_by_identifier(language_entry, output_dir, sub_lang_iso_code=None):
    """
    Split forms into groups of up to six forms per query based on identifiers.

    Parameters
    ----------
    language_entry : dict
        Dictionary containing language data with missing features.
        Format: {language_qid: {data_type_qid: [features]}}

    output_dir : str or Path
        Directory where generated query files should be saved.

    sub_lang_iso_code : str, optional
        ISO code for sub-language if applicable.

    Notes
    -----
    Groups forms based on their identifiers to avoid generating too many queries.
    Combines small groups when possible to reduce the number of query files.
    """
    for lang, data in language_entry.items():
        for data_type, missing_features_list in data.items():
            # Group features by their first identifier.
            identifier_groups = defaultdict(list)

            # First try to group by the first identifier in each feature list.
            for feature_list in missing_features_list:
                if feature_list:  # skip empty lists
                    # Use the first identifier as the grouping key.
                    key = feature_list[0]
                    identifier_groups[key].append(feature_list)

            # Now check if any groups have more than 6 features.
            final_groups = []

            for features in identifier_groups.values():
                if len(features) <= 6:
                    # This group is small enough so keep it as is.
                    final_groups.append(features)

                else:
                    # This group is too large so it needs to split further by the second identifier.
                    second_level_groups = defaultdict(list)

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
                        for i in range(0, len(second_features), 6):
                            chunk = second_features[i : i + 6]
                            final_groups.append(chunk)

            # Now combine small groups if possible to reduce query files.
            optimized_groups = []
            current_group = []

            # Sort groups by size to try combining smaller ones first.
            final_groups.sort(key=len)

            for group in final_groups:
                if len(current_group) + len(group) <= 6:
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

            # Generate queries for each optimized group.
            for i, group in enumerate(optimized_groups):
                # Create a new language entry for this group.
                group = group
                group_entry = {lang: {data_type: group}}

                print(
                    f"Generating query {i+1}/{len(optimized_groups)} for {lang} - {data_type} with {len(group)} features"
                )

                # Call generate_query with the grouped features.
                generate_query(
                    group_entry,
                    output_dir,
                    sub_lang_iso_code=sub_lang_iso_code,
                )
