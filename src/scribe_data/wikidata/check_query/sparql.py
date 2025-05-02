# SPDX-License-Identifier: GPL-3.0-or-later
"""
Functions for running SPARQL queries within the query check process.
"""

import math
import time
from urllib.error import HTTPError

import SPARQLWrapper as SPARQL
from SPARQLWrapper import SPARQLExceptions

from scribe_data.wikidata.check_query.query import QueryExecutionException, QueryFile


def sparql_context(url: str) -> SPARQL.SPARQLWrapper:
    """
    Configure a SPARQL context.

    A context allows the execution of SPARQL queries.

    Parameters
    ----------
    url : str
        A valid URL of a SPARQL endpoint.

    Returns
    -------
    SPARQLWrapper
        The context.
    """
    context = SPARQL.SPARQLWrapper(url)
    context.setReturnFormat(SPARQL.JSON)
    context.setMethod(SPARQL.POST)

    return context


def execute(
    query: QueryFile, limit: int, context: SPARQL.SPARQLWrapper, tries: int = 3
) -> dict:
    """
    Execute a SPARQL query in a given context.

    Parameters
    ----------
    query : QueryFile
        The SPARQL query to run.

    limit : int
        The maximum number of results a query should return.

    context : SPARQLWrapper
        The SPARQL context.

    tries : int
        The maximum number of times the query should be executed after failure.

    Returns
    -------
    dict
        The results of the query.
    """

    def delay_in_seconds() -> int:
        """
        How long to wait, in seconds, between executing repeat queries.

        Returns
        -------
        int
            The interval to wait based on query failures.
        """
        return int(math.ceil(10.0 / math.sqrt(tries)))

    if tries <= 0:
        raise QueryExecutionException("Failed too many times.", query)

    try:
        context.setQuery(query.load(limit))
        return context.queryAndConvert()

    except HTTPError:
        time.sleep(delay_in_seconds())
        return execute(query, limit, context, tries - 1)

    except SPARQLExceptions.SPARQLWrapperException as err:
        raise QueryExecutionException(err.msg, query) from err

    except Exception as err:
        raise QueryExecutionException(
            f"{type(err).__name__} - {str(err)}", query
        ) from err
