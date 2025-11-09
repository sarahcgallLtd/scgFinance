.. scgFinance documentation master file

.. raw:: html

   <div style="display: flex; align-items: center; margin-bottom: 40px;">
     <img src="_static/logo.png" alt="scgFinance Hex Logo" width="120" class="only-light" style="margin-right: 15px;">
     <img src="_static/logo-dark.png" alt="scgFinance Hex Logo" width="120" class="only-dark" style="margin-right: 15px;">
     <h1 style="margin: 0;">scgFinance</h1>
   </div>

Overview
========

.. image:: https://img.shields.io/badge/release-v0.1.0-blue
   :alt: Release
   :target: https://docs.sarahcgall.co.uk/scgFinance/changeLog.html

.. image:: https://github.com/sarahcgallLtd/scgFinance/actions/workflows/ci.yml/badge.svg
   :alt: CI
   :target: https://github.com/sarahcgallLtd/scgFinance/actions/workflows/ci.yml

.. image:: https://codecov.io/gh/sarahcgallLtd/scgFinance/graph/badge.svg?token=aHcnsCGhVZ
   :alt: codecov
   :target: https://codecov.io/gh/sarahcgallLtd/scgFinance

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :alt: Code style: black
   :target: https://github.com/psf/black

.. raw:: html

   <div style="margin-bottom: 10px;"></div>

``scgFinance`` is a Python package designed to simplify personal finance management. It provides tools to import,
categorise, track, visualise, and forecast financial data from bank and credit card statements. Using a
combination of rule-based and machine learning approaches, it adapts to your spending patterns over time, making
it easier to monitor budgets and identify trends.


Key Features
------------

- *Automatic Categorisation*: Uses rules and machine learning to classify transactions, improving accuracy with more data.
- *Import from Multiple Sources*: Supports bank and credit card CSV files with customisable column mappings.
- *Tracking and Visualisation*: Generate reports, charts, and forecasts for spending patterns.
- *Budget Comparison*: Compare actual spending against predefined budgets.
- *Metadata Tracking*: Avoids re-processing files by maintaining a record of imported data.


Installation
------------

``scgFinance`` requires Python 3.12 or later. You can install from PyPI.


.. code-block:: bash

   pip install scgFinance



Quickstart
----------

``scgFinance`` includes a utility function to set up a recommended project directory structure, complete with empty
folders for your data, a default rules file for categorisation, and a template script to get started with processing.
Use ``download_template`` to initialise the structure:

.. code-block:: python

    from scgFinance.utils import download_template

    # Create the project structure in the specified root directory
    download_template()


|

This will generate the following structure:

.. code-block:: python

    your_project_root/
    │
    ├── categorised/             # For saving categorised output files
    │
    ├── metadata/
    │   └── rules.csv            # Default categorisation rules (customisable)
    │
    ├── raw_data/
    │   ├── bank/                # Place your bank statement CSVs here
    │   └── credit_card/         # Place your credit card statement CSVs here
    │
    └── categorise_statements.py # Template script for running the processing pipeline

|

After setup:

1. Download your statements from your financial institution (e.g., your bank) in a CSV format.
2. Save your statements in the ``raw_data/bank/`` or ``raw_data/credit_card`` folders (rename, add, or delete folders depending on your needs e.g., to ``raw_data/HSBC/``).
3. Customise ``metadata/rules.csv`` if needed based on your financial statements and common transactions
4. Modify/run ``categorise_statements.py`` to process your data.

|

For more details, see the :doc:`User Guide <user_guide/index>`.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   user_guide/index
   api
   changeLog
