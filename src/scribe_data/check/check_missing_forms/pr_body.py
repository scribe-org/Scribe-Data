"""
Generate a formatted PR body describing missing features for each language.

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

import json
import sys
from scribe_data.utils import (
    language_metadata,
    data_type_metadata,
)


def pr_body(missing_features):
    """
    Generate a formatted PR body describing missing features for each language.

    Parameters
    ----------
    missing_features : dict
        Dictionary mapping language QIDs to their missing features.
        Format: {language_qid: {feature_type: [features]}}

    Returns
    -------
    str
        Formatted PR body content in markdown format containing a table of
        missing features grouped by language.

    Notes
    -----
    The PR body includes:
    - A header indicating this is an automated PR
    - A table showing languages and their missing feature types
    - Features are grouped by language for better readability
    """
    # Initialize PR body with a header.
    pr_body_content = "## Automated PR: Missing Features\n\n"
    pr_body_content += "This PR was automatically created by a GitHub Action.\n\n"
    pr_body_content += "### Missing Features Summary\n"
    pr_body_content += "| **Language** | **Feature Type** |\n"
    pr_body_content += "|--------------|------------------|\n"

    # Create a dictionary to group features by language.
    grouped_features = {}

    # Iterate over the missing features to populate the table.
    for entity, features in missing_features.items():
        # Check for sub-languages.
        language_name = None
        for name, data in language_metadata.items():
            if data.get("qid") == entity:
                language_name = name
                break
            if "sub_languages" in data:
                for sub_name, sub_data in data["sub_languages"].items():
                    if sub_data.get("qid") == entity:
                        language_name = f"{name} ({sub_name})"
                        break
            if language_name:
                break

        # Default to entity if no name is found.
        language_name = language_name or entity

        # Group features by language.
        if language_name not in grouped_features:
            grouped_features[language_name] = set()

        for feature in features.keys():
            feature_name = next(
                (name for name, qid in data_type_metadata.items() if qid == feature),
                feature,
            )
            grouped_features[language_name].add(feature_name)

    # Add grouped features to the PR body.
    for language, features in sorted(grouped_features.items()):
        feature_list = ", ".join(sorted(features))
        pr_body_content += f"| **{language}** | {feature_list} |\n"

    pr_body_content += "\nPlease review the changes and provide feedback.\n"

    print(pr_body_content)
    return pr_body_content


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        missing_features = json.load(f)

    pr_body(missing_features)
