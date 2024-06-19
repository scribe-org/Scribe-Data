import json
from pathlib import Path
from .utils import LANGUAGE_METADATA, LANGUAGE_MAP, print_formatted_data

DATA_DIR = Path('scribe_data_json_export')

def query_data(all_data: bool, language: str = None, word_type: str = None, output_dir: str = None, overwrite: bool = False) -> None:
    if not (all_data or language or word_type):
        print("Error: You must provide at least one of --all, --language, or --word-type.")
        return

    if output_dir:
        output_dir = Path(output_dir).expanduser()  # Ensure it's a Path object and expand user (~)
        if output_dir.suffix:
            print("Error: The output path should be a directory, not a file.")
            return

        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)  # Create directories if they do not exist
        elif not output_dir.is_dir():
            print(f"Error: {output_dir} is not a directory.")
            return
    else:
        output_dir = None

    if all_data:
        for lang in LANGUAGE_METADATA['languages']:
            lang_dir = DATA_DIR / lang['language'].capitalize()
            if lang_dir.is_dir():
                for wt in lang_dir.glob('*.json'):
                    query_and_print_data(lang['language'], wt.stem, output_dir, overwrite)
    elif language and word_type:
        query_and_print_data(language, word_type, output_dir, overwrite)
    elif language:
        normalized_language = LANGUAGE_MAP.get(language.lower())
        if not normalized_language:
            print(f"Language '{language}' is not recognized.")
            return

        language_dir = DATA_DIR / normalized_language['language'].capitalize()
        if not language_dir.exists() or not language_dir.is_dir():
            print(f"No data found for language '{normalized_language['language']}'.")
            return

        for wt in language_dir.glob('*.json'):
            query_and_print_data(normalized_language['language'], wt.stem, output_dir, overwrite)
    elif word_type:
        for lang in LANGUAGE_METADATA['languages']:
            lang_dir = DATA_DIR / lang['language'].capitalize()
            if lang_dir.is_dir():
                wt_path = lang_dir / f"{word_type}.json"
                if wt_path.exists():
                    query_and_print_data(lang['language'], word_type, output_dir, overwrite)

def query_and_print_data(language: str, word_type: str, output_dir: Path, overwrite: bool) -> None:
    normalized_language = LANGUAGE_MAP.get(language.lower())
    if not normalized_language:
        print(f"Language '{language}' is not recognized.")
        return

    data_file = DATA_DIR / normalized_language['language'].capitalize() / f"{word_type}.json"
    if not data_file.exists():
        print(f"No data found for language '{normalized_language['language']}' and word type '{word_type}'.")
        return

    try:
        with data_file.open('r') as file:
            data = json.load(file)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading '{data_file}': {e}")
        return

    if output_dir:
        output_file = output_dir / f"{normalized_language['language']}_{word_type}.json"
        if output_file.exists() and not overwrite:
            user_input = input(f"File '{output_file}' already exists. Overwrite? (y/n): ")
            if user_input.lower() != 'y':
                print(f"Skipping {normalized_language['language']} - {word_type}")
                return

        try:
            with output_file.open('w') as file:
                json.dump(data, file, indent=2)
        except IOError as e:
            print(f"Error writing to '{output_file}': {e}")
            return
        print(f"Data for language '{normalized_language['language']}' and word type '{word_type}' written to '{output_file}'")
    else:
        print(f"Data for language '{normalized_language['language']}' and word type '{word_type}':")
        print_formatted_data(data, word_type)
