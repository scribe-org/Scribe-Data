"""
Tests for the CLI get functionality.

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

import unittest
from unittest.mock import patch

from scribe_data.cli.get import get_data


class TestCLIGetCommand(unittest.TestCase):
    @unittest.skip("Mocking doesn't work as expected.")
    def test_get_command(self):
        with patch("scribe_data.cli.get.get_data") as mock_get_data:
            # Call the function you're testing
            get_data(
                language="English",
                data_type="nouns",
                output_dir="tests_output",
                output_type="json",
            )

            get_data(all=True)

            # Validate the calls.
            assert mock_get_data.call_count == 2

            args, kwargs = mock_get_data.mock_calls[0]
            self.assertEqual(args, ("English", "nouns", "tests_output"))
            self.assertFalse(kwargs.get("all"))

            args, kwargs = mock_get_data.mock_calls[-1]  # Get the last call
            self.assertIsNone(args)
            self.assertTrue(kwargs["all"])
