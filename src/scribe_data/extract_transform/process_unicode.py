"""
Process Unicode
------------

Module for processing Unicode based corpuses for autosuggestion generation.

Contents:
    gen_emoji_autosuggestions
"""

import emoji
import json

from scribe_data.load.update_utils import get_language_iso


def gen_emoji_autosuggestions(
    language="English",
    num_emojis=500,
    ignore_keywords=None,
    update_scribe_apps=False,
    verbose=True,
):
    """
    Generates a dictionary of keywords (keys) and emoji unicodes(s) associated with them (values).

    Parameters
    ----------
        language : string (default=en)
            The language autosuggestions are being generated for.

        num_emojis: int (default=500)
            The number of emojis that autosuggestions should be generated from.

        ignore_keywords : str or list (default=None)
            Keywords that should be ignored.

        update_scribe_apps : bool (default=False)
            Saves the created dictionaries as JSONs in Scribe app directories.

        verbose : bool (default=True)
            Whether to show a tqdm progress bar for the process.

    Returns
    -------
        Autosuggestions dictionaries for emoji keywords-to-unicode are saved locally or uploaded to Scribe apps.
    """

    autosuggest_dict = {}

    ### TODO further updates - here for data loading illustration

    iso = get_language_iso(language)

    cldr_file_path = f"node_modules/cldr-annotations-full/annotations/{iso}/annotations.json"

    with open(cldr_file_path, "r") as file:
        cldr_data = json.load(file)

    cldr_dict = cldr_data["annotations"]["annotations"]

    print("Number of characters loaded:", len(cldr_dict))

    for cldr_char in cldr_dict:
        # Filter CLDR data for emoji characters
        if cldr_char in emoji.EMOJI_DATA:
            emoji_annotations = cldr_dict[cldr_char]
            
            for emoji_keyword in emoji_annotations["default"]:
                # Use single-word annotations as keywords
                if len(emoji_keyword.split()) == 1:
                    autosuggest_dict.setdefault(emoji_keyword, []).append(cldr_char)

    print("Number of trigger keywords found:", len(autosuggest_dict))

    ###

    return autosuggest_dict
