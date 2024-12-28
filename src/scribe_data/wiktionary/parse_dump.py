"""
Functions for parsing Wikidata lexeme dumps.

.. raw:: html
    <!--
    * Copyright (C) 2024 Scribe
    *
    * This program is free software: you can redistribute it and/or modify
    * it under the terms of the GNU General Public License as published by
    * the Free Software Foundation, either version 3 of the License, or
    * (at your option) any later version.
    *
    * This program is distributed in the hope that it will be useful,
    * but WITHOUT ANY WARRANTY; without even the implied warranty of
    * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    * GNU General Public License for more details.
    *
    * You should have received a copy of the GNU General Public License
    * along with this program.  If not, see <https://www.gnu.org/licenses/>.
    -->
"""

import bz2
import orjson
import time
import json

from tqdm import tqdm
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Any
from scribe_data.utils import (
    DEFAULT_DUMP_EXPORT_DIR,
    language_metadata,
    data_type_metadata,
    check_index_exists,
)


class LexemeProcessor:
    def __init__(self, target_iso: str = None, parse_type: str = None):
        # Pre-compute lookups once during initialization
        self.word_index = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        self.stats = {"processed_entries": 0, "unique_words": 0, "processing_time": 0}
        self.target_iso = target_iso
        self.parse_type = parse_type
        self.lexical_category_counts = defaultdict(Counter)
        self.translation_counts = defaultdict(Counter)
        self._category_lookup = {v: k for k, v in data_type_metadata.items() if v}
        self.iso_to_name = self._build_iso_mapping()

    def _build_iso_mapping(self) -> dict:
        """Build mapping of ISO codes to language names"""
        iso_mapping = {}

        for lang_name, data in language_metadata.items():
            if self.target_iso and lang_name != self.target_iso:
                continue

            if "iso" in data:
                iso_mapping[data["iso"]] = lang_name

            if not self.target_iso and "sub_languages" in data:
                for sublang_data in data["sub_languages"].values():
                    if "iso" in sublang_data:
                        iso_mapping[sublang_data["iso"]] = lang_name

        return iso_mapping

    def _process_lexeme_translations(self, lexeme: dict) -> dict:
        """Process lexeme translations from lemmas and senses"""
        lemmas = lexeme.get("lemmas", {})
        qid = lexeme.get("lexicalCategory")

        # Early return if missing required data
        if not (lemmas and qid):
            return {}
        # Convert Qid to actual category name (e.g., Q1084 -> nouns)
        category_name = self._category_lookup.get(qid)
        if not category_name:
            return {}

        # Process first valid lemma
        for lang_code, lemma_data in lemmas.items():
            if lang_code not in self.iso_to_name:
                continue

            word = lemma_data.get("value", "").lower()
            if not word:
                continue

            # Collect all valid translations in one pass
            translations = {}
            for sense in lexeme.get("senses", []):
                for lang_code, gloss in sense.get("glosses", {}).items():
                    if lang_code in self.iso_to_name:
                        translations[lang_code] = gloss["value"]

            if translations:
                self.word_index[word][lang_code][category_name] = translations
                return {word: {lang_code: {category_name: translations}}}

            break  # Process only first valid lemma

        return {}

    def _process_lexeme_total(self, lexeme: dict) -> Dict[str, Any]:
        """
        Process lexeme forms from lemmas, datatype and senses.
        Returns a dictionary with word translations or empty dict if invalid.
        """

        lexicalCategory = lexeme.get("lexicalCategory")

        # Skip if lexicalCategory is missing or not in our data types
        if not lexicalCategory or lexicalCategory not in data_type_metadata.values():
            return {}
        lemmas = lexeme.get("lemmas", {})

        category_name = self._category_lookup.get(lexicalCategory)
        if not category_name:
            return {}

        # Process only the first valid language entry
        for lemma in lemmas.values():
            lang = lemma.get("language")
            if lang in self.iso_to_name:
                if lang not in self.lexical_category_counts:
                    self.lexical_category_counts[lang] = Counter()
                    self.translation_counts[lang] = Counter()
                # Update counts
                self.lexical_category_counts[lang][category_name] += 1
                translation_count = sum(
                    len(sense.get("glosses", {})) for sense in lexeme.get("senses", [])
                )
                self.translation_counts[lang][category_name] += translation_count
                break

        return {}

    def process_lines(self, line: str) -> Dict[str, Any]:
        """
        Process a single line of lexeme data.
        """
        try:
            lexeme = orjson.loads(line.strip().rstrip(","))

            if self.parse_type == "translations":
                return self._process_lexeme_translations(lexeme)
            elif self.parse_type == "total":
                return self._process_lexeme_total(lexeme)

        except Exception as e:
            print(f"Error processing line: {e}")
            return {}

    def process_file(self, file_path: str, batch_size: int = 50000):
        start_time = time.time()

        try:
            # Get file size and estimate number of entries (average 263 bytes per entry based on real data)
            total_entries = int(Path(file_path).stat().st_size / 263)

            with bz2.open(file_path, "rt", encoding="utf-8") as bzfile:
                first_line = bzfile.readline()
                if not first_line.strip().startswith("["):
                    bzfile.seek(0)

                batch = []
                for line in tqdm(
                    bzfile, desc="Processing entries", total=total_entries
                ):
                    stripped_line = line.strip()
                    if stripped_line in [
                        "]",
                        "[",
                        ",",
                        "",
                    ]:  # Skip structural JSON elements
                        continue

                    batch.append(line)

                    if len(batch) >= batch_size:
                        self._process_batch(batch)
                        batch = []

                    self.stats["processed_entries"] += 1

                # Process remaining items
                if batch:
                    self._process_batch(batch)

            self.stats["processing_time"] = time.time() - start_time
            self.stats["unique_words"] = len(self.word_index)
            print(
                f"Processed {self.stats['processed_entries']:,} entries in {self.stats['processing_time']:.2f} seconds"
            )
            if self.parse_type == "total":
                print(
                    f"{'Language':<20} {'Data Type':<25} {'Total Wikidata Lexemes':<25} {'Total Translations':<20}"
                )
                print("=" * 90)

                # Print counts for each language
                for lang, counts in self.lexical_category_counts.items():
                    lang_name = self.iso_to_name[lang]
                    # Print first row with language name
                    first_category = True
                    for category, count in counts.most_common():
                        translation_count = self.translation_counts[lang][category]
                        if first_category:
                            print(
                                f"{lang_name:<20} {category:<25} {count:<25,} {translation_count:<20,}"
                            )
                            first_category = False
                        else:
                            # Print subsequent rows with blank language column
                            print(
                                f"{'':<20} {category:<25} {count:<25,} {translation_count:<20,}"
                            )
                    # Add blank line between languages, but not after the last language
                    if lang != list(self.lexical_category_counts.keys())[-1]:
                        print(
                            f"\n{'Language':<20} {'Data Type':<25} {'Total Wikidata Lexemes':<25} {'Total Translations':<20}"
                        )
                        print("=" * 90)

        except FileNotFoundError:
            print(f"Error: File not found - {file_path}")
        except Exception as e:
            print(f"Error processing file: {e}")

    def _process_batch(self, batch: list) -> None:
        """
        Process multiple lines at once
        """
        for line in batch:
            self.process_lines(line)

    def export_json(self, filepath: str, language_iso: str = None) -> None:
        """
        Save index to file, optionally filtering by language ISO code.
        """
        if language_iso:
            # Only proceed if we have a valid ISO code
            if language_iso not in self.iso_to_name:
                print(f"Warning: Unknown ISO code {language_iso}, skipping...")
                return

            # Get full language name
            full_language_name = self.iso_to_name[language_iso]

            # Filter word_index for specific language
            filtered_index = {}
            for word, lang_data in self.word_index.items():
                if language_iso in lang_data:
                    filtered_index[word] = {language_iso: lang_data[language_iso]}

            # Create language-specific filepath, removing potential double paths
            base_path = Path(filepath)
            # Remove language name from base_path if it exists to prevent duplication
            if full_language_name in base_path.parts:
                parts = [p for p in base_path.parts if p != full_language_name]
                base_path = Path(*parts)

            lang_filepath = base_path.parent / full_language_name / base_path.name
            lang_filepath.parent.mkdir(parents=True, exist_ok=True)

            print(f"Saving {full_language_name} index to {lang_filepath}...")
            with open(lang_filepath, "w", encoding="utf-8") as f:
                json.dump(filtered_index, f, indent=2, ensure_ascii=False)
        else:
            print(f"Saving complete index to {filepath}...")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(
                    self._convert_defaultdict_to_dict(self.word_index),
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

    def _convert_defaultdict_to_dict(self, dd):
        if isinstance(dd, defaultdict):
            dd = {k: self._convert_defaultdict_to_dict(v) for k, v in dd.items()}
        return dd


def parse_dump(
    language: str = None,
    parse_type: str = None,
    type_output_dir: str = DEFAULT_DUMP_EXPORT_DIR,
    file_path: str = "latest-lexemes.json.bz2",
):
    """
    Process and parse Wikidata lexeme dumps, either analyzing all
    or filtering for a specific language.

    Parameters
    ----------
    language : str,
        ISO code of the language to process. If 'all', processes all languages.
    parse_type : str
        Type of parsing to perform. Options are:
        - 'total': Generate statistics about lexeme counts
        - 'translations': Create translation indexes
    type_output_dir : str
        Directory where output files will be saved. Defaults to DEFAULT_DUMP_EXPORT_DIR.
    file_path : str
        Path to the lexeme dump file. Defaults to 'latest-lexemes.json.bz2'.

    Notes
    -----
    When parse_type is 'total':
    - Total number of lexemes per language along with different lexical categories
    - Number of total translations available

    When parse_type is 'translations', it creates JSON index files containing:
    - Word-to-translation mappings
    - Lexical category information

    """
    if parse_type == "total":
        if language == "all":
            print("Processing all lexemes...")
            processor = LexemeProcessor(target_iso=None, parse_type=parse_type)
        else:
            print(f"Processing lexemes for {language}...")
            processor = LexemeProcessor(target_iso=language, parse_type=parse_type)

        processor.process_file(file_path)

    else:
        # Create the output directory if it doesn't exist
        Path(type_output_dir).mkdir(parents=True, exist_ok=True)

        if language:
            index_path = Path(type_output_dir) / language / f"lexeme_{parse_type}.json"
            if check_index_exists(index_path):
                return
        else:
            index_path = Path(type_output_dir) / f"lexeme_{parse_type}.json"
            if check_index_exists(index_path):
                return

        print(f"Will save index to: {index_path}")

        processor = LexemeProcessor(target_iso=language, parse_type=parse_type)

        print("Processing the lexeme data file...")
        processor.process_file(file_path)

        print(f"Found {len(processor.word_index)} words in total")

        # Get unique ISO codes from the processed data
        iso_codes = set()
        for word_data in processor.word_index.values():
            iso_codes.update(word_data.keys())

        # Save individual files for each valid language
        for iso_code in iso_codes:
            if iso_code in processor.iso_to_name:  # Only process known ISO codes
                processor.export_json(str(index_path), iso_code)
