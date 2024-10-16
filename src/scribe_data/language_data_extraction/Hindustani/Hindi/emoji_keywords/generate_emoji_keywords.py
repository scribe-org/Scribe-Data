"""
<<<<<<< HEAD
Generates keyword-emoji relationships from a selection of Hindi words, ensuring Urdu words are excluded.

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

from scribe_data.unicode.generate_emoji_keyword import generate_emoji_keyword
from scribe_data.unicode.common_arg_parser import setup_arg_parser 

LANGUAGE = "Hindi"

# Define the main language.
LANGUAGE = "Hindustani"  # Grouped language with sub-languages like Hindi, Urdu

# Set up the argument parser by calling the imported function.
parser = setup_arg_parser()

# Parse the command-line arguments.
args = parser.parse_args()

# Call the generate_emoji_keyword function with optional parameters.
generate_emoji_keyword(
    LANGUAGE,
    args.file_path,  
    emojis_per_keyword=args.emojis_per_keyword,  
    gender=args.gender,  
    region=args.region,  
    sub_languages=args.sub_languages,  
)