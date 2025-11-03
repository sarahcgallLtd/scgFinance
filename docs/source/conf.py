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
html_logo = '_static/logo.png'  # Path to your hexagonal PNG (create/add below)

# Optional theme customisations for pkgdown-like feel
html_theme_options = {
    'logo': {
        'text': 'scgFinance',  # Package name next to logo; omit if unwanted
        'image_light': '_static/logo.png',  # For light mode
        'image_dark': '_static/logo-dark.png',  # Optional dark variant
    },
    'icon_links': [  # Add GitHub badge/link in navbar
        {
            'name': 'GitHub',
            'url': 'https://github.com/sarahcgallLtd/your-package',
            'icon': 'fa-brands fa-github',
            'type': 'fontawesome',
        },
    ],
    'show_nav_level': 2,  # Sidebar depth like pkgdown
    'navigation_depth': 4,  # Expandable sidebar
    'search_bar_text': 'Search...',  # Custom search placeholder
    'use_edit_page_button': True,  # "Edit on GitHub" buttons
    'show_toc_level': 2,  # TOC in sidebar
}

# For edit buttons (links to GitHub source)
html_context = {
    'github_user': 'sarahcgallLtd',
    'github_repo': 'your-package',
    'github_version': 'main',  # Your branch
    'doc_path': 'docs/source',  # Path to .rst files in repo
}

# Favicon (optional, if your hex has a favicon version)
html_favicon = '_static/favicon.ico'

# For autodoc to find your package (important!)
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))
