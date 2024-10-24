"""
Functions for running SPARQL queries within the query check process.

.. raw:: html

    <!--
    * Copyright (C) 2024 Scribe
    *
    * This program is free software: you can redistribute it and/or modify
    * it under the terms of the GNU General Public License as published by
    * the Free Software Foundation, either version 3 of the License, or
    * (at your option) any later version.
    *
    * This program is distributed in the hope that it will be useful,
    * but WITHOUT ANY WARRANTY; without even the implied warranty of
    * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    * GNU General Public License for more details.
    *
    * You should have received a copy of the GNU General Public License
    * along with this program.  If not, see <https://www.gnu.org/licenses/>.
    -->
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
        SPARQLWrapper : the context.
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
        dict : the results of the query.
    """

    def delay_in_seconds() -> int:
        """
        How long to wait, in seconds, between executing repeat queries.
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
