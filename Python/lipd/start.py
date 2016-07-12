from .pkg_resources.lipd.LiPD_Library import *
from .pkg_resources.timeseries.Convert import *
from .pkg_resources.timeseries.TimeSeries_Library import *
from .pkg_resources.doi.doi_main import doi
from .pkg_resources.excel.excel_main import excel
from .pkg_resources.noaa.noaa_main import noaa
from .pkg_resources.helpers.alternates import COMPARISONS
from .pkg_resources.helpers.ts import translate_expression, get_matches
from .pkg_resources.helpers.PDSlib import *
from .pkg_resources.helpers.directory import set_source
from .pkg_resources.helpers.loggers import create_logger


def setDir():
    """
    Set the current working directory by providing a directory path.
    (ex. /Path/to/files)
    :param str path: Directory path
    """
    path = set_source()
    lipd_lib.setDir(path)
    logger = create_logger("start")
    logger.info("Set path: {}".format(path))
    return path, logger


def loadLipd(filename):
    """
    Load a single LiPD file into the workspace. File must be located in the current working directory.
    (ex. loadLiPD NAm-ak000.lpd)
    :param str filename: LiPD filename
    """
    lipd_lib.loadLipd(filename)
    print("Process Complete")
    return


def loadLipds():
    """
    Load all LiPD files in the current working directory into the workspace.
    """
    lipd_lib.loadLipds()
    print("Process Complete")
    return


# ANALYSIS - LIPD


def filter_dfs(expr):
    """
    Get data frames based on some criteria. i.e. all measurement tables or all ensembles.
    :param str expr: Search expression. (i.e. "paleo measurement tables")
    :return dict: Data frames indexed by filename
    """
    try:
        dfs = get_filtered_dfs(lipd_lib.get_master(), expr)
        print("Process Complete")
        return dfs

    except Exception:
        logger_pdslib.info("filter_dfs: Unable to filter data frames for expr: {}".format(expr))
        print("Unable to filter data frames")
        print("Process Complete")


def lipd_to_df(filename):
    """
    Get lipd data frames from lipd object
    :param str filename:
    :return dict: Pandas data frame objects
    """
    try:
        dfs = lipd_lib.getDfs(filename)
    except KeyError:
        print("Error: Unable to find LiPD file")
        logger_start.warn("lipd_to_df: KeyError: missing lipd {}".format(filename))
        dfs = None
    print("Process Complete")
    return dfs


def ts_to_df(ts, filename):
    """
    Create Pandas DataFrame from TimeSeries object.
    Use: Must first extractTimeSeries to get a time series. Then pick one item from time series and pass it through
    :param dict ts: TimeSeries
    :param str filename:
    :return dict: Pandas data frames
    """
    dfs = {}
    try:
        dfs = ts_to_dfs(ts[filename])
    except KeyError as e:
        print("Error: LiPD file not found")
        logger_start.warn("ts_to_df: KeyError: LiPD file not found: {}".format(filename, e))
    print("Process Complete")
    return dfs


def showCsv(filename):
    """
    Show CSV data for one LiPD
    :param str filename:
    :return None:
    """
    lipd_lib.showCsv(filename)
    print("Process Complete")
    return


def showMetadata(filename):
    """
    Display the contents of the specified LiPD file. (Must be previously loaded into the workspace)
    (ex. displayLiPD NAm-ak000.lpd)
    :param str filename: LiPD filename
    """
    lipd_lib.showMetadata(filename)
    print("Process Complete")
    return


def showLipds():
    """
    Prints the names of all LiPD files in the LiPD_Library
    :return None:
    """
    lipd_lib.showLipds()
    print("Process Complete")
    return


def getMetadata(filename):
    """
    Get metadata from LiPD file
    :param str filename: LiPD filename
    :return dict d: Metadata dictionary
    """
    d = {}
    try:
        d = lipd_lib.getMetadata(filename)
    except KeyError:
        print("Error: Unable to find LiPD file")
        logger_start.warn("KeyError: Unable to find record {}".format(filename))
    print("Process Complete")
    return d


def getCsv(filename):
    """
    Get CSV from LiPD file
    :param str filename: LiPD filename
    :return dict d: CSV dictionary
    """
    d = {}
    try:
        d = lipd_lib.getCsv(filename)
    except KeyError:
        print("Error: Unable to find record")
        logger_start.warn("Unable to find record {}".format(filename))
    print("Process Complete")
    return d


# ANALYSIS - TIME SERIES


def extractTimeSeries():
    """
    Create a TimeSeries using the current files in LiPD_Library.
    :return obj: TimeSeries_Library
    """
    d = {}
    try:
        # Loop over the LiPD files in the LiPD_Library
        for k, v in lipd_lib.get_master().items():
            # Get metadata from this LiPD object. Convert. Pass TSO metadata to time series dictionary output.
            d.update(convert.ts_extract_main(v.get_master(), v.get_dfs_chron()))
    except KeyError as e:
        print("Error: Unable to extractTimeSeries")
        logger_start.debug("extractTimeSeries() failed at {}".format(e))

    print("Process Complete")
    return d


def collapseTimeSeries():
    """
    Export TimeSeries back to LiPD Library. Updates information in LiPD objects.
    """
    l = []
    # Get all TSOs from TS_Library, and add them to a list
    for k, v in ts_lib.get_master().items():
        l.append({'name': v.get_lpd_name(), 'data': v.get_master()})
    # Send the TSOs list through to be converted. Then let the LiPD_Library load the metadata into itself.
    try:
        lipd_lib.load_tsos(convert.lipd_extract_main(l))
    except Exception:
        print("ERROR: Converting TSOs to LiPD")
        logger_start.debug("exportTimeSeries() failed")
    print("Process Complete")
    return


def showTso(name):
    """
    Show contents of one TimeSeries object.
    :param str name: TimeSeries Object name
    :return None:
    """
    ts_lib.showTso(name)
    print("Process Complete")
    return


def showTsos(dict_in):
    """
    Prints the names of all TimeSeries objects in the TimeSeries_Library
    :return None:
    """
    try:
        s = collections.OrderedDict(sorted(dict_in.items()))
        for k, v in s.items():
            print(k)
    except AttributeError:
        print("ERROR: Invalid TimeSeries")
    return


def showDfs(dict_in):
    """
    Print the available data frame names in a given data frame collection
    :param dict dict_in: Data frame collection
    :return none:
    """
    if "metadata" in dict_in:
        print("metadata")
    if "paleoData" in dict_in:
        try:
            for k,v in dict_in["paleoData"].items():
                print(k)
        except KeyError:
            pass
        except AttributeError:
            pass
    if "chronData" in dict_in:
        try:
            for k,v in dict_in["chronData"].items():
                print(k)
        except KeyError:
            pass
        except AttributeError:
            pass
    print("Process Complete")
    return


def find(expression, ts):
    """
    Find the names of the TimeSeries that match some criteria (expression)
    :return:
    """
    names = []
    filtered_ts = {}
    expr_lst = translate_expression(expression)
    if expr_lst:
        names = get_matches(expr_lst, ts)
        filtered_ts = TS(names, ts)
    print("Process Complete")
    return names, filtered_ts


def check_ts(parameter, names, ts):
    for i in names:
        try:
            print(ts[i][parameter])
        except KeyError:
            print("Error: TimeSeries object not found")
    return


def TS(names, ts):
    """
    Create a new TS dictionary using
    index = find(logical expression)
    newTS = TS(index)
    :param str expression:
    :return dict:
    """
    d = {}
    for name in names:
        try:
            d[name] = ts[name]
        except KeyError as e:
            logger_start.warn("TS: KeyError: {} not in timeseries, {}".format(name, e))
    return d


def get_numpy(ts):
    """
    Get all values from a TimeSeries
    :param dict ts: Time Series
    :return list of lists:
    """
    tmp = []
    try:
        for k,v in ts.items():
            try:
                tmp.append(v['paleoData_values'])
            except KeyError:
                pass
    except AttributeError as e:
        print("Error: Invalid TimeSeries")
    print("Process Complete")
    return tmp

# CLOSING


def saveLipd(filename):
    """
    Saves changes made to the target LiPD file.
    (ex. saveLiPD NAm-ak000.lpd)
    :param str filename: LiPD filename
    """
    lipd_lib.saveLipd(filename)
    print("Process Complete")
    return


def saveLipds():
    """
    Save changes made to all LiPD files in the workspace.
    """
    lipd_lib.saveLipds()
    print("Process Complete")
    return


def removeLipd(filename):
    """
    Remove LiPD object from library
    :return None:
    """
    lipd_lib.removeLipd(filename)
    print("Process Complete")
    return


def removeLipds():
    """
    Remove all LiPD objects from library.
    :return None:
    """
    lipd_lib.removeLipds()
    print("Process Complete")
    return


def quit():
    """
    Quit and exit the program. (Does not save changes)
    """
    # self.llib.close()
    print("Quitting...")
    return True


# GLOBALS
lipd_lib = LiPD_Library()
ts_lib = TimeSeries_Library()
convert = Convert()
path, logger_start = setDir()
