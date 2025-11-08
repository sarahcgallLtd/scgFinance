scgFinance.importers
====================

.. py:module:: scgFinance.importers


Functions
---------

.. autoapisummary::

   scgFinance.importers.import_statements


Module Contents
---------------

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


