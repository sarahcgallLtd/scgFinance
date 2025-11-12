import pytest
import pandas as pd
import os
import re
from io import StringIO
from datetime import datetime, timedelta
from src.scgFinance.categoriser import (
    _load_rules_file,
    _load_categorised,
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
        'category': ['Food/Dining'] * 50,
        'subcategory': ['Groceries'] * 50
    })
    rare = pd.DataFrame({
        'description': ['UNIQUE1', 'UNIQUE2', 'UNIQUE3'],
        'category': ['Transportation', 'Home', 'Utilities'],
        'subcategory': ['Rideshare', 'Maintenance', 'Electricity']
    })
    unbalanced = pd.concat([dominant, rare], ignore_index=True)
    return unbalanced

# TEST FOR LOAD_RULES_FILES() ==========================================================================================
def test_load_rules_file(sample_rules_file):
    rules = _load_rules_file(sample_rules_file)
    assert 'Food/Dining' in rules
    assert 'Groceries' in rules['Food/Dining']
    assert 'TESCO' in rules['Food/Dining']['Groceries']
    assert 'Transportation' in rules
    assert 'Public Transport' in rules['Transportation']
    assert 'TRAINLINE.COM' in rules['Transportation']['Public Transport']

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

def test_load_rules_file_default_file():
    rules = _load_rules_file(None)
    assert 'Food/Dining' in rules
    assert 'Groceries' in rules['Food/Dining']
    assert 'TESCO' in rules['Food/Dining']['Groceries']
    assert 'Transportation' in rules
    assert 'Public Transport' in rules['Transportation']
    assert 'TRAINLINE' in rules['Transportation']['Public Transport']


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


# TEST FOR DETECT_CONFLICTS() ==========================================================================================
def test_detect_conflicts():
    df = pd.DataFrame({
        'description': ['Desc1', 'Desc1', 'Desc2', 'Desc3'],
        'category': ['CatA', 'CatB', 'CatC', None],
        'original_category': ['CatA', 'CatA', None, None]
    })
    df = _detect_conflicts(df)
    assert df['conflict'].tolist() == [True, True, False, False]  # True for inconsistent cats in Desc1 and change in second

# TEST FOR GET_ML_MODEL() ==============================================================================================
def test_get_ml_model_insufficient_data():
    labeled = pd.DataFrame({
        'description': ['TEST'] * 9,
        'category': ['Cat1'] * 9,
        'subcategory': ['Sub1'] * 9
    })
    models = _get_ml_model(labeled)
    assert models['category'] is None
    assert models['subcategory'] is None

def test_get_ml_model_balanced():
    labeled = pd.DataFrame({
        'description': ['TESCO STORE', 'MCDONALDS', 'TRAINLINE.COM', 'UBER TRIP', 'BOLT'] * 5,
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
        'category': [None, 'Existing']
    })
    df = _apply_ml(df, models)
    # Spot check
    assert df.iloc[0]['category'] == 'Food/Dining'
    assert df.iloc[1]['category'] == 'Existing'

def test_apply_ml(sample_rules_file):
    labeled = pd.DataFrame({
        'description': ['TESCO STORE', 'MCDONALDS', 'TRAINLINE.COM', 'UBER TRIP', 'BOLT'] * 10,
        'category': ['Food/Dining', 'Food/Dining', 'Transportation', 'Transportation', 'Transportation'] * 10,
        'subcategory': ['Groceries', 'Restaurants/Bars', 'Public Transport', 'Rideshare', 'Rideshare'] * 10
    })
    models = _get_ml_model(labeled)
    df = pd.DataFrame({
        'description': ['TESCO', 'MCDONALDS', 'TRAINLINE', 'UBER', 'BOLT'],
        'category': [None] * 5,
        'subcategory': [None] * 5
    })
    df_out = _apply_ml(df, models)
    assert not df_out['category'].isna().all()
    assert not df_out['subcategory'].isna().all()
    # Spot check
    assert df_out.loc[0, 'category'] == 'Food/Dining'
    assert df_out.loc[0, 'subcategory'] == 'Groceries'

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
    df_out = auto_categorise(df_test, rules_file=sample_rules_file, categorised_file=cat_file)
    assert 'category' in df_out.columns
    assert 'subcategory' in df_out.columns
    assert 'review' in df_out.columns
    assert 'added_at' in df_out.columns
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


def test_auto_categorise_hybrid_method(sample_rules_file, hybrid_categorised_file, capsys):
    df_test = SAMPLE_DF.copy()
    df_out = auto_categorise(
        df_test,
        rules_file=sample_rules_file,
        categorised_file=hybrid_categorised_file
    )
    captured = capsys.readouterr()
    assert "Limited labeled data; using ML + rules hybrid." in captured.out

    assert 'category' in df_out.columns
    assert 'subcategory' in df_out.columns
    assert 'review' in df_out.columns
    assert 'added_at' in df_out.columns
    assert df_out['review'].isna().all()  # All should be categorised in hybrid with ML + rules

    # Check specific categorizations
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