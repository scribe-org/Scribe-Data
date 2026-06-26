# SPDX-License-Identifier: GPL-3.0-or-later
"""
Interactive mode runner for the Scribe-Data CLI to allow users to select request arguments.
"""

from pathlib import Path

import questionary
from prompt_toolkit import prompt
from rich import print as rprint

from scribe_data.cli.convert.wrapper import convert_wrapper
from scribe_data.cli.interactive.config import (
    THANK_YOU_MESSAGE,
    interactive_mode_config,
)
from scribe_data.cli.interactive.execute import (
    display_summary,
    execute_request,
    request_total_lexeme_loop,
)
from scribe_data.cli.interactive.prompt import (
    create_word_completer,
    prompt_for_data_types,
    prompt_for_languages,
    resolve_wiktionary_dump_path,
)
from scribe_data.utils import (
    DEFAULT_WIKIDATA_DUMP_EXPORT_DIR,
    DEFAULT_WIKTIONARY_DUMP_EXPORT_DIR,
    DEFAULT_WIKTIONARY_JSON_EXPORT_DIR,
)
from scribe_data.wikidata.wikidata_utils import parse_wd_lexeme_dump

# MARK: Configure


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
    interactive_mode_config.output_type = prompt(
        "Select output type (json/csv/tsv): ",
        default="json",
        completer=output_type_completer,
    )
    while interactive_mode_config.output_type not in ["json", "csv", "tsv"]:
        rprint("[yellow]Invalid output type selected. Please try again.[/yellow]")
        interactive_mode_config.output_type = prompt(
            "Select output type (json/csv/tsv): ",
            default="json",
            completer=output_type_completer,
        )

    # MARK: Output Directory

    if output_dir := prompt(
        f"Enter output directory (default: {interactive_mode_config.output_dir}): "
    ):
        interactive_mode_config.output_dir = Path(output_dir)

    # MARK: Overwrite Confirmation

    overwrite_completer = create_word_completer(["Y", "n"])
    overwrite = (
        prompt("Overwrite existing files? (Y/n): ", completer=overwrite_completer)
        or "y"
    )
    interactive_mode_config.overwrite = overwrite.lower() == "y"

    interactive_mode_config.configured = True
    display_summary()


# MARK: Start


def run_interactive_mode(operation: str | None = None) -> None:
    """
    Entry point for interactive mode.

    Parameters
    ----------
    operation : str
        The type of operation that interactive mode is being ran with.
    """
    while True:
        # Check if both selected_languages and selected_data_types are empty.
        if (
            interactive_mode_config.selected_languages
            or interactive_mode_config.selected_data_types
        ):
            choices = [
                questionary.Choice("Configure get data request", "configure"),
                questionary.Choice("Exit", "exit"),
            ]

            if interactive_mode_config.configured:
                choices.insert(
                    1, questionary.Choice("Run get data request with WDQS", "run")
                )
                choices.insert(
                    2,
                    questionary.Choice(
                        "Run get lexemes request with lexeme dumps", "run_all"
                    ),
                )

            elif (
                interactive_mode_config.selected_languages
                and interactive_mode_config.selected_data_types
            ):
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
                languages=interactive_mode_config.selected_languages,
                data_types=interactive_mode_config.selected_data_types,
                wikidata_dump_type=["form"],
                output_dir=interactive_mode_config.output_dir,
                wikidata_dump_path=wikidata_dump_path,
                overwrite_all=interactive_mode_config.overwrite,
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
                f"Enter input directory (default: {interactive_mode_config.input_dir}): ",
                default=str(interactive_mode_config.input_dir),
            )
            interactive_mode_config.input_dir = Path(user_input_dir)

            user_output_dir = prompt(
                f"Enter output directory (default: {interactive_mode_config.output_dir_sqlite}): ",
                default=str(interactive_mode_config.output_dir_sqlite),
            )
            interactive_mode_config.output_dir_sqlite = Path(user_output_dir)

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
                languages=interactive_mode_config.selected_languages,
                data_types=interactive_mode_config.selected_data_types,
                input_path=interactive_mode_config.input_dir,  # Use the updated configuration value
                output_dir=interactive_mode_config.output_dir_sqlite,
                output_type=output_type,
                identifier_case=identifier_case,
                overwrite=overwrite_bool,
            )
            break

        elif choice == "translations":
            from scribe_data.wiktionary.parse_translations import (
                parse_wiktionary_translations,
            )

            while True:
                wiktionary_dump_language = prompt(
                    "Select Wiktionary dump source language: ",
                    default="english",
                    completer=create_word_completer(interactive_mode_config.languages),
                ).strip()
                if wiktionary_dump_language in interactive_mode_config.languages:
                    break
                rprint(
                    f"[bold red]Error: {wiktionary_dump_language} is not a valid language.[/bold red]"
                )

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
                target_languages=interactive_mode_config.selected_languages,
                wiktionary_dump_path=Path(wiktionary_dump_path),
                output_dir=Path(translations_output_dir),
                overwrite=overwrite_bool,
            )

            break

        elif choice == "run":
            execute_request()
            rprint(THANK_YOU_MESSAGE)
            break

        else:
            rprint(THANK_YOU_MESSAGE)
            break


if __name__ == "__main__":
    run_interactive_mode()
