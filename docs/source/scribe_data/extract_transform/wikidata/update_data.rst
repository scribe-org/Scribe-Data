update_data
===========

`View code on Github <https://github.com/scribe-org/Scribe-Data/tree/main/src/scribe_data/extract_transform/wikidata/update_data.py>`_

Updates data for Scribe by running all or desired WDQS queries and formatting scripts.

Parameters
----------
    languages : list of strings (default=None)
        A subset of Scribe's languages that the user wants to update.

    word_types : list of strings (default=None)
        A subset of nouns, verbs, and prepositions that currently can be updated with this fie.

Example
-------

.. code:: bash

    python3 src/scribe_data/extract_transform/wikidata/update_data.py '["French", "German"]' '["nouns", "verbs"]'

..
