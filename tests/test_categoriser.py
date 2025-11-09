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

SAMPLE_CATEGORISED_CSV = '''date,description,amount,category,subcategory
2025-10-01,TRAINLINE.COM LONDON,22.89,Transportation,Public Transport
2025-10-07,DELIVEROO LONDON,19.37,Food/Dining,Takeaway/Delivery
2025-10-08,B&Q CHELMSFORD,5.0,Home,Maintenance
2025-10-09,UBER TRIP HTTPS://HELP.UB,7.54,Transportation,Rideshare
2025-10-10,BOLT LONDON,39.93,Transportation,Rideshare
2025-10-11,TESCO,15.25,Food/Dining,Groceries
2025-10-12,MCDONALDS,8.99,Food/Dining,Restaurants/Bars
2025-10-13,MCDONALDS,8.99,Food/Dining,Restaurants/Bars
2025-10-15,DELIVEROO LONDON,19.37,Food/Dining,Takeaway/Delivery
2025-10-20,TRAINLINE.COM LONDON,22.89,Transportation,Public Transport
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
def sample_categorised_dir(tmp_path):
    d = tmp_path / "categorised"
    d.mkdir()
    p = d / "test.csv"
    p.write_text(SAMPLE_CATEGORISED_CSV)
    return str(d)

@pytest.fixture
def empty_categorised_dir(tmp_path):
    d = tmp_path / "empty_categorised"
    d.mkdir()
    return str(d)

@pytest.fixture
def no_categorised_dir(tmp_path):
    return str(tmp_path / "non_existent_dir")

@pytest.fixture
def hybrid_categorised_dir(tmp_path):
    d = tmp_path / "hybrid_categorised"
    d.mkdir()
    sample_csv = StringIO(SAMPLE_CATEGORISED_CSV)
    hist_df = pd.read_csv(sample_csv)  # Now 7 unique rows
    base_date = datetime(2025, 10, 1)
    dfs = []
    for i in range(3):  # 3 * 7 = 21 rows, all unique dates
        df_copy = hist_df.copy()
        df_copy['date'] = [(base_date + timedelta(days=i * len(hist_df) + j)).strftime('%Y-%m-%d') for j in range(len(hist_df))]
        dfs.append(df_copy)
    repeated_df = pd.concat(dfs, ignore_index=True)
    p = d / "hybrid.csv"
    repeated_df.to_csv(p, index=False)
    return str(d)

@pytest.fixture
def full_ml_categorised_dir(tmp_path):
    d = tmp_path / "full_ml_categorised"
    d.mkdir()
    sample_csv = StringIO(SAMPLE_CATEGORISED_CSV)
    hist_df = pd.read_csv(sample_csv)  # 10 unique rows
    base_date = datetime(2025, 10, 1)
    dfs = []
    for i in range(72):  # 72 * 10 ≈ 720 rows, all unique dates
        df_copy = hist_df.copy()
        df_copy['date'] = [(base_date + timedelta(days=i * len(hist_df) + j)).strftime('%Y-%m-%d') for j in range(len(hist_df))]
        dfs.append(df_copy)
    repeated_df = pd.concat(dfs, ignore_index=True)
    p = d / "full_ml.csv"
    repeated_df.to_csv(p, index=False)
    return str(d)

@pytest.fixture
def unbalanced_labeled():
    balanced = pd.DataFrame({
        'description': ['TESCO STORE', 'MCDONALDS', 'TRAINLINE.COM', 'UBER TRIP', 'BOLT'] * 10,
        'category': ['Food/Dining', 'Food/Dining', 'Transportation', 'Transportation', 'Transportation'] * 10,
        'subcategory': ['Groceries', 'Restaurants/Bars', 'Public Transport', 'Rideshare', 'Rideshare'] * 10
    })
    new_row = pd.DataFrame({
        'description': ['NEW UNIQUE'],
        'category': ['NewCat'],
        'subcategory': ['NewSub']
    })
    unbalanced = pd.concat([balanced, new_row], ignore_index=True)
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
def test_load_categorised(sample_categorised_dir):
    categorised = _load_categorised(sample_categorised_dir)
    assert len(categorised) == 10
    assert list(categorised.columns) == ['date', 'description', 'amount', 'category', 'subcategory']
    assert categorised.iloc[0]['description'] == 'TRAINLINE.COM LONDON'

def test_load_categorised_empty(empty_categorised_dir):
    categorised = _load_categorised(empty_categorised_dir)
    assert categorised.empty
    assert 'category' in categorised.columns

def test_load_categorised_no_dir(no_categorised_dir):
    categorised = _load_categorised(no_categorised_dir)
    assert categorised.empty
    assert 'category' in categorised.columns


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
    cat, sub = _apply_rules_to_row(row, compiled, False)
    assert cat == 'Transportation'
    assert sub == 'Rideshare'

    # Test overwrite
    row['category'] = 'Other'
    cat, sub = _apply_rules_to_row(row, compiled, False)
    assert cat == 'Other'  # Not overwritten

    cat, sub = _apply_rules_to_row(row, compiled, True)
    assert cat == 'Transportation'  # Overwritten

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
def test_get_ml_model(tmp_path):
    labeled = pd.DataFrame({
        'description': ['TESCO STORE', 'MCDONALDS', 'TRAINLINE.COM', 'UBER TRIP', 'BOLT'] * 10,
        'category': ['Food/Dining', 'Food/Dining', 'Transportation', 'Transportation', 'Transportation'] * 10,
        'subcategory': ['Groceries', 'Restaurants/Bars', 'Public Transport', 'Rideshare', 'Rideshare'] * 10
    })
    models = _get_ml_model(labeled)
    assert models['category'] is not None
    assert models['subcategory'] is not None

def test_get_ml_model_with_unbalanced_classes(unbalanced_labeled):
    models = _get_ml_model(unbalanced_labeled)
    assert models['category'] is not None
    assert models['subcategory'] is not None

# TEST FOR APPLY_ML() ==================================================================================================
def test_apply_ml():
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
    assert df.iloc[0]['category'] == 'Food/Dining'
    assert df.iloc[1]['category'] == 'Existing'  # Not overwritten

# TEST FOR SAVE_CATEGORISED() ==========================================================================================
def test_save_categorised(tmp_path):
    df = SAMPLE_DF.copy()
    cat_dir = str(tmp_path / "save_test")
    save_path = _save_categorised(df, cat_dir)
    assert os.path.exists(save_path)
    loaded = pd.read_csv(save_path)
    assert loaded.shape == df.shape

# TEST FOR AUTO_CATEGORISE() ===========================================================================================
def test_auto_categorise_rules_method(sample_rules_file, tmp_path):
    cat_dir = str(tmp_path / "auto_test")
    df_test = SAMPLE_DF.copy()
    df_out = auto_categorise(df_test, rules_file=sample_rules_file, categorised_dir=cat_dir, overwrite=True)
    assert 'category' in df_out.columns
    assert 'subcategory' in df_out.columns
    assert 'review' in df_out.columns
    # Check a few
    assert df_out[df_out['description'] == 'TRAINLINE.COM LONDON']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'TRAINLINE.COM LONDON']['subcategory'].values[0] == 'Public Transport'
    # DELIVEROO not in rules, so uncategorised
    assert df_out[df_out['description'] == 'DELIVEROO LONDON']['review'].values[0] == 'uncategorised'
    # Check if any conflicts (likely not in this sample)
    assert 'category conflict - review and resolve' not in df_out['review'].values


def test_auto_categorise_hybrid_method(sample_rules_file, hybrid_categorised_dir, tmp_path, capsys):
    df_test = SAMPLE_DF.copy()
    df_out = auto_categorise(
        df_test,
        rules_file=sample_rules_file,
        overwrite=True,  # Enable overwrite to test hybrid behaviour (rules can override ML if matched)
        categorised_dir=hybrid_categorised_dir
    )
    captured = capsys.readouterr()
    assert "Limited labeled data; using ML + rules hybrid." in captured.out

    assert 'category' in df_out.columns
    assert 'subcategory' in df_out.columns
    assert 'review' in df_out.columns
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


def test_auto_categorise_full_ml_method(sample_rules_file, full_ml_categorised_dir, tmp_path, capsys):
    df_test = SAMPLE_DF.copy()
    df_out = auto_categorise(
        df_test,
        rules_file=sample_rules_file,
        overwrite=True,  # Enable overwrite for consistency; allows rules fallback if ML fails (though unlikely here)
        categorised_dir=full_ml_categorised_dir
    )
    captured = capsys.readouterr()
    assert "Sufficient labeled data; using full ML." in captured.out

    assert 'category' in df_out.columns
    assert 'subcategory' in df_out.columns
    assert 'review' in df_out.columns
    assert df_out['review'].isna().all()  # All should be categorized with ML

    # Check specific categorisations (similar to hybrid, but no rules override unless ML fails)
    # Note: Since training data only has 'Food/Dining' and 'Transportation', new categories like 'Home' won't be predicted by ML.
    # With overwrite=True, rules will override matches, so behavior similar to hybrid.
    # TRAINLINE: ML predicts Transportation/Public Transport
    assert df_out[df_out['description'] == 'TRAINLINE.COM LONDON']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'TRAINLINE.COM LONDON']['subcategory'].values[0] == 'Public Transport'

    # DELIVEROO: ML predicts Food/Dining/Takeaway/Delivery
    assert df_out[df_out['description'] == 'DELIVEROO LONDON']['category'].values[0] == 'Food/Dining'
    assert df_out[df_out['description'] == 'DELIVEROO LONDON']['subcategory'].values[0] == 'Takeaway/Delivery'

    # B&Q: Rules override to Home/Maintenance (since overwrite=True)
    assert df_out[df_out['description'] == 'B&Q CHELMSFORD']['category'].values[0] == 'Home'
    assert df_out[df_out['description'] == 'B&Q CHELMSFORD']['subcategory'].values[0] == 'Maintenance'

    # UBER: Rules override to Transportation/Rideshare
    assert df_out[df_out['description'] == 'UBER TRIP HTTPS://HELP.UB']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'UBER TRIP HTTPS://HELP.UB']['subcategory'].values[0] == 'Rideshare'

    # BOLT: Rules override to Transportation/Rideshare
    assert df_out[df_out['description'] == 'BOLT LONDON']['category'].values[0] == 'Transportation'
    assert df_out[df_out['description'] == 'BOLT LONDON']['subcategory'].values[0] == 'Rideshare'
