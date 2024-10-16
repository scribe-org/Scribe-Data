from scribe_data.cli.cli_utils import (
    LANGUAGE_DATA_EXTRACTION_DIR,
    data_type_metadata,
)


def check_data_type_metadata(output_file):
    """
    Check that subdirectories named for data types in language directories
    are also reflected in the data_type_metadata.json file, accounting for meta-languages.
    """
    # Extract valid data types from data_type_metadata
    valid_data_types = set(data_type_metadata.keys())

    def check_language_subdirs(lang_dir, meta_lang=None):
        discrepancies = []
        
        for language in lang_dir.iterdir():
            if language.is_dir():
                meta_language = meta_lang or language.name.lower()
                data_types_in_dir = []
                
                for data_type in language.iterdir():
                    if data_type.is_dir():
                        data_types_in_dir.append(data_type.name.lower())
                
                # Compare with valid data types
                missing_data_types = set(data_types_in_dir) - valid_data_types
                extra_data_types = valid_data_types - set(data_types_in_dir)
                
                if missing_data_types:
                    discrepancies.append(f"Missing in metadata for '{meta_language}': {missing_data_types}")
                if extra_data_types:
                    discrepancies.append(f"Extra in directory for '{meta_language}': {extra_data_types}")
                
                # Recursively check sub-languages (if applicable)
                sub_lang_dir = language / 'sub-languages'
                if sub_lang_dir.exists():
                    discrepancies.extend(check_language_subdirs(sub_lang_dir, meta_language))
        
        return discrepancies

    # Start checking from the base language directory
    discrepancies = check_language_subdirs(LANGUAGE_DATA_EXTRACTION_DIR)

    # Store discrepancies in the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        if discrepancies:
            for discrepancy in discrepancies:
                f.write(discrepancy + '\n')
        else:
            f.write("All data type metadata is up-to-date!\n")
    
    print(f"Discrepancies stored in: {output_file}")
