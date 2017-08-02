from .misc import rm_empty_fields, get_appended_name
from .loggers import create_logger

import demjson
from collections import OrderedDict
import os

logger_jsons = create_logger("jsons")


# IMPORT

def read_jsonld():
    """
    Find jsonld file in the cwd (or within a 2 levels below cwd), and load it in.
    :return dict: Jsonld data
    """
    _d = {}

    try:
        # Find a jsonld file in cwd. If none, fallback for a json file. If neither found, return empty.
        _filename = [file for file in os.listdir() if file.endswith(".jsonld")][0]
        if not _filename:
            _filename = [file for file in os.listdir() if file.endswith(".json")][0]

        if _filename:
            try:
                # Load and decode
                _d = demjson.decode_file(_filename, decode_float=float)
                logger_jsons.info("Read JSONLD successful: {}".format(_filename))
            except FileNotFoundError as fnf:
                print("Error: metadata file not found: {}".format(_filename))
                logger_jsons.error("read_jsonld: FileNotFound: {}, {}".format(_filename, fnf))
            except Exception as e:
                print("Error: unable to read metadata file: {}".format(e))
                logger_jsons.error("read_jsonld: Exception: {}, {}".format(_filename, e))
        else:
            print("Error: metadata file (.jsonld) not found in LiPD archive")
    except Exception as e:
        print("Error: Unable to find jsonld file in LiPD archive. This may be a corrupt file.")
        logger_jsons.error("Error: Unable to find jsonld file in LiPD archive. This may be a corrupt file.")
    logger_jsons.info("exit read_json_from_file")
    return _d


def read_json_from_file(filename):
    """
    Import the JSON data from target file.
    :param str filename: Target File
    :return dict: JSON data
    """
    logger_jsons.info("enter read_json_from_file")
    d = OrderedDict()
    try:
        # Load and decode
        d = demjson.decode_file(filename, decode_float=float)
        logger_jsons.info("successful read from json file")
    except FileNotFoundError:
        # Didn't find a jsonld file. Maybe it's a json file instead?
        try:
            d = demjson.decode_file(os.path.splitext(filename)[0] + '.json', decode_float=float)
        except FileNotFoundError as e:
            # No json or jsonld file. Exit
            print("Error: jsonld file not found: {}".format(filename))
            logger_jsons.debug("read_json_from_file: FileNotFound: {}, {}".format(filename, e))
        except Exception:
            print("Error: unable to read jsonld file")

    if d:
        d = rm_empty_fields(d)
    logger_jsons.info("exit read_json_from_file")
    return d


def idx_num_to_name(d):
    """
    Switch from index-by-number to index-by-name.
    :param dict d: Metadata
    :return dict: Modified Metadata
    """
    logger_jsons.info("enter idx_num_to_name")

    try:
        if "paleoData" in d:
            tmp_pd = _import_data(d["paleoData"], "paleo")
            d["paleoData"] = tmp_pd
        if "chronData" in d:
            tmp_cd = _import_data(d["chronData"], "chron")
            d["chronData"] = tmp_cd
    except Exception as e:
        logger_jsons.error("idx_num_to_name: Exception: {}".format(e))
    logger_jsons.info("exit idx_num_to_name")
    return d


def _import_data(section_data, crumbs):
    """
    Import the section metadata and change it to index-by-name.
    :param list section_data: Section metadata
    :param str pc: Paleo or Chron
    :return dict: Modified paleoData
    """
    logger_jsons.info("enter import_data: {}".format(crumbs))
    d = OrderedDict()
    try:
        for _idx, table in enumerate(section_data):
            tmp_table = OrderedDict()

            # Process the paleo measurement table
            if "measurementTable" in table:
                tmp_pmt = _import_meas(table["measurementTable"], "{}{}".format(crumbs, _idx))
                tmp_table["measurementTable"] = tmp_pmt

            # Process the paleo model
            if "model" in table:
                tmp_cm = _import_model(table["model"], crumbs + str(_idx))
                tmp_table["model"] = tmp_cm

            # Get the table name from the first measurement table, and use that as the index name for this table
            # _table_name = get_table_key("tableName", table, "{}{}".format(crumbs, _idx))
            _table_name = "{}{}".format(crumbs, _idx)

            # If we only have generic table names, and one exists already, don't overwrite. Create dynamic name
            if _table_name in d:
                _table_name = "{}_{}".format(_table_name, _idx)

            # Put the final product into the output dictionary. Indexed by name
            d[_table_name] = tmp_table

    except Exception as e:
        logger_jsons.info("import_data: Exception: {}".format(e))
    logger_jsons.info("exit import_data: {}".format(crumbs))
    return d


def _import_model(models, crumbs):
    """
    Change the nested items of the paleoModel data. Overwrite the data in-place.
    :param list models:
    :param str crumbs: Crumbs
    :return list:
    """
    logger_jsons.info("enter import_model".format(crumbs))
    crumbs += "model"
    _table_new = OrderedDict()
    try:
        for _idx, model in enumerate(models):
            # Keep the original dictionary, but replace the three main entries below

            # Do a direct replacement of chronModelTable columns. No table name, no table work needed.
            if "summaryTable" in model:
                model["summaryTable"] = _import_model_2(model, "summaryTable",
                                                                   "{}{}{}".format(crumbs, _idx, "summary"))
            elif "modelTable" in model:
                model["summaryTable"] = _import_model_2(model, "modelTable",
                                                                 "{}{}{}".format(crumbs, _idx, "summary"))

            # Do a direct replacement of ensembleTable columns. No table name, no table work needed.
            if "ensembleTable" in model:
                model["ensembleTable"] = _import_model_2(model, "ensembleTable",
                                                                    "{}{}{}".format(crumbs, _idx, "ensemble"))

            # Iter over each distribution. Check for calibrated ages (old) just in case
            if "calibratedAges" in model:
                model["distributionTable"] = _import_model_2(model, "calibratedAges",
                                                             "{}{}{}".format(crumbs, _idx, "distribution"))
                model.pop("calibratedAges")
            elif "distributionTable" in model:
                model["distributionTable"] = _import_model_2(model, "distributionTable",
                                                             "{}{}{}".format(crumbs, _idx, "distribution"))

            _table_name = "{}{}".format(crumbs, _idx)
            _table_new[_table_name] = model
    except Exception as e:
        logger_jsons.error("import_model: Exception: {}".format(e))
    logger_jsons.info("exit import_model: {}".format(crumbs))
    return _table_new


def _import_meas(tables, crumbs):
    """
    Index the measurement table by name
    :param dict tables: Table data
    :param str crumbs: Crumbs
    :return dict tables_new: Table data
    """
    logger_jsons.info("enter import_meas: {}".format(crumbs))
    crumbs += "measurement"
    _table_new = OrderedDict()
    try:
        for _idx, table in enumerate(tables):
            # Get the table name
            # _table_name = get_table_key("tableName", table, "{}{}{}".format(crumbs, "measurement", _idx))
            _table_name = "{}{}".format(crumbs, _idx)

            # Call idx_table_by_name
            _tmp_table = _idx_table_by_name(table)
            # Enter the named table in the output dictionary
            if _table_name in _table_new:
                _fallback_name = "{}{}{}".format(crumbs, "measurement", _idx)
                _tmp_table["tableName"] = _fallback_name
                _table_new[_fallback_name] = _tmp_table
            else:
                _tmp_table["tableName"] = _table_name
                _table_new[_table_name] = _tmp_table

    except Exception as e:
        logger_jsons.error("import_meas: Exception: {}".format(e))
    logger_jsons.info("exit import_meas: {}".format(crumbs))
    return _table_new


def _import_model_2(model, key, crumbs):
    """
    Import summary, ensemble, calibratedAges or distribution data.
    :param model: Table metadata
    :param key: calibratedAges or distributionTable
    :return: Modified table metadata
    """
    _table_new = OrderedDict()
    try:
        for _idx, _table in enumerate(model[key]):
            # Use "name" as table name
            # _table_name = get_table_key("tableName", _table, "{}{}".format(crumbs, _idx))
            _table_name = "{}{}".format(crumbs, _idx)
            # Call idx_table_by_name
            _tmp_table = _idx_table_by_name(_table)
            if _table_name in _table_new:
                _fallback_name = "{}_{}".format(crumbs, _idx)
                _tmp_table["tableName"] = _fallback_name
                _table_new[_fallback_name] = _tmp_table
            else:
                _tmp_table["tableName"] = _table_name
                _table_new[_table_name] = _tmp_table
    except Exception as e:
        logger_jsons.error("import_model_2: Exception: {}".format(e))
    return _table_new


def _idx_table_by_name(d):
    """
    Switch a table of data from indexed-by-number into indexed-by-name using table names
    :param dict d: Table data
    :return dict d: Table data
    """
    try:
        # Overwrite the columns entry with named columns
        d["columns"] = _idx_col_by_name(d["columns"])
    except Exception as e:
        print("Error: Indexing table data: {}".format(e))
        logger_jsons.info("idx_table_by_name: Exception: {}".format(e))
    return d


def _idx_col_by_name(l):
    """
    Iter over columns list. Turn indexed-by-num list into an indexed-by-name dict. Keys are the variable names.
    :param list l: Columns
    :return dict: New columns indexed-by-name
    """
    cols_new = OrderedDict()

    # Iter for each column in the list
    try:
        for col in l:
            try:
                col_name = col["variableName"]
                if col_name in cols_new:
                    col_name = get_appended_name(col_name, cols_new)
                cols_new[col_name] = col
            except KeyError:
                print("Error: missing 'variableName' in column")
                logger_jsons.info("idx_col_by_name: KeyError: missing variableName key")
    except Exception as e:
        logger_jsons.info("idx_col_by_name: Exception: {}".format(e))

    return cols_new


# PREP FOR EXPORT


def get_csv_from_json(d):
    """
    Get CSV values when mixed into json data. Pull out the CSV data and put it into a dictionary.
    :param dict d: JSON with CSV values
    :return dict: CSV values. (i.e. { CSVFilename1: { Column1: [Values], Column2: [Values] }, CSVFilename2: ... }
    """
    logger_jsons.info("enter get_csv_from_json")
    csv_data = OrderedDict()

    if "paleoData" in d:
        csv_data = _get_csv_from_section(d, "paleoData", csv_data)

    if "chronData" in d:
        csv_data = _get_csv_from_section(d, "chronData", csv_data)

    logger_jsons.info("exit get_csv_from_json")
    return csv_data


def _get_csv_from_section(d, pc, csv_data):
    """
    Get csv from paleo and chron sections
    :param dict d: Metadata
    :param str pc: Paleo or chron
    :return dict: running csv data
    """
    logger_jsons.info("enter get_csv_from_section: {}".format(pc))

    for table, table_content in d[pc].items():
        # Create entry for this table/CSV file (i.e. Asia-1.measTable.PaleoData.csv)
        # Note: Each table has a respective CSV file.
        csv_data[table_content['filename']] = OrderedDict()
        for column, column_content in table_content['columns'].items():
            # Set the "values" into csv dictionary in order of column "number"
            csv_data[table_content['filename']][column_content['number']] = column_content['values']

    logger_jsons.info("exit get_csv_from_section: {}".format(pc))
    return csv_data


def remove_csv_from_json(d):
    """
    Remove all CSV data 'values' entries from paleoData table in the JSON structure.
    :param dict d: JSON data - old structure
    :return dict: Metadata dictionary without CSV values
    """
    logger_jsons.info("enter remove_csv_from_json")

    # Check both sections
    if "paleoData" in d:
        d = _remove_csv_from_section(d, "paleoData")

    if "chronData" in d:
        d = _remove_csv_from_section(d, "chronData")

    logger_jsons.info("exit remove_csv_from_json")
    return d


def _remove_csv_from_section(d, pc):
    """
    Remove CSV from metadata in this section
    :param dict d: Metadata
    :param str pc: Paleo or chron
    :return dict: Modified metadata
    """
    logger_jsons.info("enter remove_csv_from_json: {}".format(pc))

    for table, table_content in d[pc].items():
        for column, column_content in table_content['columns'].items():
            try:
                # try to delete the values key entry
                del column_content['values']
            except KeyError as e:
                # if the key doesn't exist, keep going
                logger_jsons.debug("remove_csv_from_json: KeyError: {}, {}".format(pc, e))

    logger_jsons.info("exit remove_csv_from_json: {}".format(pc))
    return d


# EXPORT


def write_json_to_file(json_data, filename="metadata"):
    """
    Write all JSON in python dictionary to a new json file.
    :param dict json_data: JSON data
    :param str filename: Target filename (defaults to 'metadata.jsonld')
    :return None:
    """
    logger_jsons.info("enter write_json_to_file")
    json_data = rm_empty_fields(json_data)
    # Use demjson to maintain unicode characters in output
    json_bin = demjson.encode(json_data, encoding='utf-8', compactly=False)
    # Write json to file
    try:
        open("{}.jsonld".format(filename), "wb").write(json_bin)
        logger_jsons.info("wrote data to json file")
    except FileNotFoundError as e:
        print("Error: Writing json to file: {}".format(filename))
        logger_jsons.debug("write_json_to_file: FileNotFound: {}, {}".format(filename, e))
    logger_jsons.info("exit write_json_to_file")
    return


def idx_name_to_num(d):
    """
    Switch from index-by-name to index-by-number.
    :param dict d: Metadata
    :return dict: Modified metadata
    """
    logger_jsons.info("enter idx_name_to_num")

    # Process the paleoData section
    if "paleoData" in d:
        d["paleoData"] = _export_data(d["paleoData"], "paleo")

    # Process the chronData section
    if "chronData" in d:
        d["chronData"] = _export_data(d["chronData"], "chron")

    logger_jsons.info("exit idx_name_to_num")
    return d


def _export_data(section_data, pc):
    """
    Switch chron data to index-by-number
    :param dict section_data: Metadata
    :return list: Metadata
    """
    logger_jsons.info("enter export_data: {}".format(pc))
    l = []

    for name, table in section_data.items():

        # Process chron models
        if "model" in table:
            table["model"] = _export_model(table["model"], pc)

        # Process the chron measurement table
        if "measurementTable" in table:
            table["measurementTable"] = _export_measurement(table["measurementTable"], pc)

        # Add only the table to the output list
        l.append(table)

    logger_jsons.info("exit export_data: {}".format(pc))
    return l


def _export_measurement(meas, pc):
    """
    Switch measurement tables to index-by-number
    :param dict meas: Measurement metadata
    :param str pc: Paleo or Chron
    :return list: Measurement metadata
    """
    logger_jsons.info("enter export_measurement: {}".format(pc))
    dt = []
    for name, table in meas.items():
        try:
            # Get the modified table data
            tmp = _idx_table_by_num(table)
            # Append it to the growing calibrated age list of tables
            dt.append(tmp)
        except KeyError:
            logger_jsons.debug("export_measurement: {}, KeyError: missing columns key".format(pc))
    logger_jsons.info("exit export_measurement: {}".format(pc))
    return dt


def _export_model(models, pc):
    """
    Switch model tables to index-by-number
    :param list models: Metadata
    :return list: modified model
    """
    logger_jsons.info("enter export_model: {}".format(pc))
    try:
        for model in models:

            if "summaryTable" in model:
                model["summaryTable"] = _idx_table_by_num(model["summaryTable"])

            if "modelTable" in model:
                model["summaryTable"] = _idx_table_by_num(model["modelTable"])
                model.pop("modelTable")

            # Process ensemble table (special two columns)
            if "ensembleTable" in model:
                model["ensembleTable"] = _idx_table_by_num(model["ensembleTable"])

            if "distributionTable" in model:
                dt = []
                for name, table in model["distributionTable"].items():
                    try:
                        # Get the modified table data
                        tmp = _idx_table_by_num(table)
                        # Append it to the growing calibrated age list of tables
                        dt.append(tmp)
                    except KeyError:
                        logger_jsons.debug("export_model: {}, KeyError: missing columns key".format(pc))

                # Insert the newly built list in-place over the dictionary
                model["distributionTable"] = dt

    except AttributeError:
        logger_jsons.debug("export_model: {}, AttributeError: expected list type, received {} type".format(pc, type(models)))
    logger_jsons.info("exit export_model: {}".format(pc))
    return models


def _idx_table_by_num(d):
    """
    Append all the values from the dictionary to an output list. Drop the keys.
    :return:
    """
    if "columns" in d:
        try:
            # Overwrite the columns dict with a new columns list
            d["columns"] = _idx_col_by_num(d["columns"])
        except AttributeError:
            print("Error: table type is incorrect")
            logger_jsons.debug("idx_table_by_num: AttributeError: expected type dict, given type {}".format(type(d)))
    return d


def _idx_col_by_num(d):
    """
    Index columns by number instead of by name. Use "number" key in column to maintain order
    :param dict d: Column data
    :return list: modified column data
    """
    l = []
    try:
        # Create an empty list that matches the length of the column dictionary
        l = [None for i in d]

        # Loop and start placing data in the output list based on its "number" entry
        for var, data in d.items():
            try:
                # Special case for ensemble table "numbers" list
                if isinstance(data["number"], list):
                    l.append(data)
                # Place at list index based on its column number
                else:
                    # cast number to int, just in case it's stored as a string.
                    n = int(data["number"])
                    l[n - 1] = data
            except KeyError:
                print("Error: column is missing a 'number' key")
                logger_jsons.debug("idx_col_by_num: KeyError: missing number key")
            except Exception as e:
                logger_jsons.debug("idx_col_by_num: Exception: {}".format(e))
    except AttributeError:
        logger_jsons.debug("idx_col_by_num: AttributeError: expected dict type, given {} type".format(type(d)))
    return l

