"""
Setup and commands for the Scribe-Data command line interface.

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

#!/usr/bin/env python3

import argparse
from .cli_list import list_languages, list_word_types
from .cli_query import query_data

def main() -> None:
    parser = argparse.ArgumentParser(description='Scribe-Data CLI Tool')
    subparsers = parser.add_subparsers(dest='command', required=True)

    subparsers.add_parser('list-languages', aliases=['ll'], help='List available languages')

    list_word_types_parser = subparsers.add_parser('list-word-types', aliases=['lwt'], help='List available word types')
    list_word_types_parser.add_argument('-l', '--language', help='Language code')

    query_parser = subparsers.add_parser('query', help='Query data for a specific language and word type')
    query_parser.add_argument('--all', action='store_true', help='Query all data')
    query_parser.add_argument('-l', '--language', help='Language code')
    query_parser.add_argument('-wt', '--word-type', help='Word type')

    args = parser.parse_args()

    if args.command in ['list-languages', 'll']:
        list_languages()
    elif args.command in ['list-word-types', 'lwt']:
        if args.language:
            list_word_types(args.language)
        else:
            list_word_types()
    elif args.command == 'query':
        query_data(args.all, args.language, args.word_type)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
