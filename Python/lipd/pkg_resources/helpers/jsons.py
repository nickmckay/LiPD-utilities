import copy
import os
import json

import demjson

from .blanks import *
from .loggers import *

logger_jsons = create_logger("jsons")


# IMPORT


def read_json_from_file(filename):
    """
    Import the JSON data from target file.
    :param str filename: Target File
    :return dict: JSON data
    """
    logger_jsons.info("enter read_json_from_file")
    d = {}
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
            print("Error: Reading json from file: {}".format(filename))
            logger_jsons.debug("read_json_from_file: FileNotFound: {}, {}".format(filename, e))
    if d:
        d = remove_empty_fields(d)
    logger_jsons.info("exit read_json_from_file")
    return d


def idx_num_to_name(d):
    """
    Switch from index-by-number to index-by-name.
    :param dict d: Metadata
    :return dict: Modified Metadata
    """
    logger_jsons.info("enter idx_num_to_name")

    # Take whatever lipd version this file is, and convert it to the most current lipd version
    d = _update_lipd_version(d)

    if "paleoData" in d:
        tmp_pd = _import_data(d["paleoData"], "paleo")
        d["paleoData"] = tmp_pd

    if "chronData" in d:
        tmp_cd = _import_data(d["chronData"], "chron")
        d["chronData"] = tmp_cd

    logger_jsons.info("exit idx_num_to_name")
    return d


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
        logger_jsons.info("idx_table_by_name: AttributeError: expected dictionary type, given {} type".format(type(d)))

    return d


def _idx_col_by_name(l):
    """
    Iter over columns list. Turn indexed-by-num list into an indexed-by-name dict. Keys are the variable names.
    :param list l: Columns
    :return dict: New column indexed-by-name
    """
    col_new = {}

    # Iter for each column in the list
    try:
        for col in l:
            try:
                col_name = col["variableName"]
                col_new[col_name] = col
            except KeyError:
                logger_jsons.info("idx_col_by_name: KeyError: missing variableName key")
    except AttributeError:
        logger_jsons.info("idx_col_by_name: AttributeError: expected list type, given {} type".format(type(l)))

    return col_new


def _import_data(section_data, pc):
    """
    Import the section metadata and change it to index-by-name.
    :param list section_data: Section metadata
    :param str pc: Paleo or Chron
    :return dict: Modified paleoData
    """
    logger_jsons.info("enter import_data_{}".format(pc))
    d = {}
    idx = 1
    try:
        for table in section_data:
            tmp_table = {}

            # Get the table name from the first measurement table, and use that as the index name for this table
            tmp_table_name = _get_variable_name_table("{}DataTableName".format(pc), table, pc)

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
        logger_jsons.info("import_data_{}: AttributeError: paleoData: expected list type, given {}".format(pc, type(section_data)))
    logger_jsons.info("exit import_data_".format(pc))
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

            # Iter over each calibrated age table
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
    logger_jsons.info("enter import_meas_{}".format(pc))
    table_new = {}

    for table in tables:
        # Get the table name
        name_table = _get_variable_name_table("{}DataTableName".format(pc), table, pc)

        # Call idx_table_by_name
        table = _idx_table_by_name(table)

        # Enter the named table in the output dictionary
        table_new[name_table] = table
    logger_jsons.info("exit import_meas_{}".format(pc))
    return table_new


def _import_dist(model, key):
    """
    Import calibratedAges or distributionTable.
    :param model: Table metadata
    :param key: calibratedAges or distributionTable
    :return: Modified table metadata
    """
    tmp_calib = {}
    for calibration in model[key]:
        # Use "name" as table name
        name_calib = _get_variable_name_table("name", calibration)
        # Call idx_table_by_name
        table_new = _idx_table_by_name(calibration)
        # Set the new table by name into the WIP tmp_calib
        tmp_calib[name_calib] = table_new
    return tmp_calib


# EXPORT


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
    csv_data = {}

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
        csv_data[table_content['filename']] = {}
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


def idx_name_to_num(d):
    """
    Switch from index-by-name to index-by-number.
    :param dict d: Metadata
    :return dict: Modified metadata
    """
    logger_jsons.info("enter idx_name_to_num")

    # Process the paleoData section
    try:
        d["paleoData"] = _export_paleo_data(d["paleoData"])
    except KeyError:
        logger_jsons.warn("idx_name_to_num: KeyError: missing paleoData key")

    # Process the chronData section
    try:
        d["chronData"] = _export_chron_data(d["chronData"])
    except KeyError:
        logger_jsons.info("idx_name_to_num: KeyError: missing chronData key")

    logger_jsons.info("exit idx_name_to_num")
    return d


def _export_paleo_data(paleo_data):
    """
    Switch paleo data to index-by-number
    :param dict paleo_data: Name and table data
    :return list: List of table data
    """
    logger_jsons.info("enter export_paleo_data")
    l = []
    try:
        for name, table in paleo_data.items():
            try:
                # todo make sure this is actually replacing columns key
                # Switch columns to index-by-number
                table["columns"] = _idx_col_by_num(table["columns"])
                # Add table data to output list. Drop key
                l.append(table)
            except KeyError:
                logger_jsons.warn("export_paleo_data: KeyError: missing columns key")

    except AttributeError:
        logger_jsons.debug("export_paleo_data: AttributeError: expected type dict, given type {}".format(type(paleo_data)))
    logger_jsons.info("exit export_paleo_data")
    return l


def _export_chron_data(chron_data):
    """
    Switch chron data to index-by-number
    :param dict chron_data: ChronData
    :return list: ChronData tables
    """
    logger_jsons.info("enter export_chron_data")
    l = []

    # For each chron in chronData,
    for name, table in chron_data.items():

        # Process chron models
        try:
            table["chronModel"] = _export_chron_model(table["chronModel"])
        except KeyError:
            # chron model key is optional. No need to report.
            pass

        # Process the chron measurement table
        try:
            table["chronMeasurementTable"] = _idx_table_by_num(table["chronMeasurementTable"])
        except KeyError:
            logger_jsons.warn("export_chron_data: KeyError: missing chronMeasurementTable key")

        # Add only the table to the output list
        l.append(table)

    logger_jsons.info("exit export_chron_data")
    return l


def _export_chron_model(chron_model):
    """
    Switch chron model to index-by-number
    :param list chron_model: Chron model
    :return list: modified chron model
    """
    logger_jsons.info("enter export_chron_model")
    try:
        for model in chron_model:

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
                        logger_jsons.debug("export_chron_model: KeyError: missing columns key")

                # Insert the newly built list in-place over the dictionary
                model["calibratedAges"] = ca

            # Process ensemble table (special two columns)
            if "ensembleTable" in model:
                model["ensembleTable"] = _idx_table_by_num(model["ensembleTable"])

            # Process chronModelTable (normal)
            if "chronModelTable" in model:
                model["chronModelTable"] = _idx_table_by_num(model["chronModelTable"])

    except AttributeError:
        logger_jsons.debug("export_chron_model: AttributeError: expected list type, received {} type".format(type(chron_model)))
    logger_jsons.info("exit export_chron_model")
    return chron_model


def _idx_table_by_num(d):
    """
    Append all the values from the dictionary to an output list. Drop the keys.
    :return:
    """
    try:
        # Overwrite the columns dict with a new columns list
        d["columns"] = _idx_col_by_num(d["columns"])
    except AttributeError:
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
                    l[data["number"] - 1] = data
            except KeyError:
                logger_jsons.debug("idx_col_by_num: KeyError: missing number key")
    except AttributeError:
        logger_jsons.debug("idx_col_by_num: AttributeError: expected dict type, given {} type".format(type(d)))
    return l


def write_json_to_file(filename, json_data):
    """
    Write all JSON in python dictionary to a new json file.
    :param str filename: Target json file
    :param dict json_data: JSON data
    :return None:
    """
    logger_jsons.info("enter write_json_to_file")
    json_data = remove_empty_fields(json_data)
    # Use demjson to maintain unicode characters in output
    json_bin = demjson.encode(json_data, encoding='utf-8', compactly=False)
    # Write json to file
    try:
        open(filename, "wb").write(json_bin)
        logger_jsons.info("wrote data to json file")
    except FileNotFoundError as e:
        print("Error: Writing json to file: {}".format(filename))
        logger_jsons.debug("write_json_to_file: FileNotFound: {}, {}".format(filename, e))
    logger_jsons.info("exit write_json_to_file")
    return


# HELPERS


def remove_values_fields(x):
    """
    (recursive) Remove all "values" fields from the metadata
    :param any x: Any data type
    :return dict: metadata without "values"
    """
    if isinstance(x, dict):
        if "values" in x:
            del x["values"]
        else:
            for k, v in x.items():
                if isinstance(v, dict):
                    remove_values_fields(v)
                elif isinstance(v, list):
                    remove_values_fields(v)
    elif isinstance(x, list):
        for i in x:
            remove_values_fields(i)

    return x


def remove_empty_fields(x):
    """
    Go through N number of nested data types and remove all empty entries. Recursion
    :param any x: Dictionary, List, or String of data
    :return any: Returns a same data type as original, but without empties.
    """
    # No logger here because the function is recursive.
    # Int types don't matter. Return as-is.
    if not isinstance(x, int):
        if isinstance(x, str) or x is None:
            try:
                # Remove new line characters and carriage returns
                x = x.rstrip()
            except AttributeError:
                # None types don't matter. Keep going.
                pass
            if x in EMPTY:
                # Substitute empty entries with ""
                x = ''
        elif isinstance(x, list):
            # Recurse once for each item in the list
            for i, v in enumerate(x):
                x[i] = remove_empty_fields(x[i])
            # After substitutions, remove and empty entries.
            for i in x:
                if not i:
                    x.remove(i)
        elif isinstance(x, dict):
            # First, go through and substitute "" (empty string) entry for any values in EMPTY
            for k, v in x.items():
                x[k] = remove_empty_fields(v)
            # After substitutions, go through and delete the key-value pair.
            # This has to be done after we come back up from recursion because we cannot pass keys down.
            for key in list(x.keys()):
                if not x[key]:
                    del x[key]
    return x


def remove_empty_doi(d):
    """
    If an "identifier" dictionary has no doi ID, then it has no use. Delete it.
    :param dict d: JSON Metadata
    :return dict: JSON Metadata
    """
    logger_jsons.info("enter remove_empty_doi")
    try:
        # Check each publication dictionary
        for pub in d['pub']:
            # If no identifier, then we can quit here. If identifier, then keep going.
            if 'identifier' in pub:
                if 'id' in pub['identifier'][0]:
                    # If there's a DOI id, but it's EMPTY
                    if pub['identifier'][0]['id'] in EMPTY:
                        del pub['identifier']
                else:
                    # If there's an identifier section, with no DOI id
                    del pub['identifier']
    except KeyError as e:
        # What else could go wrong?
        logger_jsons.warn("remove_empty_doi: KeyError: publication key not found, {}".format(e))
    logger_jsons.info("exit remove_empty_doi")
    return d


def _get_lipd_version(d):
    """
    Check what version of LiPD this file is using. If none is found, assume it's using version 1.0
    :param dict d: Metadata
    :return float:
    """
    version = 1.0
    if "LiPDVersion" in d:
        version = d["LiPDVersion"]
        # Cast the version number to a float
        try:
            version = float(version)
        except AttributeError:
            # If the casting failed, then something is wrong with the key so assume version is 1.0
            version = 1.0
    return version


def _update_lipd_version(d):
    """
    Use the current version number to determine where to start updating from. Use "chain versioning" to make it
    modular. If a file is a few versions behind, convert to EACH version until reaching current. If a file is one
    version behind, it will only convert once to the newest.
    :param dict d: Metadata dictionary
    :return dict: Most current version metadata dictionary
    """

    # Get the lipd version number.
    version = _get_lipd_version(d)

    # Update from (N/A or 1.0) to 1.1
    if version in (1.0, "1.0"):
        d = _lipd_v1_0_to_v1_1(d)
        version = 1.1

    # Update from 1.1 to 1.2
    if version in (1.1, "1.1"):
        d = _lipd_v1_1_to_v1_2(d)
        version = 1.2

    return d


def _lipd_v1_0_to_v1_1(d):
    """
    Update LiPD version 1.0 to version 1.1.  See LiPD Version changelog for details.
    NOTE main changes: ChronData turned into a scalable lists of dictioanries.
    :param dict d: Metadata
    :return dict: v1.1 metadata dictionary
    """
    logger_jsons.info("enter lipd 1.0 to 1.1")
    tmp_all = []

    # ChronData is the only structure update
    if "chronData" in d:
        # As of v1.1, ChronData should have an extra level of abstraction.
        # No longer shares the same structure of paleoData

        # If no measurement table, then make a measurement table list with the table as the entry
        for table in d["chronData"]:
            if "chronMeasurementTable" not in table:
                tmp_all.append({"chronMeasurementTable": [table]})

            # If the table exists, but it is a dictionary, then turn it into a list with one entry
            elif "chronMeasurementTable" in table:
                if isinstance(table["chronMeasurementTable"], dict):
                    tmp_all.append({"chronMeasurementTable": [table["chronMeasurementTable"]]})
        if tmp_all:
            d["chronData"] = tmp_all

    d["LiPDVersion"] = 1.1
    logger_jsons.info("exit lipd 1.0 to 1.1")
    return d


def _lipd_v1_1_to_v1_2(d):
    """
    Update LiPD version 1.1 to version 1.2. See LiPD Version changelog for details.
    :param dict d: Metadata dictioanry
    :return dict: v1.2 metadata dictionary
    """
    logger_jsons.info("enter lipd 1.1 to 1.2")
    tmp_all = []

    # PaleoData is the only structure update
    if "paleoData" in d:

        # As of 1.2, PaleoData should match the structure of v1.1 chronData.
        # There is an extra level of abstraction and room for models, ensembles, calibrations, etc.
        for table in d["paleoData"]:
            if "paleoMeasurementTable" not in table:
                tmp_all.append({"paleoMeasurementTable": [table]})

            # If the table exists, but it is a dictionary, then turn it into a list with one entry
            elif "paleoMeasurementTable" in table:
                if isinstance(table["paleoMeasurementTable"], dict):
                    tmp_all.append({"paleoMeasurementTable": [table["paleoMeasurementTable"]]})

        if tmp_all:
            d["paleoData"] = tmp_all

    d["LiPDVersion"] = 1.2
    logger_jsons.info("exit lipd 1.1 to 1.2")
    return d


def _get_variable_name_col(d):
    """
    Get the variable name from a table or column
    :param dict d: Metadata
    :return str:
    """
    var = ""
    try:
        var = d["variableName"]
    except KeyError:
        try:
            var = d["name"]
        except KeyError:
            logger_jsons.info("get_variable_name_col: KeyError: missing key")
    return var


def _get_variable_name_table(key, d, fallback=""):
    """
    Try to get a table name from a data table
    :param str key: Key to try first
    :param dict d: Data table
    :param str fallback: (optional) If we don't find a table name, use this as a generic name fallback.
    :return str: Data table name
    """
    try:
        var = d[key]
        return var
    except KeyError:
        logger_jsons.info("get_variable_name_table: KeyError: missing {}".format(key))
        return fallback
