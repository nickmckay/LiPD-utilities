import operator
import pickle
import os
import datetime as dt
import numpy as np
import unicodedata

from ..helpers.loggers import create_logger
from ..helpers.blanks import EMPTY

logger_misc = create_logger("misc")


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


def unpickle_data(path, filename):
    """
    Unpickle the chosen file into the workspace
    :param str filename: Pickle filename
    :param str path: Source directory
    :return dict: unpickled data
    """
    d = {}
    os.chdir(path)
    # Load data (deserialize)
    try:
        with open(filename, 'rb') as handle:
            d = pickle.load(handle)
    except Exception:
        print("Error: unable to load pickle file")
    return d


def pickle_data(path, d, ans):
    """
    Pickle a dictionary of data to file, and save.
    :param dict d: Data to be pickled
    :param str path: Destination directory
    :param str ans: Pickle protocol option
    :return none:
    """
    os.chdir(path)

    # get a timestamp to append to the filename, to make it unique
    filename = 'lipd_data_{}.p'.format( dt.datetime.now().strftime('%Y%m%d%H%M%S'))

    # Store data (serialize)
    try:
        with open(filename, 'wb') as handle:
            # Object: Pickle with highest protocol
            if ans == "o":
                pickle.dump(d, handle)
            # Dictionary: Pickle with protocol 2, for use in python v2.7+
            else:
                pickle.dump(d, handle, protocol=2)
    except Exception:
        print("Error: unable to create pickle file")
    return


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


def cast_values_csvs(d, idx, x):
    """
    Attempt to cast string to float. If error, keep as a string.
    :param str x: String data
    :return any:
    """
    try:
        d[idx].append(float(x))
    except ValueError as e:
        d[idx].append(x)
        logger_misc.warn("ValueError: col: {}, {}".format(x, e))
    except KeyError as e:
        logger_misc.warn("KeyError: col: {}, {}".format(x, e))

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


def update_lipd_version(d):
    """
    Use the current version number to determine where to start updating from. Use "chain versioning" to make it
    modular. If a file is a few versions behind, convert to EACH version until reaching current. If a file is one
    version behind, it will only convert once to the newest.
    :param dict d: Metadata dictionary
    :return dict: Most current version metadata dictionary
    """

    # Get the lipds version number.
    version = get_lipd_version(d)

    # Update from (N/A or 1.0) to 1.1
    if version in (1.0, "1.0"):
        d = lipd_v1_0_to_v1_1(d)
        version = 1.1

    # Update from 1.1 to 1.2
    if version in (1.1, "1.1"):
        d = lipd_v1_1_to_v1_2(d)
        version = 1.2

    return d


def lipd_v1_0_to_v1_1(d):
    """
    Update LiPD version 1.0 to version 1.1.  See LiPD Version changelog for details.
    NOTE main changes: ChronData turned into a scalable lists of dictioanries.
    :param dict d: Metadata
    :return dict: v1.1 metadata dictionary
    """
    logger_misc.info("enter lipds 1.0 to 1.1")
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
    logger_misc.info("exit lipds 1.0 to 1.1")
    return d


def lipd_v1_1_to_v1_2(d):
    """
    Update LiPD version 1.1 to version 1.2. See LiPD Version changelog for details.
    :param dict d: Metadata dictioanry
    :return dict: v1.2 metadata dictionary
    """
    logger_misc.info("enter lipds 1.1 to 1.2")
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
    logger_misc.info("exit lipds 1.1 to 1.2")
    return d


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


def get_variable_name_table(key, d, fallback=""):
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
        logger_misc.info("get_variable_name_table: KeyError: missing {}".format(key))
        return fallback


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

