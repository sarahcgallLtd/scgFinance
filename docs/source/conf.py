# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
# For autodoc to find your package (important!)
# import os
# import sys
#
# sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'scgFinance'
copyright = '2025, Sarah C Gall'
author = 'Sarah C Gall'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # For auto-generating docs from docstrings
    'sphinx.ext.autosummary', # Generates function/method/attribute summary lists
    'sphinx.ext.napoleon',  # Support for Google/NumPy-style docstrings
    'sphinx.ext.viewcode',  # Add links to source code
    'sphinx.ext.todo',  # Support for TODO notes
    # Extensions
    'autoapi.extension',
    'sphinx_favicon',
    'sphinx_copybutton',
    'myst_parser',
]
source_suffix = [".rst", ".md"]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', "**.ipynb_checkpoints"]

# -- MyST options ------------------------------------------------------------

# This allows us to use ::: to denote directives, useful for admonitions
myst_enable_extensions = ["colon_fence", "linkify", "substitution"]
myst_heading_anchors = 2
myst_substitutions = {"rtd": "[Read the Docs](https://readthedocs.org/)"}

# -- Internationalisation ----------------------------------------------------

# specifying the natural language populates some key tags
language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_logo = '_static/logo.png'
html_favicon = '_static/favicon.ico'
html_sourcelink_suffix = ''
html_last_updated_fmt = ''  # to reveal the build date in the pages meta

# Paths to custom files
html_static_path = ["_static"]
# html_css_files = ["custom.css"]
# html_js_files = [
#     ("custom-icons.js", {"defer": "defer"}),
# ]
todo_include_todos = True

# For edit buttons (links to GitHub source)
html_context = {
    'github_user': 'sarahcgallLtd',
    'github_repo': 'scgFinance',
    'github_version': 'main',
    'doc_path': 'docs/source',
}

# -- Options for the html theme ------------------------------------------------
# Theme customisations
html_theme_options = {
    'logo': {
        'text': 'scgFinance',
        'image_light': '_static/logo.png',
        'image_dark': '_static/logo-dark.png',
    },
    # Add Links in NavBar
    'icon_links': [
        {
            'name': 'GitHub',
            'url': 'https://github.com/sarahcgallLtd/scgFinance',
            'icon': 'fa-brands fa-github',
            'type': 'fontawesome',
        },
        {
            'name': 'Website',
            'url': 'https://www.sarahcgall.co.uk',
            'icon': 'fa-solid fa-globe',
            'type': 'fontawesome',
        },
        {
            'name': 'Other Packages by Sarah Gall',
            'url': 'https://docs.sarahcgall.co.uk',
            'icon': 'fa-solid fa-database',
            'type': 'fontawesome',
        },
    ],
    'use_edit_page_button': False,  # "Edit on GitHub" buttons
    'show_toc_level': 1,  # TOC in sidebar
    'show_nav_level': 2,  # Sidebar depth
    'navigation_depth': 4,  # Expandable sidebar
    'search_bar_text': 'Search...',  # Custom search placeholder
    'secondary_sidebar_items': {
        '**': ['page-toc', 'custom_index_link']  # Add 'custom_index_link' here
    },
}



# -- favicon options ---------------------------------------------------------

# see https://sphinx-favicon.readthedocs.io for more information about the
# sphinx-favicon extension

# Favicon
favicons = [
    # generic icons compatible with most browsers
    {"href": "favicon-32x32.png"},
    "favicon-16x16.png",
    {"rel": "shortcut icon", "sizes": "any", "href": "favicon.ico"},
    # chrome specific
    "android-chrome-192x192.png",
    "android-chrome-512x512.png",
    # apple icons
    {"rel": "mask-icon", "color": "#459db9", "href": "safari-pinned-tab.svg"},
    {"rel": "apple-touch-icon", "href": "apple-touch-icon.png"},
]

# -- Options for autosummary/autodoc output ------------------------------------
autosummary_generate = True
autodoc_typehints = "description"
autodoc_member_order = "groupwise"
autodoc_default_options = {
    'members': True,            # Include public members
    'private-members': False,   # Explicitly exclude _private ones
    'special-members': False,   # Skip __special__ methods
    'undoc-members': False,     # Skip undocumented items (if helpers lack docstrings)
    'imported-members': False,  # Avoid pulling in imported helpers
    'show-inheritance': True    # Optional: Keep inheritance info
}

# -- Options for autoapi -------------------------------------------------------
autoapi_type = "python"
autoapi_dirs = ["../../src/scgFinance"]
autoapi_keep_files = True
autoapi_root = "api"
autoapi_member_order = "groupwise"
autoapi_ignore = ['*_private*']
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]