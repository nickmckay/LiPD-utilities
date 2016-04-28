import pandas as pd
from ..helpers.regexes import *

import collections

"""
Created by:
Patrick Brockmann - LSCE
2015/10/11

Additions by:
Christopher Heiser - NAU LiPD
2016/04/21
"""


def _dotnotation_for_nested_dictionary(d, key, dots):
    """
    Flattens nested data structures using dot notation.
    :param d:
    :param key:
    :param dots:
    :return:
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


def LiPD_to_df(dict_in):
    """
    Create a pandas dataframe using LiPD metadata and CSV data
    :param dict dict_in: LiPD metadata dictionary
    :return obj: Metadata DF, CSV DF
    """
    dict_in_dotted = {}
    _dotnotation_for_nested_dictionary(dict_in, '', dict_in_dotted)
    dict_in_dotted = collections.OrderedDict(sorted(dict_in_dotted.items()))
    df_meta = pd.DataFrame(list(dict_in_dotted.items()), columns=["Key", "Value"])
    df_data = pd.DataFrame(_get_lipd_cols(dict_in))
    try:
        df_chron = pd.DataFrame(_get_chron_cols(dict_in))
    except KeyError:
        df_chron = "Chronology not available"
    return df_meta, df_data, df_chron


def TS_to_df(dict_in):
    """
    Create a data frame from one TimeSeries object
    :param dict dict_in: Time Series dictionary
    :return obj: 3 Data Frame objects
    """
    s = collections.OrderedDict(sorted(dict_in.items()))
    # Put key-vars in a data frame to make it easier to visualize
    df_meta = pd.DataFrame(list(s.items()), columns=['Key', 'Value'])
    # Plot the variable + values vs year, age, depth (whichever are available)
    df_data = pd.DataFrame(_get_ts_cols(dict_in))
    # Plot the chronology variables + values in a data frame
    try:
        df_chron = dict_in["chronData_df"]
    except KeyError:
        df_chron = "Chronology not available"

    return df_meta, df_data, df_chron


def _get_ts_cols(dict_in):
    """
    Get variable + values vs year, age, depth (whichever are available)
    :param dict dict_in: TimeSeries dictionary
    :return dict: Key: variableName, Value: Panda Series object
    """
    d = {}
    try:
        # Get the main column data first
        units = " (" + dict_in["paleoData_units"] + ")"
    except KeyError:
        units = ""
    try:
        d[dict_in["paleoData_variableName"] + units] = dict_in["paleoData_values"]
    except KeyError:
        pass

    # Start looking for the additional special columns
    for k, v in dict_in.items():
        if re_pandas_x_num.match(k):
            try:
                units = " (" + dict_in[k + "Units"] + ")"
            except KeyError:
                units = ""
            d[k + units] = v

    return d


def _get_lipd_cols(dict_in):
    """
    Grab the variableName and values data from each paleoData table in the LiPD metadata
    :param dict dict_in: LiPD metadata dictionary
    :return dict: Dictionary of { variableName: [valuesArray] }
    """
    d = {}
    try:
        # TODO: make sure this accounts for multiple tables
        for table, table_data in dict_in['paleoData'].items():
            for var, arr in table_data["columns"].items():
                d[var] = pd.Series(arr["values"])
    except KeyError:
        pass

    return d


def _get_chron_cols(dict_in):
    """
    Grab the variableName and values data from each chronData table in the LiPD metadata
    : param dict dict_in: LiPD metadata dictionary
    : return dict: Dictionary of { variableName: [ValuesArray] }
    """
    d = {}
    try:
        for table, table_data in dict_in['chronData'].items():
            for var, arr in table_data["columns"].items():
                d[var] = pd.Series(arr["values"])
    except KeyError:
        pass

    return d