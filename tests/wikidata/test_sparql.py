from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

import pytest

# Adjusted import for the src/scribe_data path
from scribe_data.wikidata.check_query import sparql
from scribe_data.wikidata.check_query.query import QueryExecutionException, QueryFile


class DummyQuery(QueryFile):
    def load(self, limit: int) -> str:
        return f"SELECT * WHERE {{ ?s ?p ?o }} LIMIT {limit}"


def test_sparql_context_configures_wrapper():
    url = "https://example.org/sparql"
    context = sparql.sparql_context(url)

    # Asserts that the SPARQLWrapper context is configured correctly
    assert context.endpoint == url
    assert context.returnFormat == 4  # SPARQL.JSON == 4
    assert context.method == "POST"


def test_execute_success():
    mock_context = MagicMock()
    dummy_query = DummyQuery("dummy/path")

    # Mock the query result
    mock_context.queryAndConvert.return_value = {"results": "some-data"}

    # Execute the query
    result = sparql.execute(dummy_query, 10, mock_context)

    # Validate the result and mock calls
    assert result == {"results": "some-data"}
    mock_context.setQuery.assert_called_once()
    mock_context.queryAndConvert.assert_called_once()


def test_execute_retries_on_http_error():
    mock_context = MagicMock()
    dummy_query = DummyQuery("dummy/path")

    # Simulate HTTPError followed by a successful response
    mock_context.queryAndConvert.side_effect = [
        HTTPError(None, None, None, None, None),
        {"results": "retry-success"},
    ]

    with patch(
        "time.sleep", return_value=None
    ):  # Mock time.sleep to avoid actual delay
        result = sparql.execute(dummy_query, 10, mock_context)

    # Assert that the retry logic works and the result is correct
    assert result == {"results": "retry-success"}


def test_execute_raises_on_sparql_wrapper_exception():
    mock_context = MagicMock()
    dummy_query = DummyQuery("dummy/path")

    # Simulate a SPARQLWrapperException
    class DummySparqlException(Exception):
        def __init__(self, msg):
            self.msg = msg

    with patch(
        "scribe_data.wikidata.check_query.sparql.SPARQLExceptions.SPARQLWrapperException",
        DummySparqlException,
    ):
        # Mock the query to raise the exception
        mock_context.queryAndConvert.side_effect = DummySparqlException("SPARQL error")

        # Ensure that the QueryExecutionException is raised correctly
        with pytest.raises(QueryExecutionException) as exc_info:
            sparql.execute(dummy_query, 10, mock_context)

        # Assert that the exception message is correct
        assert "SPARQL error" in str(exc_info.value)


def test_execute_raises_on_generic_exception():
    mock_context = MagicMock()
    dummy_query = DummyQuery("dummy/path")

    # Simulate a generic exception (ValueError)
    mock_context.queryAndConvert.side_effect = ValueError("Unexpected failure")

    # Ensure that the QueryExecutionException is raised with the correct message
    with pytest.raises(QueryExecutionException) as exc_info:
        sparql.execute(dummy_query, 10, mock_context)

    # Assert that the exception contains the right error message
    assert "ValueError - Unexpected failure" in str(exc_info.value)
