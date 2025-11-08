scgFinance <a href="https://sarahcgallLtd.github.io/scgFinance/"><img src="docs/source/_static/logo.png" align="right" height="138" alt="" /></a>
================

<!-- badges: start -->

[![Release](https://img.shields.io/badge/Release-development%20version%200.1.0-blue)](https://github.com/sarahcgallLtd/scgFinance/blob/main/CHANGELOG.md)
[![CI](https://github.com/sarahcgallLtd/scgFinance/actions/workflows/ci.yml/badge.svg)](https://github.com/sarahcgallLtd/scgFinance/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/sarahcgallLtd/scgFinance/graph/badge.svg?token=aHcnsCGhVZ)](https://codecov.io/gh/sarahcgallLtd/scgFinance)

<!-- badges: end -->

## Overview


`scgFinance` is a Python package providing tools for managing personal finances, including the ability to: 
- import bank statements, 
- categorise expenses automatically or manually, 
- track and visualise spending, 
- forecast trends, and 
- compare against budgets.


# Install the development version from GitHub

```bash
pip install git+https://github.com/sarahcgallLtd/scgFinance.git@main

# Alternatively, clone the repository and install locally:
git clone https://github.com/sarahcgallLtd/scgFinance.git
cd scgFinance
pip install -e .
```

## Usage
`scgFinance` provides a streamlined workflow for importing, categorising, and managing personal finance data from 
bank and credit card statements. Below are examples demonstrating key functions. For full details, refer to 
the [package documentation](https://docs.sarahcgall.co.uk/scgFinance).


### Loading Sample Data
`scgFinance` comes with sample data for you to use, including access to the default rules file which is used to 
classify and categorise statement items when there are insufficient amounts of previously categorised data. 

Use `load_package_data` to access bundled sample datasets for testing or exploration:

``` python
from scgFinance.utils import load_package_data

# Load bank sample
bank_df = load_package_data('bank')
print(bank_df.head())

# Load credit card sample
cc_df = load_package_data('credit_card')

# Load rules
rules_df = load_package_data('rules')
```

### Processing Pipeline
The `process_statements` function runs the end-to-end workflow: 
- importing from multiple sources, 
- categorising, 
- updating metadata, and 
- saving categorised/processed files.

Example: Processing bank and credit card statements together:

``` python 
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
```

## Feedback and Contributions

Suggestions and contributions are welcome. For any proposed additions, amendments, or feedback, please [create an issue](https://github.com/sarahcgallLtd/scgFinance/issues).


## Other Packages

Check out other packages developed by Sarah C Gall Ltd here: https://docs.sarahcgall.co.uk
