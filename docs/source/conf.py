import os
import sys

# -- Path setup --------------------------------------------------------------
# Informs Sphinx where your source code is relative to this file
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
project = 'KMDS Data Helper'
copyright = '2024, Rajiv Sam'
author = 'Rajiv Sam'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'myst_parser',  # Critical for .md files
]

# Map extensions to parsers
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.venv']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# The master toctree document
master_doc = 'index'
