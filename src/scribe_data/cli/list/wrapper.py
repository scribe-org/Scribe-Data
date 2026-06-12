# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for listing languages and data types for the Scribe-Data CLI.
"""

from scribe_data.cli.list.data_types import list_data_types
from scribe_data.cli.list.languages import list_languages, list_languages_for_data_type

# MARK: All


def list_all() -> None:
    """
    List all available languages and data types.

    Returns
    -------
    None
        All available languages and data types are listed.
    """
    list_languages()
    list_data_types()


# MARK: Wrapper


def list_wrapper(
    language: str = "", data_type: str = "", all_bool: bool = False
) -> None:
    """
    Conditionally provides the full functionality of the list command.

    Parameters
    ----------
    language : str
        The language to potentially list data types for.

    data_type : str
        The data type to check for.

    all_bool : bool
        Whether all languages and data types should be listed.

    Returns
    -------
    None
        The call to list functions based on the provided arguments.
    """
    if (not language and not data_type) or all_bool:
        list_all()

    elif language is True and not data_type:
        list_languages()

    elif not language and data_type is True:
        list_data_types()

    elif language is True and data_type is True:
        print("Please specify either a language or a data type.")

    # Note: Saved for if listing languages by data type is implemented.
    elif language is True and data_type is not None:
        list_languages_for_data_type(data_type)

    elif language is not None and data_type is True:
        list_data_types(language)
