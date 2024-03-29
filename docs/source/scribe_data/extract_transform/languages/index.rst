languages
=========

`View code on Github <https://github.com/scribe-org/Scribe-Data/tree/main/src/scribe_data/extract_transform/languages>`_

Languages
---------

This directory contains all language extraction and formatting code for Scribe-Data. The structure is broken down by language, with each language sub-directory then including directories for nouns, prepositions, translations and verbs if needed. Within these word type directories are :code:`query_WORD_TYPE.sparql` SPARQL files that are ran to query Wikidata and then formatted with the given :code:`format_WORD_TYPE.py` Python files. Included in each language sub-directory is also a :code:`formatted_data` directory that includes the outputs of all word type query and formatting processes.

Use the :code:`View code on GitHub` link above to view the directory and explore the process!
