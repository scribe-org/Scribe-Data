# SPDX-License-Identifier: GPL-3.0-or-later
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.


sys.path.insert(0, os.path.abspath("../../src"))

# -- Project information -----------------------------------------------------

project = "Scribe-Data"
copyright = "2024, Scribe-Data developers (GPL 3.0 License)"
author = "Scribe-Data developers"

# The full version, including alpha/beta/rc tags
release = "5.1.4"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "numpydoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.imgmath",
]

numpydoc_show_inherited_class_members = False
numpydoc_show_class_members = False

# NOT to sort autodoc functions in alphabetical order
autodoc_member_order = "bysource"

# To avoid installing dependencies when building doc
# https://stackoverflow.com/a/15912502/8729698
autodoc_mock_imports = [
    "beautifulsoup4",
    "emoji",
    "flax",
    "langcodes",
    "mwparserfromhell",
    "pandas",
    "PyICU",
    "pytest",
    "pytest-cov",
    "ruff",
    "SPARQLWrapper",
    "tqdm",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"


# The master toctree document.
master_doc = "index"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output ----------------------------------------------

html_theme = "sphinx_rtd_theme"

# html_theme_path = [sphinx_rtd_theme]
# html_theme_path = []

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    "**": ["relations.html", "searchbox.html"]
}  # needs 'show_related': True theme option to display


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "Scribe-Data_doc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "Scribe-Data.tex",
        "Scribe-Data Documentation",
        "scribe-org",
        "manual",
    )
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "Scribe-Data", "Scribe-Data Documentation", [author], 1)]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "Scribe-Data",
        "Scribe-Data Documentation",
        author,
        "Scribe-Data",
        "Wikidata and Wikipedia language data extraction",
        "Miscellaneous",
    )
]

# Adding logo to the docs sidebar.
html_logo = "_static/ScribeDataLogo.png"
html_theme_options = {
    "logo_only": True,
    # "display_version": True,
}

# Adding favicon to the docs.
html_favicon = "_static/ScribeFavicon.ico"

# Importing custom css for theme customization.
html_css_files = [
    "custom.css",
]
