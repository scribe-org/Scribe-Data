# Scribe-Data CLI Usage

Scribe-Data provides a command-line interface (CLI) for extracting language data from Wikidata and other sources.

## Installation

### Using uv (recommended)

```bash
uv pip install scribe-data
```

### Using pip

```bash
pip install scribe-data
```

## Development build

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

## Basic Usage

```bash
scribe-data -h
scribe-data [command] [arguments]
```

## Available Commands

- `list` (`l`): List the languages, data types, and combinations available in Scribe-Data.
- `get` (`g`): Get data from Wikidata and other sources for the selected languages and data types.
- `total` (`t`): Show the total available data for selected languages and data types.
- `convert` (`c`): Convert Scribe-Data output into different file types.
- `download` (`d`): Download Wikidata lexeme or Wiktionary dumps.
- `interactive` (`i`): Run Scribe-Data in interactive mode.
- `export_contracts` (`ec`): Export Scribe-Data contracts to a local directory.
- `check_contracts (`cc`): Check that an export directory contains the language data needed by the contracts.
- `filter_data` (`fd`): Filter exported Scribe-Data data based on contract values.

## Available Arguments

The following arguments can be passed to commands where applicable:

- `--language` (`-lang`): The language to run the command for.
- `--data-type` (`-dt`): The data type to run the command for.
- `--file` (`-f`): The path to a file to run the command on.
- `--output-dir` (`-od`): The path to a directory for the outputs of the command.
- `--output-type` (`-ot`): The file type that the command should output.
- `--outputs-per-entry` (`-ope`): How many outputs should be generated per data entry.
- `--all` (`-a`): Get all results from the command.
- `--interactive` (`-i)`: Run in interactive mode where supported.

## Command Examples

### List

```bash
scribe-data list
scribe-data list --language
scribe-data list --data-type
```

### Total

```bash
scribe-data total --data-type nouns
scribe-data total --language English
scribe-data total --language English --data-type nouns
```

### Get

```bash
scribe-data get --all
scribe-data get --language German --data-type nouns
```

### Convert

```bash
scribe-data get --language English --data-type verbs --output-dir ./output_data --output-type csv

scribe-data get --language English --data-type verbs --output-dir ./output_data --output-type tsv
```

### Interactive mode

```bash
scribe-data interactive
scribe-data get --interactive
scribe-data total --interactive
```

## Additional help

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
