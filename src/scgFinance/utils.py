from importlib.resources import files
import pandas as pd


def load_package_data(data_type: str) -> pd.DataFrame:
    """
    Loads bundled package data based on the specified type.

    Args:
        data_type (str): The type of data to load. Options: 'bank' for the sample bank statement,
                         'credit_card' for the sample credit card statement, or 'rules' for the default rules.

    Returns:
        pd.DataFrame: Loaded DataFrame from the specified CSV.

    Raises:
        ValueError: If an invalid data_type is provided.
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