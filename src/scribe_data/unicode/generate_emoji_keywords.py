# SPDX-License-Identifier: GPL-3.0-or-later
"""
Centralized keyword-emoji generation file to generated emoji for a specified Language.
"""

import os
from pathlib import Path

from scribe_data.check.check_pyicu import (
    check_and_install_pyicu,
    check_if_pyicu_installed,
)
from scribe_data.unicode.process_unicode import gen_emoji_lexicon
from scribe_data.utils import export_formatted_data, get_language_iso

DATA_TYPE = "emoji-keywords"
EMOJI_KEYWORDS_DICT = 3


def generate_emoji(language, output_dir: str = None):
    """
    Generate emoji keywords for a specified language.

    This function first checks and installs the PyICU package, which is necessary for the script to run.
    If the installation is successful, it proceeds with generating emoji keywords based on the specified language.
    The results are then exported to the provided output directory.

    Parameters
    ----------
    language : str
        The ISO code of the language for which to generate emoji keywords.

    output_dir : str, optional
        The directory where the generated data will be saved.
        If not specified, the data will be saved in a default directory.

    Returns
    -------
    None
        The function does not return any value but outputs data to the specified directory.
    """
    if check_and_install_pyicu() and check_if_pyicu_installed() is False:
        print("Thank you.")

    if check_if_pyicu_installed():
        iso = get_language_iso(language=language)
        path_to_cldr_annotations = (
            Path(__file__).parent / "cldr-annotations-full" / "annotations"
        )
        if iso in os.listdir(path_to_cldr_annotations):
            print(f"Emoji Generation for language {language.capitalize()} is supported")

        else:
            print(
                f"Emoji Generation for language {language.capitalize()} is not supported"
            )
            return

        updated_path = output_dir[2:] if output_dir.startswith("./") else output_dir
        export_dir = Path(updated_path) / language.capitalize()
        export_dir.mkdir(parents=True, exist_ok=True)

        if emoji_keywords_dict := gen_emoji_lexicon(
            language=language,
            emojis_per_keyword=EMOJI_KEYWORDS_DICT,
        ):
            export_formatted_data(
                dir_path=output_dir,
                formatted_data=emoji_keywords_dict,
                query_data_in_use=True,
                language=language,
                data_type=DATA_TYPE,
            )
