# SPDX-License-Identifier: GPL-3.0-or-later
"""
Test the data_to_sqlite function.
"""

import json
import sqlite3
from unittest import mock

import pytest

from scribe_data.load.data_to_sqlite import (
    create_table,
    data_to_sqlite,
    table_insert,
    translations_to_sqlite,
)


@pytest.fixture
def temp_db(tmp_path):
    """
    Create a temporary SQLite database for testing.
    """
    db_path = tmp_path / "test.sqlite"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    yield cursor, conn
    conn.close()


@pytest.fixture
def temp_json_dir(tmp_path):
    """
    Create a temporary directory with test JSON files.
    """
    # Create test data structure.
    json_dir = tmp_path / "json_data"
    json_dir.mkdir()

    # Create English directory.
    eng_dir = json_dir / "english"
    eng_dir.mkdir()

    # Create test nouns.json.
    nouns_data = {
        "L1": {"noun": "test", "gender": "m"},
        "L2": {"noun": "example", "gender": "f"},
    }
    with open(eng_dir / "nouns.json", "w", encoding="utf-8") as f:
        json.dump(nouns_data, f)

    # Create test translations.json.
    translations_data = {
        "L1": {"lastModified": "2024-01-01", "test": {"de": "Test", "fr": "test"}}
    }
    with open(eng_dir / "translations.json", "w", encoding="utf-8") as f:
        json.dump(translations_data, f)

    return json_dir


def test_create_table(temp_db):
    """
    Test creating a table with both snake and camel case identifiers.
    """
    cursor, conn = temp_db

    # Test snake case.
    create_table(cursor, "snake", "test_table", ["TestCol", "AnotherCol"])
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'"
    )
    assert cursor.fetchone() is not None

    # Verify column names.
    cursor.execute("PRAGMA table_info(test_table)")
    columns = [info[1] for info in cursor.fetchall()]
    assert "test_col" in columns
    assert "another_col" in columns


def test_table_insert(temp_db):
    """
    Test inserting data into a table.
    """
    cursor, conn = temp_db

    # Create test table.
    create_table(cursor, "snake", "test_table", ["id", "name"])

    # Test insertion.
    table_insert(cursor, "test_table", ["1", "test_name"])

    # Verify insertion.
    cursor.execute("SELECT * FROM test_table")
    result = cursor.fetchone()
    assert result == ("1", "test_name")


@pytest.fixture
def translations_setup(tmp_path):
    """
    Pytest fixture to handle common setup for translations_to_sqlite tests.
    """
    output_dir = tmp_path / "sqlite_output"
    output_dir.mkdir()

    lang_data_type_dict = {"english": ["translations"]}
    current_languages = ["english", "german", "french"]
    expected_db_path = output_dir / "TranslationData.sqlite"

    return {
        "output_dir": output_dir,
        "lang_data_type_dict": lang_data_type_dict,
        "current_languages": current_languages,
        "expected_db_path": expected_db_path,
    }


def test_translations_to_sqlite(temp_json_dir, translations_setup):
    """
    Test translations_to_sqlite functionality.
    """
    # Run translations_to_sqlite.
    translations_to_sqlite(
        translations_setup["lang_data_type_dict"],
        translations_setup["current_languages"],
        input_file=str(temp_json_dir),
        output_file=str(translations_setup["output_dir"]),
        overwrite=True,
    )

    # Verify database creation.
    db_path = translations_setup["output_dir"] / "TranslationData.sqlite"
    assert db_path.exists()

    # Check database contents.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verify english table exists and has correct data.
    cursor.execute("SELECT * FROM english")
    rows = cursor.fetchall()
    assert len(rows) == 1  # should have 1 entry from our test data
    conn.close()


def test_overwrite_existing_file_user_confirms(temp_json_dir, translations_setup):
    """
    Test when file exists, overwrite=False, and user confirms.
    """
    with (
        mock.patch("pathlib.Path.exists", return_value=True),
        mock.patch("questionary.confirm") as mock_confirm,
        mock.patch("os.remove") as mock_remove,
    ):
        mock_confirm.return_value.ask.return_value = True

        translations_to_sqlite(
            translations_setup["lang_data_type_dict"],
            translations_setup["current_languages"],
            input_file=str(temp_json_dir),
            output_file=str(translations_setup["output_dir"]),
            overwrite=False,
        )

        expected_message = f"SQLite file {translations_setup['expected_db_path']} already exists. Overwrite?"
        mock_confirm.assert_called_once_with(expected_message)
        mock_remove.assert_called_once_with(translations_setup["expected_db_path"])


def test_overwrite_existing_file_user_declines(temp_json_dir, translations_setup):
    """
    Test when file exists, overwrite=False, and user declines.
    """
    with (
        mock.patch("pathlib.Path.exists", return_value=True),
        mock.patch("questionary.confirm") as mock_confirm,
        mock.patch("os.remove") as mock_remove,
        mock.patch("builtins.print") as mock_print,
    ):
        mock_confirm.return_value.ask.return_value = False

        translations_to_sqlite(
            translations_setup["lang_data_type_dict"],
            translations_setup["current_languages"],
            input_file=str(temp_json_dir),
            output_file=str(translations_setup["output_dir"]),
            overwrite=False,
        )

        mock_confirm.assert_called_once()
        mock_remove.assert_not_called()
        mock_print.assert_called_with("Skipping translation DB creation.")


def test_translations_to_sqlite_missing_json(temp_json_dir, translations_setup, capsys):
    """
    Test translations_to_sqlite skips language table creation if JSON file is missing.
    """
    lang_data_type_dict = {"nonexistent_lang": ["translations"]}
    current_languages = translations_setup["current_languages"]

    translations_to_sqlite(
        lang_data_type_dict,
        current_languages,
        input_file=str(
            temp_json_dir
        ),  # temp_json_dir won't have 'nonexistent_lang/translations.json'
        output_file=str(translations_setup["output_dir"]),
        overwrite=True,
    )

    captured = capsys.readouterr()
    assert (
        "Skipping nonexistent_lang translations table creation as JSON file not found."
        in captured.out
    )


class MockConnection:
    def __init__(self, real_conn):
        self._conn = real_conn

    def commit(self):
        raise sqlite3.Error("mock commit error")

    def __getattr__(self, name):
        # Delegate attribute access to the real connection.
        return getattr(self._conn, name)


def test_translations_to_sqlite_commit_error(temp_json_dir, translations_setup, capsys):
    """
    Test that translations_to_sqlite handles sqlite3.Error on commit properly.
    """

    original_connect = sqlite3.connect

    def mock_connect(*args, **kwargs):
        real_conn = original_connect(*args, **kwargs)
        return MockConnection(real_conn)

    with mock.patch("sqlite3.connect", new=mock_connect):
        translations_to_sqlite(
            translations_setup["lang_data_type_dict"],
            translations_setup["current_languages"],
            input_file=str(temp_json_dir),
            output_file=str(translations_setup["output_dir"]),
            overwrite=True,
        )

    captured = capsys.readouterr()
    assert "Error creating/updating" in captured.out
    assert "mock commit error" in captured.out


def test_data_to_sqlite_invalid_language():
    """
    Test data_to_sqlite with invalid language.
    """
    with pytest.raises(ValueError):
        data_to_sqlite(languages=["invalid_language"])


def test_create_table_duplicate_columns(temp_db):
    """
    Test creating a table with duplicate column names.
    """
    cursor, conn = temp_db

    # Test handling of duplicate column names.
    create_table(cursor, "snake", "test_table", ["Test", "test", "TEST"])

    cursor.execute("PRAGMA table_info(test_table)")
    columns = [info[1] for info in cursor.fetchall()]

    # Verify unique column names were created.
    assert len(columns) == 3
    assert len(set(columns)) == 3  # all columns should be unique


def test_data_to_sqlite_translations_and_nouns(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    # Create language folder.
    english_dir = input_dir / "english"
    english_dir.mkdir()

    # Create translations.json.
    translations_data = {
        "L1": {
            "lastModified": "2023-01-01",
            "hello": {"english": "Hello", "german": "Hallo", "french": "Bonjour"},
        }
    }
    (english_dir / "translations.json").write_text(json.dumps(translations_data))

    # Create nouns.json.
    nouns_data = {
        "L1": {"wdLexemeId": "id1", "noun": "cat"},
        "L2": {"wdLexemeId": "id2", "noun": "dog"},
    }
    (english_dir / "nouns.json").write_text(json.dumps(nouns_data))

    data_to_sqlite(
        languages=["english"],
        specific_tables=None,
        input_file=str(input_dir),
        output_file=str(output_dir),
        overwrite=True,
    )

    # Assert TranslationData.sqlite exists.
    translation_db = output_dir / "TranslationData.sqlite"
    assert translation_db.exists()

    # Assert ENLanguageData.sqlite (for other tables) exists.
    noun_db = output_dir / "ENLanguageData.sqlite"
    assert noun_db.exists()

    # Check nouns table created and has data.
    conn = sqlite3.connect(noun_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    assert "nouns" in tables

    cursor.execute("SELECT * FROM nouns;")
    rows = cursor.fetchall()
    assert len(rows) == 3  # 2 real rows + 1 default "Scribe" row

    # Optionally check the default row.
    scribe_row = [row for row in rows if row[0] == "L0"]
    assert len(scribe_row) == 1


def test_data_to_sqlite_skips_missing_json(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    lang_dir = input_dir / "english"
    lang_dir.mkdir()

    # Note: No JSON files created here - simulate missing data files.
    # Patch metadata, helpers, and ensure we only ask for 'nouns'.
    with (
        mock.patch("scribe_data.utils.data_type_metadata", {"nouns": None}),
        mock.patch("scribe_data.utils.language_metadata", {"english": {}}),
        mock.patch("scribe_data.utils.list_all_languages", return_value=["english"]),
        mock.patch("scribe_data.load.data_to_sqlite.create_table") as mock_create_table,
        mock.patch("scribe_data.load.data_to_sqlite.table_insert") as mock_table_insert,
        mock.patch(
            "scribe_data.utils.get_language_iso",
            side_effect=lambda lang: lang[:2].upper(),
        ),
    ):
        # Run data_to_sqlite for 'nouns' only, but JSON file missing.
        data_to_sqlite(
            languages=["english"],
            specific_tables=["nouns"],
            input_file=str(input_dir),
            output_file=str(tmp_path / "output"),
            overwrite=True,
        )

    # Confirm that create_table and table_insert were NOT called since file missing.
    assert not mock_create_table.called
    assert not mock_table_insert.called
