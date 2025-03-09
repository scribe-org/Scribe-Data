# SPDX-License-Identifier: GPL-3.0-or-later
"""
Order QID from a missing_unique_forms based on lexeme_form_metadata.json.
"""

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
