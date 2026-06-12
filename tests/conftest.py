# SPDX-License-Identifier: GPL-3.0-or-later
"""
Utility functions for pytest tests.
"""

import shutil
from pathlib import Path

import pytest

from scribe_data.utils import (
    DEFAULT_CONTRACTS_EXPORT_DIR,
    DEFAULT_CSV_DIR,
    DEFAULT_FILTERED_JSON_DIR,
    DEFAULT_JSON_DIR,
    DEFAULT_SQLITE_DIR,
    DEFAULT_TSV_DIR,
    DEFAULT_WIKIDATA_DUMP_DIR,
    DEFAULT_WIKTIONARY_DUMP_DIR,
    DEFAULT_WIKTIONARY_JSON_DIR,
)


def cleanup_default_directories() -> None:
    """
    Utility function to safely remove default directories during testing.
    """
    project_root = Path(__file__).parent.parent
    dirs_to_delete = [
        DEFAULT_CONTRACTS_EXPORT_DIR,
        DEFAULT_CSV_DIR,
        DEFAULT_FILTERED_JSON_DIR,
        DEFAULT_JSON_DIR,
        DEFAULT_SQLITE_DIR,
        DEFAULT_TSV_DIR,
        DEFAULT_WIKIDATA_DUMP_DIR,
        DEFAULT_WIKTIONARY_DUMP_DIR,
        DEFAULT_WIKTIONARY_JSON_DIR,
    ]

    for dir_name in dirs_to_delete:
        target_dir = project_root / dir_name
        if target_dir.exists() and target_dir.is_dir():
            shutil.rmtree(target_dir)


@pytest.fixture(scope="module", autouse=True)
def auto_cleanup_default_directories() -> None:
    """
    Automatically cleans up test data after each file finishes.
    """
    yield
    cleanup_default_directories()
