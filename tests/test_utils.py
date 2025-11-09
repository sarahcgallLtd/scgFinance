import pytest
import os
import pandas as pd
from tempfile import TemporaryDirectory
from src.scgFinance.utils import load_package_data, download_template

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

# ================================================
# Tests for download_template
# ================================================

def test_download_template_structure_creation(expected_columns):
    with TemporaryDirectory() as tmpdir:
        download_template(tmpdir)

        # Check directories exist
        assert os.path.isdir(os.path.join(tmpdir, "categorised"))
        assert os.path.isdir(os.path.join(tmpdir, "metadata"))
        assert os.path.isdir(os.path.join(tmpdir, "raw_data", "bank"))
        assert os.path.isdir(os.path.join(tmpdir, "raw_data", "credit_card"))

        # Check raw_data subdirs are empty (no sample files copied)
        assert len(os.listdir(os.path.join(tmpdir, "raw_data", "bank"))) == 0
        assert len(os.listdir(os.path.join(tmpdir, "raw_data", "credit_card"))) == 0

        # Check rules file
        rules_path = os.path.join(tmpdir, "metadata", "rules.csv")
        assert os.path.exists(rules_path)
        df = pd.read_csv(rules_path)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert set(expected_columns['rules']).issubset(df.columns)

        # Check script file
        script_path = os.path.join(tmpdir, "categorise_statements.py")
        assert os.path.exists(script_path)
        with open(script_path, 'r') as f:
            content = f.read()
            assert len(content) > 0  # Basic check that it's not empty

def test_download_template_custom_rules_filename(expected_columns):
    with TemporaryDirectory() as tmpdir:
        custom_filename = "custom_rules.csv"
        download_template(tmpdir, rules_filename=custom_filename)

        # Check custom rules file
        rules_path = os.path.join(tmpdir, "metadata", custom_filename)
        assert os.path.exists(rules_path)
        df = pd.read_csv(rules_path)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert set(expected_columns['rules']).issubset(df.columns)

        # Ensure default rules.csv does not exist
        default_path = os.path.join(tmpdir, "metadata", "rules.csv")
        assert not os.path.exists(default_path)

def test_download_template_print_output(capsys):
    with TemporaryDirectory() as tmpdir:
        download_template(tmpdir)
        captured = capsys.readouterr()
        assert f"Project template saved to: {tmpdir}" in captured.out

def test_download_template_overwrite_existing_files():
    with TemporaryDirectory() as tmpdir:
        # Create a dummy rules file to overwrite
        metadata_dir = os.path.join(tmpdir, "metadata")
        os.makedirs(metadata_dir, exist_ok=True)
        dummy_rules_path = os.path.join(metadata_dir, "rules.csv")
        with open(dummy_rules_path, 'w') as f:
            f.write("dummy content")

        # Run the function
        download_template(tmpdir)

        # Check that the file was overwritten (content should no longer be dummy)
        with open(dummy_rules_path, 'r') as f:
            content = f.read()
            assert content != "dummy content"
            # Optionally, load as DF to confirm it's the expected rules
            from io import StringIO
            df = pd.read_csv(StringIO(content))
            assert not df.empty