from importlib.resources import files
import pandas as pd


def load_package_data(data_type: str) -> pd.DataFrame:
    """
    Loads bundled package data from CSV files based on the specified data type.

    This utility function accesses sample data or metadata files packaged within the 'scgFinance' module using importlib.resources.
    It supports loading example bank statements, credit card statements, or default categorisation rules. The file paths are resolved
    dynamically, and the contents are read into a pandas DataFrame. This is useful for testing, demonstrations, or default configurations
    without requiring external file access.

    Args:
        data_type (str): The type of data to load. Valid options are:
            - 'bank': Loads the sample bank statement from 'scgFinance.data.raw_data.bank/251031 Example Bank Statement.csv'.
            - 'credit_card': Loads the sample credit card statement from 'scgFinance.data.raw_data.credit_card/251031 Example Credit Card Statement.csv'.
            - 'rules': Loads the default categorisation rules from 'scgFinance.data.metadata/rules.csv'.

    Returns:
        pd.DataFrame: A DataFrame containing the loaded data from the specified CSV file.

    Raises:
        ValueError: If an invalid 'data_type' is provided (not one of 'bank', 'credit_card', or 'rules').
        FileNotFoundError: If the bundled file is missing (though this should not occur in a properly packaged module).
        pandas.errors: If there are issues parsing the CSV file.

    Example:
        >>> bank_df = load_package_data('bank')
        >>> print(bank_df.columns)
        Index(['Date', 'Description', 'Amount'], dtype='object')  # Example columns

        >>> rules_df = load_package_data('rules')
        >>> print(rules_df.head())
          category subcategory pattern
        0  Food/Dining   Groceries   TESCO
        ...
    """
    # Get bank statement example
    if data_type == 'bank':
        file_path = files('scgFinance.data.raw_data.bank').joinpath('251031 Example Bank Statement.csv')

    # Get credit card statement example
    elif data_type == 'credit_card':
        file_path = files('scgFinance.data.raw_data.credit_card').joinpath('251031 Example Credit Card Statement.csv')

    # Get default rules
    elif data_type == 'rules':
        file_path = files('scgFinance.data.metadata').joinpath('rules.csv')
    else:
        raise ValueError(f"Invalid data_type '{data_type}'. Options: 'bank', 'credit_card', 'rules'.")

    return pd.read_csv(str(file_path))