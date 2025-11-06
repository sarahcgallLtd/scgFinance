import pytest
import pandas as pd
import os
import re
from src.scgFinance.categoriser import (
    load_rules_file,
    load_history,
    get_ml_model,
    apply_ml,
    compile_rules,
    apply_rules_to_row,
    detect_conflicts,
    save_categorised,
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

SAMPLE_HISTORY_CSV = '''date,description,amount,category,subcategory
2025-10-01,TRAINLINE.COM LONDON,22.89,Transportation,Public Transport
2025-10-07,DELIVEROO LONDON,19.37,Food/Dining,Takeaway/Delivery
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
def sample_history_dir(tmp_path):
    d = tmp_path / "categorised"
    d.mkdir()
    p = d / "test.csv"
    p.write_text(SAMPLE_HISTORY_CSV)
    return str(d)

def test_load_rules_file(sample_rules_file):
    rules = load_rules_file(sample_rules_file)
    assert 'Food/Dining' in rules
    assert 'Groceries' in rules['Food/Dining']
    assert 'TESCO' in rules['Food/Dining']['Groceries']
    assert 'Transportation' in rules
    assert 'Public Transport' in rules['Transportation']
    assert 'TRAINLINE.COM' in rules['Transportation']['Public Transport']

def test_load_history(sample_history_dir):
    history = load_history(sample_history_dir)
    assert len(history) == 2
    assert list(history.columns) == ['date', 'description', 'amount', 'category', 'subcategory']
    assert history.iloc[0]['description'] == 'TRAINLINE.COM LONDON'

def test_compile_rules():
    rules = {
        'Category1': {'Sub1': ['keyword', 'rregex pattern']},
    }
    compiled = compile_rules(rules)
    assert compiled['Category1']['Sub1'][0] == 'keyword'
    assert isinstance(compiled['Category1']['Sub1'][1], re.Pattern)
    assert compiled['Category1']['Sub1'][1].search('Regex Pattern') is not None  # Case insensitive

def test_apply_rules_to_row():
    rules = {
        'Food/Dining': {'Groceries': ['tesco']},
        'Transportation': {'Rideshare': ['uber trip']}
    }
    compiled = compile_rules(rules)
    row = pd.Series({'description': 'UBER TRIP HELP', 'category': None, 'subcategory': None})
    cat, sub = apply_rules_to_row(row, compiled, False)
    assert cat == 'Transportation'
    assert sub == 'Rideshare'

    # Test overwrite
    row['category'] = 'Other'
    cat, sub = apply_rules_to_row(row, compiled, False)
    assert cat == 'Other'  # Not overwritten

    cat, sub = apply_rules_to_row(row, compiled, True)
    assert cat == 'Transportation'  # Overwritten

def test_detect_conflicts():
    df = pd.DataFrame({
        'description': ['Desc1', 'Desc1', 'Desc2', 'Desc3'],
        'category': ['CatA', 'CatB', 'CatC', None],
        'original_category': ['CatA', 'CatA', None, None]
    })
    df = detect_conflicts(df)
    assert df['conflict'].tolist() == [True, True, False, False]  # True for inconsistent cats in Desc1 and change in second

def test_get_ml_model(tmp_path):
    labeled = pd.DataFrame({
        'description': ['TESCO STORE', 'MCDONALDS', 'TRAINLINE.COM', 'UBER TRIP', 'BOLT'] * 10,
        'category': ['Food/Dining', 'Food/Dining', 'Transportation', 'Transportation', 'Transportation'] * 10,
        'subcategory': ['Groceries', 'Restaurants/Bars', 'Public Transport', 'Rideshare', 'Rideshare'] * 10
    })
    model_file = str(tmp_path / "cat_model.pkl")
    sub_model_file = str(tmp_path / "sub_model.pkl")
    models = get_ml_model(labeled, model_file, sub_model_file)
    assert models['category'] is not None
    assert models['subcategory'] is not None

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
    df = apply_ml(df, models)
    assert df.iloc[0]['category'] == 'Food/Dining'
    assert df.iloc[1]['category'] == 'Existing'  # Not overwritten

def test_save_categorised(tmp_path):
    df = SAMPLE_DF.copy()
    hist_dir = str(tmp_path / "save_test")
    save_path = save_categorised(df, hist_dir)
    assert os.path.exists(save_path)
    loaded = pd.read_csv(save_path)
    assert loaded.shape == df.shape

def test_auto_categorise(sample_rules_file, tmp_path):
    hist_dir = str(tmp_path / "auto_test")
    df_test = SAMPLE_DF.copy()
    df_out = auto_categorise(df_test, rules_file=sample_rules_file, history_dir=hist_dir, overwrite=True)
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