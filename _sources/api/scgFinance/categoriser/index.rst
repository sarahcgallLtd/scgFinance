scgFinance.categoriser
======================

.. py:module:: scgFinance.categoriser


Functions
---------

.. autoapisummary::

   scgFinance.categoriser.auto_categorise


Module Contents
---------------

.. py:function:: auto_categorise(df, rules_file=None, categorised_file='categorised.csv', add_col=None)

   Automatically categorises transactions in a DataFrame using rules,
   machine learning, or a hybrid approach based on available data.

   This function initialises category/subcategory columns if missing,
   loads rules and previously categorised data, determines the categorisation
   mode (rules-only, hybrid, or full ML) based on the amount of labeled data,
   applies the appropriate method, detects conflicts, flags rows for review,
   and appends updated categorised data to the specified file.

   :param df: The input DataFrame with at least 'description';
              'category' may be partially filled.
   :type df: pd.DataFrame
   :param rules_file: Path to the rules CSV file. Defaults to
                      bundled 'metadata/rules.csv'.
   :type rules_file: str, optional
   :param categorised_file: Path to the categorised CSV file for
                            loading and appending. Defaults to
                            'categorised.csv'
   :type categorised_file: str, optional
   :param add_col: Add personalised column(s) to dataset (e.g.,
                   to manually flag reimbursement expenses).
                   Defaults to 'None'.
   :type add_col: str, optional

   :returns:

             The updated DataFrame with 'category', 'subcategory',
                           'review', 'added_at', and any additional columns added/filled.
   :rtype: pd.DataFrame

   :raises ValueError: Propagated from load_rules_file() if rules CSV is invalid.
   :raises Other exceptions: From underlying functions like model training or file
       operations.

   .. rubric:: Example

   >>> df = pd.DataFrame({'description': ['TESCO STORE', 'UBER TRIP']})
   >>> categorised_df = auto_categorise(df)
   No or insufficient previously categorised/labeled data; using rules
   only.
   Appended categorised data to categorised.csv. ...
   >>> print(categorised_df['category'].tolist())
   ['Food/Dining', 'Transportation']


