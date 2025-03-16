# SPDX-License-Identifier: GPL-3.0-or-later
"""
Test the data_to_sqlite function.
"""

import json
import sqlite3

import pytest

from scribe_data.load.data_to_sqlite import (
    create_table,
    data_to_sqlite,
    table_insert,
    translations_to_sqlite,
)


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary SQLite database for testing."""
    db_path = tmp_path / "test.sqlite"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    yield cursor, conn
    conn.close()


@pytest.fixture
def temp_json_dir(tmp_path):
    """Create a temporary directory with test JSON files."""
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
    """Test creating a table with both snake and camel case identifiers."""
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
    """Test inserting data into a table."""
    cursor, conn = temp_db

    # Create test table.
    create_table(cursor, "snake", "test_table", ["id", "name"])

    # Test insertion.
    table_insert(cursor, "test_table", ["1", "test_name"])

    # Verify insertion.
    cursor.execute("SELECT * FROM test_table")
    result = cursor.fetchone()
    assert result == ("1", "test_name")


def test_translations_to_sqlite(temp_json_dir, tmp_path):
    """Test translations_to_sqlite functionality."""
    output_dir = tmp_path / "sqlite_output"
    output_dir.mkdir()

    # Create language data type dictionary for test.
    lang_data_type_dict = {"english": ["translations"]}
    current_languages = ["english", "german", "french"]

    # Run translations_to_sqlite.
    translations_to_sqlite(
        lang_data_type_dict,
        current_languages,
        input_file=str(temp_json_dir),
        output_file=str(output_dir),
        overwrite=True,
    )

    # Verify database creation.
    db_path = output_dir / "TranslationData.sqlite"
    assert db_path.exists()

    # Check database contents.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verify english table exists and has correct data.
    cursor.execute("SELECT * FROM english")
    rows = cursor.fetchall()
    assert len(rows) == 1  # should have 1 entry from our test data
    conn.close()


def test_data_to_sqlite_invalid_language():
    """Test data_to_sqlite with invalid language."""
    with pytest.raises(ValueError):
        data_to_sqlite(languages=["invalid_language"])


def test_create_table_duplicate_columns(temp_db):
    """Test creating a table with duplicate column names."""
    cursor, conn = temp_db

    # Test handling of duplicate column names.
    create_table(cursor, "snake", "test_table", ["Test", "test", "TEST"])

    cursor.execute("PRAGMA table_info(test_table)")
    columns = [info[1] for info in cursor.fetchall()]

    # Verify unique column names were created.
    assert len(columns) == 3
    assert len(set(columns)) == 3  # all columns should be unique
