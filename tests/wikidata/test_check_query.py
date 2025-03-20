# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the check_query process.
"""

import argparse
from http import HTTPStatus
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch
from urllib.error import HTTPError

import pytest

from scribe_data.wikidata.check_query.check import (
    all_queries,
    changed_queries,
    check_limit,
    check_sparql_file,
    check_timeout,
    error_report,
    main,
    ping,
    success_report,
)
from scribe_data.wikidata.check_query.query import QueryExecutionException, QueryFile
from scribe_data.wikidata.check_query.sparql import execute


def normalize_path(path):
    return str(Path(path))


S_PATH = "/root/project/src/dir/query.sparql"
S_PATH = normalize_path(S_PATH)
A_PATH = Path(normalize_path(S_PATH))


@pytest.fixture
def a_query():
    return QueryFile(A_PATH)


# MARK: Query
def test_full_path(a_query):
    assert a_query.path == A_PATH


@patch("builtins.open", new_callable=mock_open, read_data="QUERY")
def test_query_load(_, a_query):
    assert a_query.load(12) == "QUERY\nLIMIT 12\n"


def test_query_equals(a_query):
    assert a_query == QueryFile(A_PATH)


def test_query_not_equals(a_query):
    assert a_query != QueryFile(normalize_path("/root/project/src/Dir/query.sparql"))


def test_query_not_equals_object(a_query):
    assert a_query != object()


def test_query_str(a_query):
    assert (
        str(a_query)
        == f"QueryFile(path={normalize_path('/root/project/src/dir/query.sparql')})"
    )


def test_query_repr(a_query):
    assert (
        repr(a_query)
        == f"QueryFile(path={normalize_path('/root/project/src/dir/query.sparql')})"
    )


def test_query_execution_exception(a_query):
    exception = QueryExecutionException("failure", a_query)
    assert str(exception) == f"{S_PATH} : failure"


# MARK: ping
@patch("urllib.request.urlopen")
def test_ping_pass(mock_urlopen):
    mock_urlopen.return_value.__enter__.return_value.getcode.return_value = (
        HTTPStatus.OK
    )

    assert ping("http://www.python.org", 0)


@patch("urllib.request.urlopen")
def test_ping_httperror_fail(mock_urlopen):
    mock_urlopen.return_value.__enter__.side_effect = HTTPError

    assert not ping("http://www.python.org", 0)


@patch("urllib.request.urlopen")
def test_ping_exception_fail(mock_urlopen):
    mock_urlopen.return_value.__enter__.side_effect = Exception

    assert not ping("http://www.python.org", 0)


@patch("urllib.request.urlopen")
def test_ping_fail(mock_urlopen):
    mock_urlopen.return_value.__enter__.return_value.getcode.return_value = (
        HTTPStatus.BAD_REQUEST
    )
    assert not ping("http://www.python.org", 0)


# MARK: check_sparql_file
@patch.object(Path, "is_file", return_value=True)
def test_check_sparql_file_exists(_):
    assert check_sparql_file(S_PATH) == A_PATH


@patch.object(Path, "is_file", return_value=False)
def test_check_sparql_file_not_exists(_):
    with pytest.raises(argparse.ArgumentTypeError) as err:
        _ = check_sparql_file(S_PATH)

    assert str(err.value) == f"Not a valid file path: {S_PATH}"


@patch.object(Path, "is_file", return_value=True)
def test_check_sparql_file_not_sparql_extension(_):
    fpath = Path("/root/query.txt")
    with pytest.raises(argparse.ArgumentTypeError) as err:
        _ = check_sparql_file(fpath)

    assert str(err.value) == f"{fpath} does not have a '.sparql' extension"


# MARK: changed_queries
@pytest.mark.parametrize(
    "git_status, expected",
    [
        ("", []),
        ("\n", []),
        ("?? README.md \n M   .gitignore", []),
        (" M /a/b/a.sparql", [QueryFile(Path("/a/b/a.sparql"))]),
        (
            "   M    /a/with space/a.sparql \n ",
            [QueryFile(Path("/a/with space/a.sparql"))],
        ),
        (" M /a/a.sparql\nM a.txt", [QueryFile(Path("/a/a.sparql"))]),
        (
            " M /a/a.sparql\nM /a/a.txt\n ??   /a/b.sparql",
            [QueryFile(Path("/a/a.sparql")), QueryFile(Path("/a/b.sparql"))],
        ),
    ],
)
@patch("subprocess.run")
def test_changed_queries(mock_run, git_status, expected):
    mock_result = MagicMock()
    mock_result.configure_mock(**{"returncode": 0, "stdout": git_status})

    mock_run.return_value = mock_result
    expected = [QueryFile(Path(p.path).resolve()) for p in expected]
    assert changed_queries() == expected


@patch("subprocess.run")
def test_changed_queries_failure(mock_run, capsys):
    mock_result = MagicMock()
    mock_result.configure_mock(**{"returncode": 1, "stderr": "no git"})

    mock_run.return_value = mock_result
    assert changed_queries() is None

    err_out = capsys.readouterr().err
    assert "ERROR: no git" == err_out.strip()


# MARK: all_queries
@pytest.mark.parametrize(
    "tree, expected",
    [
        (
            [
                ("/root", ("src",), ("README.txt",)),
                ("/root/src", (), ("spam.sh", "eggs.py")),
            ],
            [],
        ),
        (
            [
                ("/root", ("src",), ("a.sparql",)),
                ("/root/src", (), ("sparql.pdf", "b.sparql")),
            ],
            [
                QueryFile(Path(normalize_path("/root/a.sparql"))),
                QueryFile(Path(normalize_path("/root/src/b.sparql"))),
            ],
        ),
    ],
)
def test_all_queries(tree, expected):
    with patch("os.walk") as mock_walk:
        mock_walk.return_value = tree
        assert all_queries() == expected


# MARK: execute


def test_execute(a_query):
    with pytest.raises(QueryExecutionException) as err:
        _ = execute(a_query, 1, None, 0)

        assert str(err) == f"{a_query.path} : Failed too many times."


# MARK: check_limit
@pytest.mark.parametrize(
    "candidate, limit",
    [
        ("1", 1),
        ("34", 34),
        ("1000", 1000),
    ],
)
def test_check_limit_pos(candidate, limit):
    assert check_limit(candidate) == limit


@pytest.mark.parametrize(
    "candidate",
    [
        "0",
        "-1",
        "a",
        "word",
    ],
)
def test_check_limit_neg(candidate):
    with pytest.raises(argparse.ArgumentTypeError) as err:
        _ = check_limit(candidate)

    assert str(err.value) == "LIMIT must be an integer of value 1 or greater."


# MARK: check_timeout
@pytest.mark.parametrize(
    "candidate, timeout",
    [
        ("1", 1),
        ("9", 9),
        ("8888", 8888),
    ],
)
def test_check_timeout_pos(candidate, timeout):
    assert check_timeout(candidate) == timeout


@pytest.mark.parametrize(
    "candidate",
    [
        "0",
        "-1",
        "O",
        "ten",
    ],
)
def test_check_timeout_neg(candidate):
    with pytest.raises(argparse.ArgumentTypeError) as err:
        _ = check_timeout(candidate)

    assert str(err.value) == "timeout must be an integer of value 1 or greater."


# MARK: main


@pytest.mark.parametrize("arg", ["-h", "--help"])
def test_main_help(arg):
    with pytest.raises(SystemExit) as err:
        _ = main(arg)
        assert err.code == 0


@pytest.mark.parametrize(
    "args",
    [
        ["-a", "-c"],
        ["-p", "-f"],
        ["-p", "-c"],
        ["-p", "-a"],
        ["-c", "-p", "-a"],
        ["-c", "-f", "-a"],
    ],
)
def test_main_mutex_opts(args):
    """
    Some options cannot be used together.
    """
    with pytest.raises(SystemExit) as err:
        _ = main([args])
        assert err.code == 2


def test_error_report_single(a_query, capsys):
    failures = [QueryExecutionException("timeout", a_query)]
    error_report(failures)
    err_out = capsys.readouterr().err

    assert (
        err_out == "\nFollowing query failed:\n\n"
        f"{normalize_path('/root/project/src/dir/query.sparql')} : timeout\n"
    )


def test_error_report_multiple(a_query, capsys):
    failures = [
        QueryExecutionException("timeout", a_query),
        QueryExecutionException("bad format", a_query),
    ]
    error_report(failures)
    err_out = capsys.readouterr().err

    assert (
        err_out == "\nFollowing queries failed:\n\n"
        f"{normalize_path('/root/project/src/dir/query.sparql')} : timeout\n"
        f"{normalize_path('/root/project/src/dir/query.sparql')} : bad format\n"
    )


def test_error_report_no_errors(capsys):
    error_report([])
    assert capsys.readouterr().err == ""


def test_success_report_single_display_set(a_query, capsys):
    successes = [(a_query, {"a": 23})]
    success_report(successes, display=True)

    out = capsys.readouterr().out

    assert (
        out == "\nFollowing query ran successfully:\n\n"
        f"{normalize_path('/root/project/src/dir/query.sparql')} returned: {{'a': 23}}\n"
    )


def test_success_report_no_success_display_set(capsys):
    success_report([], display=True)

    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    "successes",
    [[], [(a_query, {"a": 23})], [(a_query, {"a": 23}), (a_query, {"b": 53})]],
)
def test_success_report_display_not_set(successes, capsys):
    success_report(successes, display=False)

    out = capsys.readouterr().out

    assert out == ""


def test_success_report_multiple_display_set(a_query, capsys):
    successes = [(a_query, {"a": 23}), (a_query, {"b": 57})]
    success_report(successes, display=True)
    out = capsys.readouterr().out

    assert (
        out == "\nFollowing queries ran successfully:\n\n"
        f"{normalize_path('/root/project/src/dir/query.sparql')} returned: {{'a': 23}}\n"
        f"{normalize_path('/root/project/src/dir/query.sparql')} returned: {{'b': 57}}\n"
    )
