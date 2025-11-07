.. scgFinance documentation master file

.. raw:: html

   <div style="display: flex; align-items: center; margin-bottom: 40px;">
     <img src="_static/logo.png" alt="scgFinance Hex Logo" width="120" class="only-light" style="margin-right: 15px;">
     <img src="_static/logo-dark.png" alt="scgFinance Hex Logo" width="120" class="only-dark" style="margin-right: 15px;">
     <h1 style="margin: 0;">scgFinance</h1>
   </div>

Overview
==========

The `scgFinance` package provides tools for managing personal finances, including the ability to: import bank statements, categorise expenses automatically or manually, track and visualise spending, forecast trends, and compare against budgets.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Installation
============

`scgFinance` requires Python 3.12 or later. You can install the stable version from PyPI (if available) or the development version directly from GitHub.

Stable Version (from PyPI)
--------------------------

.. code-block:: bash

   pip install scgFinance


Development Version (from GitHub)
---------------------------------

To install the latest development version, use pip to install directly from the repository:

.. code-block:: bash

   pip install git+https://github.com/sarahcgallLtd/scgFinance.git@main

Alternatively, clone the repository and install locally:

.. code-block:: bash

   git clone https://github.com/sarahcgallLtd/scgFinance.git
   cd scgFinance
   pip install -e .


Usage
============

`scgFinance` provides a streamlined workflow for importing, categorising, and managing personal finance data from
bank and credit card statements. Below are examples demonstrating key functions. For full details, refer to
the [package documentation](https://docs.sarahcgall.co.uk/scgFinance).


Loading Sample Data
-------------------

`scgFinance` comes with sample data for you to use, including access to the default rules file which is used to
classify and categorise statement items when there are insufficient amounts of previously categorised data.

Use `load_package_data` to access bundled sample datasets for testing or exploration:

.. code-block:: python

   from scgFinance.utils import load_package_data

   # Load bank sample
    bank_df = load_package_data('bank')
    print(bank_df.head())

    # Load credit card sample
    cc_df = load_package_data('credit_card')

    # Load rules
    rules_df = load_package_data('rules')



Processing Pipeline
------------------------
The `process_statements` function runs the end-to-end workflow: importing from multiple sources, categorising, updating metadata, and saving categorised/processed files.

Example: Processing bank and credit card statements together:

.. code-block:: python

    from scgFinance.process import process_statements

    # Define sources as a list of configs
    sources = [
        {
            'path': 'path/to/bank_statements/',  # Directory or single file path
            'source': 'bank',                    # Identifier for tracking (e.g., 'bank' or 'credit_card')
            'date_col': 'Date',                  # Column name for date (default = 'Date')
            'date_format': '%d/%m/%Y',           # Date format in your CSVs (default = '%d/%m/%Y')
            'time_col': 'Time',                  # Optional: Time column (set to None if absent)
            'time_format': '%H:%M:%S',           # Optional: Time format (default = '%H:%M:%S')
            'desc_col': ['Name', 'Description'], # Single column or list to concatenate
            'amt_col': 'Amount'                  # Column name for amount (default = 'Amount')
        },
        {
            'path': 'path/to/credit_card_statements/',
            'source': 'credit_card',
            'date_col': 'Date',
            'date_format': '%d/%m/%Y',
            'desc_col': 'Description',           # Single column (default = 'Description)
            'amt_col': 'Amount'
        }
    ]

    # Run the full pipeline
    categorised_df = process_statements(
        sources,
        metadata_file='metadata/processed_files.csv',  # Location for saving which imports have been processed
        categorised_dir='categorised/',                # Directory for previously categorised CSVs (used for ML training)
        rules_file=None,                               # None uses bundled default rules; or 'metadata/custom_rules.csv'
        overwrite=False                                # Set True to re-categorise existing entries
    )

    print(categorised_df.head())
