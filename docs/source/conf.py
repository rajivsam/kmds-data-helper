# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://sphinx-doc.org

# -- Project information -----------------------------------------------------
# https://sphinx-doc.org#project-information

project = 'KMDS Data Helper'
copyright = '2024, Rajiv'
author = 'Rajiv'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://sphinx-doc.org#general-configuration

extensions = [
    "myst_parser",
    "sphinx_rtd_theme",
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://sphinx-doc.org#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Set the master doc to index
master_doc = 'index'
