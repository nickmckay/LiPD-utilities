import demjson
from collections import OrderedDict

from .misc import *

logger_jsons = create_logger("jsons")


# IMPORT


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
        d = demjson.decode_file(filename)
        logger_jsons.info("successful read from json file")
    except FileNotFoundError:
        # Didn't find a jsonld file. Maybe it's a json file instead?
        try:
            d = demjson.decode_file(os.path.splitext(filename)[0] + '.json')
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

    # Take whatever lipds version this file is, and convert it to the most current lipds version
    d = update_lipd_version(d)

    if "paleoData" in d:
        tmp_pd = _import_data(d["paleoData"], "paleo")
        d["paleoData"] = tmp_pd

    if "chronData" in d:
        tmp_cd = _import_data(d["chronData"], "chron")
        d["chronData"] = tmp_cd

    logger_jsons.info("exit idx_num_to_name")
    return d


def _import_data(section_data, pc):
    """
    Import the section metadata and change it to index-by-name.
    :param list section_data: Section metadata
    :param str pc: Paleo or Chron
    :return dict: Modified paleoData
    """
    logger_jsons.info("enter import_data: {}".format(pc))
    d = OrderedDict()
    idx = 1
    try:
        for table in section_data:
            tmp_table = OrderedDict()

            # Get the table name from the first measurement table, and use that as the index name for this table
            tmp_table_name = get_variable_name_table("{}DataTableName".format(pc), table, pc)

            # Process the paleo measurement table
            if "{}MeasurementTable".format(pc) in table:
                tmp_pmt = _import_meas(table["{}MeasurementTable".format(pc)], pc)
                tmp_table["{}MeasurementTable".format(pc)] = tmp_pmt

            # Process the paleo model
            if "{}Model".format(pc) in table:
                tmp_cm = _import_model(table["{}Model".format(pc)], pc)
                tmp_table["{}Model".format(pc)] = tmp_cm

            # If we only have generic table names, and one exists already, don't overwrite. Create dynamic name
            if tmp_table_name in d:
                tmp_table_name = "{}_{}".format(tmp_table_name, idx)
                idx += 1

            # Put the final product into the output dictionary. Indexed-by-table-name
            d[tmp_table_name] = tmp_table

    except AttributeError:
        # paleoData is not a list like it should be.
        logger_jsons.info("import_data: {},  AttributeError: expected list type, given {}".format(pc, type(section_data)))
    logger_jsons.info("exit import_data: {}".format(pc))
    return d


def _import_model(models, pc):
    """
    Change the nested items of the paleoModel data. Overwrite the data in-place.
    :param list models:
    :param str pc: Paleo or Chron
    :return list:
    """
    logger_jsons.info("enter import_model".format(pc))

    try:
        for model in models:
            # Keep the original dictionary, but replace the three main entries below

            # Do a direct replacement of chronModelTable columns. No table name, no table work needed.
            if "summaryTable" in model:
                model["summaryTable"]["columns"] = _idx_col_by_name(model["summaryTable"]["columns"])
            elif "{}ModelTable".format(pc) in model:
                model["{}ModelTable".format(pc)]["columns"] = _idx_col_by_name(model["{}ModelTable".format(pc)]["columns"])

            # Do a direct replacement of ensembleTable columns. No table name, no table work needed.
            if "ensembleTable" in model:
                model["ensembleTable"]["columns"] = _idx_col_by_name(model["ensembleTable"]["columns"])

            # Iter over each distribution. Check for calibrated ages (old) just in case
            if "calibratedAges" in model:
                model["distributionTable"] = _import_dist(model, "calibratedAges")
                model.pop("calibratedAges")
            elif "distributionTable" in model:
                model["distributionTable"] = _import_dist(model, "distributionTable")

    except AttributeError:
        logger_jsons.debug("import_model_{}: AttributeError: expected list type, given {} type".format(pc, type(models)))

    logger_jsons.info("exit import_model_{}".format(pc))
    return models


def _import_meas(tables, pc):
    """
    Index the measurement table by name
    :param dict tables: Measurement table data
    :return dict:
    """
    logger_jsons.info("enter import_meas: {}".format(pc))
    table_new = OrderedDict()

    for table in tables:
        # Get the table name
        name_table = get_variable_name_table("{}DataTableName".format(pc), table, pc)

        # Call idx_table_by_name
        table = _idx_table_by_name(table)

        # Enter the named table in the output dictionary
        table_new[name_table] = table
    logger_jsons.info("exit import_meas: {}".format(pc))
    return table_new


def _import_dist(model, key):
    """
    Import calibratedAges or distributionTable.
    :param model: Table metadata
    :param key: calibratedAges or distributionTable
    :return: Modified table metadata
    """
    tmp_calib = OrderedDict()
    for calibration in model[key]:
        # Use "name" as table name
        name_calib = get_variable_name_table("name", calibration)
        # Call idx_table_by_name
        table_new = _idx_table_by_name(calibration)
        # Set the new table by name into the WIP tmp_calib
        tmp_calib[name_calib] = table_new
    return tmp_calib


def _idx_table_by_name(d):
    """
    Switch a table of data from indexed-by-number into indexed-by-name using table names
    :param dict d: Table data
    :return dict: new idx-by-name table
    """
    try:
        # Overwrite the columns entry with named columns
        d["columns"] = _idx_col_by_name(d["columns"])
    except AttributeError:
        print("Error: 'columns' data is not a dictionary")
        logger_jsons.info("idx_table_by_name: AttributeError: expected dictionary type, given {} type".format(type(d)))
    return d


def _idx_col_by_name(l):
    """
    Iter over columns list. Turn indexed-by-num list into an indexed-by-name dict. Keys are the variable names.
    :param list l: Columns
    :return dict: New column indexed-by-name
    """
    col_new = OrderedDict()

    # Iter for each column in the list
    try:
        for col in l:
            try:
                col_name = col["variableName"]
                col_new[col_name] = col
            except KeyError:
                print("Error: missing 'variableName' in column")
                logger_jsons.info("idx_col_by_name: KeyError: missing variableName key")
    except AttributeError:
        logger_jsons.info("idx_col_by_name: AttributeError: expected list type, given {} type".format(type(l)))

    return col_new


# PREP FOR EXPORT


def split_csv_json(d):
    """
    Split JSON with CSV values into separate JSON and CSV dictionaries.
    :param dict d: JSON metadata with CSV values in paleoData columns
    :return dict, dict: JSON only metadata, CSV organized by filename->column
    """
    logger_jsons.info("enter split_csv_json")
    # First, get CSV values and organize.
    csv = get_csv_from_json(d)
    # Then remove CSV values, which gives us JSON only.
    j = remove_csv_from_json(d)
    logger_jsons.info("exit split_csv_json")
    return j, csv


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


def write_json_to_file(filename, json_data):
    """
    Write all JSON in python dictionary to a new json file.
    :param str filename: Target json file
    :param dict json_data: JSON data
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
        if "{}Model".format(pc) in table:
            table["{}Model".format(pc)] = _export_model(table["{}Model".format(pc)], pc)

        # Process the chron measurement table
        if "{}MeasurementTable".format(pc) in table:
            table["{}MeasurementTable".format(pc)] = _export_measurement(table["{}MeasurementTable".format(pc)], pc)

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

            if "{}ModelTable".format(pc) in model:
                model["summaryTable"] = _idx_table_by_num(model["{}ModelTable".format(pc)])
                model.pop("{}ModelTable".format(pc))

            # Process ensemble table (special two columns)
            if "ensembleTable" in model:
                model["ensembleTable"] = _idx_table_by_num(model["ensembleTable"])

            # Process calibrated ages (nested tables)
            if "calibratedAges" in model:
                ca = []
                for name, table in model["calibratedAges"].items():
                    try:
                        # Get the modified table data
                        tmp = _idx_table_by_num(table)
                        # Append it to the growing calibrated age list of tables
                        ca.append(tmp)
                    except KeyError:
                        logger_jsons.debug("export_model: {},  KeyError: missing columns key".format(pc))

                # Insert the newly built list in-place over the dictionary
                model["distributionTable"] = ca
                model.pop("calibratedAges")
            elif "distributionTable" in model:
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


# NO EXPORT DISTRIBUTION?


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

