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
