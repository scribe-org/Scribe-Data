"""
Classes and methods for querying a file in the query check process.

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
            str : the SPARQL query.
        """
        with open(self.path, encoding="utf-8") as in_stream:
            return f"{in_stream.read()}\nLIMIT {limit}\n"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path})"


class QueryExecutionException(Exception):
    """
    Raised when execution of a query fails.
    """

    def __init__(self, message: str, query: QueryFile) -> None:
        """
        Parameters
        ----------
            message : str
                Why the query failed.

            query : QueryFile
                The query that failed.
        """
        self.message = message
        self.query = query
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.query.path} : {self.message}"
