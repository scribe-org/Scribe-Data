"""
Setup and commands for the Scribe-Data command line interface.
"""

import os
import argparse

def list_languages():
    languages = [lang for lang in os.listdir('language_data_export') if os.path.isdir(f"language_data_export/{lang}")]
    print("Available languages:")
    for lang in languages:
        print(f"- {lang}")
        word_types = [wt.replace('.json', '') for wt in os.listdir(f"language_data_export/{lang}") if wt.endswith('.json')]
        max_word_type_length = max(len(wt) for wt in word_types)
        for wt in word_types:
            print(f"  - {wt:<{max_word_type_length}}")
        print("")  

def main():
    parser = argparse.ArgumentParser(description='Scribe-Data CLI Tool')
    parser.add_argument('--list-languages', '-ll', action='store_true', help='List available language codes and word types')
    args = parser.parse_args()

    if args.list_languages:
        list_languages()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
