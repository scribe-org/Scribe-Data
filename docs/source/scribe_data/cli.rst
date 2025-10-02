cli/
====

`View code on Github <https://github.com/scribe-org/Scribe-Data/tree/main/src/scribe_data/cli>`_

Scribe-Data provides a command-line interface (CLI) for efficient interaction with its language data functionality.

Usage
-----

The basic syntax for using the Scribe-Data CLI is:

.. code-block:: bash

    scribe-data [global_options] command [command_options]

Global Options
--------------

- ``-h, --help``: Show this help message and exit.
- ``-v, --version``: Show the version of Scribe-Data.
- ``-u, --upgrade``: Upgrade the Scribe-Data CLI.

Commands
--------

The Scribe-Data CLI supports the following commands:

1. ``list`` (alias: ``l``)
2. ``get`` (alias: ``g``)
3. ``total`` (alias: ``t``)
4. ``convert`` (alias: ``c``)
5. ``download`` (alias: ``d``)

Note: For all language arguments, if the language is more than one word then the argument value needs to be passed with double quotes around it.

For example:

.. code-block:: bash

    scribe-data total --language German --data-type nouns
    scribe-data total --language "Hindi Hindustani" --data-type nouns

List Command
~~~~~~~~~~~~

Description: List languages, data types and combinations of each that Scribe-Data can be used for.

Usage:

.. code-block:: bash

    scribe-data list [arguments]

Options:
^^^^^^^^

- ``-lang, --language [LANGUAGE]``: List options for all or given languages.
- ``-dt, --data-type [DATA_TYPE]``: List options for all or given data types.
- ``-a, --all ALL``: List all languages and data types.

Example output:

The scribe-data list command (also accessible via ``scribe-data list -a``) displays both the available languages and data types.

.. code-block:: text

    $ scribe-data list

    Language     ISO  QID
    ==========================
    English      en   Q1860
    ...

    Available data types: All languages
    ===================================
    adjectives
    adverbs
    emoji-keywords
    nouns
    personal-pronouns
    postpositions
    prepositions
    proper-nouns
    verbs




.. code-block:: text

    $scribe-data list --language

    Language     ISO  QID
    ==========================
    English      en   Q1860
    ...


.. code-block:: text

    $scribe-data list -dt

    Available data types: All languages
    ===================================
    adjectives
    adverbs
    emoji-keywords
    nouns
    personal-pronouns
    postpositions
    prepositions
    proper-nouns
    verbs

Get Command
~~~~~~~~~~~

Description: Get data from Wikidata for the given languages and data types.

Usage:

.. code-block:: bash

    scribe-data get [arguments]

Options:
^^^^^^^^

- ``-lang, --language LANGUAGE``: The language(s) to get.
- ``-dt, --data-type DATA_TYPE``: The data type(s) to get.
- ``-od, --output-dir OUTPUT_DIR``: The output directory path for results.
- ``-ot, --output-type {json,csv,tsv}``: The output file type.
- ``-ope, --outputs-per-entry OUTPUTS_PER_ENTRY``: How many outputs should be generated per data entry.
- ``-o, --overwrite``: Whether to overwrite existing files (default: False).
- ``-a, --all``: Get all languages and data types. Can be combined with `-dt` to get all languages for a specific data type, or with `-lang` to get all data types for a specific language.
- ``-i, --interactive``: Run in interactive mode.
- ``-ic, --identifier-case``: The case format for identifiers in the output data (default: camel).

Examples:

.. code-block:: bash

    $ scribe-data get --all
    Getting data for all languages and all data types...

.. code-block:: bash

    $ scribe-data get --all -dt nouns
    Getting all nouns for all languages...

.. code-block:: bash

    $ scribe-data get --all -lang English
    Getting all data types for English...

.. code-block:: bash

    $ scribe-data get -l English --data-type verbs -od ~/path/for/output
    Getting and formatting English verbs
    Data updated: 100%|████████████████████████| 1/1 [00:XY<00:00, XY.Zs/process]

If we want to retrieve data using lexeme dumps, we can use the following command:

.. code-block:: bash

    $ scribe-data get -lang german -dt nouns -wdp

**Example Output:**

.. code-block:: text

    Languages to process: German
    Data types to process: ['nouns']
    Existing dump files found:
      - scribe_data_wikidata_dumps_export/latest-lexemes.json.bz2
    ? Do you want to: (Use arrow keys)
     » Delete existing dumps
       Skip download
       Use existing latest dump
       Download new version

**Instructions:**

1. Use the arrow keys to navigate through the options.
2. Press **Enter** to confirm your selection.

**Options Explained:**

- **Delete existing dumps**: Removes the existing dump files before downloading new ones.
- **Skip download**: Skips the download process.
- **Use existing latest dump**: Processes the existing dump file without downloading a new version.
- **Download new version**: Downloads the latest version of the lexeme dump.

**Note:** Ensure you have sufficient disk space and a stable internet connection if downloading a new version.

**If No Existing Dump Files Are Found:**

1. If no existing dump files are found, the command will display the following message:

    .. code-block:: text

        No existing dump files found. Downloading new version...

2. The command will then proceed to download the latest dump file:
    .. code-block:: text

        Downloading dump to scribe_data_wikidata_dumps_export\latest-lexemes.json.bz2...
        scribe_data_wikidata_dumps_export\latest-lexemes.json.bz2: 100%|███████████████████| 370M/370M [04:20<00:00, 1.42MiB/s]
        Wikidata lexeme dump download completed successfully!

Behavior and Output:
^^^^^^^^^^^^^^^^^^^^

1. The command will first check for existing data:

    .. code-block:: text

        Updating data for language(s): English; data type(s): verbs
        Data updated:   0%|

2. If existing files are found, you'll be prompted to choose an option:

    .. code-block:: text

        Existing file(s) found for English verbs:

        1. verbs.json

        Choose an option:
        1. Overwrite existing data (press 'o')
        2. Skip process (press anything else)
        Enter your choice:

3. After making a selection, the get process begins:

    .. code-block:: text

        Getting and formatting English verbs
        Data updated: 100%|████████████████████████| 1/1 [00:XY<00:00, XY.Zs/process]

4. If no data is found, you'll see a warning:

    .. code-block:: text

        No data found for language 'english' and data type '['verbs']'.
        Warning: No data file found for 'English' ['verbs']. The command must not have worked.

Notes:
^^^^^^

1. The data type can be specified with ``--data-type`` or ``-dt``.
2. The command creates timestamped JSON files by default, even if no data is found.
3. If multiple files exist, you'll be given options to manage them (keep existing, overwrite, keep both, or cancel).
4. The process may take some time, especially for large datasets.

Troubleshooting:
^^^^^^^^^^^^^^^^

- If you receive a "No data found" warning, check your internet connection and verify that the language and data type are correctly specified.
- If you're having issues with file paths, remember to use quotes around paths with spaces.
- If the command seems to hang at 0% or 100%, be patient as the process can take several minutes depending on the dataset size and your internet connection.

Total Command
~~~~~~~~~~~~~

Description: Check Wikidata for the total available data for the given languages and data types.

Usage:

.. code-block:: bash

    scribe-data total [arguments]

Options:
^^^^^^^^

- ``-lang, --language LANGUAGE``: The language(s) to check totals for. Can be a language name or QID.
- ``-dt, --data-type DATA_TYPE``: The data type(s) to check totals for.
- ``-a, --all``: Get totals for all languages and data types.

Examples:

1. Get totals for all languages and data types:

.. code-block:: text

    $ scribe-data total --all
    Total lexemes for all languages and data types:
    ==============================================
    Language     Data Type     Total Lexemes
    ==============================================
    English      nouns         123,456
                 verbs         234,567
    ...

2. Get totals for all data types in English:

.. code-block:: text

    $ scribe-data total --language English
    Returning total counts for English data types...

    Language        Data Type                 Total Wikidata Lexemes
    ================================================================
    English         adjectives                12,345
                    adverbs                   23,456
                    nouns                     34,567
    ...

3. Get totals using a Wikidata QID:

.. code-block:: text

    $ scribe-data total --language Q1860
    Wikidata QID Q1860 passed. Checking all data types.

    Language        Data Type                 Total Wikidata Lexemes
    ================================================================
    Q1860           adjectives                12,345
                    adverbs                   23,456
                    articles                  30
                    conjunctions              40
                    nouns                     56,789
                    personal pronouns         60
    ...

4. Get totals for a specific language and data type combination:

.. code-block:: text

    $ scribe-data total --language English -dt nouns
    Language: English
    Data type: nouns
    Total number of lexemes: 12,345

5. Get totals for a specific QID and data type combination:

.. code-block:: text

    $ scribe-data total --language Q1860 -dt verbs
    Language: Q1860
    Data type: verbs
    Total number of lexemes: 23,456


Download Command
~~~~~~~~~~~~~~~~
Usage:

.. code-block:: bash

    scribe-data download

Behavior and Output:
^^^^^^^^^^^^^^^^^^^^

- **If Existing Dump Files Are Found:**

1. If existing dump files are found, the command will display the following message:

    .. code-block:: text

        Existing dump files found:
          - scribe_data_wikidata_dumps_export/latest-lexemes.json.bz2

2. The command will prompt the user with options to choose from:

    .. code-block:: text

        ? Do you want to: (Use arrow keys)
         » Delete existing dumps
           Skip download
           Use existing latest dump
           Download new version

- **If Downloading New Version:**

  1. If the user chooses to proceed with the download, the dump will be downloaded to the specified directory:

    .. code-block:: text

        Downloading dump to scribe_data_wikidata_dumps_export\latest-lexemes.json.bz2...
        scribe_data_wikidata_dumps_export\latest-lexemes.json.bz2: 100%|███████████████████| 370M/370M [04:20<00:00, 1.42MiB/s]
        Wikidata lexeme dump download completed successfully!


Convert Command
~~~~~~~~~~~~~~~

Description: Convert data returned by Scribe-Data to different file types, including SQLite databases for multiple languages and data types.

Usage:

.. code-block:: bash

    scribe-data convert [arguments]

Options:
^^^^^^^^

- ``-f, --file FILE``: The file to convert to a new type.
- ``-lang, --language LANGUAGE``: The language(s) to convert (for SQLite conversion).
- ``-dt, --data-type DATA_TYPE``: The data type(s) to convert (for SQLite conversion).
- ``-ko, --keep-original``: Whether to keep the file to be converted (default: True).
- ``-ot, --output-type {json,csv,tsv,sqlite}``: The output file type.

Examples:
^^^^^^^^^

1. **Convert multiple languages and data types to SQLite:**

.. code-block:: bash

    $ scribe-data convert -lang english french -dt nouns verbs -ot sqlite
    Creating/Updating SQLite databases for the following languages: English, French
    Updating only the following tables: nouns, verbs
    Databases created:   0%|                                                    | 0/2 [00:00<?, ?dbs/s]
    ? SQLite file scribe_data_sqlite_export/ENLanguageData.sqlite already exists.
    Do you want to overwrite it? Yes
    Database for english overwritten and connection made.
    Creating/Updating english nouns table...
    Creating/Updating english verbs table...
    English database processing completed.
    Databases created:  50%|████████████████████████████████████████            | 1/2 [00:05<00:05,  5.14s/dbs]
    ? SQLite file scribe_data_sqlite_export/FRLanguageData.sqlite already exists.
    Do you want to overwrite it? Yes
    Database for french overwritten and connection made.
    Creating/Updating french nouns table...
    Creating/Updating french verbs table...
    French database processing completed.
    Databases created: 100%|████████████████████████████████████████████████████| 2/2 [00:07<00:00,  3.61s/dbs]
    Database creation/update process completed.

2. **Convert a single file to CSV:**

.. code-block:: bash

    $ scribe-data convert -f path/to/data.json -ot csv

Behavior and Output:
^^^^^^^^^^^^^^^^^^^^

**SQLite Conversion:**

1. **Database Creation:** When converting to SQLite format, the command creates separate database files for each language in the `scribe_data_sqlite_export/` directory with the naming pattern `{LANGUAGE_CODE}LanguageData.sqlite`.

2. **Interactive Overwrite Prompts:** If existing SQLite files are found, you'll be prompted to choose whether to overwrite them:

    .. code-block:: text

        ? SQLite file scribe_data_sqlite_export/ENLanguageData.sqlite already exists.
        Do you want to overwrite it? Yes

3. **Progress Tracking:** The command displays real-time progress for database creation:

    .. code-block:: text

        Databases created:  50%|████████████████████████████████████████            | 1/2 [00:05<00:05,  5.14s/dbs]

4. **Table Creation:** For each language, the command creates/updates tables for the specified data types:

    .. code-block:: text

        Creating/Updating english nouns table...
        Creating/Updating english verbs table...

**File Conversion:**

- When using the `-f` option, the command converts individual files to the specified output type.
- The original file is kept by default unless `--keep-original` is set to False.

Notes:
^^^^^^

1. **SQLite Output:** SQLite databases are created in the `scribe_data_sqlite_export/` directory.
2. **Multiple Languages:** You can specify multiple languages separated by spaces.
3. **Multiple Data Types:** You can specify multiple data types separated by spaces.
4. **Database Naming:** SQLite files follow the pattern `{LANGUAGE_CODE}LanguageData.sqlite` (e.g., `ENLanguageData.sqlite`, `FRLanguageData.sqlite`).
5. **Table Structure:** Each data type becomes a separate table within the language database.

Interactive Mode
----------------

The interactive mode provides a user-friendly interface for interacting with Scribe-Data commands.

Usage:

.. code-block:: bash

    scribe-data get -i
    scribe-data total -i

Get Command Interactive Example:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    $ scribe-data get -i
    Welcome to Scribe-Data vX.Y.Z interactive mode!
    ? What would you like to do? (Use arrow keys)
    » Configure get data request
    » Exit

1. If user selects ``Configure get data request``:

.. code-block:: text

    ? What would you like to do? Configure get data request
    Follow the prompts below. Press tab for completions and enter to select.
    Select languages (comma-separated or 'All'): english
    Select data types (comma-separated or 'All'): nouns
    Select output type (json/csv/tsv): json
    Enter output directory (default: scribe_data_json_export):
    Overwrite existing files? (Y/n): Y

    Scribe-Data Request Configuration Summary
    ┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ Setting          ┃ Value(s)                ┃
    ┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ Languages        │ english                 │
    │ Data Types       │ nouns                   │
    │ Output Type      │ json                    │
    │ Output Directory │ scribe_data_json_export │
    │ Overwrite        │ Yes                     │
    └──────────────────┴─────────────────────────┘

    ? What would you like to do? (Use arrow keys)
    » Configure get data request
    » Request for get data
    » Exit

2. If user selects ``Request for get data``:

.. code-block:: text

    ? What would you like to do? Request for get data
    Exporting english nouns data:   0%|                                                               | 0/1 [00:00<?, ?operation/s]
    Updating data for language(s): English; data type(s): Nouns
    Overwrite is enabled. Removing existing files...
    Querying and formatting English nouns
    Wrote file english/nouns.json with 59,255 nouns.
    Updated data was saved in: Scribe-Data/scribe_data_json_export.
    [01:26:58] INFO     ✔ Exported english nouns data.                                               interactive.py:239
    Exporting english nouns data: 100%|████████████████████████████████████████████████████| 1/1 [00:16<00:00, 16.36s/operation]

3. After the process is complete, we'll see a confirmation message:

.. code-block:: text

    Data request completed successfully!
    Thank you for using Scribe-Data!

Total Command Interactive Example:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    $ scribe-data total -i
    Welcome to Scribe-Data vX.Y.Z interactive mode!
    ? What would you like to do? (Use arrow keys)
    » Configure total lexemes request
    » Exit

If user selects ``Configure total lexemes request``:

.. code-block:: text

    ? What would you like to do? Configure total lexemes request
    Select languages (comma-separated or 'All'): english,basque
    Select data types (comma-separated or 'All'): nouns,adjectives

    Language             Data Type                 Total Lexemes
    ======================================================================
    english              nouns                     123,456
                         adjectives                234,567

    basque               nouns                     34,567
                         adjectives                250

The command ``scribe-data total -lang english -wdp`` retrieves total lexeme and translation counts for English, checks dumps, and provides detailed statistics.

.. code-block::

    $ scribe-data total -lang english -wdp
    Languages to process: English
    Data types to process: None
    Existing dump files found:
      - scribe_data_wikidata_dumps_export/latest-lexemes.json.bz2
    ? Do you want to: Use existing latest dump
    We'll use the following lexeme dump scribe_data_wikidata_dumps_export/latest-lexemes.json.bz2
    Processing entries:  100%|████████████████████████████████████████████████████| 1406276/1406276 [15:25<00:14, 1495.97it/s]
    Language             Data Type                 Total Lexemes             Total Translations
    ==========================================================================================
    english              nouns                     123,456                   12,345
                         adjectives                345,678                   2,345
                         adverbs                   45,678                    345
                         verbs                     5,678                     4,567
                         proper_nouns              6,789                     5,678
                         prepositions              789                       100
                         conjunctions              75                        25
                         pronouns                  50                        25
                         personal_pronouns         25                        50
                         postpositions             1

Features:
^^^^^^^^^

1. Step-by-step prompts for all options.
2. Tab completion support.
3. Clear configuration summary before execution.
4. Progress tracking during data retrieval.
5. Multiple language and data type selection support.
6. Formatted table output for results.
7. User can select ``All languages`` or ``All data types`` at once.
8. User can exit the interactive mode at any time by selecting ``Exit``.

The interactive mode is particularly useful for:
- First-time users learning the CLI options.
- Complex queries with multiple parameters.
- Viewing available options without memorizing commands.

Root Interactive Command
~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    $ scribe-data interactive
    Welcome to Scribe-Data v4.1.0 interactive mode!
    ? What would you like to do? (Use arrow keys)
     » Download a Wikidata lexemes dump
       Check for totals
       Get data
       Get translations
       Convert JSON
       Exit

The command ``scribe-data interactive`` initiates the interactive mode, allowing users to easily select and execute various Scribe-Data operations.
