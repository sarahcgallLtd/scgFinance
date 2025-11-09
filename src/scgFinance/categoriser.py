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


# ================================================
# Modular helper function: Load default rules file
# ================================================


def _load_rules_file(rules_file):
    """
    Loads categorisation rules from a specified CSV file or defaults to
    the bundled 'metadata/rules.csv'.

    This function checks for the existence of the rules file and reads
    it into a DataFrame. It validates the required columns
    ('category', 'subcategory', 'pattern') and constructs a nested
    dictionary where patterns are stored under their respective categories
    and subcategories. Duplicates within subcategory patterns are removed
    for efficiency. Patterns are stripped of whitespace and quotes for clean
    matching.

    Args:
        rules_file (str, optional): Path to the custom rules CSV file. If None,
        uses the default bundled file.

    Returns:
        dict: A nested dictionary of rules in the format
              {category: {subcategory: [pattern]}}.

    Raises:
        FileNotFoundError: If the specified rules file does not exist.
        ValueError: If the CSV is missing required columns or is empty.

    Example:
        >>> rules = _load_rules_file('metadata/custom_rules.csv')
        >>> print(rules['Food/Dining']['Groceries'])
        ['TESCO', 'SAINSBURY']
    """
    # If no rules_file provided, use the default bundled in the package
    if rules_file is None:
        # Locate default rules file in pkg and convert to str for open/read_csv
        default_rules_path = files("scgFinance." "data.metadata").joinpath(
            "rules.csv"
        )
        rules_file = str(default_rules_path)

    # Load from CSV (multi-row format: category, subcategory, pattern)
    # ================================================================
    # Check if the file exists; raise error if file not found
    if not os.path.exists(rules_file):
        raise FileNotFoundError(f"Rules file not found: {rules_file}")

    # Read the CSV into a DataFrame
    rules_df = pd.read_csv(rules_file)

    # Check for required columns to avoid malformed CSV issues
    required_cols = {"category", "subcategory", "pattern"}

    # Verify if all required columns are present; raise error if not
    if not required_cols.issubset(rules_df.columns):
        raise ValueError(
            f"Rules CSV missing required columns: "
            f"{required_cols - set(rules_df.columns)}"
        )

    # Check if the DataFrame is empty; raise error if empty
    if rules_df.empty:
        raise ValueError("Rules CSV is empty.")

    # Initialise an empty dictionary to hold the nested rules
    rules = {}  # Nested: {category: {subcategory: [pattern]}}

    # Iterate over each row in the DataFrame
    # ======================================
    for _, row in rules_df.iterrows():
        # Extract and strip whitespace from category
        category = row["category"].strip()

        # Extract and strip whitespace from subcategory
        subcategory = row["subcategory"].strip()

        # Extract pattern, strip whitespace and quotes
        pattern_str = row["pattern"].strip().strip('"').strip("'")

        # Skip if no valid pattern after parsing,
        # then continue to next row if pattern is empty
        if not pattern_str:
            continue

        # If category not yet in rules, add it, and
        # initialise subcategory dict for this category
        if category not in rules:
            rules[category] = {}

        # If subcategory not yet in category, add it,
        # and initialise list for patterns
        if subcategory not in rules[category]:
            rules[category][subcategory] = []

        # Append the pattern to the list
        rules[category][subcategory].append(pattern_str)

    # Deduplicate pattern for each subcategory
    # (optional, but helps avoid duplicates)
    # ==================================
    # Iterate over categories and subcategories to
    # remove duplicates by converting to set and back to list
    for category in rules:
        for subcategory in rules[category]:
            rules[category][subcategory] = list(
                set(rules[category][subcategory])
            )

    # Return the nested rules dictionary
    return rules


# ================================================
# Modular helper: Load previously categorised data
# ================================================


def _load_categorised(categorised_dir="categorised/"):
    """
    Loads and concatenates all previously categorised CSV files from a
    specified directory, removing duplicates.

    This function scans the directory for CSV files, reads each one, and
    combines them into a single DataFrame. Duplicates are removed based
    on 'date', 'description', and 'amount' columns to ensure data integrity.
    If no files are found or the directory does not exist, an empty DataFrame
    with expected columns is returned.

    Args:
        categorised_dir (str, optional): Path to the directory containing
        previously categorised CSV files. Defaults to 'categorised/'.

    Returns:
        pd.DataFrame: A combined DataFrame of all categorised data,
                      with duplicates removed.

    Raises:
        None explicitly, but may raise pandas errors if CSV files
        are malformed.

    Example:
        >>> categorised = _load_categorised('categorised/')
        >>> print(categorised.shape)
        (50, 6)  # Example assuming 50 unique rows loaded
    """
    # Initialise list to hold DataFrames from categorised files
    categorised_dfs = []

    # Check if the categorised directory exists and find all CSV files in
    # the directory
    if os.path.exists(categorised_dir):
        cat_files = glob.glob(os.path.join(categorised_dir, "*.csv"))

        # Iterate over each file, reading the CSV into the DataFrame and
        # appending to the list
        for cat_file in cat_files:
            cat_df = pd.read_csv(cat_file)
            categorised_dfs.append(cat_df)

    # If there are previously categorised DataFrames, concatenate them, reset
    # the index, and remove duplicates based on key columns
    if categorised_dfs:
        all_categorised = pd.concat(categorised_dfs, ignore_index=True)
        all_categorised = all_categorised.drop_duplicates(
            subset=["date", "description", "amount"]
        )
    else:
        # Define expected columns based on standardised schema
        expected_columns = [
            "date",
            "description",
            "amount",
            "source",
            "category",
            "subcategory",
        ]
        all_categorised = pd.DataFrame(columns=expected_columns)

    # Return the combined categorised DataFrame
    return all_categorised


# ================================================
# Modular helper: Train ML model
# ================================================


def _train_model(X, y, model_type="category"):
    """
    Trains a machine learning model using TF-IDF vectorization and logistic
    regression for text classification.

    This function splits the data into training and testing sets, builds a
    pipeline with TF-IDF vectorization (limited to 500 features) and
    logistic regression, trains the model, evaluates its accuracy on the
    test set, and prints the result. It skips training if there is
    insufficient data or only one unique label.

    Args:
        X (pd.Series or list): The feature data, typically transaction
                               descriptions.
        y (pd.Series or list): The target labels, either categories or
                               subcategories.
        model_type (str, optional): Specifies if training for 'category' or
                                    'subcategory' for printing purposes.
                                    Defaults to 'category'.

    Returns:
        Pipeline or None: The trained scikit-learn Pipeline if successful,
        otherwise None.

    Raises:
        None explicitly, but may raise scikit-learn errors if data issues
        arise during fitting.

    Example:
        >>> X = ['Buy groceries at TESCO', 'Ride with UBER']
        >>> y = ['Food/Dining', 'Transportation']
        >>> model = _train_model(X, y)
        Category model accuracy on test set: 1.00
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
    model = Pipeline(
        [
            # Vectorise text with max 500 features
            ("tfidf", TfidfVectorizer(max_features=500)),
            # Classifier with max 200 iterations
            ("clf", LogisticRegression(max_iter=200)),
        ]
    )

    # Train the model on training data
    model.fit(X_train, y_train)

    # Predict on test data
    preds = model.predict(X_test)

    # Calculate accuracy
    acc = accuracy_score(y_test, preds)
    # Print accuracy
    print(f"{model_type.capitalize()} model accuracy on test set: {acc:.2f}")

    # Return the trained model
    return model


# ================================================
# Modular helper: Train ML model
# ================================================


def _get_ml_model(labeled):
    """
    Trains separate ML models for predicting categories and subcategories
    using available labeled data.

    This function filters the labeled DataFrame for non-null categories
    and subcategories, then trains models using train_model() if sufficient
    data is available (more than 2 rows for categories, at least 10 for
    subcategories).

    Args:
        labeled (pd.DataFrame): The DataFrame containing labeled data with
        'description', 'category', and optionally 'subcategory'.

    Returns:
        dict: A dictionary with keys 'category' and 'subcategory', each
        mapping to a trained Pipeline or None.

    Raises:
        None explicitly, but propagates errors from train_model().

    Example:
        >>> labeled = pd.DataFrame({'description': ['TESCO', 'UBER'],
        ... 'category': ['Food/Dining', 'Transportation']})
        >>> models = _get_ml_model(labeled)
        >>> assert models['category'] is not None
    """
    models = {"category": None, "subcategory": None}

    # Category model
    # ==============
    # Check if 'category' column exists and filter non-null,
    # non-empty categories
    if "category" in labeled.columns:
        cat_labeled = labeled[
            labeled["category"].notna() & labeled["category"].ne("")
        ]

        # If enough data (more than 2 rows):
        if len(cat_labeled) > 2:
            models["category"] = _train_model(
                X=cat_labeled["description"],
                y=cat_labeled["category"],
                model_type="category",
            )

    # Subcategory model
    # ==================
    # Check if 'subcategory' column exists
    if "subcategory" in labeled.columns:
        sub_labeled = labeled[
            labeled["subcategory"].notna() & labeled["subcategory"].ne("")
        ]

        # If enough data (at least 10 rows):
        if len(sub_labeled) >= 10:
            models["subcategory"] = _train_model(
                X=sub_labeled["description"],
                y=sub_labeled["subcategory"],
                model_type="subcategory",
            )

    # Return the models dictionary
    return models


# ================================================
# Modular helper: Apply ML to unlabeled data
# ================================================


def _apply_ml(df, models):
    """
    Applies trained ML models to predict categories and subcategories for
    unlabeled rows in the DataFrame.

    This function identifies rows without categories, uses the category model
    to predict them if available, and then applies the subcategory model if
    present. The updated rows are reintegrated into the original DataFrame,
    preserving order.

    Args:
        df (pd.DataFrame): The DataFrame to update with predictions, containing
                           'description', 'category', and optionally
                           'subcategory'.
        models (dict): Dictionary of trained models {'category': Pipeline or
                       None, 'subcategory': Pipeline or None}.

    Returns:
        pd.DataFrame: The updated DataFrame with ML predictions filled in for
        unlabeled rows.

    Raises:
        None explicitly, but may raise prediction errors if models are
        incompatible with data.

    Example:
        >>> df = pd.DataFrame({'description': ['TESCO', 'UBER'],
        ... 'category': [None, 'Transportation']})
        >>> models = {'category': trained_model, 'subcategory': None}
        >>> updated_df = _apply_ml(df, models)
        >>> print(updated_df['category'].iloc[0])
        'Food/Dining'  # Assuming model prediction
    """
    # Select rows without category
    unlabeled = df[df["category"].isna() | df["category"].eq("")].copy()

    # If there are unlabeled rows and category model exists, predict categories
    if not unlabeled.empty and models["category"]:
        unlabeled["category"] = models["category"].predict(
            unlabeled["description"]
        )

        # If subcategory model exists, predict subcategories
        if models["subcategory"]:
            unlabeled["subcategory"] = models["subcategory"].predict(
                unlabeled["description"]
            )

        # Concatenate labeled and newly predicted unlabeled, sort by
        # original index
        df = pd.concat(
            [df[df["category"].notna() & df["category"].ne("")], unlabeled]
        ).sort_index()

    # Return updated DataFrame
    return df


# ================================================
# Modular helper: Compile rules for matching
# ================================================


def _compile_rules(rules):
    """
    Compiles the rules patterns for efficient matching, converting 'r'-prefixed
    patterns to regex objects.

    This function processes each pattern in the nested rules dictionary: if a
    pattern starts with 'r', it is compiled into a case-insensitive regex
    pattern; otherwise, it is converted to lowercase for substring matching.

    Args:
        rules (dict): The nested rules dictionary
        {category: {subcategory: [pattern]}}.

    Returns:
        dict: A compiled nested rules dictionary with patterns as strings or
        re.Pattern objects.

    Raises:
        re.error: If a regex pattern is invalid.

    Example:
        >>> rules = {'Cat': {'Sub': ['keyword', 'r[a-z]+']}}
        >>> compiled = _compile_rules(rules)
        >>> assert isinstance(compiled['Cat']['Sub'][1], re.Pattern)
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
                re.compile(pat[1:], re.IGNORECASE)
                if pat.startswith("r")
                else pat.lower()
                for pat in pats
            ]

    # Return compiled rules
    return compiled_rules


# ================================================
# Modular helper: Apply rules to a row
# ================================================


def _apply_rules_to_row(row, compiled_rules, overwrite):
    """
    Applies compiled rules to assign a category and subcategory to a single
    DataFrame row based on its description.

    This function checks if the row already has a category and respects the
    overwrite flag. It lowers the description for matching and iterates
    through the compiled rules, returning the first matching category and
    subcategory. Regex patterns use search(), while string patterns check
    for substring presence.

    Args:
        row (pd.Series): A single row from the DataFrame, containing at
        least 'description' and 'category'.
        compiled_rules (dict): The compiled rules dictionary.
        overwrite (bool): If True, applies rules even if a category already
        exists.

    Returns:
        tuple: (category, subcategory) - The assigned or existing values.

    Example:
        >>> row = pd.Series({'description': 'Buy at TESCO', 'category': None})
        >>> compiled_rules = {'Food/Dining': {'Groceries': ['tesco']}}
        >>> cat, sub = _apply_rules_to_row(row, compiled_rules, True)
        >>> print(cat, sub)
        'Food/Dining' 'Groceries'
    """
    # If category exists and no overwrite, keep existing
    if pd.notna(row["category"]) and not overwrite:
        # Return existing category and subcategory (if any)
        return row["category"], row.get("subcategory", None)

    # Lowercase description for matching
    desc = (
        row["description"].lower()
        if isinstance(row["description"], str)
        else ""
    )

    # Iterate over categories, subcategories, and patterns
    for category, subcats in compiled_rules.items():
        for subcategory, patterns in subcats.items():
            for pat in patterns:
                # Check for match (regex search or substring)
                if (isinstance(pat, re.Pattern) and pat.search(desc)) or (
                    isinstance(pat, str) and pat in desc
                ):
                    # Return first matching category and subcategory
                    return category, subcategory

    # If no match, return original (likely None)
    return row["category"], row.get("subcategory", None)


# ================================================
# Modular helper: Detect conflicts
# ================================================
def _detect_conflicts(df):
    """
    Detects categorisation conflicts in the DataFrame, such as changes from
    original categories or inconsistencies across similar descriptions.

    This function adds a 'conflict' boolean column to the DataFrame. Conflicts
    are flagged if a category has changed from its original value or if the
    same description has multiple different categories across rows.

    Args:
        df (pd.DataFrame): The DataFrame with 'description', 'category', and
        'original_category' columns.

    Returns:
        pd.DataFrame: The updated DataFrame with an added 'conflict' column.

    Example:
        >>> df = pd.DataFrame({'description': ['TESCO', 'TESCO'],
        ... 'category': ['Food', 'Transport'],
        ... 'original_category': ['Food', 'Food']})
        >>> updated_df = _detect_conflicts(df)
        >>> print(updated_df['conflict'].all())
        True  # Conflicts due to inconsistency and change
    """
    # Initialise conflict column as False
    df["conflict"] = False

    # Conflict if category changed from original (without overwrite intent);
    # Set True if changed
    df["conflict"] = (df["original_category"].notna()) & (
        df["original_category"] != df["category"]
    )

    # Check for similar transactions with different categories (group by
    # description) Count unique categories per description
    grouped = df.groupby("description")["category"].nunique()

    # Get descriptions with more than 1 category
    conflicting_desc = grouped[grouped > 1].index

    # Set conflict True for those
    df.loc[df["description"].isin(conflicting_desc), "conflict"] = True

    # Return updated DataFrame
    return df


# ================================================
# Modular helper: Save categorised DataFrame
# ================================================


def _save_categorised(df, categorised_dir):
    """
    Saves the categorised DataFrame to a timestamped CSV file in the specified
    directory.

    This function creates the directory if it does not exist, generates a
    unique filename based on the current timestamp, and saves the DataFrame
    without the index. It prints the save path and a reminder to review flagged
    rows.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        categorised_dir (str): The path to the directory where the file should
        be saved.

    Returns:
        str: The full path to the saved CSV file.

    Raises:
        OSError: If directory creation or file writing fails.

    Example:
        >>> df = pd.DataFrame({'date': ['2025-01-01'],
        ... 'description': ['TESCO'], 'category': ['Food/Dining']})
        >>> save_path = _save_categorised(df, 'output_dir')
        Saved categorised data to output_dir/2025-11-07_12-00-00.csv.
        Review rows where 'review' is not NaN manually.
    """
    # Create directory if it doesn't exist
    os.makedirs(categorised_dir, exist_ok=True)

    # Create timestamped filename
    save_path = os.path.join(
        categorised_dir,
        pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv",
    )

    # Save DataFrame to CSV without index
    df.to_csv(save_path, index=False)
    print(
        f"Saved categorised data to {save_path}. Review rows where "
        f"'review' is not NaN manually."
    )

    # Return the save path
    return save_path


# ================================================
# Main function: auto_categorise
# ================================================


def auto_categorise(
    df, rules_file=None, overwrite=False, categorised_dir="categorised/"
):
    """
    Automatically categorises transactions in a DataFrame using rules,
    machine learning, or a hybrid approach based on available data.

    This function initialises category/subcategory columns if missing,
    loads rules and historical categorised data, determines the categorisation
    mode (rules-only, hybrid, or full ML) based on the amount of labeled data,
    applies the appropriate method, detects conflicts, flags rows for review,
    and saves the updated DataFrame to a timestamped file.

    Args:
        df (pd.DataFrame): The input DataFrame with at least 'description';
                           'category' may be partially filled.
        rules_file (str, optional): Path to the rules CSV file. Defaults to
                                    bundled 'metadata/rules.csv'.
        overwrite (bool, optional): If True, re-applies categorisation even to
                                    existing categories. Defaults to False.
        categorised_dir (str, optional): Directory for historical categorised
                                         CSVs. Defaults to 'categorised/'.

    Returns:
        pd.DataFrame: The updated DataFrame with 'category', 'subcategory',
                      and 'review' columns added/filled.

    Raises:
        ValueError: Propagated from load_rules_file() if rules CSV is invalid.
        Other exceptions: From underlying functions like model training or file
                          operations.

    Example:
        >>> df = pd.DataFrame({'description': ['TESCO STORE', 'UBER TRIP']})
        >>> categorised_df = auto_categorise(df)
        No or insufficient previously categorised/labeled data; using rules
        only.
        Saved categorised data to categorised/2025-11-07_12-00-00.csv. ...
        >>> print(categorised_df['category'].tolist())
        ['Food/Dining', 'Transportation']
    """
    # 1. Initialise category and subcategory if not present
    # =========================================================================
    # Check and add category column if missing
    if "category" not in df.columns:
        df["category"] = None

    # Check and add subcategory column if missing
    if "subcategory" not in df.columns:
        df["subcategory"] = None

    # 2. Snapshot original for conflict detection
    # =========================================================================
    # Copy original categories for later comparison
    df["original_category"] = df["category"].copy()

    # 3. Load rules (always, as fallback/hybrid) and previously categorised
    # data (if present)
    # =========================================================================
    # Load rules from file and compile for matching
    rules = _load_rules_file(rules_file)
    compiled_rules = _compile_rules(rules)

    # Load previously categorised
    all_categorised = _load_categorised(categorised_dir)

    # 4. Prepare labeled/unlabeled (combine previously categorised +
    # df's pre-labeled)
    # =========================================================================
    # Concatenate previously categorised labeled and current labeled
    labeled = pd.concat(
        [
            all_categorised[
                all_categorised["category"].notna()
                & all_categorised["category"].ne("")
            ],
            df[df["category"].notna() & df["category"].ne("")],
        ],
        ignore_index=True,
    )  # Reset index

    # Select unlabeled in current df
    # unlabeled = df[df['category'].isna() | df['category'].eq('')]

    # 5. Determine mode based on data availability (no explicit use_ml param;
    # auto-detect)
    # =========================================================================
    # Mode 1: Rules only (no/insufficient previously categorised/data);
    #         If no previously categorised or few labeled, use rules only
    #         and apply rules to each row
    if len(all_categorised) == 0 or len(labeled) < 10:
        print(
            "No or insufficient previously categorised/labeled data; "
            "using rules only."
        )

        # Get, and apply, rules
        df[["category", "subcategory"]] = df.apply(
            lambda row: pd.Series(
                _apply_rules_to_row(row, compiled_rules, overwrite)
            ),
            axis=1,
        )

    # Mode 2: Hybrid (rules + ML) for limited data or potential conflicts;
    #         If previously categorised data is "limited" (less than 500
    #         labels), use hybrid
    elif len(labeled) < 500:
        print("Limited labeled data; using ML + rules hybrid.")

        # Get, and apply, model
        models = _get_ml_model(labeled)
        if models["category"]:
            df = _apply_ml(df, models)

        # Then apply rules (as hybrid/fallback, sets both)
        df[["category", "subcategory"]] = df.apply(
            lambda row: pd.Series(
                _apply_rules_to_row(row, compiled_rules, overwrite)
            ),
            axis=1,
        )

    # Mode 3: Full ML when enough data for over 500 labelled historical data
    else:
        print("Sufficient labeled data; using full ML.")

        # Get, and apply, model
        models = _get_ml_model(labeled)
        if models["category"]:
            df = _apply_ml(df, models)

        # Fallback to rules if model fails (safetynet)
        else:
            print("ML model unavailable; falling back to rules.")

            # Apply rules
            df[["category", "subcategory"]] = df.apply(
                lambda row: pd.Series(
                    _apply_rules_to_row(row, compiled_rules, overwrite)
                ),
                axis=1,
            )

    # Detect conflicts and add conflict column
    df = _detect_conflicts(df)

    # Create single 'review' column
    df["review"] = None
    uncat_mask = df["category"].isna() | df["category"].eq("")
    df.loc[uncat_mask, "review"] = "uncategorised"
    df.loc[df["conflict"], "review"] = "category conflict - review and resolve"

    # Print review summary
    review_count = df["review"].notna().sum()
    conflict_count = df["review"].str.contains("conflict", na=False).sum()
    if review_count > 0:
        print(
            f"{review_count} rows need manual review (including "
            f"{conflict_count} conflicts)."
        )

    # Drop temp columns (Remove temporary columns)
    df.drop(
        columns=["original_category", "conflict"],
        errors="ignore",
        inplace=True,
    )

    # Save updated df (categorised DataFrame)
    _save_categorised(df, categorised_dir)

    # Return the updated DataFrame
    return df
