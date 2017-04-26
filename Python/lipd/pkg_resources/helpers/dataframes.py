import collections

import pandas as pd

from ..helpers.regexes import re_pandas_x_num
from ..helpers.loggers import create_logger
from ..helpers.alternates import DATA_FRAMES
from ..helpers.misc import unwrap_arrays, match_arr_lengths

logger_dataframes = create_logger("PDSlib")


def _dotnotation_for_nested_dictionary(d, key, dots):
    """
    Flattens nested data structures using dot notation.
    :param dict d: Original or nested dictionary
    :param str key:
    :param dict dots: Dotted dictionary so far
    :return dict: Dotted dictionary so far
    """
    if key == 'chronData':
        # Not interested in expanding chronData in dot notation. Keep it as a chunk.
        dots[key] = d
    elif isinstance(d, dict):
        for k in d:
            _dotnotation_for_nested_dictionary(d[k], key + '.' + k if key else k, dots)
    elif isinstance(d, list) and \
            not all(isinstance(item, (int, float, complex, list)) for item in d):
        for n, d in enumerate(d):
            _dotnotation_for_nested_dictionary(d, key + '.' + str(n) if key != "" else key, dots)
    else:
        dots[key] = d
    return dots


def create_dataframe(ensemble):
    """
    Create a data frame from given nested lists of ensemble data
    :param list ensemble: Ensemble data
    :return obj: Dataframe
    """
    logger_dataframes.info("enter ens_to_df")
    # "Flatten" the nested lists. Bring all nested lists up to top-level. Output looks like [ [1,2], [1,2], ... ]
    ll = unwrap_arrays(ensemble)
    # Check that list lengths are all equal
    valid = match_arr_lengths(ll)
    if valid:
        # Lists are equal lengths, create the dataframe
        df = pd.DataFrame(ll)
    else:
        # Lists are unequal. Print error and return nothing.
        df = "empty"
        print("Error: Numpy Array lengths do not match. Cannot create data frame")
    logger_dataframes.info("exit ens_to_df")
    return df


def lipd_to_df(metadata, csvs):
    """
    Create an organized collection of data frames from LiPD data
    :param dict metadata: LiPD data
    :param dict csvs: Csv data
    :return dict: One data frame per table, organized in a dictionary by name
    """
    dfs = {}
    logger_dataframes.info("enter lipd_to_df")

    # Flatten the dictionary, but ignore the chron data items
    dict_in_dotted = {}
    logger_dataframes.info("enter dot_notation")
    _dotnotation_for_nested_dictionary(metadata, '', dict_in_dotted)
    dict_in_dotted = collections.OrderedDict(sorted(dict_in_dotted.items()))

    # Create one data frame for metadata items
    dfs["metadata"] = pd.DataFrame(list(dict_in_dotted.items()), columns=["Key", "Value"])

    # Create data frames for paleo data and chron data items. This does not use LiPD data, it uses the csv data
    dfs.update(_get_dfs(csvs))

    return dfs


def ts_to_df(metadata):
    """
    Create a data frame from one TimeSeries object
    :param dict metadata: Time Series dictionary
    :return dict: One data frame per table, organized in a dictionary by name
    """
    logger_dataframes.info("enter ts_to_df")
    dfs = {}

    # Plot the variable + values vs year, age, depth (whichever are available)
    dfs["paleoData"] = pd.DataFrame(_plot_ts_cols(metadata))

    # Plot the chronology variables + values in a data frame
    dfs["chronData"] = _get_key_data(metadata, "chronData_df")

    # Take out the chronData pandas data frame object if it exists in the metadata
    # Otherwise, the data frame renderer gets crazy and errors out.
    if "chronData_df" in metadata:
        del metadata["chronData_df"]
    s = collections.OrderedDict(sorted(metadata.items()))

    # Put key-vars in a data frame to make it easier to visualize
    dfs["metadata"] = pd.DataFrame(list(s.items()), columns=['Key', 'Value'])

    logger_dataframes.info("exit ts_to_df")
    return dfs


def _plot_ts_cols(ts):
    """
    Get variable + values vs year, age, depth (whichever are available)
    :param dict ts: TimeSeries dictionary
    :return dict: Key: variableName, Value: Panda Series object
    """
    logger_dataframes.info("enter get_ts_cols()")
    d = {}

    # Not entirely necessary, but this will make the column headers look nicer for the data frame
    # The column header will be in format "variableName (units)"
    try:
        units = " (" + ts["paleoData_units"] + ")"
    except KeyError as e:
        units = ""
        logger_dataframes.warn("get_ts_cols: KeyError: paleoData_units not found, {}".format(e))
    try:
        d[ts["paleoData_variableName"] + units] = ts["paleoData_values"]
    except KeyError as e:
        logger_dataframes.warn("get_ts_cols: KeyError: variableName or values not found, {}".format(e))

    # Start looking for age, year, depth columns
    for k, v in ts.items():
        if re_pandas_x_num.match(k):
            try:
                units = " (" + ts[k + "Units"] + ")"
                d[k + units] = v
            except KeyError as e:
                logger_dataframes.warn("get_ts_cols: KeyError: Special column units, {}, {}".format(k, e))
    logger_dataframes.info("exit get_ts_cols: found {}".format(len(d)))
    return d


def _get_dfs(csvs):
    """
    LiPD Version 1.2
    Create a data frame for each table for the given key
    :param dict csvs: LiPD metadata dictionary
    :return dict: paleo data data frames
    """
    logger_dataframes.info("enter get_lipd_cols")
    # placeholders for the incoming data frames
    dfs = {"chronData": {}, "paleoData": {}}
    try:
        for filename, cols in csvs.items():
            tmp = {}
            for var, data in cols.items():
                tmp[var] = pd.Series(data["values"])
            if "chron" in filename.lower():
                dfs["chronData"][filename] = pd.DataFrame(tmp)
            elif "paleo" in filename.lower():
                dfs["paleoData"][filename] = pd.DataFrame(tmp)
    except KeyError:
        logger_dataframes.warn("get_lipd_cols: AttributeError: expected type dict, given type {}".format(type(csvs)))

    logger_dataframes.info("exit get_lipd_cols")
    return dfs


def _get_key_data(d, key):
    """
    Generic function to grab dictionary data by key with error handling
    :return:
    """
    d2 = ""
    try:
        d2 = d[key]
    except KeyError:
        logger_dataframes.info("get_key_data: KeyError: {}".format(key))
    return d2


def get_filtered_dfs(lib, expr):
    """
    Main: Get all data frames that match the given expression
    :return dict: Filenames and data frames (filtered)
    """
    logger_dataframes.info("enter get_filtered_dfs")

    dfs = {}
    tt = None

    # Process all lipds files or one lipds file?
    specific_files = _check_expr_filename(expr)

    # Determine the table type wanted
    if "chron" in expr:
        tt = "chron"
    elif "paleo" in expr:
        tt = "paleo"

    # Get all filenames of target type.
    if tt:

        if specific_files:
            # The user has specified a single LiPD file to get data frames from.
            for file in specific_files:
                if file in lib:
                    lo_meta = lib[file].get_metadata()
                    lo_dfs = lib[file].get_dfs()

                    # Only start a search if this lipds file has data frames available. Otherwise, pointless.
                    if lo_dfs:
                        # Get list of all matching filenames
                        filenames = _match_dfs_expr(lo_meta, expr, tt)
                        # Update our output data frames dictionary
                        dfs.update(_match_filenames_w_dfs(filenames, lo_dfs))
                else:
                    print("Unable to find LiPD file in Library: {}".format(file))

        # Process all LiPD files in the library. A file has not been specified in the expression.
        else:
            # Loop once on each lipds object in the library
            for ln, lo in lib.items():
                # Get the
                lo_meta = lo.get_metadata()
                lo_dfs = lo.get_dfs()

                # Only start a search if this lipds file has data frames available. Otherwise, pointless.
                if lo_dfs:
                    # Get list of all matching filenames
                    filenames = _match_dfs_expr(lo_meta, expr, tt)
                    # Update our output data frames dictionary
                    dfs.update(_match_filenames_w_dfs(filenames, lo_dfs))

    logger_dataframes.info("exit get_filtered_dfs")
    return dfs


def _match_dfs_expr(lo_meta, expr, tt):
    """
    Use the given expression to get all data frames that match the criteria (i.e. "paleo measurement tables")
    :param dict lo_meta: Lipd object metadata
    :param str expr: Search expression
    :param str tt: Table type (chron or paleo)
    :return list: All filenames that match the expression
    """
    logger_dataframes.info("enter match_dfs_expr")
    filenames = []
    s = "{}Data".format(tt)

    # Top table level. Going through all tables of certain type (i.e. chron or paleo)
    for k, v in lo_meta["{}Data".format(tt)].items():

        # Inner table level. Get data from one specific table
        if "measurement" in expr:
            for k1, v1 in v["{}MeasurementTable".format(tt)].items():
                try:
                    f = v1["filename"]
                    if f.endswith(".csv"):
                        filenames.append(f)
                except KeyError:
                    # Not concerned if the key wasn't found.
                    logger_dataframes.info("match_dfs_expr: KeyError: filename not found in: {} {}".format(tt, "measurement"))

        elif "ensemble" in expr:
            for k1, v1 in v["{}Model".format(tt)].items():
                try:
                    f = v1["ensembleTable"]["filename"]
                    if f.endswith(".csv"):
                        filenames.append(f)
                except KeyError:
                    # Not concerned if the key wasn't found.
                    logger_dataframes.info("match_dfs_expr: KeyError: filename not found in: {} {}".format(tt, "ensemble"))

        elif "model" in expr:
            for k1, v1 in v["{}Model".format(tt)].items():
                try:
                    f = v1["{}ModelTable".format(tt)]["filename"]
                    if f.endswith(".csv"):
                        filenames.append(f)
                except KeyError:
                    # Not concerned if the key wasn't found.
                    logger_dataframes.info("match_dfs_expr: KeyError: filename not found in: {} {}".format(tt, "model"))

        elif "dist" in expr:
            for k1, v1 in v["{}Model".format(tt)].items():
                for k2, v2 in v1["distribution"].items():
                    try:
                        f = v2["filename"]
                        if f.endswith(".csv"):
                            filenames.append(f)
                    except KeyError:
                        # Not concerned if the key wasn't found.
                        logger_dataframes.info(
                            "match_dfs_expr: KeyError: filename not found in: {} {}".format(tt, "dist"))

    logger_dataframes.info("exit match_dfs_expr")
    return filenames


def _match_filenames_w_dfs(filenames, lo_dfs):
    """
    Match a list of filenames to their data frame counterparts. Return data frames
    :param list filenames: Filenames of data frames to retrieve
    :param dict lo_dfs: All data frames
    :return dict: Filenames and data frames (filtered)
    """
    logger_dataframes.info("enter match_filenames_w_dfs")
    dfs = {}

    for filename in filenames:
        try:
            if filename in lo_dfs["chronData"]:
                dfs[filename] = lo_dfs["chronData"][filename]
            elif filename in lo_dfs["paleoData"]:
                dfs[filename] = lo_dfs["paleoData"][filename]
        except KeyError:
            logger_dataframes.info("filter_dfs: KeyError: missing data frames keys")

    logger_dataframes.info("exit match_filenames_w_dfs")
    return dfs


def _check_expr_filename(expr):
    """
    Split the expression and look to see if there's a specific filename that the user wants to process.
    :param str expr: Search expression
    :return str: Filename or None
    """
    expr_lst = expr.split()
    f = [x for x in expr_lst if x not in DATA_FRAMES and x.endswith(".lpd")]
    return f
