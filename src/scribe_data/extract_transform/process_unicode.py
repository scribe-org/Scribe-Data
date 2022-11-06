"""
Process Unicode
------------

Module for processing Unicode based corpuses for autosuggestion generation.

Contents:
    gen_emoji_autosuggestions
"""

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

    language = get_language_iso(language)

    cldr_file_path = f'node_modules/cldr-annotations-derived-full/annotationsDerived/{language}/annotations.json'

    with open(cldr_file_path, 'r') as file:
        cldr_data = json.load(file)

    emoji_dict = cldr_data['annotationsDerived']['annotations']

    print("Number of emojis loaded:", len(emoji_dict))

    ###

    return autosuggest_dict
