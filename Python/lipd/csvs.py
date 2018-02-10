import csv
import math
import sys
import copy
from collections import OrderedDict

from .directory import list_files
from .loggers import create_logger
from .inferred_data import get_inferred_data_table
from .misc import cast_values_csvs, cast_int, get_missing_value_key, _replace_missing_values_table, rm_missing_values_table, is_ensemble, decimal_precision

logger_csvs = create_logger("csvs")


# MERGE - CSV w/ Metadata


def merge_csv_metadata(d, csvs):
    """
    Using the given metadata dictionary, retrieve CSV data from CSV files, and insert the CSV
    values into their respective metadata columns. Checks for both paleoData and chronData tables.

    :param dict d: Metadata
    :return dict: Modified metadata dictionary
    """
    logger_csvs.info("enter merge_csv_metadata")

    # Add CSV to paleoData
    if "paleoData" in d:
        d["paleoData"] = _merge_csv_section(d["paleoData"], "paleo", csvs)

    # Add CSV to chronData
    if "chronData" in d:
        d["chronData"] = _merge_csv_section(d["chronData"], "chron", csvs)

    logger_csvs.info("exit merge_csv_metadata")
    return d


def _merge_csv_section(sections, pc, csvs):
    """
    Add csv data to all paleo data tables

    :param dict sections: Metadata
    :return dict sections: Metadata
    """
    logger_csvs.info("enter merge_csv_section")

    try:
        # Loop through each table_data in paleoData
        for _name, _section in sections.items():

            if "measurementTable" in _section:
                sections[_name]["measurementTable"] = _merge_csv_table(_section["measurementTable"], pc, csvs)

            if "model" in _section:
                sections[_name]["model"] = _merge_csv_model(_section["model"], pc, csvs)

    except Exception as e:
        print("Error: There was an error merging CSV data into the metadata ")
        logger_csvs.error("merge_csv_section: {}".format(e))

    logger_csvs.info("exit merge_csv_section")
    return sections


def _merge_csv_model(models, pc, csvs):
    """
    Add csv data to each column in chron model

    :param dict models: Metadata
    :return dict models: Metadata
    """
    logger_csvs.info("enter merge_csv_model")

    try:
        for _name, _model in models.items():

            if "summaryTable" in _model:
                models[_name]["summaryTable"] = _merge_csv_table(_model["summaryTable"], pc, csvs)

            if "ensembleTable" in _model:
                models[_name]["ensembleTable"] = _merge_csv_table(_model["ensembleTable"], pc, csvs)

            if "distributionTable" in _model:
                models[_name]["distributionTable"] = _merge_csv_table(_model["distributionTable"], pc, csvs)

    except Exception as e:
        logger_csvs.error("merge_csv_model: {}",format(e))

    logger_csvs.info("exit merge_csv_model")
    return models


def _merge_csv_table(tables, pc, csvs):

    try:

        for _name, _table in tables.items():
            # Get the filename of this table
            filename = _get_filename(_table)
            ensemble = False
            # If there's no filename, bypass whole process because there's no way to know which file to open
            if not filename:
                print("Error: merge_csv_column: No filename found for table")
            else:
                # Call read_csv_to_columns for this filename. csv_data is list of lists.
                _one_csv = csvs[filename]

                # If all the data columns are non-numeric types, then a missing value is not necessary
                _only_numerics = _is_numeric_data(_one_csv)

                if not _only_numerics:
                    # Get the Missing Value key from the table-level data
                    _mv = get_missing_value_key(_table)
                    if _mv:
                        # Use the Missing Value key to replace all current missing values with "nan"
                        _one_csv = _replace_missing_values_table(_one_csv, _mv)
                    else:
                        print("No missing value found. You may encounter errors with this data.")
                # Merge the values into the columns
                _table, ensemble = _merge_csv_column(_table, _one_csv)
                # Remove and missing values keys that are at the column level
                _table = rm_missing_values_table(_table)
                # Now put the missing value as "nan" (standard)
                _table["missingValue"] = "nan"

            if not ensemble:
                # calculate inferred data before leaving this section! paleo AND chron tables
                _table = get_inferred_data_table(_table, pc)

            tables[_name] = _table
    except Exception as e:
        print("Error: merge_csv_table: {}, {}".format(pc, e))
        logger_csvs.error("merge_csv_table: {}, {}".format(pc, e))

    return tables


def _merge_csv_column(table, csvs):
    """
    Add csv data to each column in a list of columns

    :param dict table: Table metadata
    :param str crumbs: Hierarchy crumbs
    :param str pc: Paleo or Chron table type
    :return dict: Table metadata with csv "values" entry
    :return bool ensemble: Ensemble data or not ensemble data
    """

    # Start putting CSV data into corresponding column "values" key
    try:
        ensemble = is_ensemble(table["columns"])
        if ensemble:
            # realization columns
            if len(table["columns"]) == 1:
                for _name, _column in table["columns"].items():
                    _column["values"] = csvs
            # depth column + realization columns
            elif len(table["columns"]) == 2:
                _multi_column = False
                for _name, _column in table["columns"].items():
                    if isinstance(_column["number"], (int, float)):
                        col_num = cast_int(_column["number"])
                        _column['values'] = csvs[col_num - 1]
                    elif isinstance(_column["number"], list):
                        if _multi_column:
                            raise Exception("Error: merge_csv_column: This jsonld metadata looks wrong!\n"
                                  "\tAn ensemble table depth should not reference multiple columns of CSV data.\n"
                                  "\tPlease manually fix the ensemble columns in 'metadata.jsonld' inside of your LiPD file.")
                        else:
                            _multi_column = True
                            _column["values"] = csvs[2:]
        else:
            for _name, _column in table['columns'].items():
                col_num = cast_int(_column["number"])
                _column['values'] = csvs[col_num - 1]
    except IndexError:
        logger_csvs.warning("merge_csv_column: IndexError: index out of range of csv_data list")
    except KeyError:
        logger_csvs.error("merge_csv_column: KeyError: missing columns key")
    except Exception as e:
        logger_csvs.error("merge_csv_column: Unknown Error:  {}".format(e))
        print("Quitting...")
        exit(1)

    # We want to keep one missing value ONLY at the table level. Remove MVs if they're still in column-level
    return table, ensemble


# READ


def read_csvs():
    """


    :return:
    """
    logger_csvs.info("enter read_csvs")
    _l = {}
    for filename in list_files(".csv"):
        _l[filename] = read_csv_from_file(filename)

    return _l


def read_csv_from_file(filename):
    """
    Opens the target CSV file and creates a dictionary with one list for each CSV column.

    :param str filename:
    :return list of lists: column values
    """
    logger_csvs.info("enter read_csv_from_file")
    d = {}
    l = []
    try:
        logger_csvs.info("open file: {}".format(filename))
        with open(filename, 'r') as f:
            r = csv.reader(f, delimiter=',')

            # Create a dict with X lists corresponding to X columns
            for idx, col in enumerate(next(r)):
                d[idx] = []
                d = cast_values_csvs(d, idx, col)

            # Start iter through CSV data
            for row in r:
                for idx, col in enumerate(row):
                    # Append the cell to the correct column list
                    d = cast_values_csvs(d, idx, col)

        # Make a list of lists out of the dictionary instead
        for idx, col in d.items():
            l.append(col)
    except FileNotFoundError as e:
        print('CSV FileNotFound: ' + filename)
        logger_csvs.warn("read_csv_to_columns: FileNotFound: {}, {}".format(filename, e))
    logger_csvs.info("exit read_csv_from_file")
    return l


# WRITE


def write_csv_to_file(d):
    """
    Writes columns of data to a target CSV file.

    :param dict d: A dictionary containing one list for every data column. Keys: int, Values: list
    :return None:
    """
    logger_csvs.info("enter write_csv_to_file")

    try:
        for filename, data in d.items():
            try:
                l_columns = _reorder_csv(data, filename)
                rows = zip(*l_columns)
                with open(filename, 'w+') as f:
                    w = csv.writer(f)
                    for row in rows:
                        row2 = decimal_precision(row)
                        w.writerow(row2)
            except TypeError as e:
                print("Error: Unable to write values to CSV file, {}:\n"
                      "(1) The data table may have 2 or more identical variables. Please correct the LiPD file manually\n"
                      "(2) There may have been an error trying to prep the values for file write. The 'number' field in the data columns may be a 'string' instead of an 'integer' data type".format(filename))
                print(e)
            except Exception as e:
                print("Error: CSV file not written, {}, {}:\n"
                      "The data table may have 2 or more identical variables. Please correct the LiPD file manually".format(filename, e))
    except AttributeError as e:
        logger_csvs.error("write_csv_to_file: Unable to write CSV File: {}".format(e, exc_info=True))
    logger_csvs.info("exit write_csv_to_file")
    return


# GET


def get_csv_from_metadata(dsn, d):
    """
    Two goals. Get all csv from metadata, and return new metadata with generated filenames to match files.

    :param str dsn: Dataset name
    :param dict d: Metadata
    :return dict _csvs: Csv
    """
    logger_csvs.info("enter get_csv_from_metadata")
    _csvs = OrderedDict()
    _d = copy.deepcopy(d)

    try:
        if "paleoData" in _d:
            # Process paleoData section
            _d["paleoData"], _csvs = _get_csv_from_section(_d["paleoData"], "{}.paleo".format(dsn), _csvs)

        if "chronData" in _d:
            _d["chronData"], _csvs = _get_csv_from_section(_d["chronData"], "{}.chron".format(dsn), _csvs)

    except Exception as e:
        print("Error: get_csv_from_metadata: {}, {}".format(dsn, e))
        logger_csvs.error("get_csv_from_metadata: {}, {}".format(dsn, e))

    logger_csvs.info("exit get_csv_from_metadata")
    return _d, _csvs


def _get_csv_from_section(sections, crumbs, csvs):
    """
    Get table name, variable name, and column values from paleo metadata

    :param dict sections: Metadata
    :param str crumbs: Crumbs
    :param dict csvs: Csv
    :return dict sections: Metadata
    :return dict csvs: Csv
    """
    logger_csvs.info("enter get_csv_from_section: {}".format(crumbs))
    _idx = 0
    try:
        # Process the tables in section
        for _name, _section in sections.items():

            # Process each entry sub-table below if they exist
            if "measurementTable" in _section:
                sections[_name]["measurementTable"], csvs = _get_csv_from_table(_section["measurementTable"],"{}{}{}".format(crumbs, _idx, "measurement") , csvs)
            if "model" in _section:
                sections[_name]["model"], csvs = _get_csv_from_model(_section["model"], "{}{}{}".format(crumbs, _idx, "model") , csvs)
            _idx += 1

    except Exception as e:
        logger_csvs.error("get_csv_from_section: {}, {}".format(crumbs, e))
        print("Error: get_csv_from_section: {}, {}".format(crumbs, e))

    logger_csvs.info("exit get_csv_from_section: {}".format(crumbs))
    return sections, csvs


def _get_csv_from_model(models, crumbs, csvs):
    """
    Get csv from model data

    :param dict models: Metadata
    :param str crumbs: Crumbs
    :param dict csvs: Csv
    :return dict models: Metadata
    :return dict csvs: Csv
    """
    logger_csvs.info("enter get_csv_from_model: {}".format(crumbs))
    _idx = 0
    try:
        for _name, _model in models.items():
            if "distributionTable" in _model:
                models[_name]["distributionTable"], csvs = _get_csv_from_table(_model["distributionTable"], "{}{}{}".format(crumbs, _idx, "distribution"), csvs)

            if "summaryTable" in _model:
                models[_name]["summaryTable"], csvs = _get_csv_from_table(_model["summaryTable"], "{}{}{}".format(crumbs, _idx, "summary"), csvs)

            if "ensembleTable" in _model:
                models[_name]["ensembleTable"], csvs = _get_csv_from_table(_model["ensembleTable"], "{}{}{}".format(crumbs, _idx, "ensemble"), csvs)
            _idx += 1
    except Exception as e:
        print("Error: get_csv_from_model: {}, {}".format(crumbs, e))
        logger_csvs.error("Error: get_csv_from_model: {}, {}".format(crumbs, e))
    return models, csvs


def _get_csv_from_table(tables, crumbs, csvs):
    _idx = 0
    try:
        for _name, _table in tables.items():
            filename = "{}{}.csv".format(crumbs, _idx)
            # Set the filename inside the metadata also, so our _csv and _meta will match
            _table = _put_filename(_table, filename)
            # Get a nested list of table values
            csvs = _get_csv_from_columns(_table, filename, csvs)
            tables[_name] = _table
            _idx += 1
    except Exception as e:
        print("Error: get_csv_from_table: {}, {}".format(crumbs, e))
        logger_csvs.error("Error: get_csv_from_table: {}, {}".format(crumbs, e))

    return tables, csvs


def _get_csv_from_columns(table, filename, csvs):
    """
    Search a data tables for column values. Return a dict of column values
    :param dict d: Table data
    :return dict: Column values. ref by var name
    """
    csvs[filename] = OrderedDict()
    try:
        if "columns" in table:
            try:
                for _name, _column in table["columns"].items():
                    csvs[filename][_name] = {"number": _column["number"], "values": _column["values"]}
            except KeyError as ke:
                print("Error: get_csv_from_columns: {}, {}".format(filename, ke))
            except Exception as e:
                print("Error: get_csv_from_columns: inner: {}, {}".format(filename, e))
                logger_csvs.error("get_csv_from_columns: inner: {}, {}".format(filename, e))
    except Exception as e:
        print("Error: get_csv_from_columns: {}, {}".format(filename, e))
        logger_csvs.error("get_csv_from_columns: {}, {}".format(filename, e))

    return csvs


def _get_filename(table):
    """
    Get the filename from a data table. If it doesn't exist, create a new one based on table hierarchy in metadata file.
    format: <dataSetName>.<section><idx><table><idx>.csv
    example: ODP1098B.Chron1.ChronMeasurementTable.csv

    :param dict table: Table data
    :param str crumbs: Crumbs
    :return str filename: Filename
    """
    try:
        filename = table["filename"]
    except KeyError:
        logger_csvs.info("get_filename: KeyError: missing filename for a table")
        print("Error: Missing filename for a table")
        filename = ""
    except Exception as e:
        logger_csvs.error("get_filename: {}".format(e))
        filename = ""
    return filename


def _get_dataset_name(d):
    """
    Get data set name from metadata

    :param dict d: Metadata
    :return str: Data set name
    """
    try:
        s = d["dataSetName"]
    except KeyError:
        logger_csvs.warn("get_dataset_name: KeyError: missing dataSetName")
        s = "lipds"
    return s


# PUT


def _put_filename(table, filename):
    """
    Overwrite filename in table with our standardized filename

    :param dict table: Metadata
    :param str filename: Crumbs filename
    :return dict: Metadata
    """
    try:
        table["filename"] = filename
    except KeyError:
        logger_csvs.info("_set_filename: KeyError, Unable to set filename into table")
    return table


# HELPERS

def _reorder_csv(d, filename=""):
    """
    Preserve the csv column ordering before writing back out to CSV file. Keep column data consistent with JSONLD
    column number alignment.
    { "var1" : {"number": 1, "values": [] }, "var2": {"number": 1, "values": [] } }

    :param dict d: csv data
    :param str filename: Filename
    :return dict: csv data
    """
    _ensemble = is_ensemble(d)
    _d2 = []
    try:
        if _ensemble:
            # 1 column ensemble: realizations
            if len(d) == 1:
                for var, data in d.items():
                    if "values" in data:
                        _d2 = data["values"]
            # 2 column ensemble: depth and realizations
            else:
                _count = 0
                # count up how many columns total, and how many placeholders to make in our list
                for var, data in d.items():
                    if isinstance(data["number"], list):
                        _curr_count = len(data["number"])
                        _count += _curr_count
                    elif isinstance(data["number"], (int, float, str)):
                        _count += 1
                # make a list with X number of placeholders
                _d2 = [None for i in range(0, _count)]
                # Loop again and start combining all columns into one list of lists
                for var, data in d.items():
                    # realizations: insert at (hopefully) index 1,2...1001
                    if isinstance(data["number"], list):
                        for idx, number in enumerate(data["number"]):
                            # we can't trust the number entries. sometimes they start at "number 1",
                            # which isn't true, because DEPTH is number 1. Use enumerate index instead.
                            _insert_at = int(idx) + 1
                            # Insert at one above the index. Grab values at exact index
                            _d2[_insert_at] = data["values"][idx-1]

                    # depth column: insert at (hopefully) index 0
                    else:
                        # we can trust to use the number entry as an index placement
                        _insert_at = int(data["number"]) - 1
                        # insert at one below number, to compensate for 0-index
                        _d2[_insert_at] = data["values"]
        else:
            _count = len(d)
            _d2 = [None for i in range(0, _count)]
            for key, data in d.items():
                _insert_at = int(data["number"]) - 1
                _d2[_insert_at] = data["values"]

    except Exception as e:
        print("Error: Unable to write CSV: There was an error trying to prep the values for file write: {}".format(e))
        logger_csvs.error("reorder_csvs: Unable to write CSV file: {}, {}".format(filename, e))
    return _d2


def _is_numeric_data(ll):
    """
    List of lists of csv values data
    :param list ll:
    :return bool: True, all lists are numeric lists, False, data contains at least one numeric list.
    """
    for l in ll:
        try:
            if any(math.isnan(float(i)) or isinstance(i, str) for i in l):
                return False
            # if not all(isinstance(i, (int, float)) or math.isnan(float(i)) for i in l):
            #     # There is an entry that is a non-numeric entry in this list
            #     return False
        except ValueError:
            # Trying to case a str as a float didnt work, and we got an error
            return False
    # All arrays are 100% numeric or "nan" entries.
    return True


def _merge_ensemble(ensemble, col_nums, col_vals):
    """
    The second column is not typical.
    "number" is a list of column numbers and "values" is an array of column values.
    Before we can write this to csv, it has to match the format the writer expects.
    :param dict ensemble: First column data
    :param list col_nums: Second column numbers. list of ints
    :param list col_vals: Second column values. list of lists
    :return dict:
    """
    try:
        # Loop for each column available
        for num in col_nums:
            # first column number in col_nums is usually "2", so backtrack once since ensemble already has one entry
            # col_vals is 0-indexed, so backtrack 2 entries
            ensemble[num-1] = col_vals[num - 2]

    except IndexError:
        logger_csvs.error("merge_ensemble: IndexError: index out of range")

    return ensemble

