"""
Classes and methods for querying a file in the query check process.
"""

import pathlib
from dataclasses import dataclass


@dataclass(frozen=True)
class QueryFile:
    path: pathlib.Path

    def load(self, limit: int) -> str:
        with open(self.path, encoding="utf-8") as in_stream:
            return f"{in_stream.read()}\nLIMIT {limit}\n"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path})"


class QueryExecutionException(Exception):
    def __init__(self, message: str, query: QueryFile) -> None:
        self.message = message
        self.query = query
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.query.path} : {self.message}"
