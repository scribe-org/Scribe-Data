# SPDX-License-Identifier: GPL-3.0-or-later
"""
Interactive mode functionality for the Scribe-Data CLI to allow users to select request arguments.
"""

import logging
from pathlib import Path
from typing import List, Optional, Union

import questionary
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich import print as rprint
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from tqdm import tqdm

from scribe_data.cli.convert import convert_wrapper

# from scribe_data.cli.list import list_wrapper
from scribe_data.cli.get import get_data
from scribe_data.cli.total import total_wrapper
from scribe_data.utils import (
    DEFAULT_JSON_EXPORT_DIR,
    DEFAULT_SQLITE_EXPORT_DIR,
    DEFAULT_WIKIDATA_DUMP_EXPORT_DIR,
    DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR,
    DEFAULT_WIKTIONARY_JSON_EXPORT_DIR,
    data_type_metadata,
    language_metadata,
    list_all_languages,
    resolve_lang_iso,
)
from scribe_data.wikidata.wikidata_utils import parse_wd_lexeme_dump

# MARK: Config Setup

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],  # Enable markup for colors
)
console = Console()
logger = logging.getLogger("rich")
THANK_YOU_MESSAGE = "[bold cyan]Thank you for using Scribe-Data![/bold cyan]"


class ScribeDataConfig:
    """
    Class for the configuration of the interactive mode.
    """

    def __init__(self) -> None:
        """
        Configure the interactive mode.
        """
        self.languages = list_all_languages(language_metadata)
        self.data_types = list(data_type_metadata.keys())
        self.selected_languages: List[str] = []
        self.selected_data_types: List[str] = []
        self.output_type: str = "json"
        self.output_dir: Path = DEFAULT_JSON_EXPORT_DIR
        self.overwrite: bool = False
        self.configured: bool = False
        self.identifier_case: str = "camel"
        self.input_dir: Path = DEFAULT_JSON_EXPORT_DIR
        self.output_dir_sqlite: Path = DEFAULT_SQLITE_EXPORT_DIR


config = ScribeDataConfig()


# MARK: Summary


def display_summary() -> None:
    """
    Display a summary of the interactive mode request to run.
    """
    table = Table(
        title="Scribe-Data Request Configuration Summary", style="bright_white"
    )

    table.add_column("Setting", style="bold cyan", no_wrap=True)
    table.add_column("Value(s)", style="magenta")

    table.add_row("Languages", ", ".join(config.selected_languages) or "None")
    table.add_row("Data Types", ", ".join(config.selected_data_types) or "None")
    table.add_row("Output Type", config.output_type)
    table.add_row("Output Directory", str(config.output_dir))
    table.add_row("Overwrite", "Yes" if config.overwrite else "No")

    console.print("\n")
    console.print(table, justify="left")
    console.print("\n")


# Helper function to create a WordCompleter.
def create_word_completer(
    options: List[str], include_all: bool = False
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
    language_completer = create_word_completer(config.languages, include_all=True)
    initial_language_selection = ", ".join(config.selected_languages)
    selected_languages = prompt(
        "Select languages (comma-separated or 'All'): ",
        default=initial_language_selection,
        completer=language_completer,
    )
    if "All" in selected_languages:
        config.selected_languages = config.languages

    elif selected_languages.strip():  # check if input is not just whitespace
        config.selected_languages = [
            lang.strip()
            for lang in selected_languages.split(",")
            if lang.strip() in config.languages
        ]

    if not config.selected_languages:
        rprint("[yellow]No language selected. Please try again.[/yellow]")
        return prompt_for_languages()


def prompt_for_wiktionary_dump_language() -> str:
    """
    Ask which Wiktionary edition to use as the translation source.

    The choice selects which dump to load (e.g. ``german`` → ``dewiktionary``).

    Returns
    -------
    str
        Canonical language name (e.g. ``"german"``, ``"english"``).
    """
    language_completer = create_word_completer(config.languages)
    while True:
        selected = prompt(
            "Select Wiktionary dump source language: ",
            default="english",
            completer=language_completer,
        ).strip()
        if selected in config.languages:
            return selected
        rprint(f"[bold red]Error: {selected} is not a valid language.[/bold red]")


def _wiktionary_dump_search_dirs(location: Path) -> List[Path]:
    """
    Build an ordered list of directories to search for Wiktionary dumps.

    Each candidate is resolved and included only if it exists as a directory.
    Duplicates are skipped. Search order:

    1. ``location`` (and ``cwd / location`` if relative)
    2. :data:`~scribe_data.utils.DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR` under
       ``cwd``
    3. That same default export dir under every ancestor of ``cwd``

    Step 3 lets dumps in ``scribe_data_wiktionary_dumps_export`` be found when
    interactive mode is started from a nested folder (e.g.
    ``scribe_data_wiktionary_json_export/spanish``).

    Parameters
    ----------
    location : Path
        User-supplied dump path or search root from
        :func:`resolve_wiktionary_dump_path`.

    Returns
    -------
    list[Path]
        Unique directories, in the order above.
    """
    dirs: List[Path] = []
    seen: set[Path] = set()

    def add(candidate: Path) -> None:
        """
        Append a resolved directory to the search list.

        Parameters
        ----------
        candidate : Path
            Directory path to resolve and add if it exists.
        """
        resolved = candidate.expanduser().resolve()
        if resolved.is_dir() and resolved not in seen:
            seen.add(resolved)
            dirs.append(resolved)

    add(location)
    add(Path.cwd() / location)
    add(DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR)
    add(Path.cwd() / DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR)

    for parent in Path.cwd().parents:
        add(parent / DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR)

    return dirs


def resolve_wiktionary_dump_path(
    language: str, location: Union[str, Path]
) -> Optional[Path]:
    """
    Resolve a Wiktionary dump file for the given source language.

    Parameters
    ----------
    language : str
        Source language name (e.g. ``german``).

    location : str or Path
        Path to a dump file, or a directory to search for ``{iso}wiktionary*`` dumps.

    Returns
    -------
    Path or None
        Newest matching dump in a directory, the file itself if ``location`` is a file,
        or ``None`` if nothing matches.
    """
    path = Path(location).expanduser()
    file_candidates = [path, Path.cwd() / path]
    for file_path in file_candidates:
        if file_path.is_file():
            return file_path.resolve()

    iso = resolve_lang_iso(language)
    if not iso:
        return None

    wiktionary = f"{iso}wiktionary"
    pattern = f"{wiktionary}*pages-articles.xml*"
    dump_candidates: List[Path] = []

    for directory in _wiktionary_dump_search_dirs(path):
        dump_candidates.extend(directory.glob(pattern))

    dump_candidates.extend(Path.cwd().glob(pattern))

    if not dump_candidates:
        return None

    return max(dump_candidates, key=lambda p: p.stat().st_mtime).resolve()


# MARK: Data Type Selection


def prompt_for_data_types() -> None:
    """
    Prompt the user to select data types.

    Returns
    -------
    None
        Data types are added to the configuration or are asked for.
    """
    data_type_completer = create_word_completer(config.data_types, include_all=True)
    initial_data_type_selection = ", ".join(config.selected_data_types)

    while True:
        selected_data_types = prompt(
            "Select data types (comma-separated or 'All'): ",
            default=initial_data_type_selection,
            completer=data_type_completer,
        )
        if "All" in selected_data_types.capitalize():
            config.selected_data_types = config.data_types
            break

        elif selected_data_types.strip():  # check if input is not just whitespace
            config.selected_data_types = [
                dt.strip()
                for dt in selected_data_types.split(",")
                if dt.strip() in config.data_types
            ]
            if config.selected_data_types:
                break  # exit loop if valid data types are selected

        rprint("[yellow]No data type selected. Please try again.[/yellow]")


def configure_settings() -> None:
    """
    Configure the settings of the interactive mode request.

    Asks for:
        - Languages
        - Data types
        - Output type
        - Output directory
        - Whether to overwrite
    """
    rprint(
        "[cyan]Follow the prompts below. Press tab for completions and enter to select.[/cyan]"
    )
    prompt_for_languages()
    prompt_for_data_types()

    # MARK: Outputs

    output_type_completer = create_word_completer(["json", "csv", "tsv"])
    config.output_type = prompt(
        "Select output type (json/csv/tsv): ",
        default="json",
        completer=output_type_completer,
    )
    while config.output_type not in ["json", "csv", "tsv"]:
        rprint("[yellow]Invalid output type selected. Please try again.[/yellow]")
        config.output_type = prompt(
            "Select output type (json/csv/tsv): ",
            default="json",
            completer=output_type_completer,
        )

    # MARK: Output Directory

    if output_dir := prompt(f"Enter output directory (default: {config.output_dir}): "):
        config.output_dir = Path(output_dir)

    # MARK: Overwrite Confirmation

    overwrite_completer = create_word_completer(["Y", "n"])
    overwrite = (
        prompt("Overwrite existing files? (Y/n): ", completer=overwrite_completer)
        or "y"
    )
    config.overwrite = overwrite.lower() == "y"

    config.configured = True
    display_summary()


def run_request() -> None:
    """
    Execute the interactive mode request based on current configuration.

    Returns
    -------
    None
        An interactive mode request is ran.
    """
    if not config.selected_languages or not config.selected_data_types:
        rprint("[bold red]Error: Please configure languages and data types.[/bold red]")
        return

    # Calculate total operations
    total_operations = len(config.selected_languages) * len(config.selected_data_types)

    # MARK: Export Data

    with tqdm(
        total=total_operations,
        desc="Exporting data",
        unit="operation",
    ) as pbar:
        for language in config.selected_languages:
            for data_type in config.selected_data_types:
                pbar.set_description(f"Exporting {language} {data_type} data")

                try:
                    get_data(
                        languages=[language],
                        data_types=[data_type],
                        output_type=config.output_type,
                        output_dir=config.output_dir,
                        overwrite=config.overwrite,
                        interactive=True,
                    )
                    # The data was successfully written to file, so we can log success
                    logger.info(
                        f"[green]✔ Successfully exported {language} {data_type} data.[/green]"
                    )
                except Exception as e:
                    logger.error(
                        f"[red]✖ Failed to export {language} {data_type} data: {str(e)}[/red]"
                    )

                pbar.update(1)

    if config.overwrite:
        rprint("[bold green]Data request completed successfully![/bold green]")


def request_total_lexeme_loop() -> None:
    """
    Continuously prompts for lexeme requests until exit.
    """
    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                questionary.Choice("Configure total lexemes request", "total"),
                questionary.Choice("Run total lexemes request", "run"),
                questionary.Choice(
                    "Run total lexemes request with lexeme dumps", "run_all"
                ),
                questionary.Choice("Exit", "exit"),
            ],
        ).ask()

        if choice == "run":
            total_wrapper(
                languages=config.selected_languages,
                data_types=config.selected_data_types,
                all_bool=False,
            )
            config.selected_languages, config.selected_data_types = [], []
            rprint(THANK_YOU_MESSAGE)
            break

        elif choice == "run_all":
            if wikidata_dump_path := prompt(
                f"Enter Wikidata lexeme dump path (default: {str(DEFAULT_WIKIDATA_DUMP_EXPORT_DIR)}): "
            ):
                wikidata_dump_path = Path(wikidata_dump_path)

            else:
                wikidata_dump_path = DEFAULT_WIKIDATA_DUMP_EXPORT_DIR

            parse_wd_lexeme_dump(
                languages=config.selected_languages,
                wikidata_dump_path=wikidata_dump_path,
                wikidata_dump_type=["total"],
                interactive_mode=True,
            )
            break

        elif choice == "exit":
            return

        else:
            prompt_for_languages()
            prompt_for_data_types()


# MARK: List

# def see_list_languages():
#     """
#     See list of languages.
#     """

#     choice = select(
#         "What would you like to list?",
#         choices=[
#             Choice("All languages", "all_languages"),
#             Choice("Languages for a specific data type", "languages_for_data_type"),
#             Choice("Data types for a specific language", "data_types_for_language"),
#         ],
#     ).ask()

#     if choice == "all_languages":
#         list_wrapper(all_bool=True)

#     elif choice == "languages_for_data_type":
#         list_wrapper(data_type=True)

#     elif choice == "data_types_for_language":
#         list_wrapper(language=True)


# MARK: Start


def start_interactive_mode(operation: Optional[str] = None) -> None:
    """
    Entry point for interactive mode.

    Parameters
    ----------
    operation : str
        The type of operation that interactive mode is being ran with.
    """
    while True:
        # Check if both selected_languages and selected_data_types are empty.
        if config.selected_languages or config.selected_data_types:
            choices = [
                questionary.Choice("Configure get data request", "configure"),
                questionary.Choice("Exit", "exit"),
            ]

            if config.configured:
                choices.insert(
                    1, questionary.Choice("Run get data request with WDQS", "run")
                )
                choices.insert(
                    2,
                    questionary.Choice(
                        "Run get lexemes request with lexeme dumps", "run_all"
                    ),
                )

            elif config.selected_languages and config.selected_data_types:
                choices.insert(
                    1, questionary.Choice("Request for convert JSON", "convert_json")
                )

            else:
                choices.insert(
                    1, questionary.Choice("Request for total lexeme", "total")
                )

        elif operation == "get":
            choices = [
                questionary.Choice("Configure get data request", "configure"),
                # Choice("See list of languages", "languages"),
                questionary.Choice("Exit", "exit"),
            ]

        elif operation == "total":
            choices = [
                questionary.Choice("Configure total lexemes request", "total"),
                # Choice("See list of languages", "languages"),
                questionary.Choice("Exit", "exit"),
            ]

        elif operation == "convert":
            choices = [
                questionary.Choice("Configure convert request", "convert"),
                questionary.Choice("Exit", "exit"),
            ]

        elif operation == "translations":
            choices = [
                questionary.Choice("Configure translations request", "translations"),
                # Choice("See list of languages", "languages"),
                questionary.Choice("Exit", "exit"),
            ]

        choice = questionary.select("What would you like to do?", choices=choices).ask()

        if choice == "configure":
            configure_settings()

        elif choice == "run_all":
            if wikidata_dump_path := prompt(
                f"Enter Wikidata lexeme dump path (default: {str(DEFAULT_WIKIDATA_DUMP_EXPORT_DIR)}): "
            ):
                wikidata_dump_path = Path(wikidata_dump_path)

            else:
                wikidata_dump_path = DEFAULT_WIKIDATA_DUMP_EXPORT_DIR

            parse_wd_lexeme_dump(
                languages=config.selected_languages,
                data_types=config.selected_data_types,
                wikidata_dump_type=["form"],
                output_dir=config.output_dir,
                wikidata_dump_path=wikidata_dump_path,
                overwrite_all=config.overwrite,
                interactive_mode=True,
            )
            rprint(THANK_YOU_MESSAGE)
            break

        elif choice == "total":
            prompt_for_languages()
            prompt_for_data_types()
            request_total_lexeme_loop()
            break

        elif choice == "convert":
            prompt_for_languages()
            prompt_for_data_types()

            # Use the default explicitly so that if the user enters nothing, the default value is retained.
            user_input_dir = prompt(
                f"Enter input directory (default: {config.input_dir}): ",
                default=str(config.input_dir),
            )
            config.input_dir = Path(user_input_dir)

            user_output_dir = prompt(
                f"Enter output directory (default: {config.output_dir_sqlite}): ",
                default=str(config.output_dir_sqlite),
            )
            config.output_dir_sqlite = Path(user_output_dir)

            identifier_case = prompt(
                "Enter identifier case (default: camel): ",
                default="camel",
            )
            output_type = prompt(
                "Enter output type (default: sqlite): ",
                default="sqlite",
            )
            overwrite_str = prompt(
                "Overwrite existing files? (default: False): ",
                default="False",
            )
            overwrite_bool = overwrite_str.strip().lower() in ("true", "y", "yes")

            convert_wrapper(
                languages=config.selected_languages,
                data_types=config.selected_data_types,
                input_path=config.input_dir,  # Use the updated configuration value
                output_dir=config.output_dir_sqlite,
                output_type=output_type,
                identifier_case=identifier_case,
                overwrite=overwrite_bool,
            )
            break

        elif choice == "translations":
            from scribe_data.wiktionary.parse_translations import (
                parse_wiktionary_translations,
            )

            wiktionary_dump_language = prompt_for_wiktionary_dump_language()

            dump_location = prompt(
                "Enter Wiktionary dump directory or file path "
                f"(default: {DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR}): ",
                default=str(DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR),
            )
            wiktionary_dump_path = resolve_wiktionary_dump_path(
                wiktionary_dump_language,
                dump_location,
            )
            if not wiktionary_dump_path:
                rprint(
                    f"[bold red]No {wiktionary_dump_language} Wiktionary dump found at "
                    f"{dump_location}.[/bold red]"
                )
                break

            prompt_for_languages()

            translations_output_dir = prompt(
                "Enter output directory "
                f"(default: {DEFAULT_WIKTIONARY_JSON_EXPORT_DIR}): ",
                default=str(DEFAULT_WIKTIONARY_JSON_EXPORT_DIR),
            )

            overwrite_str = prompt(
                "Overwrite existing files? (default: False): ",
                default="False",
            )
            overwrite_bool = overwrite_str.strip().lower() in ("true", "y", "yes")

            parse_wiktionary_translations(
                target_languages=config.selected_languages,
                wiktionary_dump_path=Path(wiktionary_dump_path),
                output_dir=Path(translations_output_dir),
                overwrite=overwrite_bool,
            )

            break

        elif choice == "run":
            run_request()
            rprint(THANK_YOU_MESSAGE)
            break

        else:
            rprint(THANK_YOU_MESSAGE)
            break


if __name__ == "__main__":
    start_interactive_mode()
