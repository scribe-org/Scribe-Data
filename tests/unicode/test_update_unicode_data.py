# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for updating Unicode data from CLDR.
"""

import runpy
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import scribe_data.unicode.update_unicode_data as update_unicode_data
from scribe_data.unicode.update_unicode_data import check_install_node_modules


@patch("scribe_data.unicode.update_unicode_data.subprocess.run")
def test_check_install_node_modules_when_missing(
    mock_run: MagicMock,
    tmp_path: Path,
) -> None:
    with patch(
        "scribe_data.unicode.update_unicode_data.Path.cwd",
        return_value=tmp_path,
    ):
        check_install_node_modules()

    assert mock_run.call_args_list == [
        call(["npm", "install"], check=True),
        call(
            [
                "mv",
                "node_modules/cldr-annotations-derived-full",
                "src/scribe_data/unicode",
            ],
            check=True,
        ),
        call(
            [
                "mv",
                "node_modules/cldr-annotations-full",
                "src/scribe_data/unicode",
            ],
            check=True,
        ),
        call(["rm", "-rf", "node_modules"], check=True),
    ]


@patch("scribe_data.unicode.update_unicode_data.subprocess.run")
def test_check_install_node_modules_when_present(
    mock_run: MagicMock,
    tmp_path: Path,
) -> None:
    (tmp_path / "node_modules").mkdir()

    with patch(
        "scribe_data.unicode.update_unicode_data.Path.cwd",
        return_value=tmp_path,
    ):
        check_install_node_modules()

    assert mock_run.call_args_list == [
        call(
            [
                "mv",
                "node_modules/cldr-annotations-derived-full",
                "src/scribe_data/unicode",
            ],
            check=True,
        ),
        call(
            [
                "mv",
                "node_modules/cldr-annotations-full",
                "src/scribe_data/unicode",
            ],
            check=True,
        ),
        call(["rm", "-rf", "node_modules"], check=True),
    ]


@patch("subprocess.run")
def test_update_unicode_data_entrypoint(
    mock_run: MagicMock,
    tmp_path: Path,
) -> None:
    with patch(
        "pathlib.Path.cwd",
        return_value=tmp_path,
    ):
        runpy.run_path(
            update_unicode_data.__file__,
            run_name="__main__",
        )

    assert mock_run.call_count == 4
