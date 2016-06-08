import collections

import pandas as pd

from ..helpers.regexes import *
from ..helpers.loggers import *

logger_pdslib = create_logger("PDSlib")


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


def lipd_to_df(metadata, csvs):
    """
    Create a pandas data frame using LiPD metadata and CSV data
    :param dict metadata: LiPD metadata dictionary
    :param dict csvs: Csv data
    :return dict: One data frame per table, organized in a dictionary by name
    """
    dfs = {}
    logger_pdslib.info("enter lipd_to_df")
    dict_in_dotted = {}
    logger_pdslib.info("enter dot_notation")
    _dotnotation_for_nested_dictionary(metadata, '', dict_in_dotted)
    dict_in_dotted = collections.OrderedDict(sorted(dict_in_dotted.items()))
    dfs["metadata"] = pd.DataFrame(list(dict_in_dotted.items()), columns=["Key", "Value"])
    dfs.update(_get_dfs(csvs))
    return dfs


def ts_to_df(metadata):
    """
    Create a data frame from one TimeSeries object
    :param dict metadata: Time Series dictionary
    :return dict: One data frame per table, organized in a dictionary by name
    """
    logger_pdslib.info("enter ts_to_df")
    dfs = {}
    s = collections.OrderedDict(sorted(metadata.items()))

    # Put key-vars in a data frame to make it easier to visualize
    dfs["metadata"] = pd.DataFrame(list(s.items()), columns=['Key', 'Value'])

    # Plot the variable + values vs year, age, depth (whichever are available)
    dfs["paleoData"] = pd.DataFrame(_get_ts_cols(metadata))

    # Plot the chronology variables + values in a data frame
    dfs["chronData"] = metadata["chronData_df"]

    logger_pdslib.info("exit ts_to_df")
    return dfs


def _get_ts_cols(ts):
    """
    Get variable + values vs year, age, depth (whichever are available)
    :param dict ts: TimeSeries dictionary
    :return dict: Key: variableName, Value: Panda Series object
    """
    logger_pdslib.info("enter get_ts_cols()")
    d = {}
    try:
        # Get the main column data first
        units = " (" + ts["paleoData_units"] + ")"
    except KeyError as e:
        units = ""
        logger_pdslib.warn("get_ts_cols: KeyError: paleoData_units not found, {}".format(e))
    try:
        d[ts["paleoData_variableName"] + units] = ts["paleoData_values"]
    except KeyError as e:
        logger_pdslib.warn("get_ts_cols: KeyError: variableName or values not found, {}".format(e))

    # Start looking for the additional special columns
    for k, v in ts.items():
        if re_pandas_x_num.match(k):
            try:
                units = " (" + ts[k + "Units"] + ")"
            except KeyError as e:
                units = ""
                logger_pdslib.warn("get_ts_cols: KeyError: Special column units, {}, {}".format(k, e))
            d[k + units] = v
    logger_pdslib.info("exit get_ts_cols: found {}".format(len(d)))
    return d


def _get_dfs(csvs):
    """
    Create a data frame for each table for the given key
    :param dict csvs: LiPD metadata dictionary
    :return dict: paleo data data frames
    """
    logger_pdslib.info("enter get_lipd_cols")
    # placeholders for the incoming data frames
    dfs = {"chronData": {}, "paleoData": {}}
    try:
        for filename, cols in csvs.items():
            tmp = {}
            for var, vals in cols.items():
                tmp[var] = pd.Series(vals)
            if "chron" in filename.lower():
                dfs["chronData"][filename] = pd.DataFrame(tmp)
            elif "paleo" in filename.lower():
                dfs["paleoData"][filename] = pd.DataFrame(tmp)
    except KeyError:
        logger_pdslib.warn("get_lipd_cols: AttributeError: expected type dict, given type {}".format(type(csvs)))

    logger_pdslib.info("exit get_lipd_cols")
    return dfs

