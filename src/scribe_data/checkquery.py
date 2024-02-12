#!/usr/bin/env python3

"""
Command line tool for testing SPARQl queries against an endpoint.
"""

import argparse
import math
import os
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError

import SPARQLWrapper as SPARQL
from SPARQLWrapper import SPARQLExceptions
from tqdm.auto import tqdm


EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_CLI_ERROR = 2

PROJECT_ROOT = "Scribe-Data"


@dataclass(repr=False, frozen=True)
class QueryFile:
    """
    Holds a reference to a file containing a SPARQL query.
    """

    path: Path

    def load(self, limit: int) -> str:
        """Load the SPARQL query from 'path' into a string.

        Parameters
    -----------
        source_value : str
            The source value to find equivalents for (e.g. 'english').
        source_key : str
            The source key to reference (e.g. 'language').
        target_key : str
            The key to target (e.g. 'iso').
        error_msg : str
            The message displayed when a value cannot be found.

        Returns:
            The 'target' value given the passed arguments.
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
    -----------
        source_value : str
            The source value to find equivalents for (e.g. 'english').
        source_key : str
            The source key to reference (e.g. 'language').
        target_key : str
            The key to target (e.g. 'iso').
        error_msg : str
            The message displayed when a value cannot be found.
        """
        self.message = message
        self.query = query
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.query.path} : {self.message}"


def ping(url: str, timeout: int) -> bool:
    """
    Test if a URL is reachable.
 Parameters
    -----------
        source_value : str
            The source value to find equivalents for (e.g. 'english').
        source_key : str
            The source key to reference (e.g. 'language').
        target_key : str
            The key to target (e.g. 'iso').
        error_msg : str
            The message displayed when a value cannot be found.

    
    Returns
    --------
        The 'target' value given the passed arguments.
    """
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.getcode() == HTTPStatus.OK
    except (HTTPError, Exception) as err:
        print(f"{type(err).__name__}: {str(err)}", file=sys.stderr)

    return False


def all_queries() -> list[QueryFile]:
    """
    All the SPARQL queries in, and below, 'Scribe-Data/'.

    Returns:
        list[QueryFile]: the SPARQL query files.
    """
    parts = Path(__file__).resolve().parts
    prj_root_idx = parts.index(PROJECT_ROOT)
    prj_root = str(Path(*parts[: prj_root_idx + 1]))

    queries: list[QueryFile] = []

    for root, _, fnames in os.walk(prj_root):
        for fname in fnames:
            fpath = Path(root, fname)
            if fpath.suffix == ".sparql":
                queries.append(QueryFile(fpath))

    return queries


def changed_queries() -> Optional[list[QueryFile]]:
    """
    Find all the SPARQL queries that have changed.

    Includes new queries.

    Returns:
        Optional[list[QueryFile]]: list of changed/new SPARQL queries or None if error.
    """

    result = subprocess.run(
        (
            "git",
            "status",
            "--short",
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
    )

    if result.returncode != EXIT_SUCCESS:
        print(f"ERROR: {result.stderr}", file=sys.stderr)
        return None

    # example 'result.stdout'
    #
    # M a/b/c/changed.sparql
    # ?? ../new.sparql

    changed_files = [
        Path(norm_line.split(maxsplit=1)[1]).resolve()
        for line in result.stdout.split("\n")
        if (norm_line := line.strip())
    ]

    return [QueryFile(fpath) for fpath in changed_files if fpath.suffix == ".sparql"]


def sparql_context(url: str) -> SPARQL.SPARQLWrapper:
    """
    Configure a SPARQL context.

    A context allows the execution of SPARQL queries.
 Parameters
    -----------
        source_value : str
            The source value to find equivalents for (e.g. 'english').
        source_key : str
            The source key to reference (e.g. 'language').
        target_key : str
            The key to target (e.g. 'iso').
        error_msg : str
            The message displayed when a value cannot be found.

    Returns
    --------
        The 'target' value given the passed arguments.
    """
   
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
    -----------
        source_value : str
            The source value to find equivalents for (e.g. 'english').
        source_key : str
            The source key to reference (e.g. 'language').
        target_key : str
            The key to target (e.g. 'iso').
        error_msg : str
            The message displayed when a value cannot be found.

    Returns
    --------
        The 'target' value given the passed arguments.
    """

    def delay_in_seconds() -> int:
        """How long to wait, in seconds, between executing repeat queries."""
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


def check_sparql_file(fpath: str) -> Path:
    """
    Check meta information of SPARQL query file.

    Parameters
    -----------
        source_value : str
            The source value to find equivalents for (e.g. 'english').
        source_key : str
            The source key to reference (e.g. 'language').
        target_key : str
            The key to target (e.g. 'iso').
        error_msg : str
            The message displayed when a value cannot be found.

    Returns
    --------
        The 'target' value given the passed arguments.
    """
    path = Path(fpath)

    if not path.is_file():
        raise argparse.ArgumentTypeError(f"Not a valid file path: {path}")

    if path.suffix != ".sparql":
        raise argparse.ArgumentTypeError(f"{path} does not have a '.sparql' extension")

    return path


def check_positive_int(value: str, err_msg: str) -> int:
    """
    Ensure 'value' is a positive number.

     Parameters
    -----------
        source_value : str
            The source value to find equivalents for (e.g. 'english').
        source_key : str
            The source key to reference (e.g. 'language').
        target_key : str
            The key to target (e.g. 'iso').
        error_msg : str
            The message displayed when a value cannot be found.

    Raises
    -------
        ValueError : when a source_value is not supported.

    Returns
    --------
        The 'target' value given the passed arguments.
    """
    try:
        number = int(value)
        if number >= 1:
            return number
    except ValueError:
        pass

    raise argparse.ArgumentTypeError(err_msg)


def check_limit(limit: str) -> int:
    """
    Validate the 'limit' argument.

    Parameters
    -----------
        source_value : str
            The source value to find equivalents for (e.g. 'english').
        source_key : str
            The source key to reference (e.g. 'language').
        target_key : str
            The key to target (e.g. 'iso').
        error_msg : str
            The message displayed when a value cannot be found.

    Raises
    -------
        ValueError : when a source_value is not supported.

    Returns
    --------
        The 'target' value given the passed arguments.
    """
    return check_positive_int(limit, "LIMIT must be an integer of value 1 or greater.")


def check_timeout(timeout: str) -> int:
    """
    Validate the 'timeout' argument.

    Parameters
    -----------
        source_value : str
            The source value to find equivalents for (e.g. 'english').
        source_key : str
            The source key to reference (e.g. 'language').
        target_key : str
            The key to target (e.g. 'iso').
        error_msg : str
            The message displayed when a value cannot be found.

    Raises
    -------
        ValueError : when a source_value is not supported.

    Returns
    --------
        The 'target' value given the passed arguments.
    """
    return check_positive_int(
        timeout, "timeout must be an integer of value 1 or greater."
    )


def main(argv=None) -> int:
    """
    The main function.
 Parameters
    -----------
        source_value : str
            The source value to find equivalents for (e.g. 'english').
        source_key : str
            The source key to reference (e.g. 'language').
        target_key : str
            The key to target (e.g. 'iso').
        error_msg : str
            The message displayed when a value cannot be found.

    Returns
    --------
        The 'target' value given the passed arguments.
    """
    cli = argparse.ArgumentParser(
        description=f"run SPARQL queries from the '{PROJECT_ROOT}' project",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    group = cli.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-c",
        "--changed",
        action="store_true",
        help="run only changed/new SPARQL queries",
    )

    group.add_argument(
        "-a", "--all", action="store_true", help="run all SPARQL queries"
    )

    group.add_argument(
        "-f",
        "--file",
        help="path to a file containing a valid SPARQL query",
        type=check_sparql_file,
    )

    group.add_argument(
        "-p",
        "--ping",
        action="store_true",
        default=False,
        help="check responsiveness of endpoint",
    )

    cli.add_argument(
        "--timeout",
        type=check_timeout,
        default=10,
        help="maximum number of seconds to wait for a response from the endpoint when 'pinging'",
    )

    cli.add_argument(
        "-e",
        "--endpoint",
        type=str,
        default="https://query.wikidata.org/sparql",
        help="URL of the SPARQL endpoint",
    )

    cli.add_argument(
        "-l",
        "--limit",
        type=check_limit,
        default=5,
        help="the maximum number or results a query should return",
    )

    cli.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="increase output verbosity",
    )

    args = cli.parse_args(argv)

    endpoint = args.endpoint

    if args.ping:
        if ping(endpoint, args.timeout):
            print(f"Success: pinged '{endpoint}'")
            return EXIT_SUCCESS

        print(
            f"FAILURE: unable to contact '{endpoint}'. Network problems? "
            "Malformed URL? Increase timeout?",
            file=sys.stderr,
        )
        return EXIT_FAILURE

    queries = None

    if args.all:
        queries = all_queries()
    elif args.changed:
        queries = changed_queries()
    elif args.file:
        queries = [QueryFile(args.file)]
    else:
        assert False, "Unknown option"

    if queries is None:
        return EXIT_FAILURE

    context = sparql_context(endpoint)

    failures = []
    successes = []

    for query in tqdm(queries, position=0):
        try:
            results = execute(query, args.limit, context)
            successes.append((query, results))
        except QueryExecutionException as err:
            failures.append(err)

    success_report(successes, display=args.verbose)
    error_report(failures)

    print("\nSummary")
    print(
        f"\tQueries run: {len(queries)}, passed: {len(successes)}, failed: {len(failures)}\n"
    )

    return EXIT_FAILURE if failures else EXIT_SUCCESS


def error_report(failures: list[QueryExecutionException]) -> None:
    """
    Report failed queries.

     Parameters
    -----------
        source_value : str
            The source value to find equivalents for (e.g. 'english').
        source_key : str
            The source key to reference (e.g. 'language').
        target_key : str
            The key to target (e.g. 'iso').
        error_msg : str
            The message displayed when a value cannot be found.

    Raises
    -------
        ValueError : when a source_value is not supported.

    Returns
    --------
        The 'target' value given the passed arguments.
    """
    if not failures:
        return

    qword = "query" if len(failures) == 1 else "queries"
    print(f"\nFollowing {qword} failed:\n", file=sys.stderr)
    for failed_query in failures:
        print(str(failed_query), file=sys.stderr)


def success_report(successes: list[tuple[QueryFile, dict]], display: bool) -> None:
    """
    Report successful queries.

    Parameters
    -----------
        source_value : str
            The source value to find equivalents for (e.g. 'english').
        source_key : str
            The source key to reference (e.g. 'language').
        target_key : str
            The key to target (e.g. 'iso').
        error_msg : str
            The message displayed when a value cannot be found.

    Raises
    -------
        ValueError : when a source_value is not supported.

    Returns
    --------
        The 'target' value given the passed arguments.
    """
    if not (display and successes):
        return

    qword = "query" if len(successes) == 1 else "queries"
    print(f"\nFollowing {qword} ran successfully:\n")
    for query, results in successes:
        print(f"{query.path} returned: {results}")


if __name__ == "__main__":
    sys.exit(main())
