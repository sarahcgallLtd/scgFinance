from importlib.resources import files
import pandas as pd
import os


# ================================================
# Main function: for loading sample data
# ================================================


def load_package_data(data_type: str, save_path: str = None) -> pd.DataFrame:
    """
    Loads bundled package data from CSV files based on the specified data type.

    This utility function accesses sample data or metadata files packaged
    within the 'scgFinance' module using importlib.resources. It supports
    loading example bank statements, credit card statements, or default
    categorisation rules. The file paths are resolved dynamically, and the
    contents are read into a pandas DataFrame. This is useful for testing,
    demonstrations, or default configurations without requiring external
    file access.

    Optionally, if a save_path is provided, the loaded DataFrame will be
    saved as a CSV file to the specified local path on the user's computer.

    Args:
        data_type (str): The type of data to load. Valid options are:
            - 'bank': Loads the sample bank statement from
                      'scgFinance.data.raw_data.bank/251031
                      Example Bank Statement.csv'.
            - 'credit_card': Loads the sample credit card statement from
                             'scgFinance.data.raw_data.credit_card/251031
                             Example Credit Card Statement.csv'.
            - 'rules': Loads the default categorisation rules from
                       'scgFinance.data.metadata/rules.csv'.
        save_path (str, optional): The local file path where the loaded
                                   DataFrame should be saved as a CSV.
                                   If None (default), no save operation
                                   is performed.

    Returns:
        pd.DataFrame: A DataFrame containing the loaded data from the specified
                      CSV file.

    Raises:
        ValueError: If an invalid 'data_type' is provided (not one of 'bank',
                    'credit_card', or 'rules').
        FileNotFoundError: If the bundled file is missing (though this should
                           not occur in a properly packaged module).
        pandas.errors: If there are issues parsing the CSV file.
        OSError: If there are issues saving to the provided save_path (e.g.,
                 invalid directory or permissions issues).

    Example:
        >>> bank_df = load_package_data('bank',
        ... save_path='~/Desktop/bank_data.csv')
        >>> print(bank_df.columns)
        Index(['Date', 'Description', 'Amount'], dtype='object')
        # Example columns; data is also saved to '~/Desktop/bank_data.csv'

        >>> rules_df = load_package_data('rules')
        >>> print(rules_df.head())
          category subcategory pattern
        0  Food/Dining   Groceries   TESCO
        ...
    """
    # Get bank statement example
    if data_type == "bank":
        file_path = files("scgFinance.data.raw_data.bank").joinpath(
            "251031 Example Bank Statement.csv"
        )

    # Get credit card statement example
    elif data_type == "credit_card":
        file_path = files("scgFinance.data.raw_data.credit_card").joinpath(
            "251031 Example Credit Card Statement.csv"
        )

    # Get default rules
    elif data_type == "rules":
        file_path = files("scgFinance.data.metadata").joinpath("rules.csv")
    else:
        raise ValueError(
            f"Invalid data_type '{data_type}'. "
            f"Options: 'bank', 'credit_card', 'rules'."
        )

    df = pd.read_csv(str(file_path))

    if save_path:
        df.to_csv(save_path, index=False)

    return df


# ================================================
# Main function: for saving template structure
# ================================================


def download_template(
    root_dir: str = '.',
    rules_filename: str = "rules.csv",
) -> None:
    """
    Saves a predefined project structure to the specified root directory,
    populating it with metadata and a template script from the package.

    This function creates the following directory structure:
    - root_dir/
      - categorised/ (empty directory)
      - metadata/
        - rules.csv (or specified filename; default categorisation rules)
      - raw_data/
        - bank/ (empty directory to save bank statements)
        - credit_card/ (empty directory to save credit card statements)
      - categorise_statements.py (template script copied from package)

    Directories are created if they do not exist, and files are overwritten
    if they already exist. The sample data and template script are copied
    directly from the package resources to preserve original formatting.
    This is useful for setting up a new project with a standard template,
    improving ease of access by allowing users to initialise a local
    working directory with bundled examples. The rules.csv can be customised
    to be more specific to your financial statements. The
    categorise_statements.py is bundled in the package (e.g., at '
    scgFinance.data/categorise_statements.py') and copied to the root
    directory. Users can customise it after the template is saved.

    Args:
        root_dir (str): The path to the root directory where the structure
                        will be saved. Defaults to '.' (current working
                        directory).
        rules_filename (str, optional): The filename for the rules CSV in
                                        metadata/. Defaults to "rules.csv"
                                        to match the requested structure.

    Returns:
        None

    Raises:
        OSError: If there are issues creating directories or writing files.
        ImportError or AttributeError: If issues occur accessing package
                                       resources.

    Example:
        >>> download_template('/path/to/my_project')
        # Creates the structure in /path/to/my_project

        >>> donwload_template('/path/to/my_project',
        ... rules_filename='custom_rules.csv')
        # Uses 'custom_rules.csv' instead of 'rules.csv'
    """
    # Create directories
    os.makedirs(os.path.join(root_dir, "categorised"), exist_ok=True)

    metadata_dir = os.path.join(root_dir, "metadata")
    os.makedirs(metadata_dir, exist_ok=True)

    raw_data_dir = os.path.join(root_dir, "raw_data")
    bank_dir = os.path.join(raw_data_dir, "bank")
    os.makedirs(bank_dir, exist_ok=True)

    credit_card_dir = os.path.join(raw_data_dir, "credit_card")
    os.makedirs(credit_card_dir, exist_ok=True)

    # Copy data directly
    rules_file_path = files("scgFinance.data.metadata").joinpath("rules.csv")
    rules_target = os.path.join(metadata_dir, rules_filename)
    with rules_file_path.open("rb") as src, open(rules_target, "wb") as dst:
        dst.write(src.read())

    # Copy categorise_statements.py template directly from package
    script_file_path = files("scgFinance.data").joinpath(
        "categorise_statements.py"
    )
    script_target = os.path.join(root_dir, "categorise_statements.py")
    with script_file_path.open("rb") as src, open(script_target, "wb") as dst:
        dst.write(src.read())

    print(f"Project template saved to: {root_dir}")
