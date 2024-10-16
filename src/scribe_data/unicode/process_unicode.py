"""
Module for processing Unicode based corpuses for autosuggestion and autocompletion generation.

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

import csv
import json
from pathlib import Path

import emoji

try:
    from icu import Char, UProperty

    icu_installed = True

except ImportError:
    icu_installed = False

from tqdm.auto import tqdm

from scribe_data.unicode.unicode_utils import (
    get_emoji_codes_to_ignore,
)
from scribe_data.utils import (
    DEFAULT_JSON_EXPORT_DIR,
    get_language_iso,
)

emoji_codes_to_ignore = get_emoji_codes_to_ignore()


def gen_emoji_lexicon(
    language: str,
    emojis_per_keyword: int,
    gender=None,
    region=None,
):
    """
    Generate emoji lexicon for a given language with optional gender and region customizations.

    Parameters:
    - language (str): The language for which emoji keywords are generated.
    - emojis_per_keyword (int): Number of emojis to associate with each keyword.
    - gender (str, optional): Gender-based customization for emojis (e.g., "male", "female").
    - region (str, optional): Regional customization for emojis (e.g., "US", "JP").

    Returns:
    - dict: A dictionary containing emoji keywords and associated emojis.
    """

    # Initialize the emoji dictionary
    emoji_keywords_dict = {}

    # Define grouped languages and their specific languages
    grouped_languages = {
        "Hindustani": ["Hindi", "Urdu"],
        "Norwegian": ["Bokmål", "Nynorsk"],
        # Add more grouped languages as needed
    }

    # Function to add emojis based on gender and region
    def add_emojis_for_gender_region(lang, gender, region):
        """
        This function generates a set of emojis based on the specified language,
        gender, and region. It aims to ensure that the emojis are relevant and
        culturally appropriate for the given context.

        Parameters:
        - lang (str): The language for which emojis are being generated. This could
          affect the representation of certain emojis or their usage.
        - gender (str): A string that indicates the gender for which emojis should
          be selected. Accepted values are "male" and "female".
        - region (str): A string representing the geographical region, which can
          influence the selection of emojis to include those that are culturally
          significant or popular in that area (e.g., "IN" for India).

        Implementation Details:
        1. **Placeholder Logic**:
            - The function currently contains placeholder comments indicating where
              the actual logic for selecting emojis should be implemented. This allows
              contributors to easily identify where to add the necessary emoji-selection
              logic based on gender and region.

        2. **Gender-Based Emoji Selection**:
            - The function checks the gender parameter. Depending on whether the
              gender is "male" or "female", different sets of emojis should be
              included. For example, if the gender is "male", the logic for selecting
              male-specific emojis will be executed. Similarly, for "female",
              female-specific emojis should be considered.
            - The `pass` statement is a placeholder for the logic that should be
              implemented later. This could involve referencing a predefined list of
              emojis or generating emojis based on specific criteria related to gender.

        3. **Region-Based Emoji Selection**:
            - The function also checks the region parameter. If the region is "IN",
              the logic for selecting emojis that are relevant to India will be executed.
            - Just like with gender, the `pass` statement indicates where to add
              this logic. The selected emojis should reflect cultural significance or
              popular usage in the specified region.

        4. **Returning Emoji Data**:
            - The function is designed to return a dictionary containing the emojis that
              have been selected based on the provided parameters. The current implementation
              returns an empty dictionary, which should be replaced with the actual logic to
              populate it with emoji data generated from the gender and region logic.

        Need for Modularity:
        - As the project scales and the emoji selection logic becomes more complex,
          it is essential to keep the code modular. This means separating different
          functionalities into distinct modules or files.


        This function serves as a foundational component for generating
        emojis tailored to specific user demographics, and implementing it in a
        modular fashion will support future enhancements and maintenance.
        """

        if gender == "male":
            # Include male-specific emojis logic
            pass
        elif gender == "female":
            # Include female-specific emojis logic
            pass

        if region == "IN":
            # Include region-specific emojis logic
            pass

        # Return any generated emoji data for the given language
        return {}

    # Check if the language is a grouped language
    for grouped_language, sub_languages in grouped_languages.items():
        if language == grouped_language:
            # Process each sub-language in the grouped language
            for sub_lang in sub_languages:
                print(f"Processing sub-language: {sub_lang}")
                # Add emojis for each sub-language based on gender and region
                emojis = add_emojis_for_gender_region(sub_lang, gender, region)
                emoji_keywords_dict[sub_lang] = emojis  # Add to the dictionary

            # If you want to combine results for the grouped language
            emoji_keywords_dict[grouped_language] = emoji_keywords_dict

            return emoji_keywords_dict  # Return the dict for grouped languages

    # If it's not a grouped language, handle it as a single language
    else:
        # Generate emojis for the given single language
        emojis = add_emojis_for_gender_region(language, gender, region)
        emoji_keywords_dict[language] = emojis

    return emoji_keywords_dict


def gen_emoji_lexicon_old(
    language: str,
    emojis_per_keyword: int,
):
    """
    Generates a dictionary of keywords (keys) and emoji unicode(s) associated with them (values).

    Parameters
    ----------
        language : string (default=None)
            The language keywords are being generated for.

        emojis_per_keyword : int (default=None)
            The limit for number of emoji keywords that should be generated per keyword.

    Returns
    -------
        Keywords dictionary for emoji keywords-to-unicode are saved locally or uploaded to Scribe apps.
    """
    if not icu_installed:
        raise ImportError("Could not import required PyICU functionality.")

    keyword_dict = {}

    iso = get_language_iso(language)
    # Pre-set up the emoji popularity data.
    popularity_dict = {}

    with (Path(__file__).parent / "2021_ranked.tsv").open() as popularity_file:
        tsv_reader = csv.DictReader(popularity_file, delimiter="\t")
        for tsv_row in tsv_reader:
            popularity_dict[tsv_row["Emoji"]] = int(tsv_row["Rank"])

    # Pre-set up handling flags and tags (subdivision flags).
    # emoji_flags = Char.getBinaryPropertySet(UProperty.RGI_EMOJI_FLAG_SEQUENCE)
    # emoji_tags = Char.getBinaryPropertySet(UProperty.RGI_EMOJI_TAG_SEQUENCE)
    # regexp_flag_keyword = re.compile(r".*\: (?P<flag_keyword>.*)")

    annotations_file_path = (
        Path(__file__).parent
        / "cldr-annotations-full"
        / "annotations"
        / f"{iso}"
        / "annotations.json"
    )
    annotations_derived_file_path = (
        Path(__file__).parent
        / "cldr-annotations-derived-full"
        / "annotationsDerived"
        / f"{iso}"
        / "annotations.json"
    )

    cldr_file_paths = {
        "annotations": annotations_file_path,
        "annotationsDerived": annotations_derived_file_path,
    }

    for cldr_file_key, cldr_file_path in cldr_file_paths.items():
        with open(cldr_file_path, "r") as file:
            cldr_data = json.load(file)

        cldr_dict = cldr_data[cldr_file_key]["annotations"]

        for cldr_char in tqdm(
            iterable=cldr_dict,
            desc=f"Characters processed from '{cldr_file_key}' CLDR file for {language}",
            unit="cldr characters",
        ):
            # Filter CLDR data for emoji characters while not including certain emojis.
            if (
                cldr_char in emoji.EMOJI_DATA
                and cldr_char.encode("utf-8") not in emoji_codes_to_ignore
            ):
                emoji_rank = popularity_dict.get(cldr_char)

                # Process for emoji variants.
                has_modifier_base = Char.hasBinaryProperty(
                    cldr_char, UProperty.EMOJI_MODIFIER_BASE
                )
                if has_modifier_base and len(cldr_char) > 1:
                    continue

                # Only fully-qualified emoji should be generated by keyboards.
                # See www.unicode.org/reports/tr51/#Emoji_Implementation_Notes.
                if (
                    emoji.EMOJI_DATA[cldr_char]["status"]
                    == emoji.STATUS["fully_qualified"]
                ):
                    emoji_annotations = cldr_dict[cldr_char]

                    # # Process for flag keywords.
                    # if cldr_char in emoji_flags or cldr_char in emoji_tags:
                    #     flag_keyword_match = regexp_flag_keyword.match(
                    #         emoji_annotations["tts"][0]
                    #     )
                    #     flag_keyword = flag_keyword_match.group("flag_keyword")
                    #     keyword_dict.setdefault(flag_keyword, []).append(
                    #         {
                    #             "emoji": cldr_char,
                    #             "is_base": has_modifier_base,
                    #             "rank": emoji_rank,
                    #         }
                    #     )

                    for emoji_keyword in emoji_annotations["default"]:
                        emoji_keyword = emoji_keyword.lower()  # lower case the key
                        if (
                            # Use single-word annotations as keywords.
                            len(emoji_keyword.split()) == 1
                        ):
                            keyword_dict.setdefault(emoji_keyword, []).append(
                                {
                                    "emoji": cldr_char,
                                    "is_base": has_modifier_base,
                                    "rank": emoji_rank,
                                }
                            )

    # Check nouns files for plurals and update their data with the emojis for their singular forms.
    language_nouns_path = Path(DEFAULT_JSON_EXPORT_DIR) / f"{language}" / "nouns.json"
    if not language_nouns_path.is_file():
        print(
            "\nNote: Getting a language's nouns before emoji keywords allows for plurals to be linked to the emojis for their singulars.\n"
        )

    else:
        print(
            "\nNouns file detected in the same export directory. Linking singular word emojis to their plurals.\n"
        )
        with open(
            language_nouns_path,
            encoding="utf-8",
        ) as f:
            noun_data = json.load(f)

        plurals_to_singulars_dict = {
            noun_data[row]["plural"].lower(): row.lower()
            for row in noun_data
            if noun_data[row]["plural"] != "isPlural"
        }

        for plural, singular in plurals_to_singulars_dict.items():
            if plural not in keyword_dict and singular in keyword_dict:
                keyword_dict[plural] = keyword_dict[singular]

    # Sort by rank after all emojis already found per keyword.
    for emojis in keyword_dict.values():
        emojis.sort(
            key=lambda suggestion: float("inf")
            if suggestion["rank"] is None
            else suggestion["rank"]
        )

        # If specified, enforce limit of emojis per keyword.
        if emojis_per_keyword and len(emojis) > emojis_per_keyword:
            emojis[:] = emojis[:emojis_per_keyword]

    return keyword_dict
