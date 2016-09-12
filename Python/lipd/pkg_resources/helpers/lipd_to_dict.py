import csv
import os
import shutil
import tempfile
import zipfile
import copy

# Demjson required. "pip install demjson"
import demjson

"""
LiPD to Python Dictionary
This is not a necessary LiPD package module. This was a special request strictly for getting LiPD data into a python
dictionary without anything else.
"""


def main(name_ext):
    """
    Open a LiPD file and extract JSON and CSV as one dictionary (per LiPD file)
    :param name_ext: (str) LiPD filename
    :return: (dict) Metadata dictionary
    """
    # Running as standalone.
    # os.chdir("PATH_HERE")
    # name_ext = "FILENAME.lpd"

    # Mark our starting directory
    dir_root = os.getcwd()

    # Record name w/o extension
    name = os.path.splitext(name_ext)[0]

    # Create tmp folder
    dir_tmp = tempfile.mkdtemp()

    # Unzip LiPD contents to tmp folder, then move there
    _unzip(name_ext, dir_tmp)
    dir_data = os.path.join(dir_tmp, name, 'data')
    os.chdir(dir_data)

    # Read JSON in as dictionary, then switch to new structure
    j = _read_json_from_file(os.path.join(dir_data, name + '.jsonld'))
    metadata = _old_to_new_structure(j)

    # Read CSV, and insert into dictionary. Move back to root
    paleodata_w_csv, csv_only = _add_csv_to_json(metadata['paleoData'])
    metadata['paleoData'] = paleodata_w_csv
    os.chdir(dir_root)

    # Trash tmp folder
    shutil.rmtree(dir_tmp)

    # Return dictionary
    return metadata


def batch():
    """
    NOTE: ALTERNATE TO MAIN(). BATCH PROCESS INSTEAD OF SINGLE PROCESS.
    Get list of LiPD files from current working directory.
    :return: (dict) Dictionary of dictionaries. Key: LiPD filename, Val: Metadata dictionary
    """
    # os.chdir("PATH_HERE")
    metadata_dictionary = {}
    dir_root = os.getcwd()
    lipd_files = _list_files('lpd')

    for name_ext in lipd_files:
        # Record name w/o extension
        name = os.path.splitext(name_ext)[0]

        # Create tmp folder
        dir_tmp = tempfile.mkdtemp()

        # Unzip LiPD contents to tmp folder. Move there
        _unzip(name_ext, dir_tmp)
        dir_data = os.path.join(dir_tmp, name, 'data')
        os.chdir(dir_data)

        # Read JSON in as dictionary, then switch to new structure
        j = _read_json_from_file(os.path.join(dir_data, name + '.jsonld'))
        metadata = _old_to_new_structure(j)

        # Read CSV, and insert into dictionary. Move back to root
        paleodata_w_csv, csv_only = _add_csv_to_json(metadata['paleoData'])
        metadata['paleoData'] = paleodata_w_csv
        os.chdir(dir_root)

        # Trash tmp folder
        shutil.rmtree(dir_tmp)

        # Return dictionary
        metadata_dictionary[name] = metadata

    return metadata_dictionary


def _unzip(name_ext, dir_tmp):
    """
    Unzip .lpd file contents to tmp directory.
    :param name_ext: (str) Name of lpd file with extension
    :param dir_tmp: (str) Tmp folder to extract contents to
    :return: None
    """
    # Unzip contents to the tmp directory
    try:
        with zipfile.ZipFile(name_ext) as f:
            f.extractall(dir_tmp)
    except FileNotFoundError:
        shutil.rmtree(dir_tmp)
    return


def _read_json_from_file(filename):
    """
    Import the JSON data from target file.
    :param filename: (str) Target file
    :return: (dict) JSON data
    """
    d = {}
    try:
        # Load json into dictionary
        d = demjson.decode_file(filename)
    except FileNotFoundError:
        print("LiPD object: Load(). file not found")
    return d


def _add_csv_to_json(d):
    """
    NOTE: ONLY FOR NEW STRUCTURE
    Using the given paleoData dictionary from the JSON metadata, retrieve CSV data from CSV files, and insert the CSV
    data columns to their respective JSON paleoData table columns.
    :param d: (dict) PaleoData dictionary
    :return: (dict) Modified original dictionary (dict) CSV column data
    """
    d2 = {}
    # Loop through each table in paleoData
    for table_name, table_content in d.items():
        # Create CSV entry into dictionary that contains all columns.
        d2[table_content['filename']] = _read_csv_to_columns(table_content['filename'])
        # Start putting CSV data into corresponding JSON metadata columns under 'values' key.
        for col_name, col_content in table_content['columns'].items():
            col_content['values'] = d2[table_content['filename']][col_content['number']-1]
    return d, d2


def _read_csv_to_columns(filename):
    """
    Opens the target CSV file and creates a dictionary with one list for each CSV column.
    :param filename: (str) Filename
    :return: (dict) CSV data. Keys: Column number(int), Values: Column data (list)
    """
    d = {}
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
                    except ValueError:
                        d[idx].append(col)
    except FileNotFoundError:
        print('CSV FileNotFound: ' + filename)
    return d


def _list_files(x):
    """
    Lists file(s) in given path of the X type.
    :param x: (str) File extension that we are interested in.
    :return: (list of str) File name(s) to be worked on
    """
    file_list = []
    for file in os.listdir():
        if file.endswith(x):
            file_list.append(file)
    return file_list


def _old_to_new_structure(d):
    """
    Restructure JSON to the new format. Table and columns referenced by name, not index. (dictionaries)
    :param d:(dict) JSON metadata
    :return: (dict) JSON metadata
    """
    # PaleoData dict
    tmp_p = {}

    for table in d['paleoData']:
        # All tables, all columns, table name
        tmp_t = {}
        tmp_c = {}
        t_name = table['paleoDataTableName']

        # paleoDataTableName and variableName are current
        # tableName and parameter are deprecated

        # Restructure columns into tmp_c
        for col in table['columns']:
            c_name = col['variableName']
            tmp_c[c_name] = col

        # Move table strings into tmp_t
        for k, v in table.items():
            if isinstance(v, str):
                tmp_t[k] = v

        # Move new column structure to table
        tmp_t['columns'] = copy.deepcopy(tmp_c)

        # Move table into tmp_p
        tmp_p[t_name] = copy.deepcopy(tmp_t)

    # Overwrite original paleoData dictionary with new dictionary
    d['paleoData'] = tmp_p
    return d


if '__name__' == '__main__':
    main()

main()