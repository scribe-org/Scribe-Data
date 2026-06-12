# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions to check the total language data available on Wikidata.
"""

from pathlib import Path

from scribe_data.cli.total.print_values import print_total_lexemes
from scribe_data.cli.total.query import query_total_lexemes
from scribe_data.utils import DEFAULT_WIKIDATA_DUMP_EXPORT_DIR
from scribe_data.wikidata.wikidata_utils import parse_wd_lexeme_dump

# MARK: Wrapper


def total_wrapper(
    languages: list[str] | None = None,
    data_types: list[str] | None = None,
    all_bool: bool = False,
    wikidata_dump: Path | bool | None = None,
) -> None:
    """
    Conditionally provides the full functionality of the total command.

    Parameters
    ----------
    languages : List[str]
        The language(s) to potentially total data types for.

    data_types : List[str]
        The data type(s) to check for.

    all_bool : bool
        Whether all languages and data types should be listed.

    wikidata_dump : Optional[Union[Path, bool]]
        The local Wikidata lexeme dump path that can be used to process data.
        If True, indicates the flag was used without a path.

    Notes
    -----
    Now accepts lists for language and data type to output a table of total lexemes.
    """
    # Note: Handle --all flag via 'or ["all"]' assignments.
    # Flag without a wikidata lexeme dump path.
    if wikidata_dump is True:
        parse_wd_lexeme_dump(
            languages=languages or ["all"],
            data_types=data_types or ["all"],
            wikidata_dump_type=["total"],
            wikidata_dump_path=DEFAULT_WIKIDATA_DUMP_EXPORT_DIR,
        )
        return

    # If user provided a wikidata lexeme dump path.
    if isinstance(wikidata_dump, Path):
        parse_wd_lexeme_dump(
            languages=languages or ["all"],
            data_types=data_types or ["all"],
            wikidata_dump_type=["total"],
            wikidata_dump_path=wikidata_dump,
        )
        return

    language = languages[0] if languages else None  # in case only one is passed
    data_type = data_types[0] if data_types else None  # in case only one is passed

    if (not languages and not data_types) and all_bool:
        print_total_lexemes()

    elif languages and data_types and (len(languages) > 1 or len(data_types) > 1):
        print(f"{'Language':<20} {'Data Type':<25} {'Total Wikidata Lexemes':<25}")
        print("=" * 70)

        for lang in languages:
            # Flag to check if it's the first data type for the language.
            first_row = True

            for dt in data_types:
                total_lexemes = query_total_lexemes(
                    language=lang, data_type=dt, do_print=False
                )
                total_lexemes = (
                    f"{int(total_lexemes):,}" if total_lexemes is not None else "N/A"
                )
                if first_row:
                    print(f"{lang:<20} {dt:<25} {total_lexemes:<25}")
                    first_row = False

                else:
                    print(
                        f"{'':<20} {dt:<25} {total_lexemes:<25}"
                    )  # print empty space for language

            print()

    elif language is not None and data_type is None:
        print_total_lexemes(language=language)

    elif language is not None and data_type is not None and not all_bool:
        query_total_lexemes(language=language, data_type=data_type)

    elif language is not None and data_type is not None:
        print(
            f"You have already specified language {language.capitalize()} and data type {data_type} - no need to specify --all."
        )
        query_total_lexemes(language=language, data_type=data_type)

    else:
        raise ValueError("Invalid input or missing information")
