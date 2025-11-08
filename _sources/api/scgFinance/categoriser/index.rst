scgFinance.categoriser
======================

.. py:module:: scgFinance.categoriser


Functions
---------

.. autoapisummary::

   scgFinance.categoriser.auto_categorise


Module Contents
---------------

.. py:function:: auto_categorise(df, rules_file=None, overwrite=False, categorised_dir='categorised')

   Automatically categorises transactions in a DataFrame using rules, machine learning, or a hybrid approach based on available data.

   This function initialises category/subcategory columns if missing, loads rules and historical categorised data, determines the
   categorisation mode (rules-only, hybrid, or full ML) based on the amount of labeled data, applies the appropriate method,
   detects conflicts, flags rows for review, and saves the updated DataFrame to a timestamped file.

   :param df: The input DataFrame with at least 'description'; 'category' may be partially filled.
   :type df: pd.DataFrame
   :param rules_file: Path to the rules CSV file. Defaults to bundled 'metadata/rules.csv'.
   :type rules_file: str, optional
   :param overwrite: If True, re-applies categorisation even to existing categories. Defaults to False.
   :type overwrite: bool, optional
   :param categorised_dir: Directory for historical categorised CSVs. Defaults to 'categorised'.
   :type categorised_dir: str, optional

   :returns: The updated DataFrame with 'category', 'subcategory', and 'review' columns added/filled.
   :rtype: pd.DataFrame

   :raises ValueError: Propagated from load_rules_file() if rules CSV is invalid.
   :raises Other exceptions: From underlying functions like model training or file operations.

   .. rubric:: Example

   >>> df = pd.DataFrame({'description': ['TESCO STORE', 'UBER TRIP']})
   >>> categorised_df = auto_categorise(df)
   No or insufficient previously categorised/labeled data; using rules only.
   Saved categorised data to categorised/2025-11-07_12-00-00.csv. ...
   >>> print(categorised_df['category'].tolist())
   ['Food/Dining', 'Transportation']


