"""
Command line tool for testing SPARQl queries against an endpoint.
"""

import argparse
import contextlib
import os
import pathlib
import subprocess
import sys
import urllib.request
from typing import List, Optional, Tuple

from tqdm.auto import tqdm

from scribe_data.checkquery.query import QueryExecutionException, QueryFile
from scribe_data.checkquery.sparql import execute, sparql_context

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

PROJECT_ROOT = "Scribe-Data"


def ping(url: str, timeout: int) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.getcode() == 200
    except (urllib.error.HTTPError, Exception) as err:
        print(f"{type(err).__name__}: {str(err)}", file=sys.stderr)
    return False


def all_queries() -> List[QueryFile]:
    parts = pathlib.Path(__file__).resolve().parts
    prj_root_idx = parts.index(PROJECT_ROOT)
    prj_root = str(pathlib.Path(*parts[: prj_root_idx + 1]))

    queries: List[QueryFile] = []

    for root, _, files in os.walk(prj_root):
        for f in files:
            file_path = pathlib.Path(root, f)
            if file_path.suffix == ".sparql":
                queries.append(QueryFile(file_path))

    return queries


def changed_queries() -> Optional[List[QueryFile]]:
    result = subprocess.run(
        ("git", "status", "--short"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
    )

    if result.returncode != EXIT_SUCCESS:
        print(f"ERROR: {result.stderr}", file=sys.stderr)
        return None

    changed_files = [
        pathlib.Path(norm_line.split(maxsplit=1)[1]).resolve()
        for line in result.stdout.split("\n")
        if (norm_line := line.strip())
    ]

    return [QueryFile(fpath) for fpath in changed_files if fpath.suffix == ".sparql"]


def check_sparql_file(fpath: str) -> pathlib.Path:
    path = pathlib.Path(fpath)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"Not a valid file path: {path}")
    if path.suffix != ".sparql":
        raise argparse.ArgumentTypeError(f"{path} does not have a '.sparql' extension")
    return path


def check_positive_int(value: str, err_msg: str) -> int:
    with contextlib.suppress(ValueError):
        number = int(value)
        if number >= 1:
            return number
    raise argparse.ArgumentTypeError(err_msg)


def check_limit(limit: str) -> int:
    return check_positive_int(limit, "LIMIT must be an integer of value 1 or greater.")


def check_timeout(timeout: str) -> int:
    return check_positive_int(
        timeout, "timeout must be an integer of value 1 or greater."
    )


def main(argv: Optional[List[str]] = None) -> int:
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
            f"FAILURE: unable to contact '{endpoint}'. Network problems? Malformed URL? Increase timeout?",
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


def error_report(failures: List[QueryExecutionException]) -> None:
    if not failures:
        return
    qword = "query" if len(failures) == 1 else "queries"
    print(f"\nFollowing {qword} failed:\n", file=sys.stderr)
    for failed_query in failures:
        print(failed_query, file=sys.stderr)


def success_report(successes: List[Tuple[QueryFile, dict]], display: bool) -> None:
    if not (display and successes):
        return
    qword = "query" if len(successes) == 1 else "queries"
    print(f"\nFollowing {qword} ran successfully:\n")
    for query, results in successes:
        print(f"{query.path} returned: {results}")


if __name__ == "__main__":
    sys.exit(main())
