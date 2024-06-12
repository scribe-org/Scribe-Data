from pathlib import Path
from.utils import LANGUAGE_MAP

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

def list_all() -> None:
    list_languages()
    print()
    list_word_types()

def list_languages_for_word_type(word_type: str) -> None:
    available_languages = []
    for lang_dir in DATA_DIR.iterdir():
        if lang_dir.is_dir():
            wt_path = lang_dir / f"{word_type}.json"
            if wt_path.exists():
                available_languages.append(lang_dir.name)

    if not available_languages:
        print(f"No languages found with word type '{word_type}'.")
        return

    available_languages.sort()
    print(f"Languages with word type '{word_type}':")
    for lang in available_languages:
        print(f"- {lang}")

def list_wrapper(language: str = None, word_type: str = None) -> None:
    if language is None and word_type is None:
        list_all()
    elif language is True and word_type is None:
        list_languages()
    elif language is None and word_type is True:
        list_word_types()
    elif language is True and word_type is True:
        print("Please specify both a language and a word type.")
    elif language is True and word_type is not None:
        list_languages_for_word_type(word_type)
    elif language is not None and word_type is True:
        normalized_language = LANGUAGE_MAP.get(language.lower())
        if not normalized_language:
            print(f"Language '{language}' is not recognized.")
            return
        list_word_types(normalized_language)
    elif language is not None and word_type is not None:
        normalized_language = LANGUAGE_MAP.get(language.lower())
        if not normalized_language:
            print(f"Language '{language}' is not recognized.")
            return
        list_word_types(normalized_language)
