"""
centralized emoji_keyword file
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

import argparse
import json
from pathlib import Path

from scribe_data.unicode.process_unicode import gen_emoji_lexicon
from scribe_data.utils import export_formatted_data

DATA_TYPE = "emoji-keywords"
EMOJIS_PER_KEYWORD = 3

# Define the path to the languages JSON file.
LANGUAGES_JSON = Path(__file__).parent / "supported_language.json"


def main(file_path):
    # Read the language codes and names from the JSON.
    with open(LANGUAGES_JSON, "r", encoding="utf-8") as f:
        languages = json.load(f)

    for code, language in languages.items():
        print(f"Generating emoji keywords for {language} ({code})...")

        language_dir = file_path / f"{language}"
        emoji_dir = language_dir / "emoji_keywords"
        init_file = emoji_dir / "__init__.py"

        # Ensure that the emoji_keywords directory and __init__.py file exist.
        emoji_dir.mkdir(parents=True, exist_ok=True)

        if not init_file.exists():
            # Create the __init__.py file if it doesn't exist.
            init_file.touch()
            print(f"Created __init__.py in {emoji_dir}.")

        if emoji_keywords_dict := gen_emoji_lexicon(
            language=language,
            emojis_per_keyword=EMOJIS_PER_KEYWORD,
        ):
            export_formatted_data(
                file_path=emoji_dir / f"{code}_emoji_keywords.json",
                formatted_data=emoji_keywords_dict,
                query_data_in_use=True,
                language=language,
                data_type=DATA_TYPE,
            )
            print(f"Emoji keywords for {language} saved.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file-path", required=True, help="Path to save the emoji keywords files."
    )
    args = parser.parse_args()

    # Ensure the directory exists.
    output_dir = Path(args.file_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Call the main function.
    main(output_dir)
