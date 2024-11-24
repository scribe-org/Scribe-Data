"""
Utility functions for the Scribe-Data CLI.

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

import difflib
from typing import List, Union

from scribe_data.utils import data_type_metadata, language_to_qid

# MARK: Correct Inputs


def correct_data_type(data_type: str) -> str:
    """
    Corrects common versions of data type arguments so users can choose between them.

    Parameters
    ----------
        data_type : str
            The data type to potentially correct.

    Returns
    -------
        The data_type value or a corrected version of it.
    """
    all_data_types = data_type_metadata.keys()

    if data_type in all_data_types:
        return data_type

    for wt in all_data_types:
        if f"{data_type}s" == wt:
            return wt


# MARK: Print Formatted


def print_formatted_data(data: Union[dict, list], data_type: str) -> None:
    """
    Prints a formatted output from the Scribe-Data CLI.
    """
    if not data:
        print(f"No data available for data type '{data_type}'.")
        return

    if isinstance(data, dict):
        max_key_length = max((len(key) for key in data.keys()), default=0)

        for key, value in data.items():
            if data_type == "autosuggestions":
                print(f"{key:<{max_key_length}} : {', '.join(value)}")

            elif data_type == "emoji_keywords":
                emojis = [item["emoji"] for item in value]
                print(f"{key:<{max_key_length}} : {' '.join(emojis)}")

            elif data_type in {"prepositions"}:
                print(f"{key:<{max_key_length}} : {value}")

            elif isinstance(value, dict):
                print(f"{key:<{max_key_length}} : ")
                max_sub_key_length = max(
                    (len(sub_key) for sub_key in value.keys()), default=0
                )
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key:<{max_sub_key_length}} : {sub_value}")

            elif isinstance(value, list):
                print(f"{key:<{max_key_length}} : ")
                for item in value:
                    if isinstance(item, dict):
                        for sub_key, sub_value in item.items():
                            print(f"  {sub_key:<{max_sub_key_length}} : {sub_value}")

                    else:
                        print(f"  {item}")

            else:
                print(f"{key:<{max_key_length}} : {value}")

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for key, value in item.items():
                    print(f"{key} : {value}")

            else:
                print(item)

    else:
        print(data)


# MARK: Validate


def validate_language_and_data_type(
    language: Union[str, List[str], bool, None],
    data_type: Union[str, List[str], bool, None],
):
    """
    Validates that the language and data type QIDs are not None.

    Parameters
    ----------
        language : str or list
            The language(s) to validate.

        data_type : str or list
            The data type(s) to validate.

    Raises
    ------
        ValueError
            If any of the languages or data types is invalid, with all errors reported together.
    """

    def validate_single_item(item, valid_options, item_type):
        """
        Validates a single item against a list of valid options, providing error messages and suggestions.

        Parameters
        ----------
            item : str
                The item to validate.
            valid_options : list

                A list of valid options against which the item will be validated.

            item_type : str
                A description of the item type (e.g., "language", "data-type") used in error messages.

        Returns
        -------
            str or None
                Returns an error message if the item is invalid, or None if the item is valid.
        """
        if (
            isinstance(item, str)
            and item.lower().strip() not in valid_options
            and not item.startswith("Q")
            and not item[1:].isdigit()
        ):
            closest_match = difflib.get_close_matches(item, valid_options, n=1)
            closest_match_str = (
                f" The closest matching {item_type} is '{closest_match[0].capitalize()}'."
                if closest_match
                else ""
            )

            return f"Invalid {item_type} '{item}'.{closest_match_str}"

        return None

    errors = []

    # Handle language validation.
    if language is None or isinstance(language, bool):
        pass

    elif isinstance(language, str):
        language = [language]

    elif not isinstance(language, list):
        errors.append("Language must be a string or a list of strings.")

    if language is not None and isinstance(language, list):
        for lang in language:
            lang = lang.split(" ")[0]
            error = validate_single_item(lang, language_to_qid.keys(), "language")

            if error:
                errors.append(error)

    # Handle data type validation.
    if data_type is None or isinstance(data_type, bool):
        pass

    elif isinstance(data_type, str):
        data_type = [data_type]

    elif not isinstance(data_type, list):
        errors.append("Data type must be a string or a list of strings.")

    if data_type is not None and isinstance(data_type, list):
        for dt in data_type:
            error = validate_single_item(dt, data_type_metadata.keys(), "data-type")

            if error:
                errors.append(error)

    # Raise ValueError with the combined error message.
    if errors:
        raise ValueError("\n".join(errors))

    else:
        return True
