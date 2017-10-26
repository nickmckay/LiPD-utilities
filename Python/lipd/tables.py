import re
import sys

from .loggers import *
from .csvs import read_csv_from_file
from .directory import browse_dialog_file
from .regexes import re_model_name, re_table_name
from collections import OrderedDict


logger_ensembles = create_logger("ensembles")

def addTable(D):
    """
    Add any table type to the given dataset. Use prompts to determine index locations and table type.

    :param dict D: Metadata (dataset)
    :param dict dat: Metadata (table)
    :return dict D: Metadata (dataset)
    """

    _swap = {
        "1": "measurement",
        "2": "summary",
        "3": "ensemble",
        "4": "distribution"
    }


    print("What type of table would you like to add?\n"
          "1: measurement\n"
          "2: summary\n"
          "3: ensemble (under development)\n"
          "4: distribution (under development)\n"
          "\n Note: if you want to add a whole model, use the addModel() function")
    _ans = input(">")

    if _ans in ["3", "4"]:
        print("I don't know how to do that yet.")
    # if this is a summary or measurement, split the csv into each column
    elif _ans in ["1", "2"]:
        # read in a csv file. have the user point to it
        print("Locate the CSV file with the values for this table: ")
        _path, _files = browse_dialog_file()

        _path = _confirm_file_path(_files)
        _values = read_csv_from_file(_path)
        _table = _build_table(_values)
        _placement = _prompt_placement(D, _swap[_ans])
        D = _put_table(D, _placement, _table)

    else:
        print("That's not a valid option")

    return D


def _confirm_file_path(_files):

    if not _files:
        sys.exit("You must choose a CSV file to create a table")
    elif len(_files) > 1:
        sys.exit("You may only choose one CSV file")
    else:
        if _files[0].endswith(".csv"):
            return _files[0]
        else:
            sys.exit("File must be a CSV file type")


def _build_table(columns):

    _table = OrderedDict({"tableName": "", "missingValue": "nan", "columns": ""})
    _columns = OrderedDict()
    try:
        # Loop once for each column of values
        for _idx, _col in enumerate(columns):
            # Print out a snippet of the first 5 values in the column so the user knows what data is being referenced
            _snippet = ""
            for i in range(0,5):
                _snippet += str(_col[i]) + ", "
            print("Data Preview:")
            print(_snippet + "\n")
            # Start having the user fill in the required data about these values
            print("What is the 'variableName' for this data?")
            _vn = input(">")
            print("What are the 'units' for this data? ('unitless' if none)")
            _units = input(">")
            _columns[_vn] = {"number": _idx+1, "variableName": _vn, "units": _units, "values": _col}

        # Add the columns to the overall table
        _table["columns"] = _columns
    except Exception as e:
        print("Error: something went wrong during table creation, {}".format(e))

    return _table


def _get_available_placements(D, tt):
    """
    Called from: _prompt_placement()

    Get a list of possible places that we can put the new model data into.
    If no model exists yet, we'll use something like chron0model0. If other models exist,
    we'll go for the n+1 entry.
    ex: chron0model0 already exists, so we'll look to chron0model1 next.

    :param dict D: Metadata
    :param str tt: Table Type
    :return list _options: Possible placements
    """
    _options = []

    try:
        for _pc in ["paleoData", "chronData"]:
            if _pc in D:
                # for each entry in pc
                for section_name, section_data in D[_pc].items():
                    # looking for open spots for measurement tables
                    if tt == "measurement":
                        if "measurementTable" in section_data:
                            _options.append(_get_available_placements_1(section_data["measurementTable"], section_name, "measurement"))


                    # looking for open spots for model tables
                    else:
                        # Is there a model? Need model data to keep going
                        if "model" in section_data:
                            #  this is for adding a whole model (all 4 tables, ens/dist/sum/method)
                            if tt == "model":
                                _options.append(_get_available_placements_1(section_data["model"], section_name, "model"))
                            else:

                                # for adding individual model tables
                                for _k, _v in section_data["model"]:
                                    # keys here are stored as "<type>Table", so add "Table" to each table type
                                    _tt_table = "{}Table".format(tt)
                                    # does this table exist?
                                    if _tt_table in _v:
                                        # Get the first available position for this section
                                        _options.append(
                                            _get_available_placements_1(_v[_tt_table], _k, tt))
                                    else:
                                        # Doesn't currently exist. Make the first option index 0.
                                        _options.append("{}{}0".format(_k, tt))

                        # no models present, so we automatically default placement options to the 0 index.
                        else:
                            if tt == "model":
                                # adding a whole model, so no need to be specific
                                _options.append("{}model0".format(section_name))
                            else:
                                # adding a specific table, so the position is more specific also
                                _options.append("{}model0{}0".format(section_name, tt))


    except Exception as e:
        sys.exit("Looking for open table positions: Unable to find placement options, {}".format(e))

    # remove empty names
    _options = [i for i in _options if i]
    # Is the whole list empty? that's not good.
    if not _options:
        sys.exit("Error: No available positions found to place new data. Something went wrong.")
    return _options


def _get_available_placements_1(dat, prefix, tt):
    _idx = 0
    while True:
        _tmp_name = "{}{}{}".format(prefix, tt, _idx)
        if _tmp_name not in dat:
            break
        _idx += 1
    return _tmp_name


def _prompt_placement(D, tt):
    """
    Since automatic placement didn't work, find somewhere to place the model data manually with the help of the user.

    :param dict D: Metadata
    :param str tt: Table type
    :return str _model_name: Chosen model name for placement
    """
    _model_name = ""
    # There wasn't a table name match, so we need prompts to fix it
    _placement_options = _get_available_placements(D, tt)
    print("Please choose where you'd like to place this model:")
    for _idx, _opt in enumerate(_placement_options):
        print("({}) {}".format(_idx, _opt))
    _choice = input("> ")
    try:
        if int(_choice) <= len(_placement_options) and _choice:
            # Get the option the user chose
            _model_name = _placement_options[int(_choice)]
        else:
            # They user chose an option out of the placement list range
            print("Invalid choice input")
            return
    except Exception as e:
        # Choice was not a number or empty
        print("Invalid choice")

    return _model_name


def _put_table(D, name, table):
    """
    Use the dataset and name to place the new table data into the dataset.

    :param dict D: Dataset
    :param str name: Table name / path to store new table
    :param dict table: Newly created table data
    :return dict D: Dataset
    """

    try:
        # print("Placing table: {}".format(name))
        table["tableName"] = name
        m = re.match(re_table_name, name)
        if m:
            _pc = m.group(1) + "Data"
            _section = m.group(1) + m.group(2)
            # place a measurement table
            if m.group(3) == "measurement":
                # This shouldn't happen. User chose one of our options. That should be an empty location.
                if name in D[_pc][_section]["measurementTable"]:
                    print("Oops. This shouldn't happen. That table path is occupied in the dataset")
                # Place the data
                else:
                    D[_pc][_section]["measurementTable"][name] = table
            # place a model table type
            else:
                _model = _section + m.group(3) + m.group(4)
                _tt = m.group(5) + "Table"
                if name in D[_pc][_model][_tt]:
                    print("Oops. This shouldn't happen. That table path is occupied in the dataset")
                else:
                    D[_pc][_model][_tt][name] = table

        else:
            print("Oops. This shouldn't happen. That table name doesn't look right. Please report this error")
            return

    except Exception as e:
        print("addTable: Unable to put the table data into the dataset, {}".format(e))

    return D




def _update_table_names(name, dat):
    """
    Model placement is subject to change. That means all names within the model (names are path-dependent) are also
    subject to change. Whichever name is decided, the inner data needs to match it.

    :param dict dat: Metadata
    :param str name: Table name
    :return dict dat: Metadata
    """
    for _tabletype in ["summary", "distribution", "ensemble"]:
        _ttname = "{}Table".format(_tabletype)
        if _ttname in dat:
            _new_tables = OrderedDict()
            _idx = 0
            # change all the top level table names
            for k,v in dat[_ttname].items():
                _new_ttname= "{}{}{}".format(name, _tabletype, _idx)
                _idx +=1
                #change all the table names in the table metadata
                v["tableName"] = _new_ttname
                # remove the filename. It shouldn't be stored anyway
                if "filename" in v:
                    v["filename"] = ""
                # place dat into the new ordered dictionary
                _new_tables[_new_ttname] = v

            # place new tables into the original dat
            dat[_ttname] = _new_tables

    return dat


""" Model Specific functions """


def addModel(D, models):
    """
    Insert model data into a LiPD dataset

    Examples of model naming:
    chron0model0
    chron0model1
    chron1model0

    Example of 'models' variable:
    {
       chron0model0: {
                        "method": {...},
                        "summaryTable": [...],
                        "ensembleTable": [...],
                        "distributionTable: [...]
                    },
       chron0model1:...
    }

    :param dict D: Metadata (dataset)
    :param dict models: Model data to add
    :return dict D: Metadata (dataset)
    """
    try:
        # Loop for each model that needs to  be added
        for _model_name, _model_data in models.items():
            # split the table name into a path that we can use
            _m = re.match(re_model_name, _model_name)
            if _m:
                D = _put_model(D, _model_name, _model_data, _m)
            else:
                print("The table name found in the given model data isn't valid for automatic placement")
                _placement_name = _prompt_placement(D, "model")
                _m = re.match(re_model_name, _placement_name)
                if _m:
                    D = _put_model(D, _placement_name, _model_data, _m)
                else:
                    print("Oops. This shouldn't happen. That table name doesn't look right. Please report this error")
                    return

    except Exception as e:
        print("addModel: Model data NOT added, {}".format(e))

    return D



def _put_model(D, name, dat, m):
    """
    Place the model data given, into the location (m) given.

    :param dict D: Metadata (dataset)
    :param str name: Model name (ex: chron0model0)
    :param dict dat: Model data
    :param regex m: Model name regex groups
    :return dict D: Metadata (dataset)
    """
    try:
        # print("Placing model: {}".format(name))
        _pc = m.group(1) + "Data"
        _section = m.group(1) + m.group(2)
        if _pc not in D:
            # Section missing entirely? Can't continue
            print("{} not found in the provided dataset. Please try again".format(_pc))
            return
        else:
            if _section not in D[_pc]:
                # Creates section: Example: D[chronData][chron0]
                D[_pc][_section] = OrderedDict()
            if "model" not in D[_pc][_section]:
                # Creates model top level: Example: D[chronData][chron0]["model"]
                D[_pc][_section]["model"] = OrderedDict()
            if name not in D[_pc][_section]["model"]:
                dat = _update_table_names(name, dat)
                D[_pc][_section]["model"][name] = dat
            else:
                # Model already exists, should we overwrite it?
                _prompt_overwrite = input(
                    "This model already exists in the dataset. Do you want to overwrite it? (y/n)")
                # Yes, overwrite with the model data provided
                if _prompt_overwrite == "y":
                    dat = _update_table_names(name, dat)
                    D[_pc][_section]["model"][name] = dat
                # No, do not overwrite.
                elif _prompt_overwrite == "n":
                    _name2 = _prompt_placement(D, "model")
                    _m = re.match(re_model_name, _name2)
                    if _m:
                        D = _put_model(D, _name2, dat, _m)
                else:
                    print("Invalid choice")
    except Exception as e:
        print("addModel: Unable to put the model data into the dataset, {}".format(e))

    return D


