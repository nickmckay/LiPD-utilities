import csv
from ..helpers.loggers import *

logger_csvs = create_logger("csvs")


def add_csv_to_metadata(d):
    """
    Using the given metadata dictionary, retrieve CSV data from CSV files, and insert the CSV
    values into their respective metadata columns. Checks for both paleoData and chronData tables.
    :param dict d: Metadata
    :return dict: Modified metadata dictionary
    """
    logger_csvs.info("enter add_csv_to_json")

    # Add CSV to paleoData
    if "paleoData" in d:
        d["paleoData"] = _import_paleo_csv(d["paleoData"])

    # Add CSV to chronData
    if "chronData" in d:
        d["chronData"] = _import_chron_data_csv(d["chronData"])

    logger_csvs.info("exit add_csv_to_json")
    return d


def _add_csv_to_columns(table):
    """
    Add csv data to each column in a list of columns
    :param dict table: Table metadata
    :return dict: Table metadata with csv "values" entry
    """
    # Get the filename or this table
    filename = _get_table_csv_filename(table)

    # If there's no filename, bypass whole process
    if filename:
        # Call read_csv_to_columns for this filename. csv_data is list of lists.
        csv_data = _read_csv_to_columns(filename)

        # Start putting CSV data into corresponding column "values" key
        try:
            for col_name, col in table['columns'].items():
                # The "number" entry in the ensemble table is a list of columns, instead of an int.
                # In this case, just store all the csv data as a batch.
                if isinstance(col["number"], list):
                    col["values"] = csv_data
                # For all other cases, "number" is a single int, and "values" should hold one column list.
                else:
                    col['values'] = csv_data[col["number"] - 1]
        except IndexError:
            logger_csvs.warning("add_csv_to_json: IndexError: index out of range of csv_data list")

    return table


def _get_table_csv_filename(table):
    """
    Get the value from the filename field if the table has one
    :param dict table: Table metadata
    :return str: Filename
    """
    file = ""
    try:
        file = table["filename"]
    except KeyError:
        logger_csvs.info("get_table_csv_filename: KeyError: missing csv filename")
    return file


def _import_paleo_csv(paleo_data):
    """
    Add csv data to all paleo data tables
    :param dict paleo_data: Metadata
    :return dict: Modified metadata
    """
    logger_csvs.info("enter import_paleo_csv")

    # Loop through each table in paleoData
    for table_name, table in paleo_data.items():

        # Send whole table through. Adds csv data to columns
        paleo_data[table_name] = _add_csv_to_columns(table)

    logger_csvs.info("exit import_paleo_csv")
    return paleo_data


def _import_chron_data_csv(chron_data):
    """
    Wrapper function. Calls all the individual csv getter functions for chron related csv. Works on indexed-by-name
    dictionaries.
    :param dict chron_data: Metadata
    :return dict: Modified metadata
    """
    logger_csvs.info("enter import_chron_data_csv")
    for table_name, table_data in chron_data.items():

        # Process chronModel
        if "chronModel" in table_data:
            # Replace the chronModel in-place
            table_data["chronModel"] = _import_chron_model_csv(table_data["chronModel"])

        # Process chronMeasurementTable
        if "chronMeasurementTable" in table_data:
            # Replace the chronMeasurementTable in-place
            table_data["chronMeasurementTable"] = _add_csv_to_columns(table_data["chronMeasurementTable"])

    logger_csvs.info("exit import_chron_data_csv")
    return chron_data


def _import_chron_model_csv(chron_model):
    """
    Add csv data to each column in chron model
    :param list chron_model:
    :return:
    """
    logger_csvs.info("enter import_chron_model_csv")

    for model in chron_model:

        if "chronModelTable" in model:
            model["chronModelTable"] = _add_csv_to_columns(model["chronModelTable"])
        if "ensembleTable" in model:
            model["ensembleTable"] = _add_csv_to_columns(model["ensembleTable"])
        if "calibratedAges" in model:
            # Calibrated age tables are nested. Go down an extra layer.
            for k, v in model["calibratedAges"].items():
                model["calibratedAges"][k] = _add_csv_to_columns(v)

    logger_csvs.info("exit import_chron_model_csv")
    return chron_model


def _read_csv_to_columns(filename):
    """
    Opens the target CSV file and creates a dictionary with one list for each CSV column.
    :param str filename:
    :return list of lists: column values
    """
    logger_csvs.info("enter read_csv_to_columns")
    d = {}
    l = []
    try:
        with open(filename, 'r') as f:
            r = csv.reader(f, delimiter=',')
            # Create a dict with X lists corresponding to X columns
            for idx, col in enumerate(next(r)):
                d[idx] = []
            # Start iter through CSV data
            for row in r:
                for idx, col in enumerate(row):
                    # Append the cell to the correct column list
                    try:
                        d[idx].append(float(col))
                    except ValueError as e:
                        d[idx].append(col)
                        logger_csvs.warn("ValueError: col: {}, {}".format(col, e))
                    except KeyError as e:
                        logger_csvs.warn("KeyError: col: {}, {}".format(col, e))

        # Make a list of lists out of the dictionary instead
        for idx, col in d.items():
            l.append(col)

    except FileNotFoundError as e:
        print('CSV FileNotFound: ' + filename)
        logger_csvs.warn("read_csv_to_columns: FileNotFound: {}, {}".format(filename, e))
    logger_csvs.info("exit read_csv_to_columns")
    return l


def _write_csv_to_file(filename, d):
    """
    Writes columns of data to a target CSV file.
    :param str filename: Target CSV file
    :param dict d: A dictionary containing one list for every data column. Keys: int, Values: list
    :return None:
    """
    logger_csvs.info("enter write_csv_to_file")
    l_columns = []
    for k, v in d.items():
        l_columns.append(v)
    rows = zip(*l_columns)
    with open(filename, 'w+') as f:
        w = csv.writer(f)
        for row in rows:
            w.writerow(row)
    logger_csvs.info("exit write_csv_to_file")
    return

