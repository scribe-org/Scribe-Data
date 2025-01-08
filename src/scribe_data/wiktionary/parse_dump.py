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
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Union

import orjson
import questionary
from scribe_data.utils import (
    DEFAULT_DUMP_EXPORT_DIR,
    check_index_exists,
    data_type_metadata,
    language_metadata,
    get_language_iso_code,
    check_qid_is_language,
)
from tqdm import tqdm


class LexemeProcessor:
    def __init__(
        self,
        target_iso: Union[str, List[str]] = None,
        parse_type: List[str] = None,
        data_types: List[str] = None,
    ):
        """
        parse_type can be any combination of:
            - 'translations'
            - 'form'
            - 'total'
        data_types is a list of categories (e.g., ["nouns", "adverbs"]) for forms.
        """
        # Pre-compute sets for faster lookups.
        self.parse_type = set(parse_type or [])
        self.data_types = set(data_types or [])
        self.target_iso = set(
            [target_iso] if isinstance(target_iso, str) else target_iso or []
        )

        # Pre-compute valid categories and languages.
        self._category_lookup = {v: k for k, v in data_type_metadata.items()}
        self.valid_categories = set(data_type_metadata.values())

        # Build optimized language mapping.
        self.iso_to_name = self._build_iso_mapping()
        self.valid_iso_codes = set(self.iso_to_name.keys())

        # Separate data structures.
        self.translations_index = defaultdict(
            lambda: defaultdict(lambda: defaultdict(dict))
        )
        self.forms_index = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

        # Stats.
        self.stats = {"processed_entries": 0, "unique_words": 0, "processing_time": 0}

        # For category lookups, invert data_type_metadata.
        # E.g., {"Q1084": "nouns", "Q24905": "verbs", ...}.
        self._category_lookup = {v: k for k, v in data_type_metadata.items()}

        # Build map from ISO to full language name.
        self.iso_to_name = self._build_iso_mapping()
        # For "total" usage.
        self.lexical_category_counts = defaultdict(Counter)
        self.translation_counts = defaultdict(Counter)
        self.forms_counts = defaultdict(Counter)

    # MARK: build iso mapping
    def _build_iso_mapping(self) -> dict:
        """
        Build mapping of ISO codes to language names based on language_metadata.
        If self.target_iso is non-null, only include those iso codes.
        """
        iso_mapping = {}
        for lang_name, data in language_metadata.items():
            if self.target_iso and lang_name not in self.target_iso:
                continue

            if iso_code := data.get("iso"):
                iso_mapping[iso_code] = lang_name

        for language in self.target_iso:
            if (
                language.startswith("Q")
                or language.startswith("q")
                and language[1:].isdigit()
            ):
                qid_to_lang = check_qid_is_language(language)
                if qid_to_lang:
                    iso_code = get_language_iso_code(language.upper())
                    iso_mapping[iso_code] = qid_to_lang
                    print(f"ISO code for {language} is {iso_code}")

        return iso_mapping

    # MARK: process lines
    def process_lines(self, line: str) -> None:
        """
        Process one line of data. Depending on parse_type, we do:
            - total stats
            - translations
            - form categories (filtered by data_types)
        """
        try:
            lexeme = orjson.loads(line.strip().rstrip(","))
            if not lexeme:
                return

            # Get common values once.
            lemmas = lexeme.get("lemmas", {})
            lexical_category = lexeme.get("lexicalCategory")

            if not (lemmas and lexical_category in self.valid_categories):
                return

            category_name = self._category_lookup.get(lexical_category)
            if not category_name:
                return

            # Process each type in a single pass through the data.
            for lang_code, lemma_data in lemmas.items():
                if lang_code not in self.valid_iso_codes:
                    continue

                word = lemma_data.get("value", "").lower()
                if not word:
                    continue

                if "total" in self.parse_type:
                    self.lexical_category_counts[lang_code][category_name] += 1
                    translation_count = sum(
                        len(sense.get("glosses", {}))
                        for sense in lexeme.get("senses", [])
                    )
                    self.translation_counts[lang_code][category_name] += (
                        translation_count
                    )

                if "translations" in self.parse_type:
                    if translations := {
                        lang: gloss["value"]
                        for sense in lexeme.get("senses", [])
                        for lang, gloss in sense.get("glosses", {}).items()
                        if lang in self.valid_iso_codes
                    }:
                        self.translations_index[word][lang_code][category_name] = (
                            translations
                        )

                if "form" in self.parse_type and category_name in self.data_types:
                    forms_data = defaultdict(list)
                    for form in lexeme.get("forms", []):
                        for rep_lang, rep_data in form.get(
                            "representations", {}
                        ).items():
                            if rep_lang == lang_code:
                                if form_value := rep_data.get("value"):
                                    forms_data[form_value].extend(
                                        form.get("grammaticalFeatures", [])
                                    )

                    if forms_data:
                        self.forms_index[word][lang_code][category_name] = dict(
                            forms_data
                        )
                        self.forms_counts[lang_code][category_name] += len(forms_data)

                break  # only process first valid lemma

        except Exception as e:
            print(f"Error processing line: {e}")

    # MARK: process file
    def process_file(self, file_path: str, batch_size: int = 50000):
        """
        Main loop: read lines from file (bz2) in batches, call process_lines on each.
        """
        # Use context manager for better resource handling.
        with bz2.open(file_path, "rt", encoding="utf-8") as bzfile:
            # Skip header if present.
            first_line = bzfile.readline()
            if not first_line.strip().startswith("["):
                bzfile.seek(0)

            # Process in larger batches for better performance.
            batch = []
            start_time = time.time()
            total_entries = int(Path(file_path).stat().st_size / 263)

            for line in tqdm(bzfile, total=total_entries, desc="Processing entries"):
                if line.strip() not in ["[", "]", ",", ""]:
                    batch.append(line)

                    if len(batch) >= batch_size:
                        self._process_batch(batch)
                        batch.clear()  # more efficient than creating new list
                    self.stats["processed_entries"] += 1

            # Process remaining items.
            if batch:
                self._process_batch(batch)

        # Update stats.
        self.stats["processing_time"] = time.time() - start_time
        self.stats["unique_words"] = len(self.forms_index) + len(
            self.translations_index
        )

        # Print summary if "total" was requested.
        if "total" in self.parse_type:
            self._print_total_summary()

    def _process_batch(self, batch: list) -> None:
        """
        Process a batch of lines.
        """
        for line in batch:
            self.process_lines(line)

    # MARK: print total summary
    def _print_total_summary(self):
        """
        Print stats if parse_type == total.
        """
        print(
            f"{'Language':<20} {'Data Type':<25} {'Total Lexemes':<25} {'Total Translations':<20}"
        )
        print("=" * 90)
        for lang, counts in self.lexical_category_counts.items():
            lang_name = self.iso_to_name[lang]
            first_row = True

            for category, count in counts.most_common():
                trans_count = self.translation_counts[lang][category]

                if first_row:
                    print(
                        f"{lang_name:<20} {category:<25} {count:<25,} {trans_count:<20,}"
                    )
                    first_row = False

                else:
                    print(f"{'':<20} {category:<25} {count:<25,} {trans_count:<20,}")

            if lang != list(self.lexical_category_counts.keys())[-1]:
                print("\n" + "=" * 90 + "\n")

    # MARK: export translations
    def export_translations_json(self, filepath: str, language_iso: str = None) -> None:
        """
        Save translations_index to file, optionally filtering by language_iso.
        """
        if language_iso:
            if language_iso not in self.iso_to_name:
                print(
                    f"Warning: ISO {language_iso} unknown, skipping translations export..."
                )
                return

            filtered = {
                word: {language_iso: lang_data[language_iso]}
                for word, lang_data in self.translations_index.items()
                if language_iso in lang_data
            }

            # Check if filtered data is empty before saving.
            if not filtered:
                print(f"No translations found for {language_iso}, skipping export...")
                return

            self._save_by_language(filtered, filepath, language_iso, "translations")

    # MARK: export forms
    def export_forms_json(
        self, filepath: str, language_iso: str = None, data_type: str = None
    ) -> None:
        """
        Save forms_index to file, optionally filtering by:
            - language_iso
            - data_type (e.g. "nouns", "adverbs")

        If data_type is given, we only export that one category from forms.
        """
        if language_iso:
            if language_iso not in self.iso_to_name:
                print(f"Warning: ISO {language_iso} unknown, skipping forms export...")
                return

            filtered = {}
            for word, lang_data in self.forms_index.items():
                if language_iso in lang_data:
                    # If data_type is given, only keep that category.
                    if data_type:
                        if data_type in lang_data[language_iso]:
                            filtered[word] = {
                                language_iso: {
                                    data_type: lang_data[language_iso][data_type]
                                }
                            }

                    else:
                        filtered[word] = {language_iso: lang_data[language_iso]}

            # Check if filtered data is empty before saving.
            if not filtered:
                print(f"No forms found for {language_iso}, skipping export...")
                return

            self._save_by_language(
                filtered, filepath, language_iso, data_type or "forms"
            )

    def _save_by_language(self, data, filepath, language_iso, category_type):
        """
        Save data to exports/<langName>/filename.
        """
        base_path = Path(filepath)
        lang_name = self.iso_to_name[language_iso]

        lang_filepath = base_path.parent / lang_name / base_path.name
        lang_filepath.parent.mkdir(parents=True, exist_ok=True)

        print(f"Saving {lang_name} {category_type} index to {lang_filepath}...")
        with open(lang_filepath, "wb") as f:
            f.write(
                orjson.dumps(
                    self._to_dict(data),
                    option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS,
                )
            )

    def _to_dict(self, dd):
        """
        Recursively convert defaultdict to dict.
        """
        if isinstance(dd, defaultdict):
            dd = {k: self._to_dict(v) for k, v in dd.items()}

        return dd


# MARK: parse dump
def parse_dump(
    language: Union[str, List[str]] = None,
    parse_type: List[str] = None,
    data_types: List[str] = None,
    file_path: str = "latest-lexemes.json.bz2",
    output_dir: str = None,
    overwrite_all: bool = False,
):
    """
    Parse a Wikidata lexeme dump file and extract linguistic data.

    Parameters
    ----------
    language : str or list of str, optional
        Language(s) to parse data for. Must match language names in language_metadata.

    parse_type : list of str, optional
        Types of parsing to perform. Valid options are:
        - 'translations': Extract word translations
        - 'form': Extract grammatical forms
        - 'total': Gather statistical totals

    data_types : list of str, optional
        Categories to parse when using 'form' type (e.g. ["nouns", "adverbs"]).
        Only used if 'form' is in parse_type.

    file_path : str, default="latest-lexemes.json.bz2"
        Path to the lexeme dump file

    output_dir : str, optional
        Directory to save output files. If None, uses DEFAULT_DUMP_EXPORT_DIR.

    overwrite_all : bool, default=False
        If True, automatically overwrite existing files without prompting

    Notes
    -----
    The function processes a Wikidata lexeme dump and extracts linguistic data based on
    the specified parameters. For each language and data type combination, it creates
    separate JSON files in the output directory structure:

    If a requested index file already exists, that language/category combination
    will be skipped.
    """
    # Prepare environment - Use default if output_dir is None.
    output_dir = output_dir or DEFAULT_DUMP_EXPORT_DIR
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Convert single strings to lists.
    languages = [language] if isinstance(language, str) else language
    parse_type = parse_type or []
    data_types = data_types or []

    print(f"Languages: {languages}")
    print(f"parse_type: {parse_type}")
    if data_types:
        print(f"data_types for forms: {data_types}")

    if "total" not in parse_type:
        choice = questionary.select(
            "Choose an action:",
            choices=["Overwrite existing data", "Skip process"],
            default="Skip process",
        ).ask()
        if choice == "Overwrite existing data":
            overwrite_all = True

        # For translations, we only need to check the translations index.
        if "translations" in parse_type:
            languages_to_process = []
            for lang in languages:
                index_path = Path(output_dir) / lang / "lexeme_translations.json"

                if not check_index_exists(index_path, overwrite_all):
                    languages_to_process.append(lang)

                else:
                    print(f"Skipping {lang}/translations.json - already exists")

            # Update languages list but keep data_types as is.
            languages = languages_to_process

        # For forms, check each language/data_type combination.
        elif "form" in parse_type:
            languages_to_process = []
            data_types_to_process = set()

            for lang in languages:
                needs_processing = False
                for data_type in data_types:
                    index_path = Path(output_dir) / lang / f"lexeme_{data_type}.json"

                    if not check_index_exists(index_path, overwrite_all):
                        needs_processing = True
                        data_types_to_process.add(data_type)

                    else:
                        print(f"Skipping {lang}/{data_type}.json - already exists")

                if needs_processing:
                    languages_to_process.append(lang)

            # Update both lists.
            languages = languages_to_process
            data_types = list(data_types_to_process)

        print(f"Languages to process: {languages}")
        if data_types:
            print(f"Data types to process: {data_types}")

        if not languages:
            print("All requested data already exists. Nothing to process.")
            return

    processor = LexemeProcessor(
        target_iso=languages, parse_type=parse_type, data_types=data_types
    )
    processor.process_file(file_path)

    # MARK: Handle JSON exports

    # (a) If "translations" in parse_type -> export them.
    if "translations" in parse_type:
        index_path = Path(output_dir) / "lexeme_translations.json"

        # Export translations for each ISO found.
        iso_codes = set()
        for word_data in processor.translations_index.values():
            iso_codes.update(word_data.keys())
        for iso_code in iso_codes:
            if iso_code in processor.iso_to_name:
                processor.export_translations_json(str(index_path), iso_code)

    # (b) If "form" in parse_type -> export forms for each data_type in data_types.
    if "form" in parse_type:
        # For each data_type, we create a separate file, e.g. lexeme_nouns.json.
        for dt in data_types:
            index_path = Path(output_dir) / f"lexeme_{dt}.json"
            print(f"Exporting forms for {dt} to {index_path}...")

            iso_codes = set()
            for word_data in processor.forms_index.values():
                iso_codes.update(word_data.keys())

            for iso_code in iso_codes:
                if iso_code in processor.iso_to_name:
                    processor.export_forms_json(
                        filepath=str(index_path), language_iso=iso_code, data_type=dt
                    )
