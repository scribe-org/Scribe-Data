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
from .list import list_wrapper
from .query import query_data

def main() -> None:
    parser = argparse.ArgumentParser(description='Scribe-Data CLI Tool')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # List command
    list_parser = subparsers.add_parser('list', help='List languages and word types')
    list_parser.add_argument('--language', '-l', nargs='?', const=True, help='List all languages or filter by language code')
    list_parser.add_argument('--word-type', '-wt', nargs='?', const=True, help='List all word types or filter by word type')

    # List word types command
    list_word_types_parser = subparsers.add_parser('list-word-types', aliases=['lwt'], help='List available word types')
    list_word_types_parser.add_argument('-l', '--language', help='Language code')

    # Query command
    query_parser = subparsers.add_parser('query', aliases=['q'], help='Query data for a specific language and word type')
    query_parser.add_argument('--all', action='store_true', help='Query all data')
    query_parser.add_argument('-l', '--language', help='Language code')
    query_parser.add_argument('-wt', '--word-type', help='Word type')
    query_parser.add_argument('-od', '--output-dir', help='Output directory')
    query_parser.add_argument('-o', '--overwrite', action='store_true', help='Overwrite existing files in output directory')

    args = parser.parse_args()

    if args.command == 'list':
        list_wrapper(args.language, args.word_type)
    elif args.command in ['list-word-types', 'lwt']:
        list_wrapper(None, args.language)
    elif args.command in ['query', 'q']:
        query_data(args.all, args.language, args.word_type, args.output_dir, args.overwrite)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
