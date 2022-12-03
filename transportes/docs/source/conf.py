# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import django

sys.path.insert(0, os.path.abspath('../../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'transportes.settings'
django.setup()


project = 'TransportesEscolares'
copyright = '2022, Alejandro Muñoz Lezcano'
author = 'Alejandro Muñoz Lezcano'
release = '1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
        'sphinx.ext.intersphinx',
        'sphinx.ext.todo',
        'sphinx.ext.mathjax',
        'sphinx.ext.napoleon',
        'sphinx.ext.autosummary', # solamente si se la quiere usar
        'sphinx.ext.viewcode']

templates_path = ['_templates']
exclude_patterns = []

language = 'es'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'renku'
html_static_path = ['_static']
html_sidebars = { '**': ['globaltoc.html', 'relations.html',
        'sourcelink.html', 'searchbox.html'], }