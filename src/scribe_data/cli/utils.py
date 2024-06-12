from typing import Dict, List, Union, Optional
from difflib import SequenceMatcher

# Mapping of possible inputs to standardized language names
LANGUAGE_MAP = {
    'en': 'English', 'english': 'English',
    'fr': 'French', 'french': 'French',
    'de': 'German', 'german': 'German',
    'it': 'Italian', 'italian': 'Italian',
    'pt': 'Portuguese', 'portuguese': 'Portuguese',
    'ru': 'Russian', 'russian': 'Russian',
    'es': 'Spanish', 'spanish': 'Spanish',
    'sv': 'Swedish', 'swedish': 'Swedish'
}

def print_formatted_data(data: Union[Dict, List], word_type: str) -> None:
    if word_type == 'autosuggestions':
        max_key_length = max(len(key) for key in data.keys())
        for key, value in data.items():
            print(f"{key:<{max_key_length}} : {', '.join(value)}")
    elif word_type == 'emoji_keywords':
        max_key_length = max(len(key) for key in data.keys())
        for key, value in data.items():
            emojis = [item['emoji'] for item in value]
            print(f"{key:<{max_key_length}} : {' '.join(emojis)}")
    elif word_type == 'prepositions' or word_type == 'translations':
        max_key_length = max(len(key) for key in data.keys())
        for key, value in data.items():
            print(f"{key:<{max_key_length}} : {value}")
    else:
        if isinstance(data, dict):
            max_key_length = max(len(key) for key in data.keys())
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"{key:<{max_key_length}} : ")
                    max_sub_key_length = max(len(sub_key) for sub_key in value.keys())
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
