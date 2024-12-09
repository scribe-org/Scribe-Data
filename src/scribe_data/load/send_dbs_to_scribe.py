"""
Updates Scribe apps with the SQLite language databases that are found in the SQLite data export directory.

Example
-------
    python3 src/scribe_data/load/send_dbs_to_scribe.py

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

import os
from pathlib import Path

from scribe_data.utils import (
    DEFAULT_SQLITE_EXPORT_DIR,
    get_android_data_path,
    get_ios_data_path,
    get_language_from_iso,
)

PATH_TO_SCRIBE_DATA_ROOT = Path(__file__).parent.parent.parent.parent

dbs_to_send = list(
    Path(PATH_TO_SCRIBE_DATA_ROOT, DEFAULT_SQLITE_EXPORT_DIR).glob("*.sqlite")
)
db_names = [Path(db).stem for db in dbs_to_send]
db_names = sorted(db_names)
language_db_dict = {
    get_language_from_iso(db[:2].lower()): {
        "db_location": PATH_TO_SCRIBE_DATA_ROOT
        / DEFAULT_SQLITE_EXPORT_DIR
        / f"{db}.sqlite"
    }
    for db in db_names
    if db != "TranslationData"
}

language_db_dict["translation"] = {
    "db_location": PATH_TO_SCRIBE_DATA_ROOT
    / DEFAULT_SQLITE_EXPORT_DIR
    / "TranslationData.sqlite"
}

for language in language_db_dict:
    language_db_dict[language]["scribe_ios_db_path"] = (
        get_ios_data_path(language=language)
        / f"{str(language_db_dict[language]['db_location']).split('/')[-1]}"
    )
    language_db_dict[language]["full_path_to_scribe_ios_db"] = (
        PATH_TO_SCRIBE_DATA_ROOT.parent
        / f"{language_db_dict[language]['scribe_ios_db_path']}"
    )
    language_db_dict[language]["scribe_android_db_path"] = (
        get_android_data_path()
        / f"{str(language_db_dict[language]['db_location']).split('/')[-1]}"
    )
    language_db_dict[language]["full_path_to_scribe_android_db"] = (
        PATH_TO_SCRIBE_DATA_ROOT.parent
        / f"{language_db_dict[language]['scribe_android_db_path']}"
    )

# Note: TranslationData is one level up from language DBs in iOS.
language_db_dict["translation"]["scribe_ios_db_path"] = (
    Path("Scribe-iOS") / "Keyboards" / "LanguageKeyboards" / "TranslationData.sqlite"
)
language_db_dict["translation"]["full_path_to_scribe_ios_db"] = (
    PATH_TO_SCRIBE_DATA_ROOT.parent
    / f"{language_db_dict["translation"]['scribe_ios_db_path']}"
)
language_db_dict["translation"]["scribe_android_db_path"] = (
    get_android_data_path() / "TranslationData.sqlite"
)
language_db_dict["translation"]["full_path_to_scribe_android_db"] = (
    PATH_TO_SCRIBE_DATA_ROOT.parent
    / f"{language_db_dict["translation"]['scribe_android_db_path']}"
)

for language in language_db_dict:
    os.system(
        f'cp {language_db_dict[language]["db_location"]} {language_db_dict[language]["full_path_to_scribe_ios_db"]}'
    )
    print(
        f"Moved {language} database to Scribe-iOS at {language_db_dict[language]['scribe_ios_db_path']}."
    )
    os.system(
        f'cp {language_db_dict[language]["db_location"]} {language_db_dict[language]["full_path_to_scribe_android_db"]}'
    )
    print(
        f"Moved {language} database to Scribe-Android at {language_db_dict[language]['scribe_android_db_path']}."
    )
