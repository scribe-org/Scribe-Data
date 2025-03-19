# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the setup process.
"""

import os
import sys
import unittest
from unittest.mock import mock_open, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestSetup(unittest.TestCase):
    def test_package_data(self):
        from setup import setup_args

        self.assertIn("package_data", setup_args)
        self.assertEqual(setup_args["package_data"], {"": ["2021_ranked.tsv"]})
        self.assertTrue(setup_args["include_package_data"])

    def test_packages(self):
        from setup import setup_args

        self.assertIn("packages", setup_args)
        self.assertIn("package_dir", setup_args)
        self.assertEqual(setup_args["package_dir"], {"": "src"})

    def test_requirements(self):
        from setup import setup_args

        self.assertIn("install_requires", setup_args)
        self.assertIsInstance(setup_args["install_requires"], list)

    def test_classifiers(self):
        from setup import setup_args

        self.assertIn("classifiers", setup_args)
        self.assertGreater(len(setup_args["classifiers"]), 5)
        self.assertIn("Programming Language :: Python :: 3", setup_args["classifiers"])

    def test_entry_points(self):
        from setup import setup_args

        self.assertIn("entry_points", setup_args)
        self.assertIn("console_scripts", setup_args["entry_points"])
        self.assertIn(
            "scribe-data=scribe_data.cli.main:main",
            setup_args["entry_points"]["console_scripts"],
        )

    @patch("builtins.open", new_callable=mock_open, read_data="package1\npackage2\n")
    def test_requirements_loading(self, mock_file):
        # Re-import setup to trigger the file reading with our mock.
        import importlib

        import setup

        importlib.reload(setup)
        # Expect the newlines since they're part of the file reading.
        self.assertEqual(setup.requirements, ["package1\n", "package2\n"])

    @patch.dict(os.environ, {"READTHEDOCS": "True"})
    def test_rtd_requirements(self):
        # Re-import setup to trigger the environment check.
        import importlib

        import setup

        importlib.reload(setup)
        self.assertEqual(setup.requirements, [])
