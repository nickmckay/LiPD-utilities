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
        logger_jsons.info("Wrote data to json file")
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
    # TODO update to work with chronology also
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
    # TODO update to work with chronology also
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


def old_to_new_structure(d):
    """
    Restructure JSON to the new format. Table and columns referenced by name, not index. (dictionaries)
    :param dict d: Metadata
    :return dict: Modified Metadata
    """
    logger_jsons.info("enter old_to_new_structure")
    table_names = {"paleoData": "paleoDataTableName", "chronData": "chronDataTableName"}
    for key in ["paleoData", "chronData"]:
        if key in d:
            tmp = {}
            for table in d[key]:
                # All tables, all columns, table name
                tmp_t = {}
                tmp_c = {}
                t_name = table[table_names[key]]

                # Restructure columns into tmp_c
                try:
                    for col in table['columns']:
                        c_name = col['variableName']
                        tmp_c[c_name] = col
                except KeyError as e:
                    logger_jsons.warn("old_to_new_structure: KeyError: columns, {}".format(e))
                # Move table strings into tmp_t
                for k, v in table.items():
                    if isinstance(v, str):
                        tmp_t[k] = v

                # Move new column structure to table
                tmp_t['columns'] = copy.deepcopy(tmp_c)

                # Move table into tmp_p
                tmp[t_name] = copy.deepcopy(tmp_t)

            # Overwrite original paleoData dictionary with new dictionary
            d[key] = copy.deepcopy(tmp)
    logger_jsons.info("exit old_to_new_structure")
    return d


def new_to_old_structure(d):
    """
    Restructure JSON to the old format. Table and columns are indexed by numbers. (lists)
    :param dict d: JSON metadata
    :return dict: JSON metadata
    """
    logger_jsons.info("enter new_to_old_structure")
    tmp_p = []
    try:
        for k, v in d['paleoData'].items():
            tmp_c = []
            # For each column, append the value, forget the key.
            for i, e in v['columns'].items():
                tmp_c.append(e)
            # Replace the old column dict with the new column list
            v['columns'] = copy.deepcopy(tmp_c)
            # Append the table to the PaleoData Dict to the list, forget the key.
            tmp_p.append(v)
        # Overwrite original paleoData dictionary with new dictionary
        d['paleoData'] = tmp_p
    except KeyError as e:
        print("Error: paleoData key not found")
        logger_jsons.warn("new_to_old_structure: KeyError: paleoData key not found, {}".format(e))
    logger_jsons.info("exit new_to_old_structure")
    return d


def split_csv_json(d):
    """
    Split JSON with CSV values into separate JSON and CSV dictionaries.
    :param dict d: JSON metadata with CSV values in paleoData columns
    :return dict dict: JSON only metadata, CSV organized by filename->column
    """
    logger_jsons.info("enter split_csv_json")
    # First, get CSV values and organize.
    csv = get_csv_from_json(d)
    # Then remove CSV values, which gives us JSON only.
    j = remove_csv_from_json(d)
    logger_jsons.info("exit split_csv_json")
    return j, csv



