import pytest
import pandas as pd
import os
from datetime import datetime
from src.scgFinance.pipeline import _update_metadata, process_statements


# Fixture for temporary directory
@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


# Fixture for sample metadata CSV
@pytest.fixture
def sample_metadata(temp_dir):
    metadata_path = temp_dir / "processed_files.csv"
    data = {
        'file_name': ['old_bank.csv', 'old_cc.csv'],
        'source': ['bank', 'credit_card'],
        'status': ['processed', 'processed'],
        'process_date': ['2025-11-01 12:00:00', '2025-11-01 12:00:00']
    }
    df = pd.DataFrame(data)
    df.to_csv(metadata_path, index=False)
    return str(metadata_path)


# Fixture for sample bank statements directory and files
@pytest.fixture
def sample_bank_dir(temp_dir):
    bank_dir = temp_dir / "bank"
    os.makedirs(bank_dir, exist_ok=True)
    file1 = bank_dir / "new_bank1.csv"
    data1 = {
        'Date': ['01/10/2025'],
        'Description': ['TESCO'],
        'Amount': ['50.00']
    }
    pd.DataFrame(data1).to_csv(file1, index=False)

    file2 = bank_dir / "new_bank2.csv"
    data2 = {
        'Date': ['07/10/2025'],
        'Description': ['STARBUCKS'],
        'Amount': ['5.50']
    }
    pd.DataFrame(data2).to_csv(file2, index=False)

    return str(bank_dir)


# Fixture for sample credit card statements directory and files
@pytest.fixture
def sample_cc_dir(temp_dir):
    cc_dir = temp_dir / "credit_card"
    os.makedirs(cc_dir, exist_ok=True)
    file = cc_dir / "new_cc.csv"
    data = {
        'Date': ['14/10/2025'],
        'Description': ['AMAZON'],
        'Amount': ['20.00']
    }
    pd.DataFrame(data).to_csv(file, index=False)
    return str(cc_dir)


# Fixture for sample rules file (for categoriser)
@pytest.fixture
def sample_rules_file(temp_dir):
    rules_path = temp_dir / "rules.csv"
    rules_data = '''category,subcategory,pattern
Food/Dining,Groceries,TESCO
Food/Dining,Restaurants/Bars,STARBUCKS
Shopping,Online,AMAZON
'''
    with open(rules_path, 'w') as f:
        f.write(rules_data)
    return str(rules_path)


# Fixture for categorised directory (empty for tests)
@pytest.fixture
def sample_categorised_dir(temp_dir):
    cat_dir = temp_dir / "categorised"
    os.makedirs(cat_dir, exist_ok=True)
    return str(cat_dir)


# TESTS FOR UPDATE_METADATA() =========================================================================================
def test_update_metadata_add_new(temp_dir, sample_metadata):
    imported_files = ['new_file.csv']
    source = 'bank'
    _update_metadata(imported_files, source, metadata_file=sample_metadata)

    meta_df = pd.read_csv(sample_metadata)
    assert len(meta_df) == 3  # Original 2 + 1 new
    new_row = meta_df[meta_df['file_name'] == 'new_file.csv']
    assert not new_row.empty
    assert new_row['source'].values[0] == 'bank'
    assert new_row['status'].values[0] == 'processed'
    # Check process_date is recent (within last minute)
    process_date = datetime.strptime(new_row['process_date'].values[0], '%Y-%m-%d %H:%M:%S')
    assert (datetime.now() - process_date).total_seconds() < 60


def test_update_metadata_update_existing(temp_dir, sample_metadata):
    imported_files = ['old_bank.csv']
    source = 'bank'
    _update_metadata(imported_files, source, metadata_file=sample_metadata, status='reprocessed')

    meta_df = pd.read_csv(sample_metadata)
    assert len(meta_df) == 2  # No new rows
    updated_row = meta_df[meta_df['file_name'] == 'old_bank.csv']
    assert updated_row['status'].values[0] == 'reprocessed'
    # Check process_date updated
    process_date = datetime.strptime(updated_row['process_date'].values[0], '%Y-%m-%d %H:%M:%S')
    assert (datetime.now() - process_date).total_seconds() < 60


def test_update_metadata_empty_list(sample_metadata):
    imported_files = []
    source = 'bank'
    _update_metadata(imported_files, source, metadata_file=sample_metadata)
    meta_df = pd.read_csv(sample_metadata)
    assert len(meta_df) == 2  # Unchanged


def test_update_metadata_new_file(temp_dir):
    metadata_path = str(temp_dir / "new_metadata.csv")
    imported_files = ['file1.csv']
    source = 'test'
    _update_metadata(imported_files, source, metadata_file=metadata_path)

    assert os.path.exists(metadata_path)
    meta_df = pd.read_csv(metadata_path)
    assert len(meta_df) == 1
    assert meta_df['file_name'].values[0] == 'file1.csv'


# TESTS FOR PROCESS_STATEMENTS() ======================================================================================
def test_process_statements_multiple_sources(sample_bank_dir, sample_cc_dir, sample_metadata, sample_rules_file,
                                             sample_categorised_dir):
    sources = [
        {'path': sample_bank_dir, 'source': 'bank', 'date_col': 'Date', 'date_format': '%d/%m/%Y',
         'desc_col': 'Description', 'amt_col': 'Amount'},
        {'path': sample_cc_dir, 'source': 'credit_card', 'date_col': 'Date', 'date_format': '%d/%m/%Y',
         'desc_col': 'Description', 'amt_col': 'Amount'}
    ]
    categorised_df = process_statements(
        sources,
        metadata_file=sample_metadata,
        categorised_dir=sample_categorised_dir,
        rules_file=sample_rules_file,
        overwrite=False
    )

    assert not categorised_df.empty
    assert len(categorised_df) == 3  # 2 from bank + 1 from cc
    assert 'category' in categorised_df.columns
    assert 'subcategory' in categorised_df.columns
    assert 'review' in categorised_df.columns

    # Check categorisation (based on sample rules)
    tesco_row = categorised_df[categorised_df['description'] == 'TESCO']
    assert tesco_row['category'].values[0] == 'Food/Dining'
    assert tesco_row['subcategory'].values[0] == 'Groceries'

    # Check metadata updated
    meta_df = pd.read_csv(sample_metadata)
    assert len(meta_df) == 5  # Original 2 + 3 new (new_bank1, new_bank2, new_cc)
    assert 'new_bank1.csv' in meta_df['file_name'].values
    assert meta_df[meta_df['file_name'] == 'new_bank1.csv']['status'].values[0] == 'processed'

    # Check categorised saved (at least one file in categorised_dir)
    cat_files = os.listdir(sample_categorised_dir)
    assert len(cat_files) > 0


def test_process_statements_no_new_transactions(sample_bank_dir, sample_metadata, sample_rules_file,
                                                sample_categorised_dir):
    # Mark the files as processed in metadata
    meta_df = pd.read_csv(sample_metadata)
    new_rows = pd.DataFrame({
        'file_name': ['new_bank1.csv', 'new_bank2.csv'],
        'source': ['bank', 'bank'],
        'status': ['processed', 'processed'],
        'process_date': ['2025-11-01 12:00:00', '2025-11-01 12:00:00']
    })
    meta_df = pd.concat([meta_df, new_rows], ignore_index=True)
    meta_df.to_csv(sample_metadata, index=False)

    sources = [
        {'path': sample_bank_dir, 'source': 'bank', 'date_col': 'Date', 'date_format': '%d/%m/%Y',
         'desc_col': 'Description', 'amt_col': 'Amount'}
    ]
    categorised_df = process_statements(
        sources,
        metadata_file=sample_metadata,
        categorised_dir=sample_categorised_dir,
        rules_file=sample_rules_file
    )

    assert categorised_df.empty


def test_process_statements_overwrite(sample_bank_dir, sample_metadata, sample_rules_file, sample_categorised_dir):
    sources = [
        {'path': sample_bank_dir, 'source': 'bank', 'date_col': 'Date', 'date_format': '%d/%m/%Y',
         'desc_col': 'Description', 'amt_col': 'Amount'}
    ]
    # First run without overwrite
    process_statements(sources, metadata_file=sample_metadata, categorised_dir=sample_categorised_dir,
                       rules_file=sample_rules_file, overwrite=False)

    # Modify a categorised file to have pre-existing category (simulate overwrite need)
    cat_files = os.listdir(sample_categorised_dir)
    if cat_files:
        cat_path = os.path.join(sample_categorised_dir, cat_files[0])
        cat_df = pd.read_csv(cat_path)
        cat_df['category'] = 'OldCategory'  # Set existing category
        cat_df.to_csv(cat_path, index=False)

    # Re-run with overwrite=True (but since files processed, need to reset metadata for re-import)
    meta_df = pd.read_csv(sample_metadata)
    meta_df = meta_df[~meta_df['file_name'].str.contains('new_bank')]  # Remove to allow re-import
    meta_df.to_csv(sample_metadata, index=False)

    categorised_df = process_statements(
        sources,
        metadata_file=sample_metadata,
        categorised_dir=sample_categorised_dir,
        rules_file=sample_rules_file,
        overwrite=True
    )
    # Check if categories overwritten (based on rules, should be Food/Dining, not OldCategory)
    assert 'OldCategory' not in categorised_df['category'].values


def test_process_statements_missing_source():
    sources = [{'path': 'dummy'}]  # No 'source'
    with pytest.raises(ValueError, match="Source must be specified"):
        process_statements(sources) # triggered in import_statement


def test_process_statements_missing_path():
    sources = [{'source': 'dummy'}]  # No 'path'
    with pytest.raises(ValueError, match="Path must be specified"):
        process_statements(sources) # triggered in import_statement


def test_process_statements_missing_date(sample_bank_dir):
    sources = [
        {'path': sample_bank_dir, 'source': 'bank', 'date_col': 'IncorrectName', 'date_format': '%d/%m/%Y',
         'desc_col': 'Description', 'amt_col': 'Amount'}
    ]
    with pytest.raises(ValueError, match="Date column 'IncorrectName' not found in"):
        process_statements(sources) # triggered in process_single_file

def test_process_statements_missing_desc(sample_bank_dir):
    sources = [
        {'path': sample_bank_dir, 'source': 'bank', 'date_col': 'Date', 'date_format': '%d/%m/%Y',
         'desc_col': 'IncorrectName', 'amt_col': 'Amount'}
    ]
    with pytest.raises(ValueError, match="Description column"):
        process_statements(sources) # triggered in process_single_file

def test_process_statements_missing_amount(sample_bank_dir):
    sources = [
        {'path': sample_bank_dir, 'source': 'bank', 'date_col': 'Date', 'date_format': '%d/%m/%Y',
         'desc_col': 'Description', 'amt_col': 'IncorrectName'}
    ]
    with pytest.raises(ValueError, match="Amount column 'IncorrectName' not found in"):
        process_statements(sources) # triggered in process_single_file
