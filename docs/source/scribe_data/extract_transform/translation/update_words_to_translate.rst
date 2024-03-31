update_words_to_translate
=========================

`View code on Github <https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/extract_transform/translation/update_words_to_translate.py>`_

Updates words to translate by running the WDQS query for the given languages.

Parameters
----------
    languages : list of strings (default=None)
        A subset of Scribe's languages that the user wants to update.

Example
-------

.. code:: bash

    python3 src/scribe_data/extract_transform/translation/update_words_to_translate.py '["French", "German"]'

..
