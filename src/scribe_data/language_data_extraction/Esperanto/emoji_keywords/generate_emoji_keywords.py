"""
Generates keyword-emoji relationships from a selection of Esperanto words.

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

from scribe_data.unicode.process_unicode import gen_emoji_lexicon
from scribe_data.utils import export_formatted_data

LANGUAGE = "Esperanto"
DATA_TYPE = "emoji-keywords"
emojis_per_keyword = 3

parser = argparse.ArgumentParser()
parser.add_argument("--file-path")
args = parser.parse_args()

if emoji_keywords_dict := gen_emoji_lexicon(
    language=LANGUAGE,
    emojis_per_keyword=emojis_per_keyword,
):
    export_formatted_data(
        file_path=args.file_path,
        formatted_data=emoji_keywords_dict,
        query_data_in_use=True,
        language=LANGUAGE,
        data_type=DATA_TYPE,
    )
