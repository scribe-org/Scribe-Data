"""
Process Unicode
------------

Module for processing Unicode based corpuses for autosuggestion generation.

Contents:
    gen_emoji_autosuggestions
"""

import emoji
import json

from scribe_data.load.update_utils import get_language_iso, get_path_from_process_unicode


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

    path_to_scribe_org = get_path_from_process_unicode()
    annotations_file_path = f"{path_to_scribe_org}/Scribe-Data/node_modules/cldr-annotations-full/annotations/{iso}/annotations.json"
    annotations_derived_file_path = f"{path_to_scribe_org}/Scribe-Data/node_modules/cldr-annotations-derived-full/annotationsDerived/{iso}/annotations.json"

    cldr_file_paths = {
        "annotations": annotations_file_path, 
        "annotationsDerived": annotations_derived_file_path
    }

    for cldr_file_key, cldr_file_path in cldr_file_paths.items():
        with open(cldr_file_path, "r") as file:
            cldr_data = json.load(file)

        cldr_dict = cldr_data[cldr_file_key]["annotations"]

        print(f"Number of characters loaded for CLDR '{cldr_file_key}' for {language}: {len(cldr_dict)}")

        for cldr_char in cldr_dict:
            # Filter CLDR data for emoji characters
            if cldr_char in emoji.EMOJI_DATA:
                emoji_annotations = cldr_dict[cldr_char]
                
                for emoji_keyword in emoji_annotations["default"]:
                    # Use single-word annotations as keywords
                    if len(emoji_keyword.split()) == 1:
                        autosuggest_dict.setdefault(emoji_keyword, []).append(cldr_char)

    print(f"Number of emoji trigger keywords found for {language}: {len(autosuggest_dict)}")

    output_path = f"tmp_{iso}_emojisuggestions.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(autosuggest_dict, file, ensure_ascii=False, indent=0)

    print(f"Emoji autosuggestions for {language} generated and saved to '{output_path}'.")

    ###

    return autosuggest_dict
