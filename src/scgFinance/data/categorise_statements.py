# This is a template for categorising financial statements.
from scgFinance.pipeline import process_statements

# Define sources as a list of configs
sources = [
    {
        "path": "raw_data/bank/",  # Directory or single file path
        "source": "bank",  # Identifier for tracking (e.g., 'bank')
        "date_col": "Date",  # Column name for date (default = 'Date')
        "date_format": "%d/%m/%Y",  # Date format in your CSVs
        "time_col": "Time",  # Optional: Time column (set to None if absent)
        "time_format": "%H:%M:%S",  # Optional: Time format
        "desc_col": [
            "Name",
            "Description",
        ],
        "amt_col": "Amount",  # Column name for amount (default = 'Amount')
    },
    {
        "path": "raw_data/credit_card/",
        "source": "credit card",
        "date_col": "Date",
        "date_format": "%d/%m/%Y",
        "desc_col": "Description",  # Single column (default = 'Description)
        "amt_col": "Amount",
    },
]

# Run the full pipeline
categorised_df = process_statements(
    sources,
    # Location for saving which imports have been processed:
    metadata_file="metadata/processed_files.csv",
    # Path for previously categorised CSV (used for ML training)
    categorised_file="categorised.csv",
    # None uses bundled default rules; or 'metadata/custom_rules.csv'
    rules_file="metadata/rules.csv",
    # Set True to re-categorise existing entries
    overwrite=False,
)
