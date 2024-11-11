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

List Command
~~~~~~~~~~~~

Description: List languages, data types and combinations of each that Scribe-Data can be used for.

Usage:

.. code-block:: bash

    scribe-data list [options]

Options:
^^^^^^^^

- ``-lang, --language [LANGUAGE]``: List options for all or given languages.
- ``-dt, --data-type [DATA_TYPE]``: List options for all or given data types.
- ``-a, --all ALL``: List all languages and data types.

Example output:

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


.. code-block:: text

    $scribe-data list -a

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

Get Command
~~~~~~~~~~~

Description: Get data from Wikidata for the given languages and data types.

Usage:

.. code-block:: bash

    scribe-data get [options]

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

Interactive Mode
----------------

.. code-block:: text

    $ scribe-data get -i
    Welcome to Scribe-Data interactive mode!
    Language options:
    1. English
    2. French
    3. German
    ...

    Please enter the languages to get data for, their numbers or (a) for all languages: 1

    Data type options:
    1. autosuggestions
    2. emoji_keywords
    3. nouns
    4. prepositions
    5. verbs

    ...

Total Command
~~~~~~~~~~~~~

Description: Check Wikidata for the total available data for the given languages and data types.

Usage:

.. code-block:: bash

    scribe-data total [options]

Options:
^^^^^^^^

- ``-lang, --language LANGUAGE``: The language(s) to check totals for. Can be a language name or QID.
- ``-dt, --data-type DATA_TYPE``: The data type(s) to check totals for.
- ``-a, --all``: Get totals for all languages and data types.

Examples:

.. code-block:: text

    $ scribe-data total --all
    Total lexemes for all languages and data types:
    ==============================================
    Language     Data Type     Total Lexemes
    ==============================================
    English      nouns         123,456
                 verbs         234,567
    ...

.. code-block:: text

    $ scribe-data total --language English
    Returning total counts for English data types...

    Language        Data Type                 Total Wikidata Lexemes
    ================================================================
    English         adjectives                12,345
                    adverbs                   23,456
                    nouns                     34,567
    ...

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

.. code-block:: text

    $ scribe-data total --language English -dt nouns
    Language: English
    Data type: nouns
    Total number of lexemes: 12,345

.. code-block:: text

    $ scribe-data total --language Q1860 -dt verbs
    Language: Q1860
    Data type: verbs
    Total number of lexemes: 23,456

Convert Command
~~~~~~~~~~~~~~~

Description: Convert data returned by Scribe-Data to different file types.

Usage:

.. code-block:: bash

    scribe-data convert [options]

Options:
^^^^^^^^

- ``-f, --file FILE``: The file to convert to a new type.
- ``-ko, --keep-original``: Whether to keep the file to be converted (default: True).
- ``-ot, --output-type {json,csv,tsv,sqlite}``: The output file type.
