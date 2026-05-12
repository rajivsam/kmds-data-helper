import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'KMDS Data Helper'
copyright = '2024, Rajiv Sam'
author = 'Rajiv Sam'

extensions = [
    'sphinx.ext.autodoc',
    'myst_parser',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

master_doc = 'index'
html_theme = 'sphinx_rtd_theme'
