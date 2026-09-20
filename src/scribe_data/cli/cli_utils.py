# SPDX-License-Identifier: GPL-3.0-or-later
"""
Utility functions for the Scribe-Data CLI.
"""

import contextlib
import difflib

from scribe_data.utils import (
    data_type_metadata,
    get_language_from_iso,
    language_to_qid,
)

# MARK: Correct Inputs


def correct_data_type(data_type: str) -> str | None:
    """
    Correct common versions of data type arguments to their standardized form.

    Parameters
    ----------
    data_type : str
        The data type to potentially correct.

    Returns
    -------
    str
        The data_type value or a corrected version of it.
    """
    all_data_types = data_type_metadata.keys()

    if data_type in all_data_types:
        return data_type

    for wt in all_data_types:
        if f"{data_type}s" == wt:
            return wt


# MARK: Print Formatted


def print_formatted_data(data: dict | list, data_type: str) -> None:
    """
    Print formatted output from the Scribe-Data CLI.

    Parameters
    ----------
    data : dict | list
        The data to format and print.

    data_type : str
        The type of data being printed, used to determine formatting style.
    """
    if not data:
        print(f"No data available for data type '{data_type}'.")
        return

    if isinstance(data, dict):
        max_key_length = max((len(key) for key in data.keys()), default=0)

        for key, value in data.items():
            if data_type == "emoji_keywords":
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
                        max_sub_key_length = max(
                            (len(k) for k in item.keys()), default=0
                        )
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


def validate_languages_and_data_types(
    languages: list[str] | bool | None,
    data_types: list[str] | bool | None,
) -> bool:
    """
    Validate that the language and data type QIDs are not None.

    Parameters
    ----------
    languages : list
        The languages to validate.

    data_types : list
        The data types to validate.

    Returns
    -------
    bool
        True if validation passes, otherwise raises ValueError.

    Raises
    ------
    ValueError
        If any of the languages or data types is invalid, with all errors reported together.
    """

    def validate_single_language_or_data_type(
        item: str, valid_options: set[str], item_type: str
    ) -> str | None:
        """
        Validate a single item against a list of valid options, providing error messages and suggestions.

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
            An error message if the item is invalid, or None if the item is valid.
        """
        if not isinstance(item, str):
            return None

        item_lower = item.lower().strip()
        if item_lower in valid_options:
            return None

        if item.startswith("Q") and len(item) > 1 and item[1:].isdigit():
            return None

        if len(item_lower) in {2, 3} and item_lower.isalpha():
            with contextlib.suppress(ValueError):
                get_language_from_iso(item_lower)
                return None

        closest_match = difflib.get_close_matches(item, valid_options, n=1)
        if closest_match and item_type == "language":
            closest_match = closest_match[0].capitalize()

        elif closest_match:
            closest_match = closest_match[0]

        closest_match_str = (
            f" The closest matching {item_type} is '{closest_match}'."
            if closest_match
            else ""
        )
        return f"Invalid {item_type} '{item}'.{closest_match_str}"

    errors = []

    # Handle language validation.
    if languages is None or isinstance(languages, bool):
        pass

    elif not isinstance(languages, list):
        errors.append("Language must be a list of strings.")

    if languages is not None and not isinstance(languages, bool):
        for lang in languages:
            lang = lang.split(" ")[0]
            error = validate_single_language_or_data_type(
                item=lang,
                valid_options=set(language_to_qid.keys()),
                item_type="language",
            )

            if error:
                errors.append(error)

    # Handle data type validation.
    if data_types is None or isinstance(data_types, bool):
        pass

    elif not isinstance(data_types, list):
        errors.append("Data type must be a string or a list of strings.")

    if data_types is not None and not isinstance(data_types, bool):
        valid_data_types = set(data_type_metadata.keys()) | {"wiktionary_translations"}
        for dt in data_types:
            error = validate_single_language_or_data_type(
                item=dt, valid_options=valid_data_types, item_type="data-type"
            )

            if error:
                errors.append(error)

    # Raise ValueError with the combined error message.
    if errors:
        raise ValueError("\n".join(errors))

    else:
        return True
