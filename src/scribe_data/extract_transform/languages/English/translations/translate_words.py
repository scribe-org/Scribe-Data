"""
Translates the English words queried from Wikidata to all other Scribe languages.
"""

import json
import os
import signal

from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer


def translate_words(words_path: str):
    with open(words_path, "r", encoding="utf-8") as file:
        words_json_data = json.load(file)

    word_list = []

    for item in words_json_data:
        word_list.append(item["word"])

    model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
    tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

    with open(
        "../../../../../scribe_data/resources/language_meta_data.json",
        "r",
        encoding="utf-8",
    ) as file:
        lang_json_data = json.load(file)
    iso_list = [lang["iso"] for lang in lang_json_data["languages"]]

    target_languages = iso_list

    translations = []

    if os.path.exists("../formatted_data/translated_words.json"):
        with open(
            "../formatted_data/translated_words.json", "r", encoding="utf-8"
        ) as file:
            translations = json.load(file)

    def signal_handler(sig, frame):
        print(
            "\nThe interrupt signal has been caught and the current progress is being saved..."
        )
        with open(
            "../formatted_data/translated_words.json", "w", encoding="utf-8"
        ) as file:
            json.dump(translations, file, ensure_ascii=False, indent=4)
            file.write("\n")

        print("The current progress has been saved to the translated_words.json file.")
        exit()

    signal.signal(signal.SIGINT, signal_handler)

    for word in word_list[len(translations) :]:
        word_translations = {word: {}}
        for lang_code in target_languages:
            tokenizer.src_lang = "en"
            encoded_word = tokenizer(word, return_tensors="pt")
            generated_tokens = model.generate(
                **encoded_word, forced_bos_token_id=tokenizer.get_lang_id(lang_code)
            )
            translated_word = tokenizer.batch_decode(
                generated_tokens, skip_special_tokens=True
            )[0]
            word_translations[word][lang_code] = translated_word

        translations.append(word_translations)

        with open(
            "../formatted_data/translated_words.json", "w", encoding="utf-8"
        ) as file:
            json.dump(translations, file, ensure_ascii=False, indent=4)
            file.write("\n")

        print(f"Translation results for the word '{word}' have been saved.")

    print(
        "Translation results for all words are saved to the translated_words.json file."
    )


if __name__ == "__main__":
    translate_words("words_to_translate.json")
