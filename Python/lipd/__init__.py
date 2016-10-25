import copy

from .pkg_resources.lipds.LiPD_Library import *
from .pkg_resources.timeseries.Convert import *
from .pkg_resources.timeseries.TimeSeries_Library import *
from .pkg_resources.doi.doi_main import doi
from .pkg_resources.excel.excel_main import excel_main
from .pkg_resources.noaa.noaa_main import noaa
from .pkg_resources.helpers.alternates import COMPARISONS
from .pkg_resources.helpers.ts import translate_expression, get_matches
from .pkg_resources.helpers.dataframes import *
from .pkg_resources.helpers.directory import get_src_or_dst
from .pkg_resources.helpers.loggers import create_logger
from .pkg_resources.helpers.misc import pickle_data, unpickle_data, split_path_and_file, prompt_protocol
from .pkg_resources.helpers.ensembles import create_ensemble, insert_ensemble

# LOAD


def run():
    """
    Initialize and start objects
    :return:
    """
    # GLOBALS
    global lipd_lib, ts_lib, convert
    lipd_lib = LiPD_Library()
    ts_lib = TimeSeries_Library()
    convert = Convert()
    return


def setDir():
    """
    Set the current working directory by providing a directory path.
    (ex. /Path/to/files)
    :param str path: Directory path
    """
    global path, single_file, logger_start
    path, single_file = get_src_or_dst("load")
    lipd_lib.set_dir(path)
    logger_start = create_logger("start")
    logger_start.info("Working Directory: {}".format(path))
    # print("Working Directory: {}".format(path))
    return path


def loadLipd():
    """
    Load a single LiPD file into the workspace. File must be located in the current working directory.
    (ex. loadLiPD NAm-ak000.lpd)
    :param str filename: LiPD filename
    """
    global single_file
    lipd_lib.load_lipd(single_file)
    print("Process Complete")
    return


def loadLipds():
    """
    Load all LiPD files in the current working directory into the workspace.
    """
    global single_file
    lipd_lib.load_lipds(single_file)
    print("Process Complete")
    return


def loadPickleObj():
    pass


def loadPickle():
    """
    Load a pickle file into the workspace
    :return dict: Data loaded from pickle file
    """
    # Ask where the file is
    _path = browse_dialog_file()

    # Split the filename and the path into two
    _path, _filename = split_path_and_file(_path)

    # Unpickle the data
    d = unpickle_data(_path, _filename)

    # changed dir in unpickle_data, so move back to root
    os.chdir(path)

    # If this unpickled data reads in as an object, then refresh the global lipd_lib
    if type(d) not in (dict, str, int, float):
        global lipd_lib
        lipd_lib = d
    elif type(d) is dict:
        return d
    else:
        print("Error: unpickled data was not a valid data type")
    return


def excel():
    """
    User facing call to the excel function
    :return:
    """
    global single_file
    excel_main(single_file)
    return

# PUT


def addEnsemble(filename, ensemble):
    """
    Create ensemble entry and then add it to the specified LiPD dataset
    :param str filename: LiPD dataset name to add ensemble to
    :param list ensemble: Nested numpy array of ensemble column data.
    :return none:
    """
    # Get the master lipd library
    lib = lipd_lib.get_master()
    # Check that the given filename exists in the library
    if filename in lib:
        meta = lib[filename].get_metadata()
        # Create an ensemble dictionary entry
        ens = create_ensemble(ensemble)
        # If everything above worked, then there should be formatted ensemble data now.
        if ens:
            # Insert the formatted ensemble data into the master lipd library
            meta = insert_ensemble(meta, ens)
            # Set meta into lipd object
            lib[filename].set_metadata(meta)
            # Set the new master data back into the lipd library
            lipd_lib.set_master(lib)
    else:
        print("Error: '{}' file not found in workspace. Please use showLipds() to see available files ".format(filename))

    print("Process Complete")
    return


# DATA FRAMES


def ensToDf(ensemble):
    """
    Create an ensemble data frame from some given nested numpy arrays
    :param list ensemble: Ensemble data
    :return obj: DataFrame
    """
    df = create_dataframe(ensemble)
    return df


def lipdToDf(filename):
    """
    Get LiPD data frames from LiPD object
    :param str filename:
    :return dict: Pandas data frame objects
    """
    try:
        dfs = lipd_lib.get_dfs(filename)
    except KeyError:
        print("Error: Unable to find LiPD file")
        logger_start.warn("lipd_to_df: KeyError: missing lipds {}".format(filename))
        dfs = None
    print("Process Complete")
    return dfs


def tsToDf(ts, filename):
    """
    Create Pandas DataFrame from TimeSeries object.
    Use: Must first extractTimeSeries to get a time series. Then pick one item from time series and pass it through
    :param dict ts: TimeSeries
    :param str filename:
    :return dict: Pandas data frames
    """
    dfs = {}
    try:
        dfs = ts_to_df(ts[filename])
    except KeyError as e:
        print("Error: LiPD file not found")
        logger_start.warn("ts_to_df: KeyError: LiPD file not found: {}".format(filename, e))
    print("Process Complete")
    return dfs


def filterDfs(expr):
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
        logger_dataframes.info("filter_dfs: Unable to filter data frames for expr: {}".format(expr))
        print("Unable to filter data frames")
        print("Process Complete")


# ANALYSIS - TIME SERIES


def extractTs():
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


def collapseTs():
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
        filtered_ts = _createTs(names, ts)
    print("Process Complete")
    return names, filtered_ts


def _createTs(names, ts):
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


# SHOW


def showLipds():
    """
    Prints the names of all LiPD files in the LiPD_Library
    :return None:
    """
    lipd_lib.show_lipds()
    print("Process Complete")
    return


def showMetadata(filename):
    """
    Display the contents of the specified LiPD file. (Must be previously loaded into the workspace)
    (ex. displayLiPD NAm-ak000.lpd)
    :param str filename: LiPD filename
    """
    lipd_lib.show_metadata(filename)
    print("Process Complete")
    return


def showCsv(filename):
    """
    Show CSV data for one LiPD
    :param str filename:
    :return None:
    """
    lipd_lib.show_csv(filename)
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
            for k, v in dict_in["paleoData"].items():
                print(k)
        except KeyError:
            pass
        except AttributeError:
            pass
    if "chronData" in dict_in:
        try:
            for k, v in dict_in["chronData"].items():
                print(k)
        except KeyError:
            pass
        except AttributeError:
            pass
    print("Process Complete")
    return


# GET


def getMetadata(filename):
    """
    Get metadata from LiPD file
    :param str filename: LiPD filename
    :return dict d: Metadata dictionary
    """
    d = {}
    try:
        d = lipd_lib.get_metadata(filename)
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
        d = lipd_lib.get_csv(filename)
    except KeyError:
        print("Error: Unable to find record")
        logger_start.warn("Unable to find record {}".format(filename))
    print("Process Complete")
    return d


# SAVE


def savePickle():
    """
    Compile a single dictionary of all LiPD data, then Pickle it for later.
    * maintain compatibility for python v2.7-3+
    :return none:
    """

    # Ask user if they want to pickle the lipds library object, or create a stripped-down lipds library dictionary
    ans = prompt_protocol()

    # set the target data based on user answer
    if ans == "o":
        # hold the dir_root value.
        tmp = lipd_lib.get_dir()
        # wipe out the dir_root so it doesn't get passed to the next user
        lipd_lib.set_dir("")
        # set as the lipd_lib object
        d = copy.deepcopy(lipd_lib)
        # reinstate the dir_root now that the object is copied.
        lipd_lib.set_dir(tmp)
    else:
        # create a dictionary from lipd_lib
        d = lipd_lib.lib_to_dict()

    # prompt for where to save the file
    _path = get_src_or_dst("save")

    # send the data to be pickled
    pickle_data(_path, d, ans)

    # changed dir in pickle_data, so move back to root
    os.chdir(path)
    return


def saveLipd(filename):
    """
    Saves changes made to the target LiPD file.
    (ex. saveLiPD NAm-ak000.lpd)
    :param str filename: LiPD filename
    """
    lipd_lib.save_lipd(filename)
    print("Process Complete")
    return


def saveLipds():
    """
    Save changes made to all LiPD files in the workspace.
    """
    lipd_lib.save_lipds()
    print("Process Complete")
    return


def removeLipd(filename):
    """
    Remove LiPD object from library
    :return None:
    """
    lipd_lib.remove_lipd(filename)
    print("Process Complete")
    return


def removeLipds():
    """
    Remove all LiPD objects from library.
    :return None:
    """
    lipd_lib.remove_lipds()
    print("Process Complete")
    return


def quit():
    """
    Quit and exit the program. (Does not save changes)
    """
    # self.llib.close()
    print("Quitting...")
    return True


# GLOBALS - run these on initialization
run()
setDir()