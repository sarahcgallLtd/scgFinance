import os
import glob
import pandas as pd
from datetime import datetime  # Imported for timestamping in metadata updates (if needed elsewhere)


# Modular helper function: Load or create the metadata file
# This keeps track of processed files to avoid re-importing them.
# Returns a DataFrame with columns: 'file_name', 'source', 'status', 'process_date'
def load_metadata(metadata_file='metadata/processed_files.csv'):
    """
    Loads the metadata CSV or creates it if it doesn't exist.

    Args:
        metadata_file (str): Path to the metadata CSV.

    Returns:
        pd.DataFrame: The metadata DataFrame.
    """
    # Ensure the directory for the metadata file exists
    os.makedirs(os.path.dirname(metadata_file), exist_ok=True)

    if os.path.exists(metadata_file):
        meta_df = pd.read_csv(metadata_file)
    else:
        # Create an empty DataFrame with the required columns if file doesn't exist
        meta_df = pd.DataFrame(columns=['file_name', 'source', 'status', 'process_date'])
        meta_df.to_csv(metadata_file, index=False)
        print(f"Created new metadata file: {metadata_file}")

    return meta_df


# Modular helper function: Filter files to only include unprocessed ones
# Uses the metadata to check which files have 'status' == 'processed' for the given source.
# Returns a list of full file paths that are unprocessed.
def filter_unprocessed_files(
        path,
        source,
        meta_df
):
    """
    Filters files in the path to only those not marked as 'processed' in metadata.

    Args:
        path (str): Path to a file or directory.
        source (str): Source identifier (e.g., 'credit card', 'bank').
        meta_df (pd.DataFrame): Loaded metadata DataFrame.

    Returns:
        list: List of unprocessed file paths.
    """
    # Get all CSV files in the path (if directory) or just the single file
    if os.path.isdir(path):
        all_files = glob.glob(os.path.join(path, '*.csv'))
        if not all_files:
            raise ValueError(f"No CSV files found in directory: {path}")
    else:
        all_files = [path]

    # Get set of processed file names for this source
    processed_files = set(meta_df[(meta_df['source'] == source) & (meta_df['status'] == 'processed')]['file_name'])

    # Filter to files whose basename is not in processed_files
    unprocessed_files = [f for f in all_files if os.path.basename(f) not in processed_files]

    if not unprocessed_files:
        print(f"No unprocessed files for source '{source}' in {path}.")

    return unprocessed_files


# Modular helper function: Process a single CSV file into a standardised DataFrame
# Handles column extraction, cleaning, and standardisation for date, description, amount.
# Returns a DataFrame with columns: 'date', 'description', 'amount', 'source'
def process_single_file(
        file,
        source,
        date_col,
        date_format,
        time_col,
        time_format,
        desc_col,
        amt_col
):
    """
    Processes a single CSV file: reads, standardises columns, cleans data.

    Args:
        file (str): Path to the CSV file.
        source (str): Source identifier.
        date_col (str): Date column name.
        date_format (str): Date format string.
        time_col (str or None): Time column name (optional).
        time_format (str): Time format string (optional)..
        desc_col (str or list): Description column(s).
        amt_col (str): Amount column name.

    Returns:
        pd.DataFrame: Standardised DataFrame for this file.
    """
    # Read the CSV with all columns as strings to avoid type inference issues
    df = pd.read_csv(file, dtype=str)

    # Handle date (required)
    if date_col in df.columns:
        df['date'] = pd.to_datetime(df[date_col], errors='coerce', format=date_format)
    else:
        raise ValueError(f"Date column '{date_col}' not found in {file}.")

    # Optionally merge time into date if time_col is provided and exists
    if time_col and time_col in df.columns:
        df['date'] = pd.to_datetime(df['date'].dt.date.astype(str) + ' ' + df[time_col], errors='coerce', format='%Y-%m-%d ' + time_format)

    # Handle description (required; supports single str or list for concatenation)
    if isinstance(desc_col, list):
        # Concatenate multiple columns into one 'description'
        df['description'] = df[desc_col[0]].fillna('') if desc_col[0] in df.columns else ''
        for col in desc_col[1:]:
            if col in df.columns:
                df['description'] += ' ' + df[col].fillna('')
    elif desc_col in df.columns:
        df['description'] = df[desc_col]
    else:
        raise ValueError(f"Description column(s) '{desc_col}' not found in {file}.")

    # Handle amount (required; clean currency symbols and convert to numeric)
    if amt_col in df.columns:
        # Remove common currency symbols/commas and convert to float
        df['amount'] = pd.to_numeric(
            df[amt_col].str.replace(r'[$£€,]', '', regex=True), errors='coerce'
        )
    else:
        raise ValueError(f"Amount column '{amt_col}' not found in {file}.")

    # Select only core columns and drop rows with invalid date/amount
    df = df[['date', 'description', 'amount']].dropna(subset=['date', 'amount'])

    # Add the source column for traceability
    df['source'] = source

    return df


# Main function: import_statements
# Orchestrates the process: loads metadata, filters files, processes each, concatenates, and returns combined DF + imported file names.
def import_statements(
        path, source=None,
        date_col='Date',
        date_format='%d/%m/%Y',
        time_col=None,
        time_format='%H:%M:%S',
        desc_col='Description',
        amt_col='Amount',
        metadata_file='metadata/processed_files.csv'
):
    """
    Imports statements from CSV files, filtering unprocessed ones via metadata.
    Processes and standardises data from one or more files.

    Args:
        path (str): Path to a single file or directory of CSVs.
        source (str, optional): Source identifier (e.g., 'credit card', 'bank'). Used for metadata filtering.
        date_col (str): Date column name (default: 'Date').
        date_format (str, optional): Date column format (default: '%d/%m/%Y').
        time_col (str or None): Time column name (optional, default: None).
        time_format (str, optional): Time column format (optional, default: '%H:%M:%S').
        desc_col (str or list): Description column(s) (default: 'Description').
        amt_col (str): Amount column name (default: 'Amount').
        metadata_file (str): Path to metadata CSV (default: 'metadata/processed_files.csv').

    Returns:
        tuple: (pd.DataFrame with combined data, list of imported file base names).
    """
    if path is None:
        raise ValueError("Path must be specified for each source configuration.")

    if source is None:
        raise ValueError("Source must be specified for metadata tracking.")

    # Step 1: Load metadata
    meta_df = load_metadata(metadata_file)

    # Step 2: Filter to unprocessed files
    files = filter_unprocessed_files(path, source, meta_df)

    if not files:
        return pd.DataFrame(), []  # Return empty if nothing to process

    # Step 3: Process each file and collect DataFrames + imported base names
    dfs = []
    imported_files = []
    for file in files:
        file_df = process_single_file(file, source, date_col, date_format, time_col, time_format, desc_col, amt_col)
        dfs.append(file_df)
        imported_files.append(os.path.basename(file))

    # Step 4: Concatenate all processed DataFrames and sort by date
    combined_df = pd.concat(dfs, ignore_index=True).sort_values('date')

    return combined_df, imported_files
