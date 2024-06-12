# import os
from pathlib import Path
from .cli_utils import LANGUAGE_MAP

DATA_DIR = Path('scribe_data_json_export')

def list_languages() -> None:
    if not DATA_DIR.exists() or not DATA_DIR.is_dir():
        print(f"Directory '{DATA_DIR}' does not exist.")
        return

    languages = [lang.name for lang in DATA_DIR.iterdir() if lang.is_dir()]
    languages.sort()
    print("Available languages:")
    for lang in languages:
        print(f"- {lang}")

def list_word_types(language: str = None) -> None:
    if language:
        normalized_language = LANGUAGE_MAP.get(language.lower())
        if not normalized_language:
            print(f"Language '{language}' is not recognized.")
            return

        language_dir = DATA_DIR / normalized_language
        if not language_dir.exists() or not language_dir.is_dir():
            print(f"No data found for language '{normalized_language}'.")
            return

        word_types = [wt.stem for wt in language_dir.glob('*.json')]
        if not word_types:
            print(f"No word types available for language '{normalized_language}'.")
            return

        max_word_type_length = max(len(wt) for wt in word_types)
        print(f"Word types for language '{normalized_language}':")
        for wt in word_types:
            print(f"  - {wt:<{max_word_type_length}}")
    else:
        word_types = set()
        for lang_dir in DATA_DIR.iterdir():
            if lang_dir.is_dir():
                word_types.update(wt.stem for wt in lang_dir.glob('*.json'))

        if not word_types:
            print("No word types available.")
            return

        word_types = sorted(word_types)
        print("Available word types:")
        for wt in word_types:
            print(f"  - {wt}")
