import json
import os
import signal
import sys

PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

from scribe_data.utils import translate_to_other_languages, translation_interrupt_handler

translate_script_dir = os.path.dirname(os.path.abspath(__file__))
words_to_translate_path = os.path.join(translate_script_dir, 'words_to_translate.json')

with open(words_to_translate_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

word_list = []
for item in json_data:
    word_list.append(item["word"])

src_lang="Russian"

translations = {}
translated_words_path = os.path.join(translate_script_dir, '../formatted_data/translated_words.json')
if os.path.exists(translated_words_path):
    with open(translated_words_path, 'r', encoding='utf-8') as file:
        translations = json.load(file)

signal.signal(signal.SIGINT, lambda sig, frame: translation_interrupt_handler(src_lang, translations))

translate_to_other_languages(src_lang, word_list, translations)