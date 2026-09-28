<a id="top"></a>

# Scribe-Data CLI Usage

Scribe-Data provides a command-line interface (CLI) for extracting language data from [Wikidata](https://www.wikidata.org/) , [Wiktionary](https://www.wiktionary.org/) and [Unicode](https://home.unicode.org/) for Scribe applications. Please see the [CLI usage documentation in the Scribe-Data docs](https://scribe-data.readthedocs.io/en/latest/scribe_data/cli/index.html) for a full overview of functionality. The following is meant to serve as a brief introduction.

## Contents

- [Installation](#installation)
- [Development Build](#development-build)
- [Basic Usage](#basic-usage)
- [Command Examples](#command-examples)
  - [List](#list)
  - [Total](#total)
  - [Get](#get)
  - [Convert](#convert)
  - [Export Contracts](#export-contracts)
  - [Audit Wikidata](#audit-wikidata)
  - [Generate Queries](#generate-queries)
  - [Check Contracts](#check-contracts)
  - [Filter by Contracts](#filter-by-contracts)
  - [Interactive Mode](#interactive-mode)
- [Additional Help](#additional-help)

## Installation

### Using uv (recommended)

```bash
uv pip install scribe-data
```

### Using pip

```bash
pip install scribe-data
```

<sub><a href="#top">Back to top.</a></sub>

## Development Build

```bash
git clone https://github.com/scribe-org/Scribe-Data.git  # or your fork
cd Scribe-Data

# With uv (recommended)
uv sync --all-groups
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Or with pip
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
pip install -e .
```

<sub><a href="#top">Back to top.</a></sub>

## Basic Usage

```bash
scribe-data -h
scribe-data [command] [arguments]
```

### Available Commands

- `list` (`l`): List languages, data types and combinations of each that Scribe-Data can be used for.
- `get` (`g`): Get data from Wikidata and other sources for the given languages and data types.
- `total` (`t`): Check Wikidata for the total available data for the given languages and data types.
- `convert` (`c`): Convert data returned by Scribe-Data to different file types.
- `download` (`d`): Download Wikidata lexeme or Wiktionary dumps.
- `export_contracts` (`ec`): Export Scribe-Data contracts to a local directory.
- `audit_wd_lexeme_forms` (`awdlf`): Run an audit of the available language data forms on Wikidata.
- `generate_wd_lexeme_queries` (`gwdlq`): Generate Wikidata language data queries from contracts.
- `check_contracts` (`cc`): Check the data in a Scribe-Data export directory to see that all needed language data is included to fulfill data contracts.
- `filter_data` (`fd`): Filter exported Scribe-Data data based on provided data contract values.
- `interactive` (`i`): Run in interactive mode.

### Available Arguments

The following arguments are among those that can be passed to commands where applicable:

- `--language` (`-lang`): The language to run the command for.
- `--data-type` (`-dt`): The data type to run the command for.
- `--file` (`-f`): The path to a file to run the command on.
- `--output-dir` (`-od`): The path to a directory for the outputs of the command.
- `--output-type` (`-ot`): The file type that the command should output.
- `--outputs-per-entry` (`-ope`): How many outputs should be generated per data entry.
- `--all` (`-a`): Get all results from the command.
- `--interactive` (`-i`): Run in interactive mode where supported.

> [!NOTE]
> Use the `scribe-data -h` or `scribe-data [command] -h` commands to learn more about potential arguments.

<sub><a href="#top">Back to top.</a></sub>

## Command Examples

### List

List available languages and data types in Scribe-Data.

```bash
scribe-data list
scribe-data list --language
scribe-data list --data-type
```

### Total

Get the total data on Wikidata for the given languages and data types.

```bash
scribe-data total --data-type nouns
scribe-data total --language English
scribe-data total --language English --data-type nouns
```

### Get

Get data from Wikidata and Wiktionary dumps.

```bash
scribe-data get --all
scribe-data get --language German --data-type nouns
```

### Convert

Convert data derived from Scribe-Data `get` processes into other data types.

```bash
scribe-data get --language English --data-type verbs --output-type sqlite
scribe-data get --language English --data-type verbs --output-type csv
```

### Export Contracts

Export the Scribe-Data data contracts to investigate them.

```bash
scribe-data export_contracts
```

### Audit Wikidata

Run an audit of Wikidata's data for a given language and data type. The results can then be used to write data contracts.

```bash
scribe-data audit_wd_lexeme_forms --language German --data-type verbs --max-results 1000
```

### Generate Queries

Generate Wikidata lexeme queries for use with Scribe-Data.

```bash
scribe-data generate_wd_lexeme_queries  # all contracts
scribe-data generate_wd_lexeme_queries --language English --data-type nouns
scribe-data generate_wd_lexeme_queries --contracts-dir ./contracts --output-dir ./queries  # use own data contracts
```

### Check Contracts

Check results from Scribe-Data against values in contracts to make sure that they can be fulfilled.

```bash
scribe-data check_contracts
scribe-data check_contracts --contracts-dir ./contracts --output-dir ./data
```

### Filter by Contracts

Filter data by data contracts to assure that only values that are within the contract are in the data.

```bash
scribe-data filter_data
scribe-data filter_data --contracts-dir ./contracts --input-dir ./data --output-dir ./filtered_data
```

### Interactive Mode

Run Scribe-Data in interactive mode to set the arguments for your commands through a helpful text interface.

```bash
scribe-data interactive
scribe-data get --interactive
scribe-data total --interactive
```

<sub><a href="#top">Back to top.</a></sub>

## Additional Help

For detailed information on any command, use:

```bash
scribe-data -h
scribe-data [command] -h
```

Version and upgrade commands are also available:

```bash
scribe-data -v
scribe-data -u
```

For more information, see the [official documentation](https://scribe-data.readthedocs.io/).

<sub><a href="#top">Back to top.</a></sub>
