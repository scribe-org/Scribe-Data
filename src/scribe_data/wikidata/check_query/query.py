# SPDX-License-Identifier: GPL-3.0-or-later
"""
Classes and methods for querying a file in the query check process.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(repr=False, frozen=True)
class QueryFile:
    """
    Holds a reference to a file containing a SPARQL query.
    """

    path: Path

    def load(self, limit: int) -> str:
        """
        Load the SPARQL query from 'path' into a string.

        Parameters
        ----------
        limit : int
            The maximum number of results a query should return.

        Returns
        -------
        str
            The SPARQL query.
        """
        with open(self.path, encoding="utf-8") as in_stream:
            return f"{in_stream.read()}\nLIMIT {limit}\n"

    def __repr__(self) -> str:
        """
        Return a representation of the class.

        Returns
        -------
        str
            The class name and path to the query file.
        """
        return f"{self.__class__.__name__}(path={self.path})"


class QueryExecutionException(Exception):
    """
    Raised when execution of a query fails.

    Parameters
    ----------
    message : str
        The error message.

    query : QueryFile
        The query that failed.
    """

    def __init__(self, message: str, query: QueryFile) -> None:
        """
        Construct the query execution exception class.

        Parameters
        ----------
        message : str
            The error message.

        query : QueryFile
            The query that failed.
        """
        self.message = message
        self.query = query
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        String method.

        Returns
        -------
        str
            The query path and a message about the given query.
        """
        return f"{self.query.path} : {self.message}"
