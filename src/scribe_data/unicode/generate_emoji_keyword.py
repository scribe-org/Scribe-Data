"""
Centralize emoji keyword generation logic

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
    -->.
"""

from .process_unicode import gen_emoji_lexicon
from scribe_data.utils import export_formatted_data


def generate_emoji_keyword(
    language,
    file_path,
    emojis_per_keyword=3,  # default value for emojis_per_keyword
    gender=None,
    region=None,
    sub_languages=None,
):
    # Define grouped languages and their sub-languages.
    grouped_languages = {
        "Hindustani": ["Hindi", "Urdu"],
        "Norwegian": ["Bokmål", "Nynorsk"],
        # Add more grouped languages as needed.
    }

    # If the language is a grouped language, handle its sub-languages.
    if language in grouped_languages:
        # If specific sub-languages are provided, only process those.
        sub_languages_to_process = sub_languages or grouped_languages[language]

        for sub_lang in sub_languages_to_process:
            print(f"Processing sub-language: {sub_lang}")

            # Generate emoji keywords for the sub-language.
            emoji_keywords_dict = gen_emoji_lexicon(
                language=sub_lang,
                emojis_per_keyword=emojis_per_keyword,
                gender=gender,
                region=region,
            )

            # Export the generated emoji keywords for the sub-language.
            if emoji_keywords_dict:
                # Save the file with the sub-language included in the file name.
                export_file_path = f"{file_path}_{sub_lang}.json"
                export_formatted_data(
                    file_path=export_file_path,
                    formatted_data=emoji_keywords_dict,
                    query_data_in_use=True,
                    language=sub_lang,
                    data_type="emoji-keywords",
                )

    # If it's not a grouped language, process it as a single language.
    else:
        # generate emoji keywords for the given language.
        emoji_keywords_dict = gen_emoji_lexicon(
            language=language,
            emojis_per_keyword=emojis_per_keyword,
            gender=gender,
            region=region,
        )

        # Export the generated emoji keywords for the language.
        if emoji_keywords_dict:
            export_formatted_data(
                file_path=file_path,
                formatted_data=emoji_keywords_dict,
                query_data_in_use=True,
                language=language,
                data_type="emoji-keywords",
            )
