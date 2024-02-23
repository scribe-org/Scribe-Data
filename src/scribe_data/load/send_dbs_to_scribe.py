"""
Send Databases to Scribe
------------------------

Updates Scribe apps with the SQLite language databases that are found in src/load/databases.

Example
-------
    python send_dbs_to_scribe.py
"""

import os
import sys

PATH_TO_SCRIBE_ORG = os.path.dirname(sys.path[0]).split("Scribe-Data")[0]
PATH_TO_SCRIBE_DATA_SRC = f"{PATH_TO_SCRIBE_ORG}Scribe-Data/src"
sys.path.insert(0, PATH_TO_SCRIBE_DATA_SRC)

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
