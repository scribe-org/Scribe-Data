from checkquery_utills.query_file import QueryFile

class QueryExecutionException(Exception):
    def __init__(self, message: str, query: QueryFile) -> None:
        self.message = message
        self.query = query
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.query.path} : {self.message}"