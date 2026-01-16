# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import find_packages, setup

setup(
    version="5.1.4",
    author="Andrew Tavis McAllister",
    author_email="team@scri.be",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"": ["2021_ranked.tsv"]},
    include_package_data=True,
    description="Wikidata and Wikipedia language data extraction",
    long_description_content_type="text/markdown",
    url="https://github.com/scribe-org/Scribe-Data",
    entry_points={
        "console_scripts": [
            "scribe-data=scribe_data.cli.main:main",
        ],
    },
)
