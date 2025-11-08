import os
import glob
import pandas as pd


# ================================================
# Modular helper function: Load or create the metadata file
# ================================================


def _load_metadata(metadata_file="metadata/processed_files.csv"):
    """
    Loads the metadata CSV file that tracks processed files, or creates a new
    one if it does not exist.

    This function ensures that the directory for the metadata file exists and
    then attempts to load the CSV. If the file is missing, it creates an empty
    DataFrame with the required columns ('file_name', 'source', 'status',
    'process_date') and saves it to the specified path. This metadata is
    used to prevent re-processing of already imported files.

    Args:
        metadata_file (str, optional): The path to the metadata CSV file.
                                       Defaults to
                                       'metadata/processed_files.csv'.
                                       The directory will be created if it
                                       does not exist.

    Returns:
        pd.DataFrame: A DataFrame containing the metadata with columns:
            - 'file_name': The base name of the processed file (e.g.,
                           'statement.csv').
            - 'source': The identifier for the data source (e.g.,
                        'credit card').
            - 'status': The processing status (e.g., 'processed').
            - 'process_date': The date when the file was processed.

    Raises:
        None explicitly, but may raise OSError if directory creation fails or
        pandas errors during read/write.

    Example:
        >>> meta = _load_metadata('metadata/processed_files.csv')
        >>> print(meta.columns)
        Index(['file_name', 'source', 'status', 'process_date'],
        dtype='object')
    """
    # Ensure the directory for the metadata file exists
    os.makedirs(os.path.dirname(metadata_file), exist_ok=True)

    if os.path.exists(metadata_file):
        meta_df = pd.read_csv(metadata_file)
    else:
        # Create an empty DataFrame with the required columns if file doesn't
        # exist
        meta_df = pd.DataFrame(
            columns=["file_name", "source", "status", "process_date"]
        )
        meta_df.to_csv(metadata_file, index=False)
        print(f"Created new metadata file: {metadata_file}")

    return meta_df


# ================================================
# Modular helper function: Filter files to only include unprocessed ones
# ================================================


def _filter_unprocessed_files(path, source, meta_df):
    """
    Filters a list of CSV files to identify those that have not yet been
    processed for a given source.

    This function checks if the provided path is a directory or a single file.
    If it's a directory, it collects all CSV files within it. It then
    cross-references the base names of these files against the metadata
    DataFrame to exclude any files marked as 'processed' for the specified
    source. This ensures idempotency in the import process by avoiding
    duplicate processing.

    Args:
        path (str): The path to a single CSV file or a directory containing
                    CSV files.
        source (str): The source identifier (e.g., 'credit card', 'bank') used
                      to filter metadata.
        meta_df (pd.DataFrame): The metadata DataFrame loaded from
                                load_metadata().

    Returns:
        list: A list of full paths to unprocessed CSV files. If no unprocessed
              files are found, returns an empty list.

    Raises:
        ValueError: If no CSV files are found in the directory (when path is a
                    directory).

    Example:
        >>> meta = _load_metadata()
        >>> unprocessed = _filter_unprocessed_files('raw_data/bank',
        ... 'bank', meta)
        >>> print(unprocessed)
        ['raw_data/bank/statement_2023.csv']  # Assuming this file is
        unprocessed
    """
    # Get all CSV files in the path (if directory) or just the single file
    if os.path.isdir(path):
        all_files = glob.glob(os.path.join(path, "*.csv"))
        if not all_files:
            raise ValueError(f"No CSV files found in directory: {path}")
    else:
        all_files = [path]

    # Get set of processed file names for this source
    processed_files = set(
        meta_df[
            (meta_df["source"] == source) & (meta_df["status"] == "processed")
        ]["file_name"]
    )

    # Filter to files whose basename is not in processed_files
    unprocessed_files = [
        f for f in all_files if os.path.basename(f) not in processed_files
    ]

    if not unprocessed_files:
        print(f"No unprocessed files for source '{source}' in {path}.")

    return unprocessed_files


# ================================================
# Modular helper function: Process a single CSV file
# ================================================


def _process_single_file(
    file,
    source,
    date_col,
    date_format,
    time_col,
    time_format,
    desc_col,
    amt_col,
):
    """
    Processes a single CSV file by extracting, cleaning, and standardising
    key columns into a uniform DataFrame.

    This function reads the CSV file, parses the date (and optionally time)
    into a datetime object, constructs a description (either from a single
    column or by concatenating multiple columns), cleans  and converts the
    amount to a numeric value, and adds a source identifier. It drops any
    rows with invalid dates or amounts to ensure data quality.

    Args:
        file (str): The path to the CSV file to process.
        source (str): The source identifier to add to the DataFrame
                      (e.g., 'credit card').
        date_col (str): The name of the column containing date information.
        date_format (str): The format string for parsing the date
                           (e.g., '%d/%m/%Y').
        time_col (str or None): The name of the column containing time
                                information (optional).
        time_format (str): The format string for parsing the time
                           (e.g., '%H:%M:%S'), used if time_col is provided.
        desc_col (str or list): The name of the description column or a
                                list of columns to concatenate.
        amt_col (str): The name of the column containing amount information.

    Returns:
        pd.DataFrame: A standardised DataFrame with columns:
            - 'date': Parsed datetime object.
            - 'description': Cleaned description string.
            - 'amount': Numeric amount (float).
            - 'source': The provided source identifier.

    Raises:
        ValueError: If required columns (date_col, desc_col, amt_col)
                    are missing from the CSV.
        pandas.errors: If date/time parsing or numeric conversion fails
                       extensively.

    Example:
        >>> df = _process_single_file(file='raw_data/bank/statement.csv',
        ... source='bank', date_col='Date', date_format='%d/%m/%Y',
        ... time_col=None, time_format='%H:%M:%S', desc_col='Description',
        ... amt_col='Amount')
        >>> print(df.head())
                   date description  amount source
        0 2023-01-01  Groceries   -50.0   bank
    """
    # Read the CSV with all columns as strings to avoid type inference issues
    df = pd.read_csv(file, dtype=str)

    # Handle date (required)
    if date_col in df.columns:
        df["date"] = pd.to_datetime(
            df[date_col], errors="coerce", format=date_format
        )
    else:
        raise ValueError(f"Date column '{date_col}' not found in {file}.")

    # Optionally merge time into date if time_col is provided and exists
    if time_col and time_col in df.columns:
        df["date"] = pd.to_datetime(
            df["date"].dt.date.astype(str) + " " + df[time_col],
            errors="coerce",
            format="%Y-%m-%d " + time_format,
        )

    # Handle description (required; supports single str or list for
    # concatenation)
    if isinstance(desc_col, list):
        # Concatenate multiple columns into one 'description'
        df["description"] = (
            df[desc_col[0]].fillna("") if desc_col[0] in df.columns else ""
        )
        for col in desc_col[1:]:
            if col in df.columns:
                df["description"] += " " + df[col].fillna("")
    elif desc_col in df.columns:
        df["description"] = df[desc_col]
    else:
        raise ValueError(
            f"Description column(s) '{desc_col}' not found " f"in {file}."
        )

    # Handle amount (required; clean currency symbols and convert to numeric)
    if amt_col in df.columns:
        # Remove common currency symbols/commas and convert to float
        df["amount"] = pd.to_numeric(
            df[amt_col].str.replace(r"[$£€,]", "", regex=True), errors="coerce"
        )
    else:
        raise ValueError(f"Amount column '{amt_col}' not found in {file}.")

    # Select only core columns and drop rows with invalid date/amount
    df = df[["date", "description", "amount"]].dropna(
        subset=["date", "amount"]
    )

    # Add the source column for traceability
    df["source"] = source

    return df


# ================================================
# Main function: import_statements
# ================================================


def import_statements(
    path,
    source=None,
    date_col="Date",
    date_format="%d/%m/%Y",
    time_col=None,
    time_format="%H:%M:%S",
    desc_col="Description",
    amt_col="Amount",
    metadata_file="metadata/processed_files.csv",
):
    """
    Orchestrates the import of financial statements from one or more CSV
    files, ensuring only unprocessed files are handled.

    This is the primary entry point for importing data. It loads metadata to
    track processed files, filters out already processed ones, processes
    each remaining file using process_single_file(), concatenates the
    results into a single DataFrame sorted by date, and returns the
    combined DataFrame along with a list of imported file base names.
    Note that this function does not update the metadata; that should be
    handled by the caller after successful processing.

    Args:
        path (str): The path to a single CSV file or a directory containing
                    CSV files.
        source (str, optional): The source identifier (e.g., 'credit card').
                                Required for metadata filtering.
        date_col (str, optional): The date column name. Defaults to 'Date'.
        date_format (str, optional): The date format string. Defaults to
                                     '%d/%m/%Y'.
        time_col (str or None, optional): The time column name. Defaults
                                          to None.
        time_format (str, optional): The time format string. Defaults to
                                     '%H:%M:%S'.
        desc_col (str or list, optional): The description column(s).
                                          Defaults to 'Description'.
        amt_col (str, optional): The amount column name. Defaults to 'Amount'.
        metadata_file (str, optional): The path to the metadata CSV.
                                       Defaults to
                                       'metadata/processed_files.csv'.

    Returns:
        tuple:
            - pd.DataFrame: The combined, sorted DataFrame of all
                            processed files.
            - list: A list of base names of the imported (processed) files.

    Raises:
        ValueError: If path or source is not specified, or if no files
                    are found/processed.

    Example:
        >>> df, files = import_statements('raw_data/bank/', 'bank')
        >>> print(df.shape)
        (100, 4)  # Example output
        >>> print(files)
        ['statement_2023.csv']
    """
    if path is None:
        raise ValueError(
            "Path must be specified for each source " "configuration."
        )

    if source is None:
        raise ValueError("Source must be specified for metadata tracking.")

    # Step 1: Load metadata
    meta_df = _load_metadata(metadata_file)

    # Step 2: Filter to unprocessed files
    files = _filter_unprocessed_files(path, source, meta_df)

    if not files:
        return pd.DataFrame(), []  # Return empty if nothing to process

    # Step 3: Process each file and collect DataFrames + imported base names
    dfs = []
    imported_files = []
    for file in files:
        file_df = _process_single_file(
            file,
            source,
            date_col,
            date_format,
            time_col,
            time_format,
            desc_col,
            amt_col,
        )
        dfs.append(file_df)
        imported_files.append(os.path.basename(file))

    # Step 4: Concatenate all processed DataFrames and sort by date
    combined_df = pd.concat(dfs, ignore_index=True).sort_values("date")

    return combined_df, imported_files
