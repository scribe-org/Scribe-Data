query_profanity.sparql
======================

`View code on Github <https://github.com/scribe-org/Scribe-Data/tree/main/src/scribe_data/wikidata/query_profanity.sparql>`_

Queries all profane words for a given language. These words can then be removed from autosuggest and autocomplete options in client applications. Enter this query at https://query.wikidata.org/ and replace LANGUAGE_QID with the desired language.

.. code:: sparql

    # tool: scribe-data

    SELECT DISTINCT
      ?lexemeID
      ?lastModified
      ?profanity

    WHERE {
      ?lexemeID dct:language wd:LANGUAGE_QID;  # replace language qid here
        wikibase:lemma ?profanity;
        ontolex:sense ?sense;
        schema:dateModified ?lastModified.

      VALUES ?filter {
        wd:Q545779  # pejorative
        wd:Q1521634  # vulgar
        wd:Q184439  # profanity
      }.

      FILTER EXISTS {?sense wdt:P6191 ?filter.}.
    }

    ORDER BY
      lcase(?profanity)
