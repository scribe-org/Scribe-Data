import json
from pathlib import Path
from typing import Dict, List, Union

# Load language metadata from JSON file
METADATA_FILE = Path(__file__).parent.parent / 'resources' / 'language_meta_data.json'

def load_language_metadata() -> Dict:
    with METADATA_FILE.open('r', encoding='utf-8') as file:
        return json.load(file)

LANGUAGE_METADATA = load_language_metadata()
LANGUAGE_MAP = {lang['language'].lower(): lang for lang in LANGUAGE_METADATA['languages']}

DATA_DIR = Path('scribe_data_json_export')

def print_formatted_data(data: Union[Dict, List], word_type: str) -> None:
    if not data:
        print(f"No data available for word type '{word_type}'.")
        return

    if word_type == 'autosuggestions':
        max_key_length = max((len(key) for key in data.keys()), default=0)
        for key, value in data.items():
            print(f"{key:<{max_key_length}} : {', '.join(value)}")
    elif word_type == 'emoji_keywords':
        max_key_length = max((len(key) for key in data.keys()), default=0)
        for key, value in data.items():
            emojis = [item['emoji'] for item in value]
            print(f"{key:<{max_key_length}} : {' '.join(emojis)}")
    elif word_type in ['prepositions', 'translations']:
        max_key_length = max((len(key) for key in data.keys()), default=0)
        for key, value in data.items():
            print(f"{key:<{max_key_length}} : {value}")
    else:
        if isinstance(data, dict):
            max_key_length = max((len(key) for key in data.keys()), default=0)
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"{key:<{max_key_length}} : ")
                    max_sub_key_length = max((len(sub_key) for sub_key in value.keys()), default=0)
                    for sub_key, sub_value in value.items():
                        print(f"  {sub_key:<{max_sub_key_length}} : {sub_value}")
                elif isinstance(value, list):
                    print(f"{key:<{max_key_length}} : ")
                    for item in value:
                        if isinstance(item, dict):
                            for sub_key, sub_value in item.items():
                                print(f"  {sub_key:<{max_key_length}} : {sub_value}")
                        else:
                            print(f"  {item}")
                else:
                    print(f"{key:<{max_key_length}} : {value}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        print(f"{key} : {value}")
                else:
                    print(item)
        else:
            print(data)

def list_languages() -> None:
    languages = [lang for lang in LANGUAGE_METADATA['languages']]
    languages.sort(key=lambda x: x['language'])

    # Define column widths
    language_col_width = max(len(lang['language']) for lang in languages) + 2
    iso_col_width = 5  # Length of "ISO" column header + padding
    qid_col_width = 5  # Length of "QID" column header + padding

    print(f"{'Language':<{language_col_width}} {'ISO':<{iso_col_width}} {'QID':<{qid_col_width}}")
    print('-' * (language_col_width + iso_col_width + qid_col_width))

    for lang in languages:
        print(f"{lang['language'].capitalize():<{language_col_width}} {lang['iso']:<{iso_col_width}} {lang['qid']:<{qid_col_width}}")

def list_word_types(language: str = None) -> None:
    if language:
        normalized_language = LANGUAGE_MAP.get(language.lower())
        if not normalized_language:
            print(f"Language '{language}' is not recognized.")
            return

        language_dir = DATA_DIR / normalized_language['language'].capitalize()
        if not language_dir.exists() or not language_dir.is_dir():
            print(f"No data found for language '{normalized_language['language']}'.")
            return

        word_types = [wt.stem for wt in language_dir.glob('*.json')]
        if not word_types:
            print(f"No word types available for language '{normalized_language['language']}'.")
            return

        word_types = sorted(word_types)
        print(f"Word types for language '{normalized_language['language']}':")
        for wt in word_types:
            print(f"  - {wt}")
    else:
        word_types = set()
        for lang in LANGUAGE_METADATA['languages']:
            language_dir = DATA_DIR / lang['language'].capitalize()
            if language_dir.is_dir():
                word_types.update(wt.stem for wt in language_dir.glob('*.json'))

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
    for lang in LANGUAGE_METADATA['languages']:
        language_dir = DATA_DIR / lang['language'].capitalize()
        if language_dir.is_dir():
            wt_path = language_dir / f"{word_type}.json"
            if wt_path.exists():
                available_languages.append(lang['language'])

    if not available_languages:
        print(f"No languages found with word type '{word_type}'.")
        return

    available_languages.sort()
    print(f"Languages with word type '{word_type}':")
    for lang in available_languages:
        print(f"- {lang.capitalize()}")

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
        list_word_types(language)
    elif language is not None and word_type is not None:
        list_word_types(language)
