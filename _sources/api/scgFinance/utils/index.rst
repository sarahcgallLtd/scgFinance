scgFinance.utils
================

.. py:module:: scgFinance.utils


Functions
---------

.. autoapisummary::

   scgFinance.utils.download_template
   scgFinance.utils.load_package_data


Module Contents
---------------

.. py:function:: download_template(root_dir = '.', rules_filename = 'rules.csv')

   Saves a predefined project structure to the specified root directory,
   populating it with metadata and a template script from the package.

   This function creates the following directory structure:
   - root_dir/
     - metadata/
       - rules.csv (or specified filename; default categorisation rules)
     - raw_data/
       - bank/ (empty directory to save bank statements)
       - credit_card/ (empty directory to save credit card statements)
     - categorise_statements.py (template script copied from package)

   Directories are created if they do not exist, and files are overwritten
   if they already exist. The sample data and template script are copied
   directly from the package resources to preserve original formatting.
   This is useful for setting up a new project with a standard template,
   improving ease of access by allowing users to initialise a local
   working directory with bundled examples. The rules.csv can be customised
   to be more specific to your financial statements. The
   categorise_statements.py is bundled in the package (e.g., at '
   scgFinance.data/categorise_statements.py') and copied to the root
   directory. Users can customise it after the template is saved.

   :param root_dir: The path to the root directory where the structure
                    will be saved. Defaults to '.' (current working
                    directory).
   :type root_dir: str
   :param rules_filename: The filename for the rules CSV in
                          metadata/. Defaults to "rules.csv"
                          to match the requested structure.
   :type rules_filename: str, optional

   :returns: None

   :raises OSError: If there are issues creating directories or writing files.
   :raises ImportError or AttributeError: If issues occur accessing package
       resources.

   .. rubric:: Example

   >>> download_template('/path/to/my_project')
   # Creates the structure in /path/to/my_project

   >>> donwload_template('/path/to/my_project',
   ... rules_filename='custom_rules.csv')
   # Uses 'custom_rules.csv' instead of 'rules.csv'


.. py:function:: load_package_data(data_type, save_path = None)

   Loads bundled package data from CSV files based on the specified data type.

   This utility function accesses sample data or metadata files packaged
   within the 'scgFinance' module using importlib.resources. It supports
   loading example bank statements, credit card statements, or default
   categorisation rules. The file paths are resolved dynamically, and the
   contents are read into a pandas DataFrame. This is useful for testing,
   demonstrations, or default configurations without requiring external
   file access.

   Optionally, if a save_path is provided, the loaded DataFrame will be
   saved as a CSV file to the specified local path on the user's computer.

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
   :param save_path: The local file path where the loaded
                     DataFrame should be saved as a CSV.
                     If None (default), no save operation
                     is performed.
   :type save_path: str, optional

   :returns:

             A DataFrame containing the loaded data from the specified
                           CSV file.
   :rtype: pd.DataFrame

   :raises ValueError: If an invalid 'data_type' is provided (not one of 'bank',
       'credit_card', or 'rules').
   :raises FileNotFoundError: If the bundled file is missing (though this should
       not occur in a properly packaged module).
   :raises pandas.errors: If there are issues parsing the CSV file.
   :raises OSError: If there are issues saving to the provided save_path (e.g.,
       invalid directory or permissions issues).

   .. rubric:: Example

   >>> bank_df = load_package_data('bank',
   ... save_path='~/Desktop/bank_data.csv')
   >>> print(bank_df.columns)
   Index(['Date', 'Description', 'Amount'], dtype='object')
   # Example columns; data is also saved to '~/Desktop/bank_data.csv'

   >>> rules_df = load_package_data('rules')
   >>> print(rules_df.head())
     category subcategory pattern
   0  Food/Dining   Groceries   TESCO
   ...


