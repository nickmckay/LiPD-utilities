import operator

from .regexes import re_filter_expr
from .alternates import comparisons
from .loggers import create_logger

logger_ts = create_logger("ts")


def get_truth(inp, relate, cut):
    """
    Compare two items. Match a string operator to an operator function
    :param str inp: Comparison item
    :param str relate: Comparison operator
    :param any cut: Comparison item
    :return bool: Comparison truth
    """
    logger_ts.info("enter get_truth")
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
        logger_ts.warn("get_truth: KeyError: Invalid operator input: {}, {}".format(relate, e))
    logger_ts.info("exit get_truth")
    return truth


def parse_str(string):
    """
    Attempt to cleanup string or convert to number value.
    :param str string:
    :return float or str:
    """
    try:
        string = float(string)
    except ValueError:
        try:
            string = string.rstrip()
        except AttributeError as e:
            logger_ts.warn("parse_str: AttributeError: String not number or word, {}, {}".format(string, e))
    return string


def translate_expression(expression):
    """
    Check if the expression is valid, then check turn it into an expression that can be used for filtering.
    :return list of lists: One or more matches. Each list has 3 strings.
    """
    logger_ts.info("enter translate_expression")
    m = re_filter_expr.findall(expression)
    matches = []
    if m:
        for i in m:
            logger_ts.info("parse match: {}".format(i))
            tmp = list(i[1:])
            if tmp[1] in comparisons:
                tmp[1] = comparisons[tmp[1]]
            tmp[0] = parse_str(tmp[0])
            tmp[2] = parse_str(tmp[2])
            matches.append(tmp)
    else:
        logger_ts.warn("translate_expression: invalid expression: {}".format(expression))
        print("Invalid input expression")
    logger_ts.info("exit translate_expression")
    return matches


def get_matches(expr_lst, ts):
    """
    Get a list of TimeSeries objects that match the given expression.
    :param list expr_lst: Expression
    :param dict ts: TimeSeries
    :return list names: Matched TimeSeries objects
    """
    logger_ts.info("enter get_matches")
    names = []
    match = False
    try:
        for ts_name, ts_data in ts.items():
            for expr in expr_lst:
                try:
                    val = ts_data[expr[0]]
                    # Check what comparison operator is being used
                    if expr[1] == 'in':
                        # "IN" operator can't be used in get_truth. Handle first.
                        if expr[2] in val:
                            match = True
                    elif get_truth(val, expr[1], expr[2]):
                        # If it's a typical operator, check with the truth test.
                        match = True
                    else:
                        # If one comparison is false, then it can't possibly be a match
                        match = False
                        break
                except KeyError as e:
                    logger_ts.warn("get_matches: KeyError: getting value from TimeSeries object, {}, {}".format(expr, e))
                    match = False
                except IndexError as e:
                    logger_ts.warn("get_matches: IndexError: getting value from TimeSeries object, {}, {}".format(expr, e))
                    match = False
            if match:
                names.append(ts_name)
    except AttributeError as e:
        logger_ts.debug("get_matches: AttributeError: invalid timeseries, {},  {}".format(type(ts), e))
        print("Error: Invalid TimeSeries")
    logger_ts.info("exit get_matches")
    return names


def extractTimeSeries(lipd_library, timeseries_library, convert):
    """
    Create a TimeSeries using the current files in LiPD_Library.
    :return obj: TimeSeries_Library
    """
    # Loop over the LiPD objects in the LiPD_Library
    for k, v in lipd_library.get_master().items():
        # Get metadata from this LiPD object. Convert it. Pass TSO metadata to the TS_Library.
        timeseries_library.loadTsos(v.get_name_ext(), convert.ts_extract_main(v.get_master()))


def exportTimeSeries(lipd_library, timeseries_library, convert):
    """
    Export TimeSeries back to LiPD Library. Updates information in LiPD objects.
    """
    l = []
    # Get all TSOs from TS_Library, and add them to a list
    for k, v in timeseries_library.get_master().items():
        l.append({'name': v.get_lpd_name(), 'data': v.get_master()})
    # Send the TSOs list through to be converted. Then let the LiPD_Library load the metadata into itself.
    lipd_library.load_tsos(convert.lipd_extract_main(l))

