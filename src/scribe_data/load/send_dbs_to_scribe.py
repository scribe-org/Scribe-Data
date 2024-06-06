"""
Updates Scribe apps with the SQLite language databases that are found in src/load/databases.

Example
-------
    python3 send_dbs_to_scribe.py

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

from scribe_data.utils import (
    get_ios_data_path,
    get_language_from_iso,
    get_path_from_load_dir,
)

dbs_to_send = os.listdir("databases")
db_names = [os.path.splitext(db)[0] for db in dbs_to_send]
language_db_dict = {
    get_language_from_iso(db[:2]): {"db_location": f"databases/{db}.sqlite"}
    for db in db_names
}

for language in language_db_dict:
    language_db_dict[language]["scribe_ios_db_path"] = (
        get_path_from_load_dir()
        + get_ios_data_path(language=language)
        + "/"
        + language_db_dict[language]["db_location"].split("/")[1]
    )

for language in language_db_dict:
    os.system(
        f'cp {language_db_dict[language]["db_location"]} {language_db_dict[language]["scribe_ios_db_path"]}'
    )
    print(f"Moved {language} language database to Scribe-iOS.")
