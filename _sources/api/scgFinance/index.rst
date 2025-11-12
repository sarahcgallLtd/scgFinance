scgFinance
==========

.. py:module:: scgFinance


Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/scgFinance/categoriser/index
   /api/scgFinance/importers/index
   /api/scgFinance/pipeline/index
   /api/scgFinance/utils/index


Functions
---------

.. autoapisummary::

   scgFinance.auto_categorise
   scgFinance.download_template
   scgFinance.import_statements
   scgFinance.load_package_data
   scgFinance.process_statements


Package Contents
----------------

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
                           'review', 'added_at', and any additional columns
                           added/filled.
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


.. py:function:: download_template(root_dir = '.', rules_filename = 'rules.csv')

   Saves a predefined project structure to the specified root directory,
   populating it with metadata and a template script from the package.

   This function creates the following directory structure:
   - root_dir/
     - categorised/ (empty directory)
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


.. py:function:: import_statements(path, source=None, date_col='Date', date_format='%d/%m/%Y', time_col=None, time_format='%H:%M:%S', desc_col='Description', amt_col='Amount', metadata_file='metadata/processed_files.csv')

   Orchestrates the import of financial statements from one or more CSV
   files, ensuring only unprocessed files are handled.

   This is the primary entry point for importing data. It loads metadata to
   track processed files, filters out already processed ones, processes
   each remaining file using process_single_file(), concatenates the
   results into a single DataFrame sorted by date, and returns the
   combined DataFrame along with a list of imported file base names.
   Note that this function does not update the metadata; that should be
   handled by the caller after successful processing.

   :param path: The path to a single CSV file or a directory containing
                CSV files.
   :type path: str
   :param source: The source identifier (e.g., 'credit card').
                  Required for metadata filtering.
   :type source: str, optional
   :param date_col: The date column name. Defaults to 'Date'.
   :type date_col: str, optional
   :param date_format: The date format string. Defaults to
                       '%d/%m/%Y'.
   :type date_format: str, optional
   :param time_col: The time column name. Defaults
                    to None.
   :type time_col: str or None, optional
   :param time_format: The time format string. Defaults to
                       '%H:%M:%S'.
   :type time_format: str, optional
   :param desc_col: The description column(s).
                    Defaults to 'Description'.
   :type desc_col: str or list, optional
   :param amt_col: The amount column name. Defaults to 'Amount'.
   :type amt_col: str, optional
   :param metadata_file: The path to the metadata CSV.
                         Defaults to
                         'metadata/processed_files.csv'.
   :type metadata_file: str, optional

   :returns:

                 - pd.DataFrame: The combined, sorted DataFrame of all
                                 processed files.
                 - list: A list of base names of the imported (processed) files.
   :rtype: tuple

   :raises ValueError: If path or source is not specified, or if no files
       are found/processed.

   .. rubric:: Example

   >>> df, files = import_statements('raw_data/bank/', 'bank')
   >>> print(df.shape)
   (100, 4)  # Example output
   >>> print(files)
   ['statement_2023.csv']


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


.. py:function:: process_statements(sources, metadata_file='metadata/processed_files.csv', categorised_file='categorised/', add_col=None, rules_file=None)

   Orchestrates the full financial statement processing pipeline: importing,
   categorising, updating metadata, and appending results to a single file.

   This function processes statements from multiple sources by importing
   unprocessed files, combining them into a single DataFrame, applying
   automatic categorisation, updating the metadata to mark files as
   processed, and returning the categorised DataFrame. If no new transactions
   are found, an empty or original DataFrame is returned. Custom import
   parameters can be provided per source.

   :param sources:
                   A list of dictionaries, each specifying a
                                       source configuration:
                   - 'path' (str): Path to the file or directory of CSV statements.
                   - 'source' (str): Identifier for the source (e.g., 'Lloyds',
                                     'HSBC').
                   - Optional keys: 'date_col', 'date_format', 'time_col',
                                    'time_format', 'desc_col', 'amt_col' for
                                    custom import settings.
   :type sources: list of dict
   :param metadata_file: Path to the metadata CSV for tracking
                         processed files. Defaults to
                         'metadata/processed_files.csv'.
   :type metadata_file: str, optional
   :param categorised_file: Path to the categorised CSV file for
                            loading and appending. Defaults to
                            'categorised.csv'
   :type categorised_file: str, optional
   :param add_col: Add personalised column(s) to dataset (e.g.,
                   to manually flag reimbursement expenses).
                   Defaults to 'None'.
   :type add_col: str, optional
   :param rules_file: Path to a custom rules CSV for
                      categorisation; None uses the default
                      bundled rules.
   :type rules_file: str, optional

   :returns:

             The combined and categorised DataFrame, or an empty
                           DataFrame if no new transactions were processed.
   :rtype: pd.DataFrame

   :raises ValueError: If 'path' or 'source' is missing in any source
       configuration, or if columns are not found during import.
   :raises Other exceptions: Propagated from import_statements() or
       auto_categorise(), such as FileNotFoundError for
       rules_file.

   .. rubric:: Example

   >>> sources = [
   ...     {'path': 'bank_statements/', 'source': 'bank',
   ...     'date_col': 'Date', 'date_format': '%d/%m/%Y',
   ...      'desc_col': 'Description', 'amt_col': 'Amount'}
   ... ]
   >>> df = process_statements(sources, rules_file='custom_rules.csv')
   >>> print(df.shape)
   (10, 7)  # Example assuming 10 transactions processed with 7 columns


