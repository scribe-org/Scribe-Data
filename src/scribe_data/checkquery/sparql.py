"""
Functions for running SPARQL queries within the query check process.
"""

import math
import time
from urllib.error import HTTPError

import SPARQLWrapper as SPARQL
from SPARQLWrapper import SPARQLExceptions

from scribe_data.checkquery.query import QueryExecutionException, QueryFile


def sparql_context(url: str) -> SPARQL.SPARQLWrapper:
    context = SPARQL.SPARQLWrapper(url)
    context.setReturnFormat(SPARQL.JSON)
    context.setMethod(SPARQL.POST)
    return context


def execute(query: QueryFile, limit: int, context: SPARQL.SPARQLWrapper) -> dict:
    def delay_in_seconds() -> int:
        return int(math.ceil(10.0 / math.sqrt(3)))

    try:
        context.setQuery(query.load(limit))
        return context.queryAndConvert()
    except HTTPError:
        time.sleep(delay_in_seconds())
        return execute(query, limit, context)
    except SPARQLExceptions.SPARQLWrapperException as err:
        raise QueryExecutionException(err.msg, query) from err
    except Exception as err:
        raise QueryExecutionException(
            f"{type(err).__name__} - {str(err)}", query
        ) from err
