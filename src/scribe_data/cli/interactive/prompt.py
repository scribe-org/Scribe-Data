# SPDX-License-Identifier: GPL-3.0-or-later
"""
Interactive mode prompting for the Scribe-Data CLI to allow users to select request arguments.
"""

from pathlib import Path

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich import print as rprint

from scribe_data.cli.interactive.config import interactive_mode_config
from scribe_data.utils import DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR, resolve_lang_iso

# MARK: Word Completion


def create_word_completer(
    options: list[str], include_all: bool = False
) -> WordCompleter:
    """
    Return a word completer object of the given options.

    Parameters
    ----------
    options : List[str]
        The options that could complete the current input.

    include_all : bool
        Whether 'All' should be an option.

    Returns
    -------
    WordCompleter
        The word completer object from which completions can be shown to the user.
    """
    if include_all:
        options = ["All"] + options

    return WordCompleter(options, ignore_case=True)


# MARK: Language Selection


def prompt_for_languages() -> None:
    """
    Request language and data type for lexeme totals.

    Returns
    -------
    None
        Languages are added to the configuration or are asked for.
    """
    language_completer = create_word_completer(
        interactive_mode_config.languages, include_all=True
    )
    initial_language_selection = ", ".join(interactive_mode_config.selected_languages)
    selected_languages = prompt(
        "Select languages (comma-separated or 'All'): ",
        default=initial_language_selection,
        completer=language_completer,
    )
    if "All" in selected_languages:
        interactive_mode_config.selected_languages = interactive_mode_config.languages

    elif selected_languages.strip():  # check if input is not just whitespace
        interactive_mode_config.selected_languages = [
            lang.strip()
            for lang in selected_languages.split(",")
            if lang.strip() in interactive_mode_config.languages
        ]

    if not interactive_mode_config.selected_languages:
        rprint("[yellow]No language selected. Please try again.[/yellow]")
        return prompt_for_languages()


def _wiktionary_dump_search_dirs(location: Path) -> list[Path]:
    """
    Build an ordered list of directories to search for Wiktionary dumps.

    Each candidate directory is resolved and included only if it exists.
    Duplicate paths are omitted while preserving the following search order:

    1. The provided ``location`` directory.
    2. The default export directory (:data:`~scribe_data.utils.DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR`).
    3. The default export directory under every ancestor of the current working directory.
    4. The current working directory itself.

    Searching ancestor directories allows dumps to be found when the interactive mode
    is started from a nested folder (e.g., ``scribe_data_wiktionary_json_export/spanish``).

    Parameters
    ----------
    location : Path
        User-supplied dump path or search root from
        :func:`resolve_wiktionary_dump_path`.

    Returns
    -------
    list[Path]
        A deduplicated list of existing directories to search.
    """
    candidates = [
        location,
        DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR,
        *(parent / DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR for parent in Path.cwd().parents),
        Path.cwd(),
    ]
    resolved_paths = [path.expanduser().resolve() for path in candidates]
    return list(dict.fromkeys(path for path in resolved_paths if path.is_dir()))


def resolve_wiktionary_dump_path(language: str, location: str | Path) -> Path | None:
    """
    Resolve a Wiktionary dump file for the given source language.

    Locates the newest Wiktionary XML dump for the specified language.
    If the ``location`` argument points directly to a file, that file is returned.
    Otherwise, it searches through a prioritized list of directories for dumps
    matching the ``{iso}wiktionary*pages-articles.xml*`` pattern.

    Parameters
    ----------
    language : str
        Source language name (e.g. ``german``).

    location : str or Path
        Path to a specific dump file, or a base directory to begin searching from.

    Returns
    -------
    Path or None
        The path to the newest matching dump file, the explicit file if ``location``
        is a file, or ``None`` if no matching dump is found.
    """
    path = Path(location).expanduser().resolve()
    if path.is_file():
        return path

    if not (iso := resolve_lang_iso(language)):
        return None

    dumps = [
        dump_path
        for search_dir in _wiktionary_dump_search_dirs(path)
        for dump_path in search_dir.glob(f"{iso}wiktionary*pages-articles.xml*")
    ]
    return (
        max(dumps, key=lambda dump_path: dump_path.stat().st_mtime).resolve()
        if dumps
        else None
    )


# MARK: Data Type Selection


def prompt_for_data_types() -> None:
    """
    Prompt the user to select data types.

    Returns
    -------
    None
        Data types are added to the configuration or are asked for.
    """
    data_type_completer = create_word_completer(
        interactive_mode_config.data_types, include_all=True
    )
    initial_data_type_selection = ", ".join(interactive_mode_config.selected_data_types)

    while True:
        selected_data_types = prompt(
            "Select data types (comma-separated or 'All'): ",
            default=initial_data_type_selection,
            completer=data_type_completer,
        )
        if "All" in selected_data_types.capitalize():
            interactive_mode_config.selected_data_types = (
                interactive_mode_config.data_types
            )
            break

        elif selected_data_types.strip():  # check if input is not just whitespace
            interactive_mode_config.selected_data_types = [
                dt.strip()
                for dt in selected_data_types.split(",")
                if dt.strip() in interactive_mode_config.data_types
            ]
            if interactive_mode_config.selected_data_types:
                break  # exit loop if valid data types are selected

        rprint("[yellow]No data type selected. Please try again.[/yellow]")
