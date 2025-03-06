# SPDX-License-Identifier: GPL-3.0-or-later

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from setuptools import find_packages

package_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(package_directory, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

with open(
    os.path.join(package_directory, "requirements.txt"), encoding="utf-8"
) as req_file:
    requirements = req_file.readlines()

on_rtd = os.environ.get("READTHEDOCS") == "True"
if on_rtd:
    requirements = []

setup_args = dict(
    name="scribe-data",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    version="4.1.0",
    author="Andrew Tavis McAllister",
    author_email="team@scri.be",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    package_data={"": ["2021_ranked.tsv"]},
    include_package_data=True,
    description="Wikidata and Wikipedia language data extraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scribe-org/Scribe-Data",
    entry_points={
        "console_scripts": [
            "scribe-data=scribe_data.cli.main:main",
        ],
    },
)

if __name__ == "__main__":
    setup(**setup_args)
