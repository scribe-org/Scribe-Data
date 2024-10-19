
"""
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
"""

import argparse
from scribe_data.unicode.generate_emoji_keyword import generate_emoji_keyword

# Define the main language
LANGUAGE = "Norwegian"  # Change to a grouped language if needed
emojis_per_keyword = 3

# Set up the argument parser
parser = argparse.ArgumentParser(
    description="Generate emoji keywords for a specific language."
)
parser.add_argument(
    "--file-path", required=True, help="Path to save the generated emoji keywords."
)
parser.add_argument(
    "--sub-languages",
    nargs="*",
    help="List of specific sub-languages to process (e.g., Bokmal and Nynorsk. If omitted, all sub-languages will be processed.",
)
parser.add_argument(
    "--gender",
    choices=["male", "female", "neutral"],
    help="Specify the gender for emoji customization.",
)
parser.add_argument(
    "--region", help="Specify the region for emoji customization (e.g., US, IN)."
)

# Parse the command-line arguments
args = parser.parse_args()

# Call the generate_emoji_keyword function with optional parameters
generate_emoji_keyword(
    LANGUAGE,
    emojis_per_keyword,
    args.file_path,
    gender=args.gender,
    region=args.region,
    sub_languages=args.sub_languages,
)
