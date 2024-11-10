"""
Python script to replace the translation with the lower case version of the word if the following is found:
    - The key is lower case
    - The translation is not a German noun
"""

import json
import os
from pathlib import Path

from tqdm import tqdm

sub_folders = [f.path for f in os.scandir("scribe_data_json_export") if f.is_dir()]
sub_translation_files = [f"{f}/translations.json" for f in sub_folders]
german_noun_file = "scribe_data_json_export/German/nouns.json"

with Path(german_noun_file).open("r", encoding="utf-8") as file:
    german_nouns_dict = json.load(file)

german_nouns = []
for n in german_nouns_dict:
    german_nouns.append(n["nominativeSingular"])

    if "nominativePlural" in n.keys():
        german_nouns.append(n["nominativePlural"])

german_nouns = list(set(german_nouns))

for t in sub_translation_files:
    print(f"Fixing {t} translations...")
    new_translations_dict = {}
    with Path(t).open("r", encoding="utf-8") as file:
        translations_dict = json.load(file)

    for k in tqdm(
        translations_dict.keys(),
        desc="Translations converted",
        unit="translations",
    ):
        new_translations = {}
        if k[0].islower():
            for sub_key in translations_dict[k].keys():
                if (
                    sub_key == "de"
                    and translations_dict[k][sub_key] not in german_nouns
                ):
                    new_translations[sub_key] = translations_dict[k][sub_key].lower()

                else:
                    new_translations[sub_key] = translations_dict[k][sub_key]

        else:
            for sub_key in translations_dict[k].keys():
                new_translations[sub_key] = translations_dict[k][sub_key]

        new_translations_dict[k] = new_translations

    with open(t, "w") as file:
        json.dump(new_translations_dict, file, ensure_ascii=False, indent=0)
        file.close()
