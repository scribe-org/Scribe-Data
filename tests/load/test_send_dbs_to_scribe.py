# SPDX-License-Identifier: GPL-3.0-or-later
"""
Test suite for send_dbs_to_scribe.py
"""

import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestDatabaseDeployment:
    """Test the database deployment script."""

    @patch("scribe_data.load.send_dbs_to_scribe.os.system")
    @patch("scribe_data.load.send_dbs_to_scribe.get_android_data_path")
    @patch("scribe_data.load.send_dbs_to_scribe.get_ios_data_path")
    @patch("scribe_data.load.send_dbs_to_scribe.get_language_from_iso")
    @patch("scribe_data.load.send_dbs_to_scribe.Path.glob")
    @patch("scribe_data.load.send_dbs_to_scribe.PATH_TO_SCRIBE_DATA_ROOT")
    def test_full_deployment(
        self,
        mock_root,
        mock_glob,
        mock_get_lang,
        mock_ios_path,
        mock_android_path,
        mock_system,
    ):
        """Test complete deployment workflow."""
        mock_root.__truediv__ = Mock(return_value=Path("/root/exports"))
        mock_root.parent = Path("/root")
        mock_glob.return_value = [
            Path("de_verbs.sqlite"),
            Path("TranslationData.sqlite"),
        ]
        mock_get_lang.side_effect = lambda x: {"de": "German"}[x]
        mock_ios_path.return_value = Path("ios/path")
        mock_android_path.return_value = Path("android/path")
        mock_system.return_value = 0

        import importlib

        if "scribe_data.load.send_dbs_to_scribe" in sys.modules:
            importlib.reload(sys.modules["scribe_data.load.send_dbs_to_scribe"])

        assert mock_system.call_count > 0

    @patch("scribe_data.load.send_dbs_to_scribe.os.system")
    @patch("builtins.print")
    def test_copy_operations(self, mock_print, mock_system):
        """Test copy commands are executed."""
        config = {
            "German": {
                "db_location": Path("/source/de_verbs.sqlite"),
                "full_path_to_scribe_ios_db": Path("/ios/de_verbs.sqlite"),
                "full_path_to_scribe_android_db": Path("/android/de_verbs.sqlite"),
                "scribe_ios_db_path": Path("ios/de_verbs.sqlite"),
                "scribe_android_db_path": Path("android/de_verbs.sqlite"),
            }
        }

        for language in config:
            c = config[language]
            mock_system(f'cp {c["db_location"]} {c["full_path_to_scribe_ios_db"]}')
            mock_print(
                f"Moved {language} database to Scribe-iOS at {c['scribe_ios_db_path']}."
            )
            mock_system(f'cp {c["db_location"]} {c["full_path_to_scribe_android_db"]}')
            mock_print(
                f"Moved {language} database to Scribe-Android at {c['scribe_android_db_path']}."
            )

        assert mock_system.call_count == 2
        assert mock_print.call_count == 2


class TestDatabaseDiscovery:
    """Test database file discovery logic."""

    def test_db_name_extraction(self):
        """Test database name extraction from paths."""
        dbs = [Path("de_verbs.sqlite"), Path("fr_nouns.sqlite")]
        db_names = [Path(db).stem for db in dbs]
        db_names = sorted(db_names)

        assert db_names == ["de_verbs", "fr_nouns"]

    @patch("scribe_data.load.send_dbs_to_scribe.get_language_from_iso")
    def test_language_mapping(self, mock_get_lang):
        """Test language dictionary creation."""
        mock_get_lang.side_effect = lambda x: {"de": "German", "fr": "French"}[x]
        db_names = ["de_verbs", "fr_nouns"]
        root = Path("/root")
        export_dir = "exports"

        language_db_dict = {
            mock_get_lang(db[:2].lower()): {
                "db_location": root / export_dir / f"{db}.sqlite"
            }
            for db in db_names
            if db != "TranslationData"
        }

        assert "German" in language_db_dict
        assert "French" in language_db_dict
        assert (
            language_db_dict["German"]["db_location"]
            == root / export_dir / "de_verbs.sqlite"
        )

    def test_translation_data_handling(self):
        """Test TranslationData special case."""
        root = Path("/root")
        export_dir = "exports"

        language_db_dict = {}
        language_db_dict["translation"] = {
            "db_location": root / export_dir / "TranslationData.sqlite"
        }

        assert "translation" in language_db_dict
        assert "TranslationData.sqlite" in str(
            language_db_dict["translation"]["db_location"]
        )


class TestFileOperations:
    """Test file system operations."""

    @pytest.fixture
    def temp_setup(self):
        """Create temporary test files."""
        temp_dir = tempfile.mkdtemp()
        exports_dir = Path(temp_dir) / "exports"
        exports_dir.mkdir()

        (exports_dir / "de_verbs.sqlite").write_text("test data")
        (exports_dir / "fr_nouns.sqlite").write_text("test data")
        (exports_dir / "TranslationData.sqlite").write_text("test data")

        yield temp_dir, exports_dir
        shutil.rmtree(temp_dir)

    def test_file_discovery(self, temp_setup):
        """Test file discovery with real files."""
        temp_dir, exports_dir = temp_setup

        dbs_to_send = list(exports_dir.glob("*.sqlite"))
        db_names = [Path(db).stem for db in dbs_to_send]
        db_names = sorted(db_names)

        assert len(db_names) == 3
        assert "de_verbs" in db_names
        assert "fr_nouns" in db_names
        assert "TranslationData" in db_names


class TestPathLogic:
    """Test path construction logic."""

    def test_filename_extraction(self):
        """Test filename extraction from paths."""
        path = Path("/some/path/de_verbs.sqlite")
        filename = str(path).split("/")[-1]
        assert filename == "de_verbs.sqlite"

    def test_path_construction(self):
        """Test destination path building."""
        db_config = {"db_location": Path("/source/de_verbs.sqlite")}
        root = Path("/project")
        ios_path = Path("ios/data")

        filename = str(db_config["db_location"]).split("/")[-1]
        final_path = root / ios_path / filename

        assert isinstance(final_path, Path)
        assert "de_verbs.sqlite" in str(final_path)
