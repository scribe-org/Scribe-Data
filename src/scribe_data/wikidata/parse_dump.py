# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for parsing Wikidata lexeme dumps.
"""

import bz2
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Union

import orjson
from rich import print as rprint
from tqdm import tqdm

from scribe_data.utils import (
    DEFAULT_DUMP_EXPORT_DIR,
    check_index_exists,
    check_qid_is_language,
    data_type_metadata,
    get_language_iso_code,
    language_metadata,
    lexeme_form_metadata,
)


class LexemeProcessor:
    def __init__(
        self,
        target_lang: Union[str, List[str]] = None,
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
        self.target_lang = set(
            [target_lang] if isinstance(target_lang, str) else target_lang or []
        )

        # Pre-compute valid categories and languages.
        self._category_lookup = {v: k for k, v in data_type_metadata.items()}
        self.valid_categories = set(data_type_metadata.values())

        # Build optimized language mapping.
        self.iso_to_name = self._build_iso_mapping()
        self.valid_iso_codes = set(self.iso_to_name.keys())

        # Separate data structures.
        self.translations_index = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        )
        self.forms_index = defaultdict(lambda: defaultdict(list))

        # Stats.
        self.stats = {"processed_entries": 0, "processing_time": 0}

        # For "total" usage.
        self.lexical_category_counts = defaultdict(Counter)
        self.translation_counts = defaultdict(Counter)
        self.forms_counts = defaultdict(Counter)

        # For "unique_forms" usage.
        self.unique_forms = defaultdict(lambda: defaultdict(list))

        # Cache for feature labels.
        self._feature_label_cache = {}
        for category, items in lexeme_form_metadata.items():
            for item_data in items.values():
                self._feature_label_cache[item_data["qid"]] = (
                    category,
                    item_data["label"],
                )

    # MARK: Build ISO Mapping

    def _build_iso_mapping(self) -> dict:
        """
        Build mapping of ISO codes to language names based on language_metadata.
        If self.target_lang is non-null, only include those iso codes.
        """
        iso_mapping = {}
        for lang_name, data in language_metadata.items():
            # Handle sub-languages if they exist.
            if "sub_languages" in data:
                for sub_lang, sub_data in data["sub_languages"].items():
                    if self.target_lang and sub_lang not in self.target_lang:
                        continue

                    if iso_code := sub_data.get("iso"):
                        iso_mapping[iso_code] = sub_lang
                continue  # skip main language if it only has sub-languages

            # Handle main languages.
            if self.target_lang and lang_name not in self.target_lang:
                continue

            if iso_code := data.get("iso"):
                iso_mapping[iso_code] = lang_name

        for language in self.target_lang:
            if language.lower().startswith("q") and language[1:].isdigit():
                if qid_to_lang := check_qid_is_language(language):
                    iso_code = get_language_iso_code(language.upper())
                    iso_mapping[iso_code] = qid_to_lang
                    print(f"ISO code for {language} is {iso_code}")

        return iso_mapping

    # MARK: Process Lines
    def process_lines(self, line: str) -> None:
        """
        Process one line of data with optimized parsing.
        """
        try:
            # Use faster exception handling.
            lexeme = orjson.loads(line.strip().rstrip(","))
            if not lexeme:
                return

            # Combine field checks into single lookup.
            required_fields = ("lemmas", "lexicalCategory")
            if any(field not in lexeme for field in required_fields):
                return

            lexical_category = lexeme["lexicalCategory"]
            if lexical_category not in self.valid_categories:
                return

            dt_name = self._category_lookup.get(lexical_category)
            if not dt_name:
                return

            # Process valid lemma only.
            for lang_iso, lemma_data in lexeme["lemmas"].items():
                if lang_iso not in self.valid_iso_codes:
                    continue

                word = lemma_data.get("value", "").lower()
                if not word:
                    continue

                parse_types = self.parse_type
                if "translations" in parse_types and lexeme.get("senses"):
                    self._process_translations(lexeme, word, lang_iso, dt_name)

                if "form" in parse_types and dt_name in self.data_types:
                    self._process_forms(lexeme, lang_iso, dt_name)

                if "total" in parse_types:
                    self._process_totals(lexeme, lang_iso, dt_name)

        except Exception as e:
            print(f"Error processing line: {e}")

    def _process_translations(self, lexeme, word, lang_iso, dt_name):
        """
        Optimized translations processing.
        """
        translations = {}
        valid_iso_codes = self.valid_iso_codes
        lexeme_id = lexeme["id"]
        modified_date = lexeme["modified"]

        # Pre-fetch senses to avoid repeated lookups.
        for sense in lexeme["senses"]:
            if glosses := sense.get("glosses"):
                translations.update(
                    (lang, gloss["value"])
                    for lang, gloss in glosses.items()
                    if lang in valid_iso_codes
                )

        if translations:
            # Update to store lastModified at the lexeme level.
            if lexeme_id not in self.translations_index[lang_iso][dt_name]:
                self.translations_index[lang_iso][dt_name][lexeme_id] = {
                    "lastModified": modified_date,
                    word: translations,
                }
            else:
                self.translations_index[lang_iso][dt_name][lexeme_id][word] = (
                    translations
                )

    def _process_forms(self, lexeme, lang_iso, dt_name):
        """
        Optimized forms processing with proper nested dictionary merging.
        Uses pipe-separated strings for form values to maintain uniqueness.
        """
        lexeme_id = lexeme["id"]
        language_qid = lexeme["language"]
        lexicalCategory = lexeme["lexicalCategory"]
        lastModified = lexeme["modified"]
        forms_data = {}

        # Pre-compute form data structure
        forms_dict = forms_data.setdefault(lexeme_id, {})
        lang_dict = forms_dict.setdefault(lang_iso, {})
        cat_dict = lang_dict.setdefault(dt_name, {})

        for form in lexeme.get("forms", []):
            if not (representations := form.get("representations")):
                continue

            for rep_lang_iso, rep_data in representations.items():
                if rep_lang_iso != lang_iso:
                    continue

                form_value = rep_data.get("value")

                if form_value:
                    features = form.get("grammaticalFeatures", [])

                    if (
                        features
                        and features
                        not in self.unique_forms[language_qid][lexicalCategory]
                    ):
                        self.unique_forms[language_qid][lexicalCategory].append(
                            features
                        )

                    if features := form.get("grammaticalFeatures"):
                        if form_name := self._get_form_name(features):
                            # If this form name already exists, merge values using comma separation.
                            if form_name in cat_dict:
                                existing_values = set(cat_dict[form_name].split(" | "))
                                existing_values.add(form_value)
                                cat_dict[form_name] = " | ".join(
                                    sorted(existing_values)
                                )
                            else:
                                cat_dict[form_name] = form_value

        if forms_data:
            for lexeme_id, new_lang_data in forms_data.items():
                if lexeme_id not in self.forms_index:
                    self.forms_index[lexeme_id] = {}

                for lang, new_cat_data in new_lang_data.items():
                    if lang not in self.forms_index[lexeme_id]:
                        self.forms_index[lexeme_id][lang] = {}

                    for cat, new_form_data in new_cat_data.items():
                        # If category already exists, merge the form data.
                        if cat in self.forms_index[lexeme_id][lang]:
                            existing_data = self.forms_index[lexeme_id][lang][cat]

                            # Merge form values.
                            for form_name, form_value in new_form_data.items():
                                if form_name in existing_data:
                                    existing_values = set(
                                        existing_data[form_name].split(" | ")
                                    )
                                    existing_values.add(form_value)
                                    existing_data[form_name] = " | ".join(
                                        sorted(existing_values)
                                    )
                                else:
                                    existing_data[form_name] = form_value
                        else:
                            # Store new forms and modified date.
                            self.forms_index[lexeme_id][lang][cat] = {
                                "lastModified": lastModified,
                                **new_form_data,
                            }

            self.forms_counts[lang_iso][dt_name] += len(forms_data)

    def _get_form_name(self, features):
        """
        Optimized form name generation.
        """
        if not features:
            return ""

        categorized_features = defaultdict(list)
        for feature in features:
            if feature_info := self._feature_label_cache.get(feature):
                category, label = feature_info
                categorized_features[category].append((label, feature))

        form_parts = []
        is_first = True
        for category in sorted(categorized_features.keys()):
            for label, _ in sorted(categorized_features[category]):
                if is_first:
                    form_parts.append(label.lower())
                    is_first = False

                else:
                    form_parts.append(label)

        return "".join(form_parts)

    def _process_totals(self, lexeme, lang_iso, dt_name):
        """
        Process totals for statistical counting.
        """
        # Skip if we have specific data types and this category isn't in them.
        if self.data_types and dt_name.lower() not in [
            dt.lower() for dt in self.data_types
        ]:
            return

        # Increment lexeme count for this language and category.
        self.lexical_category_counts[lang_iso][dt_name] += 1

        # Count translations if they exist.
        if lexeme.get("senses"):
            translation_count = sum(
                bool(
                    sense.get("glosses")
                    and any(
                        lang in self.valid_iso_codes for lang in sense["glosses"].keys()
                    )
                )
                for sense in lexeme["senses"]
            )
            if translation_count > 0:
                self.translation_counts[lang_iso][dt_name] += translation_count

    # MARK: Process File

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

    # MARK: Print Totals
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

    # MARK: Export Translations

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

            # Flatten the category level while preserving lastModified.
            filtered = {}
            for category_data in self.translations_index[language_iso].values():
                for lexeme_id, lexeme_data in category_data.items():
                    filtered[lexeme_id] = {
                        "lastModified": lexeme_data["lastModified"],
                        **{k: v for k, v in lexeme_data.items() if k != "lastModified"},
                    }

            lang_name = self.iso_to_name[language_iso]

            # Create the output directory structure.
            main_lang = None
            for lang, data in language_metadata.items():
                if "sub_languages" in data:
                    for sub_lang, sub_data in data["sub_languages"].items():
                        if sub_lang == lang_name:
                            main_lang = lang
                            break
                    if main_lang:
                        break

            # If it's a sub-language, then create a path like example/language/sublanguage/.
            if main_lang:
                output_path = Path(filepath).parent / main_lang / lang_name
            else:
                output_path = Path(filepath).parent / lang_name

            output_path.mkdir(parents=True, exist_ok=True)
            output_file = output_path / "translations.json"

            # Save the filtered data.
            try:
                with open(output_file, "wb") as f:
                    f.write(orjson.dumps(filtered, option=orjson.OPT_INDENT_2))
                print(
                    f"Successfully exported translations for {lang_name.capitalize()} to {output_file}"
                )
            except Exception as e:
                print(f"Error saving translations for {lang_name.capitalize()}: {e}")

    # MARK: Export Forms

    def export_forms_json(
        self, filepath: str, language_iso: str = None, data_type: str = None
    ):
        """
        Export grammatical forms to a JSON file with readable feature labels.

        Parameters
        ----------
        filepath : str
            Base path where the JSON file will be saved.

        language_iso : str, optional
            ISO code of the language to export. If None, exports all languages.

        data_type : str, optional
            Category of forms to export (e.g., "nouns", "verbs"). If None, exports all types.

        Notes
        -----
        Creates a directory structure: <filepath>/<language_name>/<data_type>.json
        Skips export if no forms are found for the specified language and data type.
        """
        if language_iso:
            if language_iso not in self.iso_to_name:
                print(f"Warning: ISO {language_iso} unknown, skipping forms export...")
                return

            filtered = {}
            has_multiple_forms = False

            # Process each lexeme in the forms_index.
            for lexeme_id, lang_data in self.forms_index.items():
                # Check if this lexeme has data for our target language.
                if language_iso in lang_data:
                    # Check if the language data contains our target data type.
                    if data_type in lang_data[language_iso]:
                        # Get the form data for this language and data type.
                        form_data = lang_data[language_iso][data_type]
                        filtered[lexeme_id] = form_data

                        # Check if any values contain pipe separator
                        if not has_multiple_forms:
                            for form_values in form_data.values():
                                if (
                                    isinstance(form_values, str)
                                    and " | " in form_values
                                ):
                                    has_multiple_forms = True
                                    break

            lang_name = self.iso_to_name[language_iso]

            if not filtered:
                print(
                    f"No forms found for {lang_name.capitalize()} {data_type}, skipping export..."
                )
                return

            # Create the output directory structure.
            main_lang = None
            for lang, data in language_metadata.items():
                if "sub_languages" in data:
                    for sub_lang, sub_data in data["sub_languages"].items():
                        if sub_lang == lang_name:
                            main_lang = lang
                            break
                    if main_lang:
                        break

            # If it's a sub-language, create path like: parent/chinese/mandarin/.
            if main_lang:
                output_path = Path(filepath).parent / main_lang / lang_name
            else:
                output_path = Path(filepath).parent / lang_name

            output_path.mkdir(parents=True, exist_ok=True)
            output_file = output_path / f"{data_type}.json"

            # Save the filtered data.
            try:
                with open(output_file, "wb") as f:
                    f.write(orjson.dumps(filtered, option=orjson.OPT_INDENT_2))

                print(
                    f"Successfully exported forms for {lang_name.capitalize()} {data_type} to {output_file}"
                )

                if has_multiple_forms:
                    rprint(
                        "[bold yellow]Note: Multiple versions of forms have been returned. These have been combined with '|' in the resulting data fields.[/bold yellow]"
                    )

            except Exception as e:
                print(
                    f"Error saving forms for {lang_name.capitalize()} {data_type}: {e}"
                )


# MARK: Parse Dump


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

    if "total" not in parse_type:
        # For translations, we only need to check the translations index.
        if "translations" in parse_type:
            languages_to_process = []
            for lang in languages:
                index_path = Path(output_dir) / lang / "translations.json"

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
                # Check if this is a sub-language
                main_lang = None
                for lang_name, data in language_metadata.items():
                    if "sub_languages" in data:
                        for sub_lang in data["sub_languages"]:
                            if sub_lang == lang:
                                main_lang = lang_name
                                break
                    if main_lang:
                        break

                for data_type in data_types:
                    # Create appropriate path based on whether it's a sub-language.
                    if main_lang:
                        index_path = (
                            Path(output_dir) / main_lang / lang / f"{data_type}.json"
                        )

                    else:
                        index_path = Path(output_dir) / lang / f"{data_type}.json"

                    if not check_index_exists(index_path, overwrite_all):
                        needs_processing = True
                        data_types_to_process.add(data_type)

                    else:
                        # Update path display in skip message.
                        skip_path = (
                            f"{main_lang}/{lang}/{data_type}.json"
                            if main_lang
                            else f"{lang}/{data_type}.json"
                        )
                        print(f"Skipping {skip_path} - already exists")

                if needs_processing:
                    languages_to_process.append(lang)

            # Update both lists.
            languages = languages_to_process
            data_types = list(data_types_to_process)

        if "translations" not in parse_type and (not data_types or not languages):
            print("No data types or languages provided. Nothing to process.")
            return

        if not languages:
            print("All requested data already exists. Nothing to process.")
            return

    processor = LexemeProcessor(
        target_lang=languages, parse_type=parse_type, data_types=data_types
    )
    processor.process_file(file_path)

    # MARK: Handle JSON Exports

    if "translations" in parse_type:
        for language in languages:
            if iso_code := next(
                (
                    iso
                    for iso, name in processor.iso_to_name.items()
                    if name.lower() == language.lower()
                ),
                None,
            ):
                index_path = Path(output_dir) / "translations.json"

                processor.export_translations_json(str(index_path), iso_code)
            else:
                print(f"Warning: Could not find ISO code for {language}")

    # If "form" in parse_type -> export forms for each data_type in data_types.
    if "form" in parse_type:
        # For each data_type, we create a separate file, e.g. nouns.json.
        for dt in data_types:
            index_path = Path(output_dir) / f"{dt}.json"
            iso_codes = set()
            for word_data in processor.forms_index.values():
                iso_codes.update(word_data.keys())

            for iso_code in iso_codes:
                if iso_code in processor.iso_to_name:
                    processor.export_forms_json(
                        filepath=str(index_path), language_iso=iso_code, data_type=dt
                    )
