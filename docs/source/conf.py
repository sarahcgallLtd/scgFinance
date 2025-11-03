# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'scgFinance'
copyright = '2025, Sarah C Gall'
author = 'Sarah C Gall'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',    # For auto-generating docs from docstrings
    'sphinx.ext.napoleon',   # Support for Google/NumPy-style docstrings
    'sphinx.ext.viewcode',   # Add links to source code
    'sphinx.ext.todo',       # Support for TODO notes
    # Add more as needed, e.g., 'sphinx.ext.mathjax' for math
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'

# Logo setup (hex sticker)
html_logo = '_static/logo.png'

# Theme customisations
html_theme_options = {
    'logo': {
        'text': 'scgFinance',
        'image_light': '_static/logo.png',
    },
    # Add GitHub badge/link in navbar
    'icon_links': [
        {
            'name': 'GitHub',
            'url': 'https://github.com/sarahcgallLtd/scgFinance',
            'icon': 'fa-brands fa-github',
            'type': 'fontawesome',
        },
    ],
    'show_nav_level': 2,  # Sidebar depth
    'navigation_depth': 4,  # Expandable sidebar
    'search_bar_text': 'Search...',  # Custom search placeholder
    'use_edit_page_button': True,  # "Edit on GitHub" buttons
    'show_toc_level': 2,  # TOC in sidebar
}

# For edit buttons (links to GitHub source)
html_context = {
    'github_user': 'sarahcgallLtd',
    'github_repo': 'scgFinance',
    'github_version': 'main',
    'doc_path': 'docs/source',
}

# Favicon
html_favicon = '_static/favicon.ico'

# For autodoc to find your package (important!)
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))
