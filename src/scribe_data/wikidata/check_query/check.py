"""
Command line tool for testing SPARQl queries against an endpoint.

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

import argparse
import contextlib
import os
import subprocess
import sys
import urllib.request
from http import HTTPStatus
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError

from tqdm.auto import tqdm

from scribe_data.wikidata.check_query.query import QueryExecutionException, QueryFile
from scribe_data.wikidata.check_query.sparql import execute, sparql_context

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

PROJECT_ROOT = "Scribe-Data"


def ping(url: str, timeout: int) -> bool:
    """
    Test if a URL is reachable.

    Parameters
    ----------
        url : str
            The URL to test.

        timeout : int
            The maximum number of seconds to wait for a reply.

    Returns
    -------
        bool : True if connectivity is established or False otherwise.
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

    Returns
    -------
        list[QueryFile] : the SPARQL query files.
    """
    parts = Path(__file__).resolve().parts
    prj_root_idx = parts.index(PROJECT_ROOT)
    prj_root = str(Path(*parts[: prj_root_idx + 1]))

    queries: list[QueryFile] = []

    for root, _, files in os.walk(prj_root):
        for f in files:
            file_path = Path(root, f)
            if file_path.suffix == ".sparql":
                queries.append(QueryFile(file_path))

    return queries


def changed_queries() -> Optional[list[QueryFile]]:
    """
    Find all the SPARQL queries that have changed.

    Includes new queries.

    Returns
    -------
        Optional[list[QueryFile]] : list of changed/new SPARQL queries or None if there's an error.
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

    changed_files = [
        Path(norm_line.split(maxsplit=1)[1]).resolve()
        for line in result.stdout.split("\n")
        if (norm_line := line.strip())
    ]

    return [QueryFile(fpath) for fpath in changed_files if fpath.suffix == ".sparql"]


def check_sparql_file(fpath: str) -> Path:
    """
    Check meta information of SPARQL query file.

    Parameters
    ----------
        fpath : str
            The file to validate.

    Returns
    -------
        Path : the validated file.
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
    ----------
        value : str
            The value to be validated.

        err_msg : str
            Used when value fails validation.

    Returns
    -------
        int : the validated number.

    Raises
    ------
        argparse.ArgumentTypeError
    """
    with contextlib.suppress(ValueError):
        number = int(value)
        if number >= 1:
            return number

    raise argparse.ArgumentTypeError(err_msg)


def check_limit(limit: str) -> int:
    """
    Validate the 'limit' argument.

    Parameters
    ----------
        limit : str
            The LIMIT to be validated.

    Returns
    -------
        int : the validated LIMIT.

    Raises
    ------
        argparse.ArgumentTypeError
    """
    return check_positive_int(limit, "LIMIT must be an integer of value 1 or greater.")


def check_timeout(timeout: str) -> int:
    """
    Validate the 'timeout' argument.

    Parameters
    ----------
        timeout : str
            The timeout to be validated.

    Returns
    -------
        int : the validated timeout.

    Raises
    ------
        argparse.ArgumentTypeError
    """
    return check_positive_int(
        timeout, "timeout must be an integer of value 1 or greater."
    )


def main(argv=None) -> int:
    """
    The main function.

    Parameters
    ----------
        argv (default=None)
            If set to None then argparse will use sys.argv as the arguments.

    Returns
    --------
        int : the exit status - 0 - success; any other value - failure.
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
    ----------
        failures (list[QueryExecutionException]) : failed queries.
    """
    if not failures:
        return

    qword = "query" if len(failures) == 1 else "queries"
    print(f"\nFollowing {qword} failed:\n", file=sys.stderr)
    for failed_query in failures:
        print(failed_query, file=sys.stderr)


def success_report(successes: list[tuple[QueryFile, dict]], display: bool) -> None:
    """
    Report successful queries.

    Parameters
    ----------
        successes : list[tuple[QueryFile, dict]]
            Successful queries.

        display : bool
            Whether there should be an output or not.
    """
    if not (display and successes):
        return

    qword = "query" if len(successes) == 1 else "queries"
    print(f"\nFollowing {qword} ran successfully:\n")
    for query, results in successes:
        print(f"{query.path} returned: {results}")


if __name__ == "__main__":
    sys.exit(main())
