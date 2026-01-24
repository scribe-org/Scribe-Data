.. image:: https://raw.githubusercontent.com/scribe-org/Scribe-Data/main/.github/resources/images/ScribeDataLogo.png
    :height: 150
    :align: center
    :target: https://github.com/scribe-org/Scribe-Data

|platform| |rtd| |issues| |language| |pypi| |pypistatus| |license| |coc| |mastodon| |matrix|

.. |platform| image:: https://img.shields.io/badge/Wikidata-990000.svg?logo=wikidata&logoColor=ffffff
    :target: https://github.com/scribe-org/Scribe-Data

.. |rtd| image:: https://img.shields.io/readthedocs/scribe-data.svg?label=%20&logo=read-the-docs&logoColor=ffffff
    :target: http://scribe-data.readthedocs.io/en/latest/

.. |issues| image:: https://img.shields.io/github/issues/scribe-org/Scribe-Data?label=%20&logo=github
    :target: https://github.com/scribe-org/Scribe-Data/issues

.. |language| image:: https://img.shields.io/badge/Python%203-306998.svg?logo=python&logoColor=ffffff
    :target: https://github.com/scribe-org/Scribe-Data/blob/main/CONTRIBUTING.md

.. |pypi| image:: https://img.shields.io/pypi/v/scribe-data.svg?label=%20&color=4B8BBE
    :target: https://pypi.org/project/scribe-data/

.. |pypistatus| image:: https://img.shields.io/pypi/status/scribe-data.svg?label=%20
    :target: https://pypi.org/project/scribe-data/

.. |license| image:: https://img.shields.io/github/license/scribe-org/Scribe-Data.svg?label=%20
    :target: https://github.com/scribe-org/Scribe-Data/blob/main/LICENSE.txt

.. |coc| image:: https://img.shields.io/badge/Contributor%20Covenant-ff69b4.svg
    :target: https://github.com/scribe-org/Scribe-Data/blob/main/.github/CODE_OF_CONDUCT.md

.. |mastodon| image:: https://img.shields.io/badge/Mastodon-6364FF.svg?logo=mastodon&logoColor=ffffff
    :target: https://wikis.world/@scribe

.. |matrix| image:: https://img.shields.io/badge/Matrix-000000.svg?logo=matrix&logoColor=ffffff
    :target: https://matrix.to/#/#scribe_community:matrix.org

**Wikidata and Wikipedia language data extraction**

Installation
============

Scribe-Data is available for installation via `pip <https://pypi.org/project/scribe-data/>`_:

.. code-block:: shell

    # Using uv (recommended - fast, Rust-based installer):
    uv pip install scribe-data

    # Or using pip:
    pip install scribe-data

The latest development version can further be installed the `source code on GitHub <https://github.com/scribe-org/Scribe-Data>`_:

.. code-block:: shell

    # With uv (recommended):
    uv sync --all-extras  # Install all dependencies
    source .venv/bin/activate  # Activate venv (macOS/Linux)
    # .venv\Scripts\activate  # Activate venv (Windows)

    # Or with pip:
    python -m venv .venv  # Create virtual environment
    source .venv/bin/activate  # Activate venv (macOS/Linux)
    # .venv\Scripts\activate  # Activate venv (Windows)
    pip install -e .

To utilize the Scribe-Data CLI, you can execute variations of the following command in your terminal:

.. code-block:: shell

    scribe-data -h  # view the cli options
    scribe-data [command] [arguments]

Available Commands
==================

- ``list`` (``l``): Enumerate available languages, data types and their combinations.
- ``get`` (``g``): Retrieve data from Wikidata for specified languages and data types.
- ``total`` (``t``): Display the total available data for given languages and data types.
- ``convert`` (``c``): Transform data returned by Scribe-Data into different file formats.

Contents
========

.. toctree::
    :maxdepth: 2

    scribe_data/index

Contributing
============

.. toctree::
    :maxdepth: 2

    notes

Project Indices
===============

* :ref:`genindex`
