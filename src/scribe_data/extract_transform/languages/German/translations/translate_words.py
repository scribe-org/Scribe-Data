import json
import os
import sys

# Set up paths
PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

# Import the translation function
from scribe_data.utils import translate_to_other_languages

# Set the source language to German
SRC_LANG = "German"
# Get the directory of the current script
translate_script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the full path to the words_to_translate.json file
words_to_translate_path = os.path.join(translate_script_dir, "words_to_translate.json")

# Load words to be translated
with open(words_to_translate_path, "r", encoding="utf-8") as file:
    json_data = json.load(file)
word_list = [item["word"] for item in json_data]

# Initialize the translations dictionary
translations = {}

# Check if the translated words file already exists to append translations
translated_words_path = os.path.join(
    translate_script_dir, "../formatted_data/translated_words.json"
)
if os.path.exists(translated_words_path):
    with open(translated_words_path, "r", encoding="utf-8") as file:
        translations = json.load(file)

# Set the batch size to a smaller number to reduce memory usage
BATCH_SIZE = 10

# Add a try-except block to catch any exceptions and log progress
try:
    # Log the start of translation
    print("Starting the translation process...")
    
    # Perform the translation
    translate_to_other_languages(
        source_language=SRC_LANG,
        word_list=word_list,
        translations=translations,
        batch_size=BATCH_SIZE,
    )
    
    # Log the completion of translation
    print("Translation process completed.")
except Exception as e:
    print(f"An error occurred: {e}")

# Save the translations back to the file
try:
    with open(translated_words_path, "w", encoding="utf-8") as file:
        json.dump(translations, file, ensure_ascii=False, indent=4)
    print(f"Translations saved to {translated_words_path}")
except Exception as e:
    print(f"An error occurred while saving translations: {e}")
