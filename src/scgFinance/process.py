from src.scgFinance.importers import import_statements
from src.scgFinance.categoriser import auto_categorise
import pandas as pd
import os
from datetime import datetime

# Helper function for tracking which files have been processed and which have not
# This function updates the metadata CSV with the status and process date for the imported files.
def update_metadata(imported_files, source, metadata_file='metadata/processed_files.csv', status='processed'):
    """
    Updates the metadata CSV with processed status and date for given files.

    Args:
        imported_files (list): List of file base names that were imported.
        source (str): 'credit card' or 'bank'.
        metadata_file (str): Path to metadata CSV.
        status (str): Status to set (default: 'processed').
    """
    if not imported_files:
        return

    # Ensure the directory for the metadata file exists
    if os.path.exists(metadata_file):
        meta_df = pd.read_csv(metadata_file)
    else:
        meta_df = pd.DataFrame(columns=['file_name', 'source', 'status', 'process_date'])

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Load existing metadata or create new if it doesn't exist
    for file_name in imported_files:
        mask = (meta_df['file_name'] == file_name) & (meta_df['source'] == source)
        if mask.any():
            meta_df.loc[mask, 'status'] = status
            meta_df.loc[mask, 'process_date'] = current_time
        else:
            new_row = {'file_name': file_name, 'source': source, 'status': status, 'process_date': current_time}
            meta_df = pd.concat([meta_df, pd.DataFrame([new_row])], ignore_index=True)

    # Save updated metadata
    meta_df.to_csv(metadata_file, index=False)
    print(f"Updated metadata for {len(imported_files)} files with status '{status}'.")


# Main function: process_statements
def process_statements(
        sources,
        metadata_file='metadata/processed_files.csv',
        categorised_dir='categorised/',
        rules_file=None,
        overwrite=False
):
    """
    Runs the full finance pipeline: imports statements from multiple sources,
    categorises them, updates metadata, and saves categorised.

    Args:
        sources (list of dict): Each dict contains:
            - 'path': str, path to statements (file or directory)
            - 'source': str, source identifier (e.g., 'Lloyds', 'HSBC', 'Mastercard')
            - Optional custom params: 'desc_col', 'time_col', etc., passed to import_statements
        metadata_file (str): Path to metadata CSV for tracking processed files.
        categorised_dir (str): Directory for saving categorised/processed files.
        rules_file (str, optional): Path to custom rules CSV; None uses default.
        overwrite (bool): If True, re-categorise existing categories.

    Returns:
        pd.DataFrame: The categorised DataFrame, or empty if no new transactions.
    """
    all_df = pd.DataFrame()
    imported_by_source = {}

    # Step 1-2: Import unprocessed statements for each source
    for src_config in sources:
        path = src_config.get('path')
        source = src_config.get('source')

        # Extract custom params if any, else default
        import_kwargs = {k: v for k, v in src_config.items() if k not in ['path', 'source']}
        import_kwargs['metadata_file'] = metadata_file

        df, imported_files = import_statements(
            path,
            source=source,
            **import_kwargs
        )

        all_df = pd.concat([all_df, df], ignore_index=True)
        imported_by_source[source] = imported_files

    if all_df.empty:
        print("No new transactions to process.")
        return pd.DataFrame()

    # Step 3: Categorise the combined DataFrame
    # Use auto_categorise with optional rules_file (None for default), and other params as needed
    categorised_df = auto_categorise(
        all_df,
        rules_file=rules_file,  # Use None for bundled rules, or specify a path
        overwrite=overwrite,  # Set to True if you want to re-categorise existing categories
        categorised_dir=categorised_dir  # Saves the categorised DF here
    )

    # Step 4: Update metadata to mark imported files as processed
    for source, imported_files in imported_by_source.items():
        update_metadata(imported_files, source, metadata_file=metadata_file)

    return categorised_df