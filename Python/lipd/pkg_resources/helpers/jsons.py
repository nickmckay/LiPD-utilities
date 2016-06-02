import copy
import os
import json

import demjson

from .blanks import *
from .loggers import *

logger_jsons = create_logger("jsons")


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


def read_json_from_file(filename):
    """
    Import the JSON data from target file.
    :param str filename: Target File
    :return dict: JSON data
    """
    logger_jsons.info("enter read_json_from_file")
    d = {}
    try:
        # Open json file and read in the contents. Execute DOI Resolver?
        # with open(filename, 'r') as f:
            # Load json into dictionary
        d = demjson.decode_file(filename)
        logger_jsons.info("successful read from json file")
    except FileNotFoundError:
        try:
            d = demjson.decode_file(os.path.splitext(filename)[0] + '.json')
        except FileNotFoundError as e:
            print("Error: Reading json from file: {}".format(filename))
            logger_jsons.debug("read_json_from_file: FileNotFound: {}, {}".format(filename, e))
    d = remove_empty_fields(d)
    logger_jsons.info("exit read_json_from_file")
    return d


def remove_csv_from_json(d):
    """
    Remove all CSV data 'values' entries from paleoData table in the JSON structure.
    :param dict d: JSON data - old structure
    :return dict: Metadata dictionary without CSV values
    """
    # TODO Update to work with chronology?
    # Loop through each table in paleoData
    logger_jsons.info("enter remove_csv_from_json")
    try:
        for table, table_content in d['paleoData'].items():
            for column, column_content in table_content['columns'].items():
                try:
                    # try to delete the values key entry
                    del column_content['values']
                except KeyError as e:
                    # if the key doesn't exist, keep going
                    logger_jsons.debug("remove_csv_from_json: KeyError: {}".format(e))
    except KeyError as e:
        print("Error: Failed to remove csv from json")
        logger_jsons.debug("remove_csv_from_json: KeyError: paleoData key not found: {}".format(e))
    logger_jsons.info("exit remove_csv_from_json")
    return d


def get_csv_from_json(d):
    """
    Get CSV values when mixed into json data. Pull out the CSV data and put it into a dictionary.
    :param dict d: JSON with CSV values
    :return dict: CSV values. (i.e. { CSVFilename1: { Column1: [Values], Column2: [Values] }, CSVFilename2: ... }
    """
    # TODO Update to work with chronology?
    logger_jsons.info("enter get_csv_from_json")
    csv = {}
    try:
        for table, table_content in d['paleoData'].items():
            # Create entry for this table/CSV file (i.e. Asia-1.measTable.PaleoData.csv)
            # Note: Each table has a respective CSV file.
            csv[table_content['filename']] = {}
            for column, column_content in table_content['columns'].items():
                # Set the "values" into csv dictionary in order of column "number"
                csv[table_content['filename']][column_content['number']] = column_content['values']
    except KeyError as e:
        print("Error: Getting CSV from JSON - No paleoData key")
        logger_jsons.debug("get_csv_from_json: KeyError: paleoData key not found, {}".format(e))
    logger_jsons.info("exit get_csv_from_json")
    return csv


def remove_empty_fields(d):
    """
    Go through N number of nested data types and remove all empty entries. Recursion
    :param any d: Dictionary, List, or String of data
    :return any: Returns a same data type as original, but without empties.
    """
    # No logger here because the function is recursive.
    # Int types don't matter. Return as-is.
    if not isinstance(d, int):
        if isinstance(d, str) or d is None:
            try:
                # Remove new line characters and carriage returns
                d = d.rstrip()
            except AttributeError:
                # None types don't matter. Keep going.
                pass
            if d in EMPTY:
                # Substitute empty entries with ""
                d = ''
        elif isinstance(d, list):
            # Recurse once for each item in the list
            for i, v in enumerate(d):
                d[i] = remove_empty_fields(d[i])
            # After substitutions, remove and empty entries.
            for i in d:
                if not i:
                    d.remove(i)
        elif isinstance(d, dict):
            # First, go through and substitute "" (empty string) entry for any values in EMPTY
            for k, v in d.items():
                d[k] = remove_empty_fields(v)
            # After substitutions, go through and delete the key-value pair.
            # This has to be done after we come back up from recursion because we cannot pass keys down.
            for key in list(d.keys()):
                if not d[key]:
                    del d[key]
    return d


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


def _update_structure(d):
    """
    Change an old LiPD version structure to the most recent LiPD version structure
    :param dict d: Metadata
    :return dict bool:
    """
    logger_jsons.info("enter update_structure")
    tmp_all = []
    try:
        # As of v1.1, ChronData should have an extra level of abstraction.
        # No longer shares the same structure of paleoData
        for table in d["chronData"]:
            tmp_all.append({"chronMeasurementTable": table})
    except KeyError:
        # chronData section doesn't exist. Return unsuccessful and continue without chronData
        logger_jsons.info("update_structure: KeyError: missing chronData key")
        return d, False

    d["chronData"] = tmp_all
    d["LiPDVersion"] = 1.1
    # Update successful. Return new dict and flag
    logger_jsons.info("exit update_structure")
    return d, True


def _import_chron_data(chron_data):
    """
    Import the chronData metadata and change it to index-by-name.
    :param list chron_data: ChronData metadata
    :return dict: Modified chronData
    """
    logger_jsons.info("enter import_chron_data")
    d = {}
    idx = 1
    try:
        for table in chron_data:
            tmp_table = {}

            # Get the table name, and use that as the index name for this table
            tmp_table_name = _get_variable_name_table("chronTableName", table["chronMeasurementTable"], "chronology")

            # Process the chron measurement table
            try:
                tmp_cmt = _import_chron_meas_table(table["chronMeasurementTable"])
                tmp_table["chronMeasurementTable"] = tmp_cmt
            except KeyError:
                logger_jsons.info("import_chron_data: KeyError: {} table missing chronMeasurementTable".format(tmp_table_name))

            # Process the chron model
            try:
                tmp_cm = _import_chron_model(table["chronModel"])
                tmp_table["chronModel"] = tmp_cm
            except KeyError:
                # chronModel may often not be included. That's okay.
                pass

            # If we only have generic table names, and one exists already, don't overwrite. Create dynamic name
            if tmp_table_name in d:
                tmp_table_name = "{}_{}".format(tmp_table_name, idx)
                idx += 1

            # Put the final product into the output dictionary. Indexed-by-table-name
            d[tmp_table_name] = tmp_table

    except AttributeError:
        # chronData is not a list like it should be.
        logger_jsons.info("import_chron_data: AttributeError: chronData: expected list type, given {}".format(type(chron_data)))
    logger_jsons.info("exit import_chron_data")
    return d


def _import_chron_model(chron_model):
    """
    Change the nested items of the chronModel data. Overwrite the data in-place.
    :param list chron_model:
    :return list:
    """
    logger_jsons.info("enter import_chron_data")
    try:
        for model in chron_model:
            # Keep the original dictionary, but replace the three main entries below

            # Do a direct replacement of chronModelTable columns. No table name, no table work needed.
            model["chronModelTable"]["columns"] = _idx_col_by_name(model["chronModelTable"]["columns"])

            # Do a direct replacement of ensembleTable columns. No table name, no table work needed.
            model["ensembleTable"]["columns"] = _idx_col_by_name(model["ensembleTable"]["columns"])

            # Iter over each calibrated age table
            tmp_calib = {}
            for calibration in model["calibratedAges"]:
                # Use "name" as table name
                name_calib = _get_variable_name_table("name", calibration)
                # Call idx_table_by_name
                table_new = _idx_table_by_name(calibration)
                # Set the new table by name into the WIP tmp_calib
                tmp_calib[name_calib] = table_new
            model["calibratedAges"] = tmp_calib

    except AttributeError:
        logger_jsons.debug("import_chron_model: AttributeError: expected list type, given {} type".format(type(chron_model)))

    logger_jsons.info("exit import_chron_data")
    return chron_model


def _import_chron_meas_table(d):
    """
    Index the chronology measurement table by name
    :param dict d: Chronology measurement table data
    :return:
    """
    table_new = {}

    # Get the table name
    name_table = d["chronTableName"]

    # Call idx_table_by_name
    d = _idx_table_by_name(d)

    # Enter the named table in the output dictionary
    table_new[name_table] = d

    return d


def _import_paleo_data(paleo_data):
    """
    Index the paleo data table by name
    :param list paleo_data:
    :return dict: Modified paleoData
    """
    d = {}
    idx = 1

    # Iter for each table in paleoData
    for table in paleo_data:
        # Get table name
        name_table = _get_variable_name_table("paleoDataTableName", table, "data")
        # If the table is missing a name, and we're faced with overwriting tables, make up a dynamic "data_X" name.
        if name_table in d:
            name_table = "{}_{}".format(name_table, idx)
            idx += 1
        # Process the table. Set at with named index in output dictionary
        d[name_table] = _idx_table_by_name(table)

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


def _reorganize_table_export(table):
    """

    :param table:
    :return:
    """
    # todo Export process

    return


def idx_num_to_name(d):
    """
    Switch from index-by-number to index-by-name.
    :param dict d: Metadata
    :return dict: Modified Metadata
    """
    logger_jsons.info("enter idx_num_to_name")

    # Find out what LiPD version is being used
    version = _get_lipd_version(d)

    # Success flag marks that updating the structure was a success, or if we're already at the most recent LiPDVersion
    success = True
    # todo for some reason this is triggering on file with 1.1 version and it shouldn't be
    if version == 1.0 or "1.0":
        d, success = _update_structure(d)

    # Only continue if newest structure is being used
    if success:
        try:
            tmp_pd = _import_paleo_data(d["paleoData"])
            d["paleoData"] = tmp_pd
        except KeyError:
            logger_jsons.info("idx_num_to_name: KeyError: missing paleoData")

        try:
            tmp_cd = _import_chron_data(d["chronData"])
            d["chronData"] = tmp_cd
        except KeyError:
            logger_jsons.info("idx_num_to_name: KeyError: missing chronData")
    else:
        print("Chronology incorrectly formatted.")

    logger_jsons.info("exit idx_num_to_name")
    return d


def idx_name_to_num(d):
    """
    Restructure metadata to the old format. Table and columns are indexed-by-number in lists.
    :param dict d: Metadata
    :return dict: Modified metadata
    """
    # todo rewrite as a modular process.
    logger_jsons.info("enter idx_name_to_num")

    # Process the paleoData section

    # Process the chronData section

    logger_jsons.info("exit idx_name_to_num")
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