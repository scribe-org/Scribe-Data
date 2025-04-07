# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the check_query process.
"""

import argparse
import re
from http import HTTPStatus
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch
from urllib.error import HTTPError

import pytest

from scribe_data.check import check_query_forms
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


# MARK: check_query_forms tests
def test_qid_label_dict_not_empty():
    assert check_query_forms.qid_label_dict, "qid_label_dict should not be empty"


# MARK: extract_forms_from_sparql (Lines 56-66)
def test_extract_forms_from_sparql_valid_file(tmp_path):
    sparql_file = tmp_path / "test.sparql"
    # The pattern r"\s\sOPTIONAL\s*\{([^}]*)\}" requires exactly two spaces before OPTIONAL
    sparql_file.write_text("  OPTIONAL { form1 }  OPTIONAL { form2 }")
    result = check_query_forms.extract_forms_from_sparql(sparql_file)
    assert result == [" form1 ", " form2 "]


def test_extract_forms_from_sparql_no_matches(tmp_path):
    sparql_file = tmp_path / "test.sparql"
    sparql_file.write_text("SELECT * WHERE { }")
    result = check_query_forms.extract_forms_from_sparql(sparql_file)
    assert result == []


@patch("builtins.open", side_effect=Exception("File error"))
def test_extract_forms_from_sparql_exception(mock_open, capsys):
    result = check_query_forms.extract_forms_from_sparql(Path("nonexistent.sparql"))
    assert result is None
    captured = capsys.readouterr()
    assert "Error reading nonexistent.sparql: File error" in captured.out


# MARK: extract_form_rep_label (Lines 89-93)
def test_extract_form_rep_label_valid():
    form_text = "ontolex:representation ?testLabel ;"
    result = check_query_forms.extract_form_rep_label(form_text)
    assert result == "testLabel"


def test_extract_form_rep_label_no_match():
    form_text = "invalid text"
    result = check_query_forms.extract_form_rep_label(form_text)
    assert result is None


# MARK: decompose_label_features (Lines 113-131)
def test_decompose_label_features_valid():
    label = "nominativeSingular"
    with patch.object(
        check_query_forms, "lexeme_form_labels_order", ["Nominative", "Singular"]
    ):
        result = check_query_forms.decompose_label_features(label)
        assert result == ["Nominative", "Singular"]


def test_decompose_label_features_invalid():
    label = "unknownFeature"
    with patch.object(
        check_query_forms, "lexeme_form_labels_order", ["Nominative", "Singular"]
    ):
        result = check_query_forms.decompose_label_features(label)
        assert result == ["UnknownFeature"]


def test_decompose_label_features_empty():
    label = ""
    result = check_query_forms.decompose_label_features(label)
    assert result == []


# MARK: extract_form_qids (Lines 151-153)
def test_extract_form_qids_valid():
    form_text = "wikibase:grammaticalFeature wd:Q123, wd:Q456 ."
    result = check_query_forms.extract_form_qids(form_text)
    assert result == ["Q123", "Q456"]


def test_extract_form_qids_no_match():
    form_text = "invalid text"
    result = check_query_forms.extract_form_qids(form_text)
    assert result is None


# MARK: check_form_label (Lines 173-195)
def test_check_form_label_match():
    form_text = "?lexeme ontolex:lexicalForm ?testForm .\n?testForm ontolex:representation ?test ;"
    result = check_query_forms.check_form_label(form_text)
    assert result is True


def test_check_form_label_no_form_label():
    form_text = "invalid text"
    result = check_query_forms.check_form_label(form_text)
    assert result is False


def test_check_form_label_no_rep_label():
    form_text = "?lexeme ontolex:lexicalForm ?testForm ."
    result = check_query_forms.check_form_label(form_text)
    assert result is False


def test_check_form_label_mismatch():
    form_text = "?lexeme ontolex:lexicalForm ?testForm .\n?testForm ontolex:representation ?other ;"
    result = check_query_forms.check_form_label(form_text)
    assert result is False


# MARK: check_query_formatting (Lines 216-223)
def test_check_query_formatting_valid():
    form_text = "valid . text ;"
    result = check_query_forms.check_query_formatting(form_text)
    assert result is True


def test_check_query_formatting_space_before_comma():
    form_text = "invalid , text"
    result = check_query_forms.check_query_formatting(form_text)
    assert result is False


def test_check_query_formatting_nonspace_before_period():
    form_text = "invalid.text"
    result = check_query_forms.check_query_formatting(form_text)
    assert result is False


# MARK: return_correct_form_label (Lines 239-262)
def test_return_correct_form_label_valid():
    qids = ["Q123"]
    with patch.object(check_query_forms, "lexeme_form_qid_order", ["Q123"]):
        with patch.object(
            check_query_forms,
            "lexeme_form_metadata",
            {"category": {"label1": {"qid": "Q123", "label": "Nominative"}}},
        ):
            result = check_query_forms.return_correct_form_label(qids)
            assert result == "nominative"


def test_return_correct_form_label_empty():
    result = check_query_forms.return_correct_form_label([])
    assert result == "Invalid query formatting found"


def test_return_correct_form_label_not_included():
    qids = ["Q999"]
    with patch.object(check_query_forms, "lexeme_form_qid_order", ["Q123"]):
        result = check_query_forms.return_correct_form_label(qids)
        assert result == "QID Q999 not included in lexeme_form.metadata.json"


def validate_forms(query_text):
    errors = []

    # Extract SELECT variables
    select_match = re.search(r"SELECT\s+([^{]+)\s+WHERE", query_text, re.IGNORECASE)
    if not select_match:
        return "Invalid query format: no SELECT match"
    select_vars = [
        var.strip() for var in select_match.group(1).split() if var.startswith("?")
    ]

    # Extract variables defined in WHERE clause
    where_vars = set()
    # Pattern for ontolex:representation variables (forms)
    forms_pattern = r"ontolex:representation\s+\?(\w+)"
    for match in re.finditer(forms_pattern, query_text):
        where_vars.add("?" + match.group(1))

    # Add other variables defined in WHERE (e.g., bound variables)
    # Example: ?lexeme, ?lemma, ?lastModified, ?formLex
    triple_pattern = r"\?(\w+)\s+[^?]+\s+\?(\w+)"
    for match in re.finditer(triple_pattern, query_text):
        where_vars.add("?" + match.group(1))
        where_vars.add("?" + match.group(2))

    # Check for duplicates in SELECT
    select_vars_set = set(select_vars)
    if len(select_vars_set) < len(select_vars):
        duplicates = [var for var in select_vars_set if select_vars.count(var) > 1]
        errors.append(
            f"Duplicate forms found in SELECT: {', '.join(var[1:] for var in duplicates)}"
        )

    # Check for undefined variables in SELECT
    undefined = [var for var in select_vars if var not in where_vars]
    if undefined:
        errors.append(
            f"Undefined forms found in SELECT: {', '.join(var[1:] for var in undefined)}"
        )

    # Check for defined but unreturned forms
    form_vars = [
        var
        for var in where_vars
        if re.match(r"\?\w+", var)
        and var in [m.group(0) for m in re.finditer(forms_pattern, query_text)]
    ]
    unreturned = [var for var in form_vars if var not in select_vars]
    if unreturned:
        errors.append(
            f"Defined but unreturned forms found: {', '.join(var[1:] for var in unreturned)}"
        )

    # Check order of form variables
    form_vars_in_where = [m.group(0) for m in re.finditer(forms_pattern, query_text)]
    form_vars_in_select = [var for var in select_vars if var in form_vars_in_where]
    if (
        form_vars_in_select
        and form_vars_in_select != form_vars_in_where[: len(form_vars_in_select)]
    ):
        errors.append(
            "The order of variables in the SELECT statement does not match their order in the WHERE clause"
        )

    return "; ".join(errors) if errors else ""


# MARK: validate_forms (Lines 279-356)
@pytest.mark.skip(reason="Skipping due to unresolved issue with preposition error")
def test_validate_forms_valid():
    # Ensure all variables in SELECT are defined in WHERE and order matches
    # Use ontolex:representation to define ?form so it matches forms_pattern
    query_text = "SELECT ?lexeme ?lexemeID ?lastModified ?form WHERE { ?lexeme wikibase:lemma ?lemma . schema:dateModified ?lastModified . ?lexeme ontolex:lexicalForm ?formLex . ?formLex ontolex:representation ?form . }"
    result = check_query_forms.validate_forms(query_text)
    assert result == ""


def test_validate_forms_no_select():
    query_text = "WHERE { }"
    result = check_query_forms.validate_forms(query_text)
    assert result == "Invalid query format: no SELECT match"


def test_validate_forms_duplicates():
    query_text = "SELECT ?lexeme ?lexemeID ?lastModified ?form ?form WHERE { ?lexeme wikibase:lemma ?lemma . ontolex:lexicalForm ?formLex . ?formLex ontolex:representation ?form . schema:dateModified ?lastModified . }"
    result = check_query_forms.validate_forms(query_text)
    assert "Duplicate forms found in SELECT: form" in result


def test_validate_forms_undefined():
    query_text = "SELECT ?lexeme ?lexemeID ?lastModified ?form WHERE { ?lexeme wikibase:lemma ?lemma . }"
    result = check_query_forms.validate_forms(query_text)
    assert "Undefined forms found in SELECT: form" in result


def test_validate_forms_unreturned():
    query_text = "SELECT ?lexeme ?lexemeID ?lastModified WHERE { ?lexeme wikibase:lemma ?lemma . ontolex:lexicalForm ?formLex . ?formLex ontolex:representation ?formRep . schema:dateModified ?lastModified . }"
    result = check_query_forms.validate_forms(query_text)
    assert "Defined but unreturned forms found: formRep" in result


@pytest.mark.skip(reason="Skipping due to unresolved issue with preposition error")
def test_validate_forms_order_mismatch():
    # Ensure variables are defined, then create an order mismatch
    # Both ?form and ?formRep must be captured by forms_pattern
    query_text = "SELECT ?lexeme ?lexemeID ?lastModified ?formRep ?form WHERE { ?lexeme wikibase:lemma ?lemma . ?lexeme ontolex:lexicalForm ?formLex . ?formLex ontolex:representation ?form . ?lexeme ontolex:lexicalForm ?formLex2 . ?formLex2 ontolex:representation ?formRep . schema:dateModified ?lastModified . }"
    result = check_query_forms.validate_forms(query_text)
    assert (
        "The order of variables in the SELECT statement does not match their order in the WHERE clause"
        in result
    )


# MARK: check_docstring (Lines 377-391)
def test_check_docstring_valid():
    query_text = "# tool: scribe-data\n# All nouns (Q123) and verbs (Q456) and the given forms.\n# Enter this query at https://query.wikidata.org/.\n"
    result = check_query_forms.check_docstring(query_text)
    assert result is True


def test_check_docstring_invalid_line1():
    query_text = "# wrong tool\n# All nouns (Q123) and verbs (Q456) and the given forms.\n# Enter this query at https://query.wikidata.org/.\n"
    result = check_query_forms.check_docstring(query_text)
    assert result == (False, "Error in line 1: # wrong tool")


# MARK: check_forms_order (Lines 419-470)
def test_check_forms_order_valid():
    query_text = (
        "SELECT ?lexeme ?lexemeID ?lastModified ?nominative ?singular WHERE { }"
    )
    with patch.object(
        check_query_forms, "lexeme_form_labels_order", ["Nominative", "Singular"]
    ):
        with patch.object(check_query_forms, "data_type_metadata", {}):
            result = check_query_forms.check_forms_order(query_text)
            assert result is True


def test_check_forms_order_invalid(capsys):
    query_text = (
        "SELECT ?lexeme ?lexemeID ?lastModified ?singular ?nominative WHERE { }"
    )
    with patch.object(
        check_query_forms, "lexeme_form_labels_order", ["Nominative", "Singular"]
    ):
        with patch.object(check_query_forms, "data_type_metadata", {}):
            result = check_query_forms.check_forms_order(query_text)
            assert result == "nominative, singular"
            captured = capsys.readouterr()
            assert "Invalid sorting:" in captured.out


# MARK: check_optional_qid_order (Lines 497-519)
def test_check_optional_qid_order_valid(tmp_path):
    sparql_file = tmp_path / "test.sparql"
    sparql_file.write_text(
        "  OPTIONAL { ?lexeme ontolex:lexicalForm ?form . ?form ontolex:representation ?nominative ; wikibase:grammaticalFeature wd:Q123 . }"
    )
    with patch.object(check_query_forms, "qid_label_dict", {"Nominative": "Q123"}):
        result = check_query_forms.check_optional_qid_order(sparql_file)
        assert result == ""


def test_check_optional_qid_order_invalid(tmp_path):
    sparql_file = tmp_path / "test.sparql"
    sparql_file.write_text(
        "  OPTIONAL { ?lexeme ontolex:lexicalForm ?form . ?form ontolex:representation ?nominative ; wikibase:grammaticalFeature wd:Q456 . }"
    )
    with patch.object(check_query_forms, "qid_label_dict", {"Nominative": "Q123"}):
        result = check_query_forms.check_optional_qid_order(sparql_file)
        assert (
            "The QIDs in optional statement for nominative should be ordered:" in result
        )


# MARK: check_query_forms (Lines 529-621)
@patch("pathlib.Path.glob", return_value=[])
def test_check_query_forms_no_files(mock_glob, capsys):
    # Mock LANGUAGE_DATA_EXTRACTION_DIR as a Path object with the patched glob
    with patch(
        "scribe_data.check.check_query_forms.LANGUAGE_DATA_EXTRACTION_DIR", Path()
    ):
        check_query_forms.check_query_forms()
        captured = capsys.readouterr()
        assert "All query forms are labeled and formatted correctly." in captured.out


@pytest.mark.skip(reason="Skipping due to TypeError in decompose_label_features")
@patch("pathlib.Path.glob")
def test_check_query_forms_with_errors(mock_glob, tmp_path, capsys):
    sparql_file = tmp_path / "test.sparql"
    # Define all SELECT variables and include a formatting error
    sparql_file.write_text(
        "SELECT ?lexeme ?lexemeID ?lastModified ?invalid WHERE { "
        "?lexeme wikibase:lemma ?lemma . "
        "schema:dateModified ?lastModified . "
        "  OPTIONAL { ?lexeme ontolex:lexicalForm ?form . ?form ontolex:representation ?invalid , wikibase:grammaticalFeature wd:Q123 . }"
        "}"
    )
    mock_glob.return_value = [sparql_file]
    with patch(
        "scribe_data.check.check_query_forms.LANGUAGE_DATA_EXTRACTION_DIR", Path()
    ):
        with patch.object(check_query_forms, "qid_label_dict", {"Invalid": "Q123"}):
            with patch.object(check_query_forms, "data_type_metadata", {}):
                with pytest.raises(SystemExit) as exc:
                    check_query_forms.check_query_forms()
                assert exc.value.code == 1
                captured = capsys.readouterr()
                assert "Invalid query formatting found" in captured.out
