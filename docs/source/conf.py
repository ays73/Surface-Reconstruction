# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join('..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join('..', '..', 'tests')))

project = 'From Unreal Engine to Mitsuba Renderer'
copyright = '2025, Aysegül Peközsoy'
author = 'Aysegül Peközsoy'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_parser','sphinx.ext.autodoc', 'sphinx.ext.napoleon']

html_theme = 'sphinx_rtd_theme'

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
