# Scribe-Data CLI Usage

Scribe-Data provides a command-line interface (CLI) for efficient interaction with its language data functionality.

## Basic Usage

To utilize the Scribe-Data CLI, you can execute the following command in your terminal:

```bash
pip install scribe-data

# For a development build:
git clone https://github.com/scribe-org/Scribe-Data.git  # or ideally your fork
cd Scribe-Data
pip install -e .

scribe-data -h  # view the cli options
scribe-data [command] [arguments]
```

## Available Commands

- `list` (`l`): Enumerate available languages, data types and their combinations.
- `get` (`g`): Retrieve data from Wikidata for specified languages and data types.
- `total` (`t`): Display the total available data for given languages and data types.
- `convert` (`c`): Transform data returned by Scribe-Data into different file formats.

## Available Arguments

The following arguments can be passed to the Scribe-Data commands whenever sensible:

- `--language` (`-lang`): The language to run the command for.
- `--data-type` (`-dt`): The data type to run the command for.
- `--file` (`-f`): The path to a file to run the command on.
- `--output-dir` (`-od`): The path to a directory for the outputs of the command.
- `--output-type` (`-ot`): The file type that the command should output.
- `--outputs-per-entry` (`-ope`): How many outputs should be generated per data entry.
- `--all` (`-a`): Get all results from the command.

## Command Examples

### List Command

1. Display all available options:

   ```bash
   scribe-data list # -a --all
   ```

2. Display available languages:

   ```bash
   scribe-data list -lang # --language
   ```

3. Display available data types:

   ```bash
   scribe-data list -dt # --data-type
   ```

### Total Command

1. Display total available data for a specific data type (e.g. nouns):

   ```bash
   scribe-data total -dt nouns
   ```

2. Display total available data for a specific language (e.g. English):

   ```bash
   scribe-data total -lang English
   ```

3. Display total available data for both language and data type (e.g. English nouns):

   ```bash
   scribe-data total -lang English -dt nouns
   ```

### Get Command

1. Get all available languages and data types:

   ```bash
   scribe-data get -a # --all
   ```

2. Get specific language and data type (e.g. German nouns):

   ```bash
   scribe-data get -lang German -dt nouns
   ```

### Convert Command

1. Retrieve data for both language and data type (e.g. English nouns) in CSV format:

   ```bash
   scribe-data get -lang english -dt verbs -od ./output_data -ot csv
   ```

2. Retrieve data for both language and data type (e.g. English nouns) in TSV format:

   ```bash
   scribe-data get -lang english -t verbs -od ./output_data -ot tsv
   ```

### Interactive Get Mode

The CLI also offers an interactive get mode, which can be initiated with the following command:

```bash
scribe-data get -i # --interactive
```

This mode guides users through the data retrieval process with a series of prompts:

1. Language selection: Users can choose from a list of available languages or select all.
2. Data type selection: Users can specify which types of data to get.
3. Output configuration: Users can set the file format, export directory, and overwrite preferences.

The interactive mode is particularly useful for users who prefer a guided approach or are exploring the available data options.

## Additional Assistance

For more detailed information on each command and its options, append the `--help` flag:

```bash
scribe-data -h # --help
scribe-data [command] -h
```

The CLI also has functions to check the version and upgrade the package if necessary.

```bash
scribe-data -v # --version
scribe-data -u # --upgrade
```

For comprehensive usage instructions and examples, please refer to the [official documentation](https://scribe-data.readthedocs.io/).
