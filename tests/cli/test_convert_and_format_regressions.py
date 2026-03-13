# SPDX-License-Identifier: GPL-3.0-or-later
"""
Regression tests for bug fixes in CLI convert, cli_utils, and data_to_sqlite.

Bug 1: convert_to_csv_or_tsv crashed with UnboundLocalError when identifier_case
        was "camel" for non-emoji list-of-dict JSON data. Also wrote double header
        when identifier_case was "snake".
Bug 2: print_formatted_data crashed with UnboundLocalError when a list value
        with dict items was encountered before any dict value (max_sub_key_length
        was undefined).
Bug 3: convert_to_json only processed the first row of single-column CSVs,
        silently dropping all subsequent rows.
"""

import csv
import json
import sqlite3

from scribe_data.cli.cli_utils import print_formatted_data
from scribe_data.cli.convert import convert_to_csv_or_tsv, convert_to_json
from scribe_data.load.data_to_sqlite import create_table, table_insert

# MARK: Bug 1 — convert_to_csv_or_tsv camelCase list-of-dict


class TestBug1CsvListOfDictCamelCase:
    """
    Bug 1: When identifier_case != 'snake', the else branch used `columns`
    before it was assigned, causing UnboundLocalError. Also, the header was
    written twice when identifier_case == 'snake'.
    """

    def test_list_of_dict_camel_case_no_crash(self, tmp_path):
        """
        Converting non-emoji list-of-dict JSON to CSV with camelCase should
        not raise UnboundLocalError.
        """
        json_data = {"key1": [{"colA": "v1", "colB": "v2"}]}
        json_file = tmp_path / "input.json"
        json_file.write_text(json.dumps(json_data))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        convert_to_csv_or_tsv(
            language="test",
            data_type="items",
            output_type="csv",
            input_file=str(json_file),
            output_dir=str(output_dir),
            overwrite=True,
            identifier_case="camel",
        )

        out_file = output_dir / "Test" / "items.csv"
        assert out_file.exists()

        with open(out_file) as f:
            rows = list(csv.reader(f))

        # Should have exactly 1 header + 1 data row (no double header).
        assert len(rows) == 2
        assert rows[0] == ["item", "colA", "colB"]
        assert rows[1] == ["key1", "v1", "v2"]

    def test_list_of_dict_snake_case_single_header(self, tmp_path):
        """
        Converting non-emoji list-of-dict JSON to CSV with snake_case should
        write the header exactly once (not twice).
        """
        json_data = {"key1": [{"colA": "v1", "colB": "v2"}]}
        json_file = tmp_path / "input.json"
        json_file.write_text(json.dumps(json_data))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        convert_to_csv_or_tsv(
            language="test",
            data_type="items",
            output_type="csv",
            input_file=str(json_file),
            output_dir=str(output_dir),
            overwrite=True,
            identifier_case="snake",
        )

        out_file = output_dir / "Test" / "items.csv"
        with open(out_file) as f:
            rows = list(csv.reader(f))

        # Should have exactly 1 header + 1 data row.
        assert len(rows) == 2
        assert rows[0] == ["item", "col_a", "col_b"]

    def test_list_of_dict_camel_case_tsv(self, tmp_path):
        """
        Same fix should work for TSV output as well.
        """
        json_data = {
            "a": [{"Name": "Alice", "Age": "30"}],
            "b": [{"Name": "Bob", "Age": "25"}],
        }
        json_file = tmp_path / "input.json"
        json_file.write_text(json.dumps(json_data))

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        convert_to_csv_or_tsv(
            language="test",
            data_type="records",
            output_type="tsv",
            input_file=str(json_file),
            output_dir=str(output_dir),
            overwrite=True,
            identifier_case="camel",
        )

        out_file = output_dir / "Test" / "records.tsv"
        assert out_file.exists()

        with open(out_file) as f:
            reader = csv.reader(f, delimiter="\t")
            rows = list(reader)

        assert len(rows) == 3  # header + 2 data rows
        assert rows[0] == ["record", "Name", "Age"]


# MARK: Bug 2 — print_formatted_data max_sub_key_length undefined


class TestBug2PrintFormattedDataListFirst:
    """
    Bug 2: max_sub_key_length was only defined in the `isinstance(value, dict)`
    branch but referenced in the `isinstance(value, list)` branch. If a list
    value with dict items was the first value encountered, it crashed with
    UnboundLocalError.
    """

    def test_list_of_dicts_as_first_value_no_crash(self):
        """
        When the first value in the dict is a list of dicts, it should not
        crash with UnboundLocalError for max_sub_key_length.
        """
        data = {
            "first_key": [{"emoji": "😀", "is_base": True, "rank": 1}],
            "second_key": {"sub1": "val1"},
        }
        # Should not raise — before the fix this would crash.
        print_formatted_data(data, "test_type")

    def test_only_list_values_no_crash(self):
        """
        When ALL values are lists of dicts (no dict values at all),
        it should still work without crashing.
        """
        data = {
            "a": [{"k1": "v1", "k2": "v2"}],
            "b": [{"k3": "v3"}],
        }
        print_formatted_data(data, "test_type")

    def test_list_of_dicts_correct_formatting(self, capsys):
        """
        Verify the output formatting is correct when list-of-dicts is the
        first value encountered.
        """
        data = {"word": [{"emoji": "🐱", "rank": "1"}]}
        print_formatted_data(data, "test_type")

        captured = capsys.readouterr()
        assert "emoji" in captured.out
        assert "🐱" in captured.out
        assert "rank" in captured.out


# MARK: Bug 3 — convert_to_json single-column CSV


class TestBug3SingleColumnCsv:
    """
    Bug 3: When a CSV had exactly 1 column, only the first row was processed
    and all subsequent rows were silently dropped.
    """

    def test_single_column_all_rows_processed(self, tmp_path):
        """
        All rows from a single-column CSV should appear in the JSON output.
        """
        csv_file = tmp_path / "input.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["word"])
            writer.writerow(["hello"])
            writer.writerow(["world"])
            writer.writerow(["test"])

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        convert_to_json(
            language="test",
            data_type="words",
            output_type="json",
            input_file=str(csv_file),
            output_dir=str(output_dir),
            overwrite=True,
        )

        out_file = output_dir / "Test" / "words.json"
        assert out_file.exists()

        with open(out_file) as f:
            result = json.load(f)

        # All 3 data rows should be present (not just the first).
        assert len(result) == 3
        assert "hello" in result
        assert "world" in result
        assert "test" in result
        # Single-column values should be None.
        assert result["hello"] is None
        assert result["world"] is None
        assert result["test"] is None

    def test_single_column_one_row(self, tmp_path):
        """
        Single row single-column CSV works correctly (baseline).
        """
        csv_file = tmp_path / "input.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["item"])
            writer.writerow(["only_one"])

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        convert_to_json(
            language="test",
            data_type="items",
            output_type="json",
            input_file=str(csv_file),
            output_dir=str(output_dir),
            overwrite=True,
        )

        out_file = output_dir / "Test" / "items.json"
        with open(out_file) as f:
            result = json.load(f)

        assert len(result) == 1
        assert result["only_one"] is None


# MARK: Bug 4 & 5 — SQL identifier quoting


class TestBug4And5SqlQuoting:
    """
    Bug 4: create_table and table_insert used unquoted table/column names in
    SQL statements, which could break on SQL reserved words or names with
    special characters.

    Bug 5: DELETE FROM statements used unquoted language/data-type names
    which could break with multi-word names or reserved words.
    """

    def test_create_table_with_reserved_word(self):
        """
        Table names that are SQL reserved words (like 'order', 'group', 'select')
        should work because they are now quoted with [].
        """
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        # 'order' is a SQL reserved word.
        create_table(cursor, "camel", data_type="order", cols=["key", "value"])

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='order'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    def test_table_insert_with_reserved_word(self):
        """
        Inserting into a table named with a SQL reserved word should work.
        """
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        create_table(cursor, "camel", data_type="order", cols=["key", "value"])
        table_insert(cursor, data_type="order", keys=["k1", "v1"])

        cursor.execute("SELECT * FROM [order]")
        rows = cursor.fetchall()
        assert rows == [("k1", "v1")]
        conn.close()

    def test_create_table_with_reserved_word_group(self):
        """
        Another SQL reserved word: 'group'.
        """
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        create_table(cursor, "snake", data_type="group", cols=["Id", "Name"])

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='group'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    def test_delete_from_reserved_word_table(self):
        """
        DELETE FROM should work on tables named with SQL reserved words.
        """
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        create_table(cursor, "camel", data_type="index", cols=["word"])
        table_insert(cursor, data_type="index", keys=["test"])
        conn.commit()

        # This is the pattern used in data_to_sqlite — should not crash.
        cursor.execute("DELETE FROM [index]")
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM [index]")
        assert cursor.fetchone()[0] == 0
        conn.close()

    def test_column_with_reserved_word(self):
        """
        Column names that are SQL reserved words should be properly quoted.
        """
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        # 'order', 'select', 'from' are all reserved words.
        create_table(
            cursor, "camel", data_type="test_table", cols=["order", "select", "from"]
        )
        table_insert(cursor, data_type="test_table", keys=["1", "2", "3"])

        cursor.execute("SELECT * FROM [test_table]")
        rows = cursor.fetchall()
        assert rows == [("1", "2", "3")]
        conn.close()

    def test_multiple_inserts_with_reserved_word_table(self):
        """
        Multiple inserts into a reserved-word table should work.
        """
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        create_table(cursor, "camel", data_type="values", cols=["id", "data"])
        table_insert(cursor, data_type="values", keys=["1", "a"])
        table_insert(cursor, data_type="values", keys=["2", "b"])
        table_insert(cursor, data_type="values", keys=["3", "c"])
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM [values]")
        assert cursor.fetchone()[0] == 3
        conn.close()
