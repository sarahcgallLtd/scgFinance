from .importers import import_statements
from .categoriser import auto_categorise
import pandas as pd
import os
from datetime import datetime


# ================================================
# Helper function: for tracking
# ================================================


def _update_metadata(
        imported_files,
        source,
        metadata_file="metadata/processed_files.csv",
        status="processed",
):
    """
    Updates the metadata CSV file with the processing status and timestamp for
    the specified imported files.

    This function loads the existing metadata DataFrame or creates a new one if
    it does not exist. For each imported file, it checks if an entry already
    exists for that file and source; if so, it updates the status and process
    date; otherwise, it adds a new row. The updated metadata is then saved back
    to the CSV file.

    Args:
        imported_files (list): A list of base file names (e.g.,
                               'statement.csv') that were successfully
                               imported.
        source (str): The source identifier (e.g., 'bank', 'credit_card')
                      for the files.
        metadata_file (str, optional): Path to the metadata CSV file. Defaults
                                       to 'metadata/processed_files.csv'.
        status (str, optional): The status to set for the files (e.g.,
                                'processed', 'reprocessed'). Defaults to
                                'processed'.

    Returns:
        None

    Raises:
        pandas.errors: If there are issues reading or writing the CSV file.

    Example:
        >>> imported_files = ['statement1.csv', 'statement2.csv']
        >>> _update_metadata(imported_files, 'bank', 'my_metadata.csv')
        Updated metadata for 2 files with status 'processed'.
    """
    if not imported_files:
        return

    # Ensure the directory for the metadata file exists
    if os.path.exists(metadata_file):
        meta_df = pd.read_csv(metadata_file)
    else:
        meta_df = pd.DataFrame(
            columns=["file_name", "source", "status", "process_date"]
        )

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Load existing metadata or create new if it doesn't exist
    for file_name in imported_files:
        mask = (meta_df["file_name"] == file_name) & (
                meta_df["source"] == source
        )
        if mask.any():
            meta_df.loc[mask, "status"] = status
            meta_df.loc[mask, "process_date"] = current_time
        else:
            new_row = {
                "file_name": file_name,
                "source": source,
                "status": status,
                "process_date": current_time,
            }
            meta_df = pd.concat(
                [meta_df, pd.DataFrame([new_row])], ignore_index=True
            )

    # Save updated metadata
    meta_df.to_csv(metadata_file, index=False)
    print(
        f"Updated metadata for {len(imported_files)} files with status "
        f"'{status}'."
    )


# ================================================
# Main function: process_statements
# ================================================


def process_statements(
        sources,
        metadata_file="metadata/processed_files.csv",
        categorised_file="categorised/",
        add_col=None,
        rules_file=None
):
    """
    Orchestrates the full financial statement processing pipeline: importing,
    categorising, updating metadata, and appending results to a single file.

    This function processes statements from multiple sources by importing
    unprocessed files, combining them into a single DataFrame, applying
    automatic categorisation, updating the metadata to mark files as
    processed, and returning the categorised DataFrame. If no new transactions
    are found, an empty or original DataFrame is returned. Custom import
    parameters can be provided per source.

    Args:
        sources (list of dict): A list of dictionaries, each specifying a
                                source configuration:
            - 'path' (str): Path to the file or directory of CSV statements.
            - 'source' (str): Identifier for the source (e.g., 'Lloyds',
                              'HSBC').
            - Optional keys: 'date_col', 'date_format', 'time_col',
                             'time_format', 'desc_col', 'amt_col' for
                             custom import settings.
        metadata_file (str, optional): Path to the metadata CSV for tracking
                                       processed files. Defaults to
                                       'metadata/processed_files.csv'.
        categorised_file (str, optional): Path to the categorised CSV file for
                                          loading and appending. Defaults to
                                          'categorised.csv'
        add_col (str, optional): Add personalised column(s) to dataset (e.g.,
                                 to manually flag reimbursement expenses).
                                 Defaults to 'None'.
        rules_file (str, optional): Path to a custom rules CSV for
                                    categorisation; None uses the default
                                    bundled rules.

    Returns:
        pd.DataFrame: The combined and categorised DataFrame, or an empty
                      DataFrame if no new transactions were processed.

    Raises:
        ValueError: If 'path' or 'source' is missing in any source
                    configuration, or if columns are not found during import.
        Other exceptions: Propagated from import_statements() or
                          auto_categorise(), such as FileNotFoundError for
                          rules_file.

    Example:
        >>> sources = [
        ...     {'path': 'bank_statements/', 'source': 'bank',
        ...     'date_col': 'Date', 'date_format': '%d/%m/%Y',
        ...      'desc_col': 'Description', 'amt_col': 'Amount'}
        ... ]
        >>> df = process_statements(sources, rules_file='custom_rules.csv')
        >>> print(df.shape)
        (10, 7)  # Example assuming 10 transactions processed with 7 columns
    """
    all_df = pd.DataFrame()
    imported_by_source = {}

    # Step 1-2: Import unprocessed statements for each source
    for src_config in sources:
        path = src_config.get("path")
        source = src_config.get("source")

        # Extract custom params if any, else default
        import_kwargs = {
            k: v for k, v in src_config.items() if k not in ["path", "source"]
        }
        import_kwargs["metadata_file"] = metadata_file

        df, imported_files = import_statements(
            path, source=source, **import_kwargs
        )

        all_df = pd.concat([all_df, df], ignore_index=True)
        imported_by_source[source] = imported_files

    if all_df.empty:
        print("No new transactions to process.")
        return pd.DataFrame()

    # Step 3: Categorise the combined DataFrame
    # Use auto_categorise with optional rules_file (None for default),
    # and other params as needed
    categorised_df = auto_categorise(
        all_df,
        rules_file=rules_file,
        categorised_file=categorised_file,
    )

    # Step 4: Update metadata to mark imported files as processed
    for source, imported_files in imported_by_source.items():
        _update_metadata(imported_files, source, metadata_file=metadata_file)

    return categorised_df
