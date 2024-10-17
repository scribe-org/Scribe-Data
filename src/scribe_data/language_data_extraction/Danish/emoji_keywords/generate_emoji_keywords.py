"""
Generates keyword-emoji relationships from a selection of Danish words.

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
from scribe_data.unicode.generate_emoji_keyword import generate_emoji_keyword

LANGUAGE = "Danish"
emojis_per_keyword = 3

parser = argparse.ArgumentParser(
    description="Generate emoji keywords for the language."
)
parser.add_argument(
    "--file-path", required=True, help="Path to save the generated emoji keywords."
)
parser.add_argument(
    "--gender",
    choices=["male", "female", "neutral"],
    help="Specify the gender for emoji customization.",
)
parser.add_argument(
    "--region", help="Specify the region for emoji customization."
)

args = parser.parse_args()

generate_emoji_keyword(
    LANGUAGE,
    emojis_per_keyword,
    args.file_path,
    gender=args.gender,
    region=args.region,
)
