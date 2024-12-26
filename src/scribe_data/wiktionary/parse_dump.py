import bz2
import orjson
from collections import defaultdict
import time
import json
from typing import Dict, Any
from pathlib import Path
from scribe_data.utils import DEFAULT_DUMP_EXPORT_DIR
from scribe_data.utils import language_metadata
from tqdm import tqdm
from collections import Counter

from scribe_data.utils import data_type_metadata


class LexemeProcessor:
    def __init__(self, target_iso: str = None, parse_type: str = None):
        self.word_index = {}
        self.stats = {"processed_entries": 0, "unique_words": 0, "processing_time": 0}
        self.target_iso = target_iso
        self.parse_type = parse_type
        self.lexical_category_counts = {}
        self.translation_counts = {}
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
        q_code = lexeme.get("lexicalCategory")

        # Convert Q-code to actual category name (e.g., Q1084 -> nouns)
        category_name = self._category_lookup.get(q_code)

        if not (lemmas and category_name):
            return {}

        try:
            first_lang, first_lemma = next(iter(lemmas.items()))
            word = first_lemma.get("value", "").lower()
            word_lang = first_lemma.get("language", "")

            if not (word and word_lang in self.iso_to_name):
                return {}

            translations = {
                lang_code: gloss["value"]
                for sense in lexeme.get("senses", [])
                for lang_code, gloss in sense.get("glosses", {}).items()
                if lang_code in self.iso_to_name
            }

            if translations:
                if word not in self.word_index:
                    self.word_index[word] = {}
                if word_lang not in self.word_index[word]:
                    self.word_index[word][word_lang] = {}

                self.word_index[word][word_lang][category_name] = translations
                return {word: {word_lang: {category_name: translations}}}

        except (StopIteration, AttributeError):
            pass

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

    def process_file(self, file_path: str, batch_size: int = 1000) -> None:
        start_time = time.time()

        try:
            # Get file size and estimate number of entries (average 263 bytes per entry based on real data)
            total_entries = int(Path(file_path).stat().st_size / 263)

            with bz2.open(file_path, "rt", encoding="utf-8") as bzfile:
                first_line = bzfile.readline()
                if not first_line.strip().startswith("["):
                    bzfile.seek(0)

                batch = []
                # Use dynamic total based on file size
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
        for line in batch:
            # self.process_lines_for_forms(line)
            self.process_lines(line)

    def save_index(self, filepath: str, language_iso: str = None) -> None:
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

            # Create language-specific filepath using full name
            base_path = Path(filepath)
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

    def load_index(self, filepath: str) -> None:
        print(f"Loading index from {filepath}...")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                self.word_index = defaultdict(
                    lambda: defaultdict(lambda: defaultdict(dict))
                )
                self._recursive_update(self.word_index, loaded_data)
        except FileNotFoundError:
            print(f"Error: Index file not found - {filepath}")
        except Exception as e:
            print(f"Error loading index: {e}")

    def _recursive_update(self, dd, data):
        for key, value in data.items():
            if isinstance(value, dict):
                dd[key] = defaultdict(lambda: defaultdict(dict))
                self._recursive_update(dd[key], value)
            else:
                dd[key] = value

    def get_word_info(self, word: str) -> Dict[str, Any]:
        return self.word_index.get(word.lower(), {})


def parse_dump(
    language: str = None,
    parse_type: str = None,
    type_output_dir: str = DEFAULT_DUMP_EXPORT_DIR,
    file_path: str = "latest-lexemes.json.bz2",
):
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

        index_path = Path(type_output_dir) / f"lexeme_index_{parse_type}.json"
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
                processor.save_index(str(index_path), iso_code)
