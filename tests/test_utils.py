import pytest
import pandas as pd
from src.scgFinance.utils import load_package_data

@pytest.fixture
def expected_columns():
    return {
        'bank': ['Date', 'Description', 'Amount'],  # Adjust based on actual columns in the sample
        'credit_card': ['Date', 'Description', 'Amount'],  # Adjust as needed
        'rules': ['category', 'subcategory', 'pattern']
    }

def test_load_package_data_bank(expected_columns):
    df = load_package_data('bank')
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert set(expected_columns['bank']).issubset(df.columns)

def test_load_package_data_credit_card(expected_columns):
    df = load_package_data('credit_card')
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert set(expected_columns['credit_card']).issubset(df.columns)

def test_load_package_data_rules(expected_columns):
    df = load_package_data('rules')
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert set(expected_columns['rules']).issubset(df.columns)

def test_load_package_data_invalid_type():
    with pytest.raises(ValueError, match="Invalid data_type 'invalid'"):
        load_package_data('invalid')