# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import django

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
]

sys.path.insert(0, os.path.abspath('../..'))  

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'  

# Setup Django
django.setup()

project = 'My Bank App'
copyright = '2025, Mcebo Mnguni'
author = 'Mcebo Mnguni'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
