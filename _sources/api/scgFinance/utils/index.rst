scgFinance.utils
================

.. py:module:: scgFinance.utils


Functions
---------

.. autoapisummary::

   scgFinance.utils.load_package_data


Module Contents
---------------

.. py:function:: load_package_data(data_type)

   Loads bundled package data from CSV files based on the specified data type.

   This utility function accesses sample data or metadata files packaged
   within the 'scgFinance' module using importlib.resources. It supports
   loading example bank statements, credit card statements, or default
   categorisation rules. The file paths are resolved dynamically, and the
   contents are read into a pandas DataFrame. This is useful for testing,
   demonstrations, or default configurations without requiring external
   file access.

   :param data_type: The type of data to load. Valid options are:
                     - 'bank': Loads the sample bank statement from
                               'scgFinance.data.raw_data.bank/251031
                               Example Bank Statement.csv'.
                     - 'credit_card': Loads the sample credit card statement from
                                      'scgFinance.data.raw_data.credit_card/251031
                                      Example Credit Card Statement.csv'.
                     - 'rules': Loads the default categorisation rules from
                                'scgFinance.data.metadata/rules.csv'.
   :type data_type: str

   :returns:

             A DataFrame containing the loaded data from the specified
                           CSV file.
   :rtype: pd.DataFrame

   :raises ValueError: If an invalid 'data_type' is provided (not one of 'bank',
       'credit_card', or 'rules').
   :raises FileNotFoundError: If the bundled file is missing (though this should
       not occur in a properly packaged module).
   :raises pandas.errors: If there are issues parsing the CSV file.

   .. rubric:: Example

   >>> bank_df = load_package_data('bank')
   >>> print(bank_df.columns)
   Index(['Date', 'Description', 'Amount'], dtype='object')
   # Example columns

   >>> rules_df = load_package_data('rules')
   >>> print(rules_df.head())
     category subcategory pattern
   0  Food/Dining   Groceries   TESCO
   ...


