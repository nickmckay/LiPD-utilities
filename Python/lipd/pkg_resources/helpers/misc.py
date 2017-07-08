import datetime as dt
import math
import operator
import os
import random
import re
import shutil
import string
import unicodedata

import numpy as np

from ..helpers.alternates import FILE_TYPE_MAP, VER_1_3
from ..helpers.blanks import EMPTY
from ..helpers.directory import list_files
from ..helpers.loggers import create_logger

logger_misc = create_logger("misc")


def cast_values_csvs(d, idx, x):
    """
    Attempt to cast string to float. If error, keep as a string.
    :param dict d: Data
    :param int idx: Index number
    :param str x: Data
    :return any:
    """
    try:
        d[idx].append(float(x))
    except ValueError:
        d[idx].append(x)
        # logger_misc.warn("cast_values_csv: ValueError")
        # logger_misc.warn("ValueError: col: {}, {}".format(x, e))
    except KeyError as e:
        logger_misc.warn("cast_values_csv: KeyError: col: {}, {}".format(x, e))

    return d


def cast_float(x):
    """
    Attempt to cleanup string or convert to number value.
    :param any x:
    :return float:
    """
    try:
        x = float(x)
    except ValueError:
        try:
            x = x.strip()
        except AttributeError as e:
            logger_misc.warn("parse_str: AttributeError: String not number or word, {}, {}".format(x, e))
    return x


def cast_int(x):
    """
    Cast unknown type into integer
    :param any x:
    :return int:
    """
    try:
        x = int(x)
    except ValueError:
        try:
            x = x.strip()
        except AttributeError as e:
            logger_misc.warn("parse_str: AttributeError: String not number or word, {}, {}".format(x, e))
    return x


def check_dsn(name, _json):
    """
    Get a dataSetName. If one is not provided, then insert the filename as the dataSetName.
    :param str name: Filename w/o extension
    :param dict _json: Metadata
    :return dict _json: Metadata
    """
    if "dataSetName" not in _json:
        _json["dataSetName"] = name
    return _json


def clean_doi(doi_string):
    """
    Use regex to extract all DOI ids from string (i.e. 10.1029/2005pa001215)
    :param str doi_string: Raw DOI string value from input file. Often not properly formatted.
    :return list: DOI ids. May contain 0, 1, or multiple ids.
    """
    regex = re.compile(r'\b(10[.][0-9]{3,}(?:[.][0-9]+)*/(?:(?!["&\'<>,])\S)+)\b')
    try:
        # Returns a list of matching strings
        m = re.findall(regex, doi_string)
    except TypeError as e:
        # If doi_string is None type, return empty list
        logger_misc.warn("TypeError cleaning DOI: {}, {}".format(doi_string, e))
        m = []
    return m


def fix_coordinate_decimal(d):
    """
    Coordinate decimal degrees calculated by an excel formula are often too long as a repeating decimal.
    Round them down to 5 decimals
    :param dict d: Metadata
    :return dict d: Metadata
    """
    try:
        for idx, n in enumerate(d["geo"]["geometry"]["coordinates"]):
            d["geo"]["geometry"]["coordinates"][idx] = round(n, 5)
    except Exception as e:
        logger_misc.error("fix_coordinate_decimal: {}".format(e))
    return d


def generate_timestamp(fmt=None):
    """
    Generate a timestamp to mark when this file was last modified.
    :param str fmt: Special format instructions
    :return str: YYYY-MM-DD format, or specified format
    """
    if fmt:
        time = dt.datetime.now().strftime(fmt)
    else:
        time = dt.date.today()
    return str(time)


def generate_tsid(size=8):
    """
    Generate a TSid string. Use the "PYT" prefix for traceability, and 8 trailing generated characters
    ex: PYT9AG234GS
    :return:
    """
    chars = string.ascii_uppercase + string.digits
    _gen = "".join(random.choice(chars) for _ in range(size))
    return "PYT" + str(_gen)


def get_appended_name(name, columns):
    """
    Append numbers to a name until it no longer conflicts with the other names in a column.
    Necessary to avoid overwriting columns and losing data. Loop a preset amount of times to avoid an infinite loop.
    There shouldn't ever be more than two or three identical variable names in a table.
    :param str name: Variable name in question
    :param dict columns: Columns listed by variable name
    :return str: Appended variable name
    """
    loop = 0
    while name in columns:
        loop += 1
        if loop > 10:
            logger_misc.warn("get_appended_name: Too many loops: Tried to get appended name but something looks wrong")
            break
        tmp = name + "-" + str(loop)
        if tmp not in columns:
            return tmp
    return name + "-99"


def get_authors_as_str(x):
    """
    Take author or investigator data, and convert it to a concatenated string of names.
    Author data structure has a few variations, so account for all.
    :param any x: Author data
    :return str: Author string
    """
    _authors = ""
    # if it's a string already, we're done
    if isinstance(x, str):
        return x

    # elif it's a list, keep going
    elif isinstance(x, list):
        # item in list is a str
        if isinstance(x[0], str):
            # loop and concat until the last item
            for name in x[:-1]:
                # all inner items get a semi-colon at the end
                _authors += str(name) + "; "
            # last item does not get a semi-colon at the end
            _authors += str(x[-1])

        # item in list is a dictionary
        elif isinstance(x[0], dict):
            # dictionary structure SHOULD have authors listed until the "name" key.
            try:
                # loop and concat until the last item
                for entry in x[:-1]:
                    # all inner items get a semi-colon at the end
                    _authors += str(entry["name"]) + "; "
                # last item does not get a semi-colon at the end
                _authors += str(x[-1]["name"])
            except KeyError:
                logger_misc.warn("get_authors_as_str: KeyError: Authors incorrect data structure")

    else:
        logger_misc.debug("get_authors_as_str: TypeError: author/investigators isn't str or list: {}".format(type(x)))

    return _authors


def get_dsn(d):
    """
    Get the dataset name from a record
    :param dict d: Metadata
    :return str: Dataset name
    """

    try:
        return d["dataSetName"]
    except Exception as e:
        logger_misc.warn("get_dsn: Exception: No datasetname found: {}".format(e))
        return "unknown_dataset"


def get_ensemble_counts(d):
    """
    Determine if this is a 1 or 2 column ensemble. Then determine how many columns and rows it has.
    :param d:
    :return:
    """
    _rows_cols = {"rows": 0, "cols": 0}
    try:

        if len(d) == 1:
            for var, data in d.items():
                # increment columns by one
                _rows_cols["cols"] += len(data["values"])
                # get row count by getting len of column (since it's only one list
                _rows_cols["rows"] = len(data["values"][0])
                break

        elif len(d) == 2:
            for var, data in d.items():
                # multiple columns in one. list of lists
                if isinstance(data["number"], list):
                    # add total amount of columns to the running total
                    _rows_cols["cols"] += len(data["values"])
                # single column. one list
                else:
                    # increment columns by one
                    _rows_cols["cols"] += 1
                    # get row count by getting len of column (since it's only one list
                    _rows_cols["rows"] = len(data["values"])

    except Exception as e:
        logger_misc.warn("get_ensemble_counts: {}".format(e))

    return _rows_cols


def get_missing_value_key(d):
    """
    Get the Missing Value entry from a table of data. If none is found, try the columns.
    If still none found, prompt user.
    :param dict d: Table of data
    :return str: Missing Value
    """
    _mv = "nan"

    # Attempt to find a table-level missing value key
    try:
        # check for missing value key at the table root
        _mv = d["missingValue"]
    except KeyError as e:
        logger_misc.info("get_missing_value: No missing value key found: {}".format(e))
    except AttributeError as e:
        logger_misc.warn("get_missing_value: Column is wrong data type: {}".format(e))

    # No table-level missing value found. Attempt to find a column-level missing value key
    if not _mv:
        try:
            # loop for each column of data, searching for a missing value key
            for k, v in d["columns"].items():
                # found a column with a missing value key. Store it and exit the loop.
                _mv = v["missingValue"]
                break
        except KeyError:
            # There are no columns in this table. We've got bigger problems!
            pass

    # No table-level or column-level missing value. Out of places to look. Ask the user to enter the missing value
    # used in this data
    # if not _mv:
    #     print("No 'missingValue' key provided. Please type the missingValue used in this file: {}\n".format(filename))
    #     _mv = input("missingValue: ")
    return _mv


def get_variable_name_col(d):
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
            num = "unknown"
            if "number" in d:
                num = d["number"]
            print("Error: column number <{}> is missing a variableName. Please fix.".format(num))
            logger_misc.info("get_variable_name_col: KeyError: missing key")
    return var


def get_table_key(key, d, fallback=""):
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
        logger_misc.info("get_variable_name_table: KeyError: missing {}, use name: {}".format(key, fallback))
        return fallback


def get_lipd_version(d):
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


def is_ensemble(d):
    """
    Check if a table of data is an ensemble table. Is the first values index a list? ensemble. Int/float? not ensemble.
    :param dict d: Table data
    :return bool: Ensemble or not ensemble
    """
    for var, data in d.items():
        try:
            if isinstance(data["number"], list):
                return True
        except Exception as e:
            logger_misc.debug("misc: is_ensemble: {}".format(e))
    return False


def load_fn_matches_ext(file_path, file_type):
    """
    Check that the file extension matches the target extension given.
    :param str file_path: Path to be checked
    :param str file_type: Target extension
    :return bool:
    """
    correct_ext = False
    curr_ext = os.path.splitext(file_path)[1]
    exts = [curr_ext, file_type]
    try:
        # special case: if file type is excel, both extensions are valid.
        if ".xlsx" in exts and ".xls" in exts:
            correct_ext = True
        elif curr_ext == file_type:
            correct_ext = True
        else:
            print("Use '{}' to load this file: {}".format(FILE_TYPE_MAP[curr_ext]["load_fn"],
                                                          os.path.basename(file_path)))
    except Exception as e:
        logger_misc.debug("load_fn_matches_ext: {}".format(e))

    return correct_ext


def match_operators(inp, relate, cut):
    """
    Compare two items. Match a string operator to an operator function
    :param str inp: Comparison item
    :param str relate: Comparison operator
    :param any cut: Comparison item
    :return bool: Comparison truth
    """
    logger_misc.info("enter match_operators")
    ops = {'>': operator.gt,
           '<': operator.lt,
           '>=': operator.ge,
           '<=': operator.le,
           '=': operator.eq
           }
    try:
        truth = ops[relate](inp, cut)
    except KeyError as e:
        truth = False
        logger_misc.warn("get_truth: KeyError: Invalid operator input: {}, {}".format(relate, e))
    logger_misc.info("exit match_operators")
    return truth


def match_arr_lengths(l):
    """
    Check that all the array lengths match so that a DataFrame can be created successfully.
    :param list l: Nested arrays
    :return bool: Valid or invalid
    """
    try:
        # length of first list. use as basis to check other list lengths against.
        inner_len = len(l[0])
        # check each nested list
        for i in l:
            # if the length doesn't match the first list, then don't proceed.
            if len(i) != inner_len:
                return False
    except IndexError:
        # couldn't get index 0. Wrong data type given or not nested lists
        print("Error: Array data is not formatted correctly.")
        return False
    except TypeError:
        # Non-iterable data type given.
        print("Error: Array data missing")
        return False
    # all array lengths are equal. made it through the whole list successfully
    return True


def _merge_interpretations(d):
    """

    :param d:
    :return:
    """
    _tmp = []
    try:
        # Now loop and aggregate the interpretation data into one list
        for k, v in d.items():
            if k in ["climateInterpretation", "isotopeInterpretation", "interpretation"]:
                # now add in the new data
                if isinstance(v, list):
                    for i in v:
                        _tmp.append(i)
                elif isinstance(v, dict):
                    _tmp.append(d[k])
        # Set the aggregate data into the interpretation key
        d["interpretation"] = _tmp

    except Exception as e:
        print("Error: merge_interpretations: {}".format(e))

    # Now remove the old interpretation keys
    for key in ["climateInterpretation", "isotopeInterpretation"]:
        try:
            d[key] = ""
        except Exception:
            pass

    return d


def mv_files(src, dst):
    """
    Move all files from one directory to another
    :param str src: Source directory
    :param str dst: Destination directory
    :return none:
    """
    # list the files in the src directory
    files = os.listdir(src)
    # loop for each file found
    for file in files:
        # move the file from the src to the dst
        shutil.move(os.path.join(src, file), os.path.join(dst, file))
    return


def normalize_name(s):
    """
    Remove foreign accents and characters to normalize the string. Prevents encoding errors.
    :param str s:
    :return str:
    """
    # Normalize the string into a byte string form
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    # Remove the byte string and quotes from the string
    s = str(s)[2:-1]
    return s


def path_type(path, target):
    """
    Determine if given path is file, directory, or other. Compare with target to see if it's the type we wanted.
    :param str path: Path
    :param str target: Target type wanted
    :return bool:
    """
    if os.path.isfile(path) and target == "file":
        return True
    elif os.path.isdir(path) and target == "directory":
        return True
    else:
        print("Error: Path given is not a {}: {}".format(target, path))
    return False


def _prompt_filename():
    """
    Ask user if they want to provide a filename, or choose a generic time-stamped filename.
    :return:
    """
    filename = ""
    return filename


def prompt_protocol():
    """
    Prompt user if they would like to save pickle file as a dictionary or an object.
    :return str: Answer
    """
    stop = 3
    ans = ""
    while True and stop > 0:
        ans = input("Save as (d)ictionary or (o)bject?\n"
                    "* Note:\n"
                    "Dictionaries are more basic, and are compatible with Python v2.7+.\n"
                    "Objects are more complex, and are only compatible with v3.4+ ")
        if ans not in ("d", "o"):
            print("Invalid response: Please choose 'd' or 'o'")
        else:
            break
    # if a valid answer isn't captured, default to dictionary (safer, broader)
    if ans == "":
        ans = "d"
    return ans


def put_tsids(x):
    """
    Recursively add in TSids into any columns that do not have them.
    Look for "columns" keys, and then start looping and adding generated TSids to each column
    :param any x: Recursive, so could be any data type.
    :return any x: Recursive, so could be any data type.
    """
    try:
        if isinstance(x, dict):
            try:
                for k, v in x.items():
                    # Is this the columns key?
                    if k == "columns":
                        try:
                            # loop over each column of data. Sorted by variableName key
                            for var, data in v.items():
                                try:
                                    # make a case-insensitive keys list for checking existence of "tsid"
                                    keys = [key.lower() for key in data.keys()]
                                    # If a TSid already exists, then we don't need to do anything.
                                    if "tsid" not in keys:
                                        # generate the TSid, and add it to the dictionary
                                        data["TSid"] = generate_tsid()
                                        logger_misc.info("put_tsids: Generated new TSid: {}".format(data["TSid"]))
                                except AttributeError as e:
                                    logger_misc.debug("put_tsids: level 3: AttributeError: {}".format(e))
                                except Exception as e:
                                    logger_misc.debug("put_tsids: level 3: Exception: {}".format(e))
                        except Exception as e:
                            print("put_tsids: level 2: Exception: {}, {}".format(k, e))
                    # If it's not "columns", then dive deeper.
                    else:
                        x[k] = put_tsids(v)
            except Exception as e:
                print("put_tsids: level 1: Exception: {}, {}".format(k, e))
        # Item is a list, dive deeper for each item in the list
        elif isinstance(x, list):
            for idx, entry in enumerate(x):
                x[idx] = put_tsids(entry)
    except Exception as e:
        print("put_tsids: root: Exception: {}, {}".format(k, e))
    return x


def rm_empty_fields(x):
    """
    Go through N number of nested data types and remove all empty entries. Recursion
    :param any x: Dictionary, List, or String of data
    :return any: Returns a same data type as original, but without empties.
    """
    # No logger here because the function is recursive.
    # Int types don't matter. Return as-is.
    if not isinstance(x, int) and not isinstance(x, float):
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
                x[i] = rm_empty_fields(x[i])
            # After substitutions, remove empty entries.
            for i in x:
                # Many 0 values are important (coordinates, m/m/m/m). Don't remove them.
                if not i and i not in [0, 0.0]:
                    x.remove(i)
        elif isinstance(x, dict):
            # First, go through and substitute "" (empty string) entry for any values in EMPTY
            for k, v in x.items():
                x[k] = rm_empty_fields(v)
            # After substitutions, go through and delete the key-value pair.
            # This has to be done after we come back up from recursion because we cannot pass keys down.
            for key in list(x.keys()):
                if not x[key] and x[key] not in [0, 0.0]:
                    del x[key]
    return x


def rm_empty_doi(d):
    """
    If an "identifier" dictionary has no doi ID, then it has no use. Delete it.
    :param dict d: JSON Metadata
    :return dict: JSON Metadata
    """
    logger_misc.info("enter remove_empty_doi")
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
        logger_misc.warn("remove_empty_doi: KeyError: publication key not found, {}".format(e))
    logger_misc.info("exit remove_empty_doi")
    return d


def rm_files(path, extension):
    """
    Remove all files in the given directory with the given extension
    :param str path: Directory
    :param str extension: File type to remove
    :return none:
    """
    files = list_files(extension, path)
    for file in files:
        if file.endswith(extension):
            os.remove(os.path.join(path, file))
    return


def rm_values_fields(x):
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
                    rm_values_fields(v)
                elif isinstance(v, list):
                    rm_values_fields(v)
    elif isinstance(x, list):
        for i in x:
            rm_values_fields(i)

    return x


def rm_missing_values_table(d):
    """
    Loop for each table column and remove the missingValue key & data
    :param dict d: Table data
    :return dict d: Table data
    """
    try:
        for k, v in d["columns"].items():
            d["columns"][k] = rm_keys_from_dict(v, ["missingValue"])
    except Exception:
        # If we get a KeyError or some other error, it's not a big deal. Keep going.
        pass
    return d


def rm_keys_from_dict(d, keys):
    """
    Given a dictionary and a key list, remove any data in the dictionary with the given keys.
    :param dict d: Data
    :param list keys: List of key data to remove
    :return dict d: Data (with keys + data removed)
    """
    # Loop for each key given
    for key in keys:
        # Is the key in the dictionary?
        if key in d:
            try:
                d.pop(key, None)
            except KeyError:
                # Not concerned with an error. Keep going.
                pass
    return d


def _replace_missing_values_table(values, mv):
    """
    Receive all table column values as a list of lists. Loop for each column of values
    :param list values: One list per column
    :param any mv: Missing Value being used
    :return list: List of lists with updated "nan" missing values
    """

    for idx, column in enumerate(values):
        values[idx] = _replace_missing_values_column(column, mv)

    return values


def _replace_missing_values_column(values, mv):
    """
    Replace Missing Values in the values list where applicable
    :param list values: One column of values
    :return list: Column with updated "nan" missing values
    """
    for idx, v in enumerate(values):
        try:
            if v in EMPTY or v == mv:
                values[idx] = "nan"
            elif math.isnan(float(v)):
                values[idx] = "nan"
            else:
                values[idx] = v
        except (TypeError, ValueError):
            values[idx] = v

    return values


def split_path_and_file(s):
    """
    Given a full path to a file, split and return a path and filename
    :param str s: Full path
    :return str str: Path, filename
    """
    _path = s
    _filename = ""
    try:
        x = os.path.split(s)
        _path = x[0]
        _filename = x[1]
    except Exception:
        print("Error: unable to split path")

    return _path, _filename


def update_lipd_version(d):
    """
    Metadata is indexed by number at this step.

    Use the current version number to determine where to start updating from. Use "chain versioning" to make it
    modular. If a file is a few versions behind, convert to EACH version until reaching current. If a file is one
    version behind, it will only convert once to the newest.
    :param dict d: Metadata
    :return dict d: Metadata
    """
    # Get the lipd version number.
    version = get_lipd_version(d)

    # Update from (N/A or 1.0) to 1.1
    if version in [1.0, "1.0"]:
        d = update_lipd_v1_1(d)
        version = 1.1

    # Update from 1.1 to 1.2
    if version in [1.1, "1.1"]:
        d = update_lipd_v1_2(d)
        version = 1.2
    if version in [1.2, "1.2"]:
        d = update_lipd_v1_3(d)
        version = 1.3

    return d


def update_lipd_v1_1(d):
    """
    Update LiPD v1.0 to v1.1
    - chronData entry is a list that allows multiple tables
    - paleoData entry is a list that allows multiple tables
    - chronData now allows measurement, model, summary, modelTable, ensemble, calibratedAges tables
    - Added 'lipdVersion' key

    :param dict d: Metadata v1.0
    :return dict d: Metadata v1.1
    """
    logger_misc.info("enter update_lipd_v1_1")
    tmp_all = []

    try:
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

        # Log that this is now a v1.1 structured file
        d["lipdVersion"] = 1.1
    except Exception as e:
        logger_misc.error("update_lipd_v1_1: Exception: {}".format(e))
    logger_misc.info("exit update_lipd_v1_1")
    return d


def update_lipd_v1_2(d):
    """
    Update LiPD v1.1 to v1.2
    - Added NOAA compatible keys : maxYear, minYear, originalDataURL, WDCPaleoURL, etc
    - 'calibratedAges' key is now 'distribution'
    - paleoData structure mirrors chronData. Allows measurement, model, summary, modelTable, ensemble,
        distribution tables
    :param dict d: Metadata v1.1
    :return dict d: Metadata v1.2
    """
    logger_misc.info("enter update_lipd_v1_2")
    tmp_all = []

    try:
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
        # Log that this is now a v1.1 structured file
        d["lipdVersion"] = 1.2
    except Exception as e:
        logger_misc.error("update_lipd_v1_2: Exception: {}".format(e))

    logger_misc.info("exit update_lipd_v1_2")
    return d


def update_lipd_v1_3(d):
    """
    Update LiPD v1.2 to v1.3
    - Added 'createdBy' key
    - Top-level folder inside LiPD archives are named "bag". (No longer <datasetname>)
    - .jsonld file is now generically named 'metadata.jsonld' (No longer <datasetname>.lpd )
    - All "paleo" and "chron" prefixes are removed from "paleoMeasurementTable", "paleoModel", etc.
    - Merge isotopeInterpretation and climateInterpretation into "interpretation" block
    - ensemble table entry is a list that allows multiple tables
    - summary table entry is a list that allows multiple tables
    :param dict d: Metadata v1.2
    :return dict d: Metadata v1.3
    """
    # sub routine (recursive): changes all the key names and merges interpretation
    d = update_lipd_v1_3_names(d)
    # sub routine: changes ensemble and summary table structure
    d = update_lipd_v1_3_structure(d)
    d["lipdVersion"] = 1.3
    if "LiPDVersion" in d:
        del d["LiPDVersion"]
    return d


def update_lipd_v1_3_names(d):
    """
    Update the key names and merge interpretation data
    :param dict d: Metadata
    :return dict d: Metadata
    """
    try:
        if isinstance(d, dict):
            for k, v in d.items():
                # dive down for dictionaries
                d[k] = update_lipd_v1_3_names(v)

                # see if the key is in the remove list
                if k in VER_1_3["swap"]:
                    # replace the key in the dictionary
                    _key_swap = VER_1_3["swap"][k]
                    d[_key_swap] = d.pop(k)
                elif k in VER_1_3["tables"]:
                    d[k] = ""
            for _key in ["climateInterpretation", "isotopeInterpretation"]:
                if _key in d:
                    d = _merge_interpretations(d)

        elif isinstance(d, list):
            # dive down for lists
            for idx, i in enumerate(d):
                d[idx] = update_lipd_v1_3_names(i)
    except Exception as e:
        print("Error: Unable to update file to LiPD v1.3: {}".format(e))
        logger_misc.error("update_lipd_v1_3_names: Exception: {}".format(e))
    return d


def update_lipd_v1_3_structure(d):
    """
    Update the structure for summary and ensemble tables
    :param dict d: Metadata
    :return dict d: Metadata
    """
    for key in ["paleoData", "chronData"]:
        if key in d:
            for entry1 in d[key]:
                if "model" in entry1:
                    for entry2 in entry1["model"]:
                        for key_table in ["summaryTable", "ensembleTable"]:
                            if key_table in entry2:
                                if isinstance(entry2[key_table], dict):
                                    try:
                                        _tmp = entry2[key_table]
                                        entry2[key_table] = []
                                        entry2[key_table].append(_tmp)
                                    except Exception as e:
                                        logger_misc.error("update_lipd_v1_3_structure: Exception: {}".format(e))
    return d


def unwrap_arrays(l):
    """
    Unwrap nested lists to be one "flat" list of lists. Mainly for prepping ensemble data for DataFrame() creation
    :param list l: Nested lists
    :return list: Flattened lists
    """
    # keep processing until all nesting is removed
    process = True
    # fail safe: cap the loops at 20, so we don't run into an error and loop infinitely.
    # if it takes more than 20 loops then there is a problem with the data given.
    loops = 25
    while process and loops > 0:
        try:
            # new "flat" list
            l2 = []
            for k in l:
                # all items in this list are numeric, so this list is done. append to main list
                if all(isinstance(i, float) or isinstance(i, int) for i in k):
                    l2.append(k)
                # this list has more nested lists inside. append each individual nested list to the main one.
                elif all(isinstance(i, list) or isinstance(i, np.ndarray) for i in k):
                    for i in k:
                        l2.append(i)
        except Exception:
            print("something went wrong during process")
        # verify the main list
        try:
            # if every list has a numeric at index 0, then there is no more nesting and we can stop processing
            if all(isinstance(i[0], (int, str, float)) for i in l2):
                process = False
            else:
                l = l2
        except IndexError:
            # there's no index 0, so there must be mixed data types or empty data somewhere.
            print("something went wrong during verify")
        loops -= 1
    return l2

