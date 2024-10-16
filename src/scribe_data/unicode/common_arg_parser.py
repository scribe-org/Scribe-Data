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

import argparse

def setup_arg_parser():
    parser = argparse.ArgumentParser(
        description="Generate emoji keywords for a specific language."
    )
    parser.add_argument(
        "--file-path", required=True, help="Path to save the generated emoji keywords."
    )
    parser.add_argument(
        "--sub-languages",
        nargs="*",
        help="List of specific sub-languages to process (e.g., Hindi Urdu). If omitted, all sub-languages will be processed.",
    )
    parser.add_argument(
        "--gender",
        choices=["male", "female", "neutral"],
        help="Specify the gender for emoji customization.",
    )
    parser.add_argument(
        "--region", help="Specify the region for emoji customization (e.g., US, IN)."
    )
    parser.add_argument(
        "--emojis-per-keyword",
        type=int,
        help="Number of emojis to generate per keyword.",
    )
    return parser
