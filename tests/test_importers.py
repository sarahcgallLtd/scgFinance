import os
import pandas as pd
import pytest
from src.scgFinance.importers import (
    _load_metadata,
    _filter_unprocessed_files,
    _process_single_file,
    import_statements
)


# Fixture to create a temporary directory and files for testing
@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

# Fixture for sample bank CSV
@pytest.fixture
def sample_bank_csv(temp_dir):
    bank_dir = temp_dir / "bank"
    os.makedirs(bank_dir, exist_ok=True)
    file_path = bank_dir / "251031_Example_Bank_Statement.csv"
    data = {
        'Date': ['01/10/2025', '07/10/2025'],
        'Time': ['08:56:01', '11:33:54'],
        'Name': ['TESCO', 'STARBUCKS'],
        'Description': ['Groceries', 'Coffee'],
        'Amount': ['50.00', '5.50']
    }
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    return str(file_path), str(bank_dir)

@pytest.fixture
def sample_credit_card_csv(temp_dir):
    cc_dir = temp_dir / "credit_card"
    os.makedirs(cc_dir, exist_ok=True)
    file_path = cc_dir / "251031_Example_Credit_Card_Statement.csv"
    data = {
        'Date': ['01/10/2025', '14/10/2025'],
        'Description': ['AMAZON', 'NETFLIX'],
        'Amount': ['20.00', '10.00']
    }
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    return str(file_path), str(cc_dir)


@pytest.fixture
def sample_metadata(temp_dir):
    metadata_path = temp_dir / "processed_files.csv"
    data = {
        'file_name': ['old_file.csv'],
        'source': ['bank'],
        'status': ['processed'],
        'process_date': ['2025-11-01 12:00:00']
    }
    df = pd.DataFrame(data)
    df.to_csv(metadata_path, index=False)
    return str(metadata_path)

# Additional fixture for a sample CSV with currency symbols in amount
@pytest.fixture
def sample_dirty_amount_csv(temp_dir):
    dir_path = temp_dir / "dirty"
    os.makedirs(dir_path, exist_ok=True)
    file_path = dir_path / "dirty_amount.csv"
    data = {
        'Date': ['2025-10-01'],
        'Description': ['Test'],
        'Amount': ['$1,234.56']
    }
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    return str(file_path)

# TEST FOR LOAD_METADATA() =============================================================================================
def test_load_metadata_new_file(temp_dir):
    metadata_path = str(temp_dir / "new_metadata.csv")
    meta_df = _load_metadata(metadata_path)
    assert os.path.exists(metadata_path)
    assert list(meta_df.columns) == ['file_name', 'source', 'status', 'process_date']
    assert meta_df.empty

def test_load_metadata_existing_file(sample_metadata):
    meta_df = _load_metadata(sample_metadata)
    assert not meta_df.empty
    assert meta_df['file_name'].iloc[0] == 'old_file.csv'
    assert meta_df['source'].iloc[0] == 'bank'
    assert meta_df['status'].iloc[0] == 'processed'

# TEST FOR FILTER_UNPROCESSED_FILES() ==================================================================================
def test_filter_unprocessed_files_directory(sample_bank_csv, sample_metadata):
    _, bank_dir = sample_bank_csv
    meta_df = _load_metadata(sample_metadata)
    unprocessed = _filter_unprocessed_files(bank_dir, 'bank', meta_df)
    assert len(unprocessed) == 1
    assert os.path.basename(unprocessed[0]) == '251031_Example_Bank_Statement.csv'

def test_filter_unprocessed_files_single_file(sample_bank_csv, sample_metadata):
    file_path, _ = sample_bank_csv
    meta_df = _load_metadata(sample_metadata)
    unprocessed = _filter_unprocessed_files(file_path, 'bank', meta_df)
    assert len(unprocessed) == 1
    assert unprocessed[0] == file_path

def test_filter_unprocessed_files_processed(sample_bank_csv, temp_dir):
    file_path, bank_dir = sample_bank_csv
    metadata_path = str(temp_dir / "processed_metadata.csv")
    meta_data = {
        'file_name': ['251031_Example_Bank_Statement.csv'],
        'source': ['bank'],
        'status': ['processed'],
        'process_date': ['2025-11-01 12:00:00']
    }
    meta_df = pd.DataFrame(meta_data)
    meta_df.to_csv(metadata_path, index=False)
    meta_df = _load_metadata(metadata_path)
    unprocessed = _filter_unprocessed_files(bank_dir, 'bank', meta_df)
    assert len(unprocessed) == 0

def test_filter_unprocessed_files_no_files(temp_dir, sample_metadata):
    empty_dir = str(temp_dir / "empty")
    os.makedirs(empty_dir, exist_ok=True)
    meta_df = _load_metadata(sample_metadata)
    with pytest.raises(ValueError, match="No CSV files found in directory"):
        _filter_unprocessed_files(empty_dir, 'bank', meta_df)

# TEST FOR PROCESS_SINGLE_FILE() =======================================================================================
def test_process_single_file_bank(sample_bank_csv):
    file_path, _ = sample_bank_csv
    df = _process_single_file(file_path, 'bank', date_col='Date', date_format='%d/%m/%Y',
                             time_col='Time', time_format='%H:%M:%S', desc_col=['Name', 'Description'],
                             amt_col='Amount')
    assert list(df.columns) == ['date', 'description', 'amount', 'source']
    assert len(df) == 2
    assert df['date'].iloc[0] == pd.to_datetime('2025-10-01 08:56:01')
    assert df['description'].iloc[0] == 'TESCO Groceries'
    assert df['amount'].iloc[0] == 50.00
    assert df['source'].iloc[0] == 'bank'

def test_process_single_file_credit_card(sample_credit_card_csv):
    file_path, _ = sample_credit_card_csv
    df = _process_single_file(file_path, 'credit_card', date_col='Date', date_format='%d/%m/%Y',
                             time_col=None, time_format=None, desc_col='Description', amt_col='Amount')
    assert len(df) == 2
    assert df['date'].iloc[0] == pd.to_datetime('2025-10-01')
    assert df['description'].iloc[0] == 'AMAZON'
    assert df['amount'].iloc[0] == 20.00
    assert df['source'].iloc[0] == 'credit_card'

def test_process_single_file_dirty_amount(sample_dirty_amount_csv):
    df = _process_single_file(sample_dirty_amount_csv, 'test', date_col='Date', date_format='%Y-%m-%d',
                             time_col=None, time_format=None, desc_col='Description', amt_col='Amount')
    assert df['amount'].iloc[0] == 1234.56

def test_process_single_file_missing_column(sample_bank_csv):
    file_path, _ = sample_bank_csv
    with pytest.raises(ValueError, match="Date column 'MissingDate' not found"):
        _process_single_file(file_path, 'bank', date_col='MissingDate', date_format='%d/%m/%Y',
                            time_col='Time', time_format='%H:%M:%S', desc_col='Description', amt_col='Amount')

def test_process_single_file_invalid_data(sample_bank_csv):
    file_path, _ = sample_bank_csv
    # Modify the CSV to have invalid date
    df = pd.read_csv(file_path)
    df.loc[0, 'Date'] = 'invalid'
    df.to_csv(file_path, index=False)
    processed_df = _process_single_file(file_path, 'bank', date_col='Date', date_format='%d/%m/%Y',
                                       time_col='Time', time_format='%H:%M:%S', desc_col='Description',
                                       amt_col='Amount')
    assert len(processed_df) == 1  # One row dropped due to invalid date

# TEST FOR IMPORT_STATEMENTS() =========================================================================================
def test_import_statements_directory(sample_bank_csv, temp_dir):
    _, bank_dir = sample_bank_csv
    metadata_path = str(temp_dir / "import_metadata.csv")
    combined_df, imported_files = import_statements(bank_dir, source='bank', metadata_file=metadata_path)
    assert len(combined_df) == 2
    assert len(imported_files) == 1
    assert imported_files[0] == '251031_Example_Bank_Statement.csv'
    assert 'source' in combined_df.columns
    assert combined_df['source'].unique() == ['bank']

def test_import_statements_single_file(sample_credit_card_csv, temp_dir):
    file_path, _ = sample_credit_card_csv
    metadata_path = str(temp_dir / "import_metadata.csv")
    combined_df, imported_files = import_statements(file_path, source='credit_card', metadata_file=metadata_path)
    assert len(combined_df) == 2
    assert len(imported_files) == 1

def test_import_statements_no_unprocessed(sample_bank_csv, temp_dir):
    _, bank_dir = sample_bank_csv
    metadata_path = str(temp_dir / "full_metadata.csv")
    meta_data = {
        'file_name': ['251031_Example_Bank_Statement.csv'],
        'source': ['bank'],
        'status': ['processed'],
        'process_date': ['2025-11-01 12:00:00']
    }
    meta_df = pd.DataFrame(meta_data)
    meta_df.to_csv(metadata_path, index=False)
    combined_df, imported_files = import_statements(bank_dir, source='bank', metadata_file=metadata_path)
    assert combined_df.empty
    assert imported_files == []

def test_import_statements_no_source():
    with pytest.raises(ValueError, match="Source must be specified"):
        import_statements('dummy_path')

def test_import_statements_sort_by_date(sample_bank_csv, sample_credit_card_csv, temp_dir):
    # Create a mixed dir with both files
    mixed_dir = temp_dir / "mixed"
    os.makedirs(mixed_dir, exist_ok=True)
    bank_file = sample_bank_csv[0]
    cc_file = sample_credit_card_csv[0]
    # Copy files to mixed_dir
    import shutil
    shutil.copy(bank_file, mixed_dir)
    shutil.copy(cc_file, mixed_dir)
    metadata_path = str(temp_dir / "mixed_metadata.csv")
    # But since source different, need same source for test, or separate calls
    # For this test, assume same source, but adjust dates
    combined_df, _ = import_statements(str(mixed_dir), source='mixed', metadata_file=metadata_path, desc_col='Description')
    assert combined_df['date'].is_monotonic_increasing