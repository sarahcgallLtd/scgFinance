import re
import os
import glob
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from importlib.resources import files

# Modular helper function: Load default rules file
# This function loads categorisation rules from a CSV file, either a custom one or a default bundled file.
# It parses the CSV into a nested dictionary structure: {category: {subcategory: [patterns]}}
def load_rules_file(rules_file):
    """
    Loads rules from the specified CSV or defaults to the bundled 'metadata/rules.csv'.

    Args:
        rules_file (str, optional): Path to custom rules CSV.

    Returns:
        dict: Nested rules {category: {subcategory: [pattern]}}.
    """
    # If no rules_file provided, use the default bundled in the package
    if rules_file is None:
        # Locate the default rules file in the package and convert to str for open/read_csv
        default_rules_path = files('scgFinance.data.metadata').joinpath('rules.csv')
        rules_file = str(default_rules_path)

    # Load from CSV (multi-row format: category, subcategory, pattern) =================================================
    # Check if the file exists; raise error if file not found
    if not os.path.exists(rules_file):
        raise FileNotFoundError(f"Rules file not found: {rules_file}")

    # Read the CSV into a DataFrame
    rules_df = pd.read_csv(rules_file)

    # Check for required columns to avoid malformed CSV issues
    required_cols = {'category', 'subcategory', 'pattern'}

    # Verify if all required columns are present; raise error if columns missing
    if not required_cols.issubset(rules_df.columns):
        raise ValueError(f"Rules CSV missing required columns: {required_cols - set(rules_df.columns)}")

    # Check if the DataFrame is empty; raise error if empty
    if rules_df.empty:
        raise ValueError("Rules CSV is empty.")

    # Initialise an empty dictionary to hold the nested rules
    rules = {}  # Nested: {category: {subcategory: [pattern]}}

    # Iterate over each row in the DataFrame ===========================================================================
    for _, row in rules_df.iterrows():
        category = row['category'].strip() # Extract and strip whitespace from category
        subcategory = row['subcategory'].strip() # Extract and strip whitespace from subcategory
        pattern_str = row['pattern'].strip().strip('"').strip("'")  # Extract pattern, strip whitespace and quotes

        # Skip if no valid pattern after parsing, then continue to next row if pattern is empty
        if not pattern_str:
            continue

        # If category not yet in rules, add it, and initialise subcategory dict for this category
        if category not in rules:
            rules[category] = {}

        # If subcategory not yet in category, add it, and initialise list for patterns
        if subcategory not in rules[category]:
            rules[category][subcategory] = []

        # Append the pattern to the list
        rules[category][subcategory].append(pattern_str)

    # Deduplicate pattern for each subcategory (optional, but helps avoid duplicates) ==================================
    # Iterate over categories and subcategories to remove duplicates by converting to set and back to list
    for category in rules:
        for subcategory in rules[category]:
            rules[category][subcategory] = list(set(rules[category][subcategory]))

    # Return the nested rules dictionary
    return rules

# Modular helper: Load previously categorised data from directory
# This function loads all previously categorised CSV files from a directory, concatenates them, and removes duplicates.
def load_categorised(categorised_dir='categorised'):
    """
    Loads and concatenates all previously categorised CSVs from the directory, if any.

    Args:
        categorised_dir (str): Path to previously categorised directory.

    Returns:
        pd.DataFrame: Combined categorised DataFrame (deduplicated).
    """
    # Initialise list to hold DataFrames from categorised files
    categorised_dfs = []

    # Check if the categorised directory exists and find all CSV files in the directory
    if os.path.exists(categorised_dir):
        cat_files = glob.glob(os.path.join(categorised_dir, '*.csv'))

        # Iterate over each file, reading the CSV into the DataFrame and appending to the list
        for cat_file in cat_files:
            cat_df = pd.read_csv(cat_file)
            categorised_dfs.append(cat_df)

    # If there are previously categorised DataFrames, concatenate them, reset the index, and remove duplicates based on key columns
    if categorised_dfs:
        all_categorised = pd.concat(categorised_dfs, ignore_index=True)
        all_categorised = all_categorised.drop_duplicates(subset=['date', 'description', 'amount'])
    else:
        # Define expected columns based on standardised schema
        expected_columns = ['date', 'description', 'amount', 'source', 'category', 'subcategory']
        all_categorised = pd.DataFrame(columns=expected_columns)

    # Return the combined categorised DataFrame
    return all_categorised


# Modular helper: Train ML model
# This function trains a new ML model using TF-IDF vectorization and logistic regression for classification.
def train_model(
        X, # Features (descriptions)
        y, # Labels (categories or subcategories)
        model_type='category' # Type for printing (category or subcategory)
):
    """
    Trains a new ML model using TF-IDF vectorization and logistic regression.

    Args:
        X (pd.Series or list): Features, typically transaction descriptions.
        y (pd.Series or list): Labels, either categories or subcategories.
        model_type (str, optional): Type ('category' or 'subcategory') for printing accuracy. Defaults to 'category'.

    Returns:
        Pipeline or None: The trained scikit-learn Pipeline model, or None if insufficient data.
    """
    # Check if data is sufficient for training
    if len(X) < 5 or len(np.unique(y)) < 2:
        # Skip training for very small data or single class
        return None  # Return None if insufficient data

    # Split data into train and test sets: 80/20 split, stratified by labels
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Create a pipeline: TF-IDF vectorizer + Logistic Regression
    model = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=500)), # Vectorise text with max 500 features
        ('clf', LogisticRegression(max_iter=200)) # Classifier with max 200 iterations
    ])

    # Train the model on training data
    model.fit(X_train, y_train)

    # Predict on test data
    preds = model.predict(X_test)

    # Calculate accuracy
    acc = accuracy_score(y_test, preds)
    print(f"{model_type.capitalize()} model accuracy on test set: {acc:.2f}") # Print accuracy

    # Return the trained model
    return model


# Modular helper: Train ML model
# This function gets ML models for category and subcategory, training them based on labeled data.
def get_ml_model(labeled):
    """
    Trains ML models for category and subcategory (if available).

    Args:
        labeled (pd.DataFrame): Labeled data for training.

    Returns:
        dict: {'category': Pipeline or None, 'subcategory': Pipeline or None}
    """
    models = {'category': None, 'subcategory': None}

    # Category model ===================================================================================================
    # Check if 'category' column exists and filter non-null, non-empty categories
    if 'category' in labeled.columns:
        cat_labeled = labeled[labeled['category'].notna() & labeled['category'].ne('')]

        # If enough data (more than 2 rows):
        if len(cat_labeled) > 2:
            models['category'] = train_model(
                X=cat_labeled['description'],
                y=cat_labeled['category'],
                model_type='category'
            )

    # Subcategory model ================================================================================================
    # Check if 'subcategory' column exists
    if 'subcategory' in labeled.columns:
        sub_labeled = labeled[labeled['subcategory'].notna() & labeled['subcategory'].ne('')]

        # If enough data (at least 10 rows):
        if len(sub_labeled) >= 10:
            models['subcategory'] = train_model(
                X=sub_labeled['description'],
                y=sub_labeled['subcategory'],
                model_type='subcategory'
            )

    # Return the models dictionary
    return models


# Modular helper: Apply ML to unlabeled data
# This function applies loaded/trained ML models to predict categories and subcategories for unlabeled rows.
def apply_ml(df, models):
    """
    Applies ML predictions to unlabeled rows in df for category and subcategory (if model available).

    Args:
        df (pd.DataFrame): DataFrame to categorise.
        models (dict): {'category': Pipeline, 'subcategory': Pipeline or None}

    Returns:
        pd.DataFrame: Updated df with ML predictions.
    """
    # Select rows without category
    unlabeled = df[df['category'].isna() | df['category'].eq('')].copy()

    # If there are unlabeled rows and category model exists, predict categories
    if not unlabeled.empty and models['category']:
        unlabeled['category'] = models['category'].predict(unlabeled['description'])

        # If subcategory model exists, predict subcategories
        if models['subcategory']:
            unlabeled['subcategory'] = models['subcategory'].predict(unlabeled['description'])

        # Concatenate labeled and newly predicted unlabeled, sort by original index
        df = pd.concat([df[df['category'].notna() & df['category'].ne('')], unlabeled]).sort_index()

    # Return updated DataFrame
    return df


# Modular helper: Compile rules for efficient matching
# This function compiles patterns into regex objects (if prefixed with 'r') or lowercase strings for matching.
def compile_rules(rules):
    """
    Compiles rules pattern into regex/lowercase for matching.

    Args:
        rules (dict): Nested rules dict.

    Returns:
        dict: Compiled nested rules.
    """
    # Initialise dictionary for compiled rules
    compiled_rules = {}

    # Iterate over categories and subcategories
    for category, subcats in rules.items():
        # Initialise subcategory dict
        compiled_rules[category] = {}

        # Iterate over subcategories and patterns
        for subcategory, pats in subcats.items():
            # Compile each pattern: regex if 'r' prefix, else lowercase string
            compiled_rules[category][subcategory] = [
                re.compile(pat[1:], re.IGNORECASE) if pat.startswith('r') else pat.lower() for pat in pats
            ]

    # Return compiled rules
    return compiled_rules


# Modular helper: Apply rules to a row
# This function applies compiled rules to a single row's description to assign category and subcategory.
def apply_rules_to_row(row, compiled_rules, overwrite):
    """
    Applies rules to a single row, assigning category and subcategory if matched.

    Args:
        row (pd.Series): DataFrame row.
        compiled_rules (dict): Compiled rules.
        overwrite (bool): Whether to overwrite existing category.

    Returns:
        tuple: (category, subcategory)
    """
    # If category exists and no overwrite, keep existing
    if pd.notna(row['category']) and not overwrite:
        # Return existing category and subcategory (if any)
        return row['category'], row.get('subcategory', None)

    # Lowercase description for matching
    desc = row['description'].lower() if isinstance(row['description'], str) else ''

    # Iterate over categories, subcategories, and patterns
    for category, subcats in compiled_rules.items():
        for subcategory, patterns in subcats.items():
            for pat in patterns:
                # Check for match (regex search or substring)
                if (isinstance(pat, re.Pattern) and pat.search(desc)) or (isinstance(pat, str) and pat in desc):
                    # Return first matching category and subcategory
                    return category, subcategory

    # If no match, return original (likely None)
    return row['category'], row.get('subcategory', None)


# Modular helper: Detect conflicts
# This function detects conflicts in categorisation, such as changes from original or inconsistent categories for same description.
def detect_conflicts(df):
    """
    Detects category conflicts in the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with 'category', 'original_category'.

    Returns:
        pd.DataFrame: Updated df with 'conflict' column.
    """
    # Initialise conflict column as False
    df['conflict'] = False

    # Conflict if category changed from original (without overwrite intent); Set True if changed
    df['conflict'] = (df['original_category'].notna()) & (df['original_category'] != df['category'])

    # Check for similar transactions with different categories (group by description)
    # Count unique categories per description
    grouped = df.groupby('description')['category'].nunique()

    # Get descriptions with more than 1 category
    conflicting_desc = grouped[grouped > 1].index

    # Set conflict True for those
    df.loc[df['description'].isin(conflicting_desc), 'conflict'] = True

    # Return updated DataFrame
    return df


# Modular helper: Save categorised DataFrame
# This function saves the categorised DataFrame to a timestamped CSV in the categorised directory.
def save_categorised(df, categorised_dir):
    """
    Saves the updated DataFrame to categorised_dir with timestamp.

    Args:
        df (pd.DataFrame): DataFrame to save.
        categorised_dir (str): Path to categorised directory.

    Returns:
        str: Path where saved.
    """
    # Create directory if it doesn't exist
    os.makedirs(categorised_dir, exist_ok=True)

    # Create timestamped filename
    save_path = os.path.join(categorised_dir, pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv')

    # Save DataFrame to CSV without index
    df.to_csv(save_path, index=False)
    print(f"Saved categorised data to {save_path}. Review rows where 'review' is not NaN manually.")

    # Return the save path
    return save_path


# Main function: auto_categorise
# This is the main function that orchestrates the categorisation process using rules, ML, or hybrid based on data availability.
# It loads rules and previously categorised files, applies categorisation, detects conflicts, generates review file, and saves the result.
def auto_categorise(
        df, # Input DataFrame to categorise
        rules_file=None, # Optional rules file path
        overwrite=False, # Whether to overwrite existing categories
        categorised_dir='categorised' # Previously categorised directory
):
    """
    Automatically categorises transactions based on description. Supports rules-based or ML-based (optional), using historical data.

    Args:
        df (pd.DataFrame): New DataFrame with 'description' and 'category' columns (from import).
        rules_file (str, optional): Path to CSV file with rules (defaults to bundled 'metadata/rules.csv').
        overwrite (bool): If True, re-categorise even if 'category' exists.
        categorised_dir (str): Directory with previously categorised CSVs (default: 'categorised').

    Returns:
        pd.DataFrame: Updated DF with 'category' and 'subcategory' filled, plus 'review' column for flagging rows needing manual review.
        Also saves to categorised_dir.
    """
    # 1. Initialise category and subcategory if not present (since import doesn't add them) ============================
    # Check and add category column if missing
    if 'category' not in df.columns:
        df['category'] = None

    # Check and add subcategory column if missing
    if 'subcategory' not in df.columns:
        df['subcategory'] = None

    # 2. Snapshot original for conflict detection ======================================================================
    # Copy original categories for later comparison
    df['original_category'] = df['category'].copy()

    # 3. Load rules (always, as fallback/hybrid) and previously categorised data (if present) ==========================
    # Load rules from file and compile for matching
    rules = load_rules_file(rules_file)
    compiled_rules = compile_rules(rules)

    # Load previously categorised
    all_categorised = load_categorised(categorised_dir)

    # 4. Prepare labeled/unlabeled (combine previously categorised + df's pre-labeled) =================================
    # Concatenate previously categorised labeled and current labeled
    labeled = pd.concat([
        all_categorised[all_categorised['category'].notna() & all_categorised['category'].ne('')],
        df[df['category'].notna() & df['category'].ne('')]
    ], ignore_index=True) # Reset index

    # Select unlabeled in current df
    unlabeled = df[df['category'].isna() | df['category'].eq('')]

    # 5. Determine mode based on data availability (no explicit use_ml param; auto-detect) =============================
    # Mode 1: Rules only (no/insufficient previously categorised/data); If no previously categorised or few labeled,
    #         use rules only and apply rules to each row
    if len(all_categorised) == 0 or len(labeled) < 10:
        print("No or insufficient previously categorised/labeled data; using rules only.")

        # Get, and apply, rules
        df[['category', 'subcategory']] = df.apply(
            lambda row: pd.Series(apply_rules_to_row(row, compiled_rules, overwrite)),
            axis=1
        )

    # Mode 2: Hybrid (rules + ML) for limited data or potential conflicts; If previously categorised data is "limited"
    #         (less than 500 labels), use hybrid
    elif len(labeled) < 500:
        print("Limited labeled data; using ML + rules hybrid.")

        # Get, and apply, model
        models = get_ml_model(labeled)
        if models['category']:
            df = apply_ml(df, models)

        # Then apply rules (as hybrid/fallback, sets both)
        df[['category', 'subcategory']] = df.apply(
            lambda row: pd.Series(apply_rules_to_row(row, compiled_rules, overwrite)),
            axis=1
        )

    # Mode 3: Full ML when enough data for over 500 labelled historical data
    else:
        print("Sufficient labeled data; using full ML.")

        # Get, and apply, model
        models = get_ml_model(labeled)
        if models['category']:
            df = apply_ml(df, models)

        # Fallback to rules if model fails (safetynet)
        else:
            print("ML model unavailable; falling back to rules.")

            # Apply rules
            df[['category', 'subcategory']] = df.apply(
                lambda row: pd.Series(apply_rules_to_row(row, compiled_rules, overwrite)),
                axis=1
            )

    # Detect conflicts and add conflict column
    df = detect_conflicts(df)

    # Create single 'review' column
    df['review'] = None
    uncat_mask = df['category'].isna() | df['category'].eq('')
    df.loc[uncat_mask, 'review'] = 'uncategorised'
    df.loc[df['conflict'], 'review'] = 'category conflict - review and resolve'

    # Print review summary
    review_count = df['review'].notna().sum()
    conflict_count = df['review'].str.contains('conflict', na=False).sum()
    if review_count > 0:
        print(f"{review_count} rows need manual review (including {conflict_count} conflicts).")

    # Drop temp columns (Remove temporary columns)
    df.drop(columns=['original_category', 'conflict'], errors='ignore', inplace=True)

    # Save updated df (categorised DataFrame)
    save_categorised(df, categorised_dir)

    # Return the updated DataFrame
    return df