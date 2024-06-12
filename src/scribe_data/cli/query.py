# src/scribe_data/cli/query.py
import json
from pathlib import Path
from .utils import LANGUAGE_MAP, print_formatted_data

DATA_DIR = Path('scribe_data_json_export')

def query_data(all_data: bool, language: str = None, word_type: str = None) -> None:
    if not (all_data or language or word_type):
        print("Error: You must provide at least one of --all, --language, or --word-type.")
        return

    if all_data:
        for lang_dir in DATA_DIR.iterdir():
            if lang_dir.is_dir():
                for wt in lang_dir.glob('*.json'):
                    query_and_print_data(lang_dir.name, wt.stem)
    elif language and word_type:
        query_and_print_data(language, word_type)
    elif language:
        normalized_language = LANGUAGE_MAP.get(language.lower())
        if not normalized_language:
            print(f"Language '{language}' is not recognized.")
            return

        language_dir = DATA_DIR / normalized_language
        if not language_dir.exists() or not language_dir.is_dir():
            print(f"No data found for language '{normalized_language}'.")
            return

        for wt in language_dir.glob('*.json'):
            query_and_print_data(language, wt.stem)
    elif word_type:
        for lang_dir in DATA_DIR.iterdir():
            if lang_dir.is_dir():
                wt_path = lang_dir / f"{word_type}.json"
                if wt_path.exists():
                    query_and_print_data(lang_dir.name, word_type)

def query_and_print_data(language: str, word_type: str) -> None:
    normalized_language = LANGUAGE_MAP.get(language.lower())
    if not normalized_language:
        print(f"Language '{language}' is not recognized.")
        return

    data_file = DATA_DIR / normalized_language / f"{word_type}.json"
    if not data_file.exists():
        print(f"No data found for language '{normalized_language}' and word type '{word_type}'.")
        return

    try:
        with data_file.open('r') as file:
            data = json.load(file)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading '{data_file}': {e}")
        return

    print(f"Data for language '{normalized_language}' and word type '{word_type}':")
    print_formatted_data(data, word_type)
    