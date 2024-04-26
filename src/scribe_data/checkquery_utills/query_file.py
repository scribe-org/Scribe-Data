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
