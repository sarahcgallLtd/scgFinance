import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
import re
from io import StringIO
from datetime import datetime, timedelta
from src.scgFinance.categoriser import (
    _load_rules_file,
    _load_categorised,
    _train_model,
    _get_ml_model,
    _apply_ml,
    _compile_rules,
    _apply_rules_to_row,
    _detect_conflicts,
    _save_categorised,
    auto_categorise
)

# Sample data
SAMPLE_RULES_CSV = '''category,subcategory,pattern
Food/Dining,Groceries,TESCO
Food/Dining,Restaurants/Bars,MCDONALDS
Transportation,Public Transport,TRAINLINE.COM
Transportation,Rideshare,UBER TRIP
Transportation,Rideshare,BOLT
Home,Maintenance,B&Q
'''

SAMPLE_CATEGORISED_CSV = '''date,description,amount,category,subcategory,added_at
2025-10-01,TRAINLINE.COM LONDON,22.89,Transportation,Public Transport,2025-01-01 00:00:00
2025-10-07,DELIVEROO LONDON,19.37,Food/Dining,Takeaway/Delivery,2025-01-01 00:00:00
2025-10-08,B&Q CHELMSFORD,5.0,Home,Maintenance,2025-01-01 00:00:00
2025-10-09,UBER TRIP HTTPS://HELP.UB,7.54,Transportation,Rideshare,2025-01-01 00:00:00
2025-10-10,BOLT LONDON,39.93,Transportation,Rideshare,2025-01-01 00:00:00
2025-10-11,TESCO,15.25,Food/Dining,Groceries,2025-01-01 00:00:00
2025-10-12,MCDONALDS,8.99,Food/Dining,Restaurants/Bars,2025-01-01 00:00:00
2025-10-13,MCDONALDS,8.99,Food/Dining,Restaurants/Bars,2025-01-01 00:00:00
2025-10-15,DELIVEROO LONDON,19.37,Food/Dining,Takeaway/Delivery,2025-01-01 00:00:00
2025-10-20,TRAINLINE.COM LONDON,22.89,Transportation,Public Transport,2025-01-01 00:00:00
'''

SAMPLE_DF_DATA = {
    'date': ['2025-10-01', '2025-10-07', '2025-10-14', '2025-10-15', '2025-10-29'],
    'description': ['TRAINLINE.COM LONDON', 'DELIVEROO LONDON', 'B&Q CHELMSFORD', 'UBER TRIP HTTPS://HELP.UB', 'BOLT LONDON'],
    'amount': [22.89, 19.37, 5.0, 7.54, 39.93]
}
SAMPLE_DF = pd.DataFrame(SAMPLE_DF_DATA)

@pytest.fixture
def sample_rules_file(tmp_path):
    p = tmp_path / "rules.csv"
    p.write_text(SAMPLE_RULES_CSV)
    return str(p)

@pytest.fixture
def empty_rules_file(tmp_path):
    p = tmp_path / "empty_rules.csv"
    p.write_text("category,subcategory,pattern\n")
    return str(p)

@pytest.fixture
def bad_rules_file(tmp_path):
    p = tmp_path / "bad_rules.csv"
    p.write_text("category,subcategory\n")
    return str(p)

@pytest.fixture
def rules_file_with_empty_pattern(tmp_path):
    p = tmp_path / "rules_with_empty.csv"
    content = '''category,subcategory,pattern
Food/Dining,Groceries,TESCO
Food/Dining,Restaurants/Bars,
Transportation,Public Transport,""
Transportation,Rideshare,UBER TRIP
'''
    p.write_text(content)
    return str(p)

@pytest.fixture
def sample_categorised_file(tmp_path):
    p = tmp_path / "categorised.csv"
    p.write_text(SAMPLE_CATEGORISED_CSV)
    return str(p)

@pytest.fixture
def empty_categorised_file(tmp_path):
    p = tmp_path / "empty_categorised.csv"
    return str(p)

@pytest.fixture
def no_categorised_file(tmp_path):
    return str(tmp_path / "non_existent.csv")

@pytest.fixture
def hybrid_categorised_file(tmp_path):
    sample_csv = StringIO(SAMPLE_CATEGORISED_CSV)
    hist_df = pd.read_csv(sample_csv)  # Now 7 unique rows
    base_date = datetime(2025, 10, 1)
    dfs = []
    for i in range(3):  # 3 * 7 = 21 rows, all unique dates
        df_copy = hist_df.copy()
        df_copy['date'] = [(base_date + timedelta(days=i * len(hist_df) + j)).strftime('%Y-%m-%d') for j in range(len(hist_df))]
        dfs.append(df_copy)
    repeated_df = pd.concat(dfs, ignore_index=True)
    p = tmp_path / "hybrid.csv"
    repeated_df.to_csv(p, index=False)
    return str(p)

@pytest.fixture
def full_ml_categorised_file(tmp_path):
    sample_csv = StringIO(SAMPLE_CATEGORISED_CSV)
    hist_df = pd.read_csv(sample_csv)  # 10 unique rows
    base_date = datetime(2025, 10, 1)
    dfs = []
    for i in range(7200):  # 7200 * 10 ≈ 72000 rows, all unique dates
        df_copy = hist_df.copy()
        df_copy['date'] = [(base_date + timedelta(days=i * len(hist_df) + j)).strftime('%Y-%m-%d') for j in range(len(hist_df))]
        dfs.append(df_copy)
    repeated_df = pd.concat(dfs, ignore_index=True)
    p = tmp_path / "full_ml.csv"
    repeated_df.to_csv(p, index=False)
    return str(p)

@pytest.fixture
def unbalanced_labeled():
    dominant = pd.DataFrame({
        'description': ['TESCO STORE'] * 50,
        'amount': np.random.uniform(1, 100, 50),
        'category': ['Food/Dining'] * 50,
        'subcategory': ['Groceries'] * 50
    })
    rare = pd.DataFrame({
        'description': ['UNIQUE1', 'UNIQUE2', 'UNIQUE3'],
        'amount': np.random.uniform(1, 100, 3),
        'category': ['Transportation', 'Home', 'Utilities'],
        'subcategory': ['Rideshare', 'Maintenance', 'Electricity']
    })
    unbalanced = pd.concat([dominant, rare], ignore_index=True)
    return unbalanced

@pytest.fixture
def full_ml_bad_data_file(tmp_path):
    sample_csv = StringIO(SAMPLE_CATEGORISED_CSV)
    hist_df = pd.read_csv(sample_csv)  # 10 unique rows
    hist_df['description'] = 'IDENTICAL TRANSACTION'  # Set all to same for low acc
    hist_df['amount'] = 50.0  # Set all amounts identical to force low accuracy
    base_date = datetime(2025, 10, 1)
    dfs = []
    for i in range(7200):  # 7200 * 10 = 72000 rows
        df_copy = hist_df.copy()
        df_copy['date'] = [(base_date + timedelta(days=i * len(hist_df) + j)).strftime('%Y-%m-%d') for j in range(len(hist_df))]
        dfs.append(df_copy)
    repeated_df = pd.concat(dfs, ignore_index=True)
    p = tmp_path / "full_ml_bad.csv"
    repeated_df.to_csv(p, index=False)
    return str(p)


# TEST FOR LOAD_RULES_FILES() ==========================================================================================
def test_load_rules_file(sample_rules_file):
    rules = _load_rules_file(sample_rules_file)
    assert 'Food/Dining' in rules
    assert 'Groceries' in rules['Food/Dining']
    assert 'TESCO' in rules['Food/Dining']['Groceries']
    assert 'Transportation' in rules
    assert 'Public Transport' in rules['Transportation']
    assert 'TRAINLINE.COM' in rules['Transportation']['Public Transport']

def test_load_rules_file_default_file():
    rules = _load_rules_file(None)
    assert 'Food/Dining' in rules
    assert 'Groceries' in rules['Food/Dining']
    assert 'TESCO' in rules['Food/Dining']['Groceries']
    assert 'Transportation' in rules
    assert 'Public Transport' in rules['Transportation']
    assert 'TRAINLINE' in rules['Transportation']['Public Transport']

def test_load_rules_file_empty(empty_rules_file):
    with pytest.raises(ValueError, match="Rules CSV is empty."):
        _load_rules_file(empty_rules_file)

def test_load_rules_file_missing_cols(bad_rules_file):
    with pytest.raises(ValueError, match="missing required columns"):
        _load_rules_file(bad_rules_file)

def test_load_rules_file_no_file(tmp_path):
    no_file = str(tmp_path / "no_rules.csv")
    with pytest.raises(FileNotFoundError):
        _load_rules_file(no_file)

def test_load_rules_file_with_empty_patterns(rules_file_with_empty_pattern):
    rules = _load_rules_file(rules_file_with_empty_pattern)
    # Check non-empty patterns are loaded
    assert 'Food/Dining' in rules
    assert 'Groceries' in rules['Food/Dining']
    assert 'TESCO' in rules['Food/Dining']['Groceries']
    assert 'Restaurants/Bars' in rules['Food/Dining']
    assert rules['Food/Dining']['Restaurants/Bars'] == ['']
    assert 'Transportation' in rules
    assert 'Public Transport' in rules['Transportation']
    assert rules['Transportation']['Public Transport'] == ['']
    assert 'Rideshare' in rules['Transportation']
    assert 'UBER TRIP' in rules['Transportation']['Rideshare']


# TEST FOR LOAD_CATEGORISED() ==========================================================================================
def test_load_categorised(sample_categorised_file):
    categorised = _load_categorised(sample_categorised_file)
    assert isinstance(categorised, pd.DataFrame)
    assert not categorised.empty
    assert len(categorised) == 10
    assert list(categorised.columns) == ['date', 'description', 'amount', 'category', 'subcategory', "added_at"]
    assert categorised.iloc[0]['description'] == 'TRAINLINE.COM LONDON'

def test_load_categorised_empty(empty_categorised_file):
    categorised = _load_categorised(empty_categorised_file)
    assert isinstance(categorised, pd.DataFrame)
    assert categorised.empty
    expected_columns = ["date", "description", "amount", "source", "category", "subcategory", "added_at"]
    assert list(categorised.columns) == expected_columns

def test_load_categorised_non_existent(no_categorised_file):
    categorised = _load_categorised(no_categorised_file)
    assert isinstance(categorised, pd.DataFrame)
    assert categorised.empty
    expected_columns = ["date", "description", "amount", "source", "category", "subcategory", "added_at"]
    assert list(categorised.columns) == expected_columns


# TEST FOR COMPILE_RULES() =============================================================================================
def test_compile_rules():
    rules = {
        'Category1': {'Sub1': ['keyword', 'rregex pattern']},
    }
    compiled = _compile_rules(rules)
    assert compiled['Category1']['Sub1'][0] == 'keyword'
    assert isinstance(compiled['Category1']['Sub1'][1], re.Pattern)
    assert compiled['Category1']['Sub1'][1].search('Regex Pattern') is not None  # Case insensitive


# TEST FOR APPLY_RULES_TO_ROW() ========================================================================================
def test_apply_rules_to_row():
    rules = {
        'Food/Dining': {'Groceries': ['tesco']},
        'Transportation': {'Rideshare': ['uber trip']}
    }
    compiled = _compile_rules(rules)
    row = pd.Series({'description': 'UBER TRIP HELP', 'category': None, 'subcategory': None})
    cat, sub = _apply_rules_to_row(row, compiled)
    assert cat == 'Transportation'
    assert sub == 'Rideshare'

def test_apply_rules_to_row_preserves_existing_category():
    # Compiled rules that would match the description to a different category
    compiled_rules = {
        'Transportation': {
            'Rideshare': ['uber']  # String pattern (lowercase)
        }
    }
    # Row with existing category (non-NaN), and description that would match rules
    row = pd.Series({
        'description': 'UBER TRIP',
        'category': 'Food/Dining',  # Existing, different from rule match
        'subcategory': 'Takeaway'   # Existing subcategory
    })
    cat, sub = _apply_rules_to_row(row, compiled_rules)
    assert cat == 'Food/Dining'  # Preserves existing category
    assert sub == 'Takeaway'     # Preserves existing subcategory

def test_apply_rules_to_row_preserves_existing_category_no_subcategory():
    # Compiled rules that would match
    compiled_rules = {
        'Transportation': {
            'Rideshare': ['uber']
        }
    }
    # Row with existing category, but no subcategory
    row = pd.Series({
        'description': 'UBER TRIP',
        'category': 'Food/Dining',
        # No 'subcategory' key
    })
    cat, sub = _apply_rules_to_row(row, compiled_rules)
    assert cat == 'Food/Dining'  # Preserves existing
    assert sub is None           # Returns None if no subcategory


# TEST FOR DETECT_CONFLICTS() ==========================================================================================
def test_detect_conflicts():
    df = pd.DataFrame({
        'description': ['Desc1', 'Desc1', 'Desc2', 'Desc3'],
        'category': ['CatA', 'CatB', 'CatC', None],
        'original_category': ['CatA', 'CatA', None, None]
    })
    df = _detect_conflicts(df)
    assert df['conflict'].tolist() == [True, True, False, False]  # True for inconsistent cats in Desc1 and change in second



# TEST FOR TRAIN_MODEL() ===============================================================================================
def test_train_model_returns_none_when_insufficient_data():
    X = pd.DataFrame({
        'description': ['A', 'B', 'C'],
        'amount': [-10, 20, -30]
    })
    y = pd.Series(['Cat1', 'Cat1', 'Cat1'])
    model = _train_model(X, y, model_type='category')
    assert model is None

def test_train_model_returns_none_when_single_class():
    X = pd.DataFrame({
        'description': ['A'] * 20,
        'amount': np.random.uniform(1, 100, 20)
    })
    y = pd.Series(['CategoryA'] * 20)
    model = _train_model(X, y, model_type='category')
    assert model is None

def test_train_model_returns_none_when_mean_acc_below_threshold():
    # Data with identical descriptions but different labels: model can't distinguish, low acc
    X = pd.DataFrame({
        'description': ['identical transaction'] * 20,
        'amount': [50.0] * 20  # Identical to prevent distinction
    })
    y = pd.Series(['CategoryA'] * 10 + ['CategoryB'] * 10)
    model = _train_model(X, y, model_type='category')
    assert model is None  # Returns None due to mean_acc < 0.8


@patch('sklearn.model_selection.StratifiedShuffleSplit.split')
def test_train_model_returns_none_on_value_error(mock_split, capsys):
    # Good data that would normally train successfully
    X = pd.Series(['food purchase'] * 10 + ['transport fare'] * 10)
    y = pd.Series(['Food'] * 10 + ['Transport'] * 10)

    # Mock split to raise ValueError
    mock_split.side_effect = ValueError("Simulated CV split error")

    model = _train_model(X, y, model_type='category')

    # Check printed error
    captured = capsys.readouterr()
    assert "Error in CV split for category: Simulated CV split error" in captured.out

    assert model is None  # Returns None due to exception

def test_train_model_trains_successfully(capsys):
    # Balanced data with distinguishable descriptions
    descriptions = ['TESCO groceries'] * 10 + ['UBER ride'] * 10
    amounts = np.random.uniform(1, 50, 10).tolist() + np.random.uniform(51, 100, 10).tolist()  # Correlate with categories
    X = pd.DataFrame({
        'description': descriptions,
        'amount': amounts
    })
    y = pd.Series(['Food/Dining'] * 10 + ['Transportation'] * 10)
    model = _train_model(X, y, model_type='category')
    assert model is not None
    captured = capsys.readouterr()
    assert 'Category model accuracy on test set:' in captured.out

def test_train_model_skips_unbalanced_classes(unbalanced_labeled):
    # Rare classes have <5 samples, should be skipped
    model = _train_model(
        X=unbalanced_labeled[['description', 'amount']],
        y=unbalanced_labeled['category'],
        model_type='category'
    )
    assert model is None  # Only one sufficient class after filtering


# TEST FOR GET_ML_MODEL() ==============================================================================================
def test_get_ml_model_insufficient_data():
    labeled = pd.DataFrame({
        'description': ['TEST'] * 9,
        'amount': [10] * 9,
        'category': ['Cat1'] * 9,
        'subcategory': ['Sub1'] * 9
    })
    models = _get_ml_model(labeled)
    assert models['category'] is None
    assert models['subcategory'] is None

def test_get_ml_model_balanced():
    labeled = pd.DataFrame({
        'description': ['TESCO STORE', 'MCDONALDS', 'TRAINLINE.COM', 'UBER TRIP', 'BOLT'] * 5,
        'amount': np.random.uniform(1, 100, 25),
        'category': ['Food/Dining', 'Food/Dining', 'Transportation', 'Transportation', 'Transportation'] * 5,
        'subcategory': ['Groceries', 'Restaurants/Bars', 'Public Transport', 'Rideshare', 'Rideshare'] * 5
    })
    models = _get_ml_model(labeled)
    assert 'category' in models
    assert 'subcategory' in models
    assert models['category'] is not None
    assert models['subcategory'] is not None

def test_get_ml_model_unbalanced(unbalanced_labeled):
    models = _get_ml_model(unbalanced_labeled)
    assert models['category'] is None
    assert models['subcategory'] is None


# TEST FOR APPLY_ML() ==================================================================================================
def test_apply_ml_mock():
    # Simple mock model
    class MockModel:
        def predict(self, X):
            return ['Food/Dining'] * len(X)

    models = {'category': MockModel(), 'subcategory': MockModel()}
    df = pd.DataFrame({
        'description': ['TESCO', None],
        'amount': [2,-5],
        'category': [None, 'Existing']
    })
    df = _apply_ml(df, models)
    # Spot check
    assert df.iloc[0]['category'] == 'Food/Dining'
    assert df.iloc[1]['category'] == 'Existing'

def test_apply_ml(sample_rules_file):
    labeled = pd.DataFrame({
        'description': ['TESCO STORE', 'MCDONALDS', 'TRAINLINE.COM', 'UBER TRIP', 'BOLT'] * 10,
        'amount': np.random.uniform(1, 100, 50),
        'category': ['Food/Dining', 'Food/Dining', 'Transportation', 'Transportation', 'Transportation'] * 10,
        'subcategory': ['Groceries', 'Restaurants/Bars', 'Public Transport', 'Rideshare', 'Rideshare'] * 10
    })
    models = _get_ml_model(labeled)
    df = pd.DataFrame({
        'description': ['TESCO', 'MCDONALDS', 'TRAINLINE', 'UBER', 'BOLT'],
        'amount': np.random.uniform(1, 100, 5),
        'category': [None] * 5,
        'subcategory': [None] * 5
    })
    df_out = _apply_ml(df, models)
    assert not df_out['category'].isna().all()
    assert not df_out['subcategory'].isna().all()
    # Spot check
    assert df_out.loc[0, 'category'] == 'Food/Dining'
    assert df_out.loc[0, 'subcategory'] == 'Groceries'

def test_apply_ml_skips_when_no_model():
    models = {'category': None, 'subcategory': None}
    df = pd.DataFrame({
        'description': ['A', 'B'],
        'amount': [10, 20],
        'category': [np.nan, np.nan],
        'subcategory': [np.nan, np.nan]
    })
    df_out = _apply_ml(df, models)
    assert df_out['category'].isna().all()
    assert df_out['subcategory'].isna().all()

def test_apply_ml_no_change_when_all_categorised():
    models = {'category': 'mock', 'subcategory': 'mock'}
    df = pd.DataFrame({
        'description': ['A'],
        'amount': [10],
        'category': ['Cat1'],
        'subcategory': ['Sub1']
    })
    df_out = _apply_ml(df, models)
    assert df_out.equals(df)


# TEST FOR SAVE_CATEGORISED() ==========================================================================================
def test_save_categorised_new_file(tmp_path):
    cat_file = str(tmp_path / "new_categorised.csv")
    df = SAMPLE_DF.copy()
    df['category'] = ['Transportation', 'Food/Dining', 'Home', 'Transportation', 'Transportation']
    df['subcategory'] = ['Public Transport', 'Takeaway/Delivery', 'Maintenance', 'Rideshare', 'Rideshare']
    df['review'] = [None, None, None, None, None]
    _save_categorised(df, cat_file)
    saved_df = pd.read_csv(cat_file)
    assert 'added_at' in saved_df.columns
    assert not saved_df.empty
    assert len(saved_df) == len(df)
    # Check timestamp is recent
    process_date = datetime.strptime(saved_df['added_at'].iloc[0], '%Y-%m-%d %H:%M:%S')
    assert (datetime.now() - process_date).total_seconds() < 60

def test_save_categorised_append(sample_categorised_file):
    df = SAMPLE_DF.copy()
    df['category'] = ['Transportation', 'Food/Dining', 'Home', 'Transportation', 'Transportation']
    df['subcategory'] = ['Public Transport', 'Takeaway/Delivery', 'Maintenance', 'Rideshare', 'Rideshare']
    df['review'] = [None, None, None, None, None]
    _save_categorised(df, sample_categorised_file)
    saved_df = pd.read_csv(sample_categorised_file)
    assert len(saved_df) == 10 + 5  # Original 10 + new 5 (no dedup)
    assert 'added_at' in saved_df.columns
    assert saved_df['added_at'].notna().all()
    # New rows have recent timestamp
    new_dates = saved_df['added_at'].tail(5)
    for date_str in new_dates:
        process_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        assert (datetime.now() - process_date).total_seconds() < 60

# TEST FOR AUTO_CATEGORISE() ===========================================================================================
def test_auto_categorise_rules_method(sample_rules_file, tmp_path):
    cat_file = str(tmp_path / "auto_test.csv")
    df_test = SAMPLE_DF.copy()
    df_out = auto_categorise(df_test, rules_file=sample_rules_file, categorised_file=cat_file, add_col='to_reimburse')
    assert 'category' in df_out.columns
    assert 'subcategory' in df_out.columns
    assert 'review' in df_out.columns
    assert 'added_at' in df_out.columns
    assert 'to_reimburse' in df_out.columns
    # Check a few
    assert df_out[df_out['description'] == 'TRAINLINE.COM LONDON']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'TRAINLINE.COM LONDON']['subcategory'].values[0] == 'Public Transport'
    # DELIVEROO not in rules, so uncategorised
    assert df_out[df_out['description'] == 'DELIVEROO LONDON']['review'].values[0] == 'uncategorised'
    # Check if any conflicts (likely not in this sample)
    assert 'category conflict - review and resolve' not in df_out['review'].values
    # Check saved file
    saved_df = pd.read_csv(cat_file)
    assert len(saved_df) == 5
    assert 'added_at' in saved_df.columns

def test_auto_categorise_handles_partial_labels(sample_rules_file, sample_categorised_file):
    df_test = pd.DataFrame({
        'description': ['PRE-LABELED', 'UNCATEGORISED'],
        'amount': [10.0, 20.0],
        'category': ['Food/Dining', np.nan],
        'subcategory': [np.nan, np.nan]  # Partial
    })
    df_out = auto_categorise(
        df_test,
        rules_file=sample_rules_file,
        categorised_file=sample_categorised_file
    )
    # PRE-LABELED: Keeps category, flags partial if sub missing
    assert df_out[df_out['description'] == 'PRE-LABELED']['category'].values[0] == 'Food/Dining'
    assert df_out[df_out['description'] == 'PRE-LABELED']['review'].values[0] == 'partially uncategorised'

    # UNCATEGORISED: Applies rules/ML, but no match -> uncategorised
    assert pd.isna(df_out[df_out['description'] == 'UNCATEGORISED']['category'].values[0])
    assert df_out[df_out['description'] == 'UNCATEGORISED']['review'].values[0] == 'uncategorised'

def test_auto_categorise_detects_conflicts(sample_rules_file, sample_categorised_file):
    df_test = pd.DataFrame({
        'description': ['TRAINLINE.COM LONDON', 'TRAINLINE.COM LONDON'],
        'amount': [22.89, 22.89],
        'category': ['Transportation', 'Travel']  # Pre-label conflict
    })
    df_out = auto_categorise(
        df_test,
        rules_file=sample_rules_file,
        categorised_file=sample_categorised_file
    )
    # Rules apply Transportation/Public Transport, but pre-labels differ -> conflict
    assert df_out['review'].str.contains('conflict').all()

def test_auto_categorise_adds_custom_columns(sample_rules_file, empty_categorised_file):
    df_test = SAMPLE_DF.copy()
    df_out = auto_categorise(
        df_test,
        rules_file=sample_rules_file,
        categorised_file=empty_categorised_file,
        add_col='reimbursable'
    )
    assert 'reimbursable' in df_out.columns
    assert df_out['reimbursable'].isna().all()  # Initialised to None

def test_auto_categorise_hybrid_method(sample_rules_file, hybrid_categorised_file, capsys):
    df_test = SAMPLE_DF.copy()
    df_out = auto_categorise(
        df_test,
        rules_file=sample_rules_file,
        categorised_file=hybrid_categorised_file,
        add_col=['to_reimburse', 'reimbursement_date'],
    )
    captured = capsys.readouterr()
    assert "Limited labeled data; using ML + rules hybrid." in captured.out

    assert 'category' in df_out.columns
    assert 'subcategory' in df_out.columns
    assert 'review' in df_out.columns
    assert 'added_at' in df_out.columns
    assert 'to_reimburse' in df_out.columns
    assert 'reimbursement_date' in df_out.columns
    assert df_out['review'].isna().all()  # All should be categorised in hybrid with ML + rules

    # Check specific categorisations
    # TRAINLINE: Rules match, overrides if different but consistent here
    assert df_out[df_out['description'] == 'TRAINLINE.COM LONDON']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'TRAINLINE.COM LONDON']['subcategory'].values[0] == 'Public Transport'

    # DELIVEROO: Not in rules, ML predicts from history
    assert df_out[df_out['description'] == 'DELIVEROO LONDON']['category'].values[0] == 'Food/Dining'
    assert df_out[df_out['description'] == 'DELIVEROO LONDON']['subcategory'].values[0] == 'Takeaway/Delivery'

    # B&Q: Rules match, should override ML prediction
    assert df_out[df_out['description'] == 'B&Q CHELMSFORD']['category'].values[0] == 'Home'
    assert df_out[df_out['description'] == 'B&Q CHELMSFORD']['subcategory'].values[0] == 'Maintenance'

    # UBER: Rules match, overrides ML (which would likely misclassify)
    assert df_out[df_out['description'] == 'UBER TRIP HTTPS://HELP.UB']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'UBER TRIP HTTPS://HELP.UB']['subcategory'].values[0] == 'Rideshare'

    # BOLT: Rules match, overrides ML
    assert df_out[df_out['description'] == 'BOLT LONDON']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'BOLT LONDON']['subcategory'].values[0] == 'Rideshare'

    # Check saved file appended
    saved_df = pd.read_csv(hybrid_categorised_file)
    assert len(saved_df) == 30 + 5  # Original 30 + new 5 (no dedup)


def test_auto_categorise_full_ml_method(sample_rules_file, full_ml_categorised_file, capsys):
    df_test = SAMPLE_DF.copy()
    df_out = auto_categorise(
        df_test,
        rules_file=sample_rules_file,
        categorised_file=full_ml_categorised_file
    )
    captured = capsys.readouterr()
    assert "Sufficient labeled data; using full ML." in captured.out

    assert 'category' in df_out.columns
    assert 'subcategory' in df_out.columns
    assert 'review' in df_out.columns
    assert 'added_at' in df_out.columns
    assert df_out['review'].isna().all()  # All should be categorized with ML

    # Check specific categorisations (similar to hybrid, but no rules override unless ML fails)
    # Note: Since training data only has 'Food/Dining' and 'Transportation', new categories like 'Home' won't be predicted by ML.
    # With rules will override matches, so behavior similar to hybrid.
    # TRAINLINE: ML predicts Transportation/Public Transport
    assert df_out[df_out['description'] == 'TRAINLINE.COM LONDON']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'TRAINLINE.COM LONDON']['subcategory'].values[0] == 'Public Transport'

    # DELIVEROO: ML predicts Food/Dining/Takeaway/Delivery
    assert df_out[df_out['description'] == 'DELIVEROO LONDON']['category'].values[0] == 'Food/Dining'
    assert df_out[df_out['description'] == 'DELIVEROO LONDON']['subcategory'].values[0] == 'Takeaway/Delivery'

    # B&Q: Rules override to Home/Maintenance
    assert df_out[df_out['description'] == 'B&Q CHELMSFORD']['category'].values[0] == 'Home'
    assert df_out[df_out['description'] == 'B&Q CHELMSFORD']['subcategory'].values[0] == 'Maintenance'

    # UBER: Rules override to Transportation/Rideshare
    assert df_out[df_out['description'] == 'UBER TRIP HTTPS://HELP.UB']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'UBER TRIP HTTPS://HELP.UB']['subcategory'].values[0] == 'Rideshare'

    # BOLT: Rules override to Transportation/Rideshare
    assert df_out[df_out['description'] == 'BOLT LONDON']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'BOLT LONDON']['subcategory'].values[0] == 'Rideshare'

    # Check saved file appended
    saved_df = pd.read_csv(full_ml_categorised_file)
    assert len(saved_df) == 72000 + 5  # Original + new 5 (no dedup)


def test_auto_categorise_full_ml_fallback_to_rules(sample_rules_file, full_ml_bad_data_file, capsys):
    df_test = SAMPLE_DF.copy()
    df_out = auto_categorise(
        df_test,
        rules_file=sample_rules_file,
        categorised_file=full_ml_bad_data_file
    )
    captured = capsys.readouterr()
    assert "Sufficient labeled data; using full ML." in captured.out
    assert "ML model unavailable; falling back to rules." in captured.out
    # Check categorisations from rules only (ML failed)
    # TRAINLINE: rules match
    assert df_out[df_out['description'] == 'TRAINLINE.COM LONDON']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'TRAINLINE.COM LONDON']['subcategory'].values[0] == 'Public Transport'
    # DELIVEROO: no rule, remains uncategorised
    assert pd.isna(df_out[df_out['description'] == 'DELIVEROO LONDON']['category'].values[0])
    assert df_out[df_out['description'] == 'DELIVEROO LONDON']['review'].values[0] == 'uncategorised'
    # B&Q: rules match
    assert df_out[df_out['description'] == 'B&Q CHELMSFORD']['category'].values[0] == 'Home'
    assert df_out[df_out['description'] == 'B&Q CHELMSFORD']['subcategory'].values[0] == 'Maintenance'
    # UBER: rules match
    assert df_out[df_out['description'] == 'UBER TRIP HTTPS://HELP.UB']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'UBER TRIP HTTPS://HELP.UB']['subcategory'].values[0] == 'Rideshare'
    # BOLT: rules match
    assert df_out[df_out['description'] == 'BOLT LONDON']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'BOLT LONDON']['subcategory'].values[0] == 'Rideshare'
    # Check saved file appended
    saved_df = pd.read_csv(full_ml_bad_data_file)
    assert len(saved_df) == 72000 + 5  # Original + new 5