"""
Module for downloading Wikipedia based lexeme JSON dump.

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

import requests
import re
from datetime import datetime


def parse_date(date_string):
    """
    Parses a date string into a `datetime.date` object.

    Supported formats:
        - YYYYMMDD
        - YYYY/MM/DD
        - YYYY-MM-DD

    Args:
        date_string (str): The date string to be parsed.

    Returns:
        datetime.date: Parsed date object if the format is valid.
        None: If the date format is invalid.
    """
    formats = ["%Y%m%d", "%Y/%m/%d", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
    print(
        f"Invalid date format: {date_string}. Expected formats: YYYYMMDD, YYYY/MM/DD, or YYYY-MM-DD."
    )
    return None


def available_closest_lexeme_dumpfile(target_entity, other_old_dumps, try_old_dump):
    """
    Finds the closest available dump file based on the target date.

    Args:
        target_entity (str): The target date for which the dump is requested (format: YYYY/MM/DD or similar).
        other_old_dumps (list): List of available dump folders as strings.
        try_old_dump (function): A function to validate if the dump file exists.

    Returns:
        str: The closest available dump file date (as a string).
        None: If no suitable dump is found.
    """
    available_dates = []
    target_date = parse_date(target_entity)
    closest_date = None
    closest_diff = None

    if target_date:
        for i in other_old_dumps:
            if i == "..":
                continue
            try:
                if try_old_dump(i):
                    available_dates.append(i)
                    current_date = parse_date(i)
                    diff = abs((current_date - target_date).days)

                    if closest_diff is None or diff < closest_diff:
                        closest_date = i
                        closest_diff = diff

                    if current_date >= target_date:
                        break
            except requests.exceptions.HTTPError:
                pass
        return closest_date


def download_wiki_lexeme_dump(target_entity="latest-lexemes"):
    """
    Downloads a Wikimedia lexeme dump based on the specified target entity or date.

    Args:
        target_entity (str, optional): The target dump to download. Defaults to "latest-lexemes".
            - If "latest-lexemes", downloads the latest dump.
            - If a valid date (e.g., YYYYMMDD), attempts to download the dump for that date.

    Returns:
        str: The URL of the requested or closest available dump.
        None: If no suitable dump is found or the request fails.
    """
    base_url = "https://dumps.wikimedia.org/wikidatawiki/entities"

    def try_old_dump(target_entity):
        """
        Checks if the specified dump file exists for a target entity.

        Args:
            target_entity (str): The target entity or date folder to check.

        Returns:
            str: The URL of the dump file if it exists.
            None: If the dump file does not exist.
        """
        entity_url = f"{base_url}/{target_entity}/"
        entity_response = requests.get(entity_url)
        entity_response.raise_for_status()
        dump_filenames = re.findall(r'href="([^"]+)"', entity_response.text)

        fileurl = f"wikidata-{target_entity}-lexemes.json.bz2"
        if fileurl in dump_filenames:
            return f"{base_url}/{target_entity}/{fileurl}"

    if target_entity != "latest-lexemes":
        try:
            if parse_date(target_entity):
                target_entity = target_entity.replace("/", "").replace("-", "")
                return try_old_dump(target_entity)

        except requests.exceptions.HTTPError as http_err:
            print(
                f"HTTP error occurred: {http_err} Status code: {http_err.response.status_code}"
            )
            print("We could not find your requested wikidata lexeme dump.")

            response = requests.get(base_url)
            other_old_dumps = re.findall(r'href="([^"]+)/"', response.text)

            user_input = input(
                "Do you want to see the closest vailable old dumps? [Y/n]"
            ).lower()

            if user_input == "n":
                return

            if user_input == "y" or user_input == "":
                if other_old_dumps:
                    closest_date = available_closest_lexeme_dumpfile(
                        target_entity, other_old_dumps, try_old_dump
                    )
                    print(
                        f"\nClosest available older dumps(YYYYMMDD): {parse_date(closest_date)}"
                    )
                    fileurl = f"{closest_date}/wikidata-{closest_date}-lexemes.json.bz2"
                    if closest_date:
                        return f"{base_url}/{fileurl}"
                    else:
                        return
            return other_old_dumps

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        latest_dump = re.findall(r'href="([^"]+)"', response.text)
        if "latest-all.json.bz2" in latest_dump:
            latest_dump_link = f"{base_url}/latest-lexemes.json.bz2"
            return latest_dump_link

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
