scgFinance.pipeline
===================

.. py:module:: scgFinance.pipeline


Functions
---------

.. autoapisummary::

   scgFinance.pipeline.process_statements


Module Contents
---------------

.. py:function:: process_statements(sources, metadata_file='metadata/processed_files.csv', categorised_file='categorised.csv', add_col=None, rules_file=None)

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


