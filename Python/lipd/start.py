from .pkg_resources.lipd.LiPD_Library import *
from .pkg_resources.timeseries.Convert import *
from .pkg_resources.timeseries.TimeSeries_Library import *
from .pkg_resources.doi.doi_main import doi
from .pkg_resources.excel.excel_main import excel
from .pkg_resources.noaa.noaa_main import noaa
from .pkg_resources.helpers.alternates import comparisons
from .pkg_resources.helpers.ts import translate_expression, get_matches

def setDir():
    """
    Set the current working directory by providing a directory path.
    (ex. /Path/to/files)
    :param path: (str) Directory path
    """
    global path
    path = set_source()
    lipd_lib.setDir(path)
    return path


def loadLipd(filename):
    """
    Load a single LiPD file into the workspace. File must be located in the current working directory.
    (ex. loadLiPD NAm-ak000.lpd)
    :param filename: (str) LiPD filename
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


def showCsv(filename):
    """
    Show CSV data for one LiPD
    :param filename:
    :return:
    """
    lipd_lib.showCsv(filename)
    print("Process Complete")
    return


def showMetadata(filename):
    """
    Display the contents of the specified LiPD file. (Must be previously loaded into the workspace)
    (ex. displayLiPD NAm-ak000.lpd)
    :param filename: (str) LiPD filename
    """
    lipd_lib.showMetadata(filename)
    print("Process Complete")
    return


def showLipds():
    """
    Prints the names of all LiPD files in the LiPD_Library
    """
    lipd_lib.showLipds()
    print("Process Complete")
    return


def showMap(filename):
    """

    :param filename:
    :return:
    """
    lipd_lib.showMap(filename)
    print("Process Complete")
    return


def getMetadata(filename):
    """

    :param filename:
    :param parameter:
    :return:
    """
    d = {}
    try:
        d = lipd_lib.getMetadata(filename)
    except KeyError:
        print("ERROR: Unable to find record")

    return d


def getCsv(filename):
    d = {}
    try:
        d = lipd_lib.getCsv(filename)
    except KeyError:
        print("ERROR: Unable to find record")

    return d


# ANALYSIS - TIME SERIES


def extractTimeSeries():
    """
    Create a TimeSeries using the current files in LiPD_Library.
    :return: (obj) TimeSeries_Library
    """
    d = {}
    try:
        # Loop over the LiPD objects in the LiPD_Library
        for k, v in lipd_lib.get_master().items():
            # Get metadata from this LiPD object. Convert it. Pass TSO metadata to the TS_Library.
            # ts_lib.loadTsos(v.get_name_ext(), convert.ts_extract_main(v.get_master()))
            d.update(convert.ts_extract_main(v.get_master()))
    except KeyError:
        print("ERROR: Unable to extractTimeSeries")
    print("Process Complete")
    return d


def exportTimeSeries():
    """
    Export TimeSeries back to LiPD Library. Updates information in LiPD objects.
    """
    l = []
    # Get all TSOs from TS_Library, and add them to a list
    for k, v in ts_lib.get_master().items():
        l.append({'name': v.get_lpd_name(), 'data': v.get_master()})
    # Send the TSOs list through to be converted. Then let the LiPD_Library load the metadata into itself.
    lipd_lib.load_tsos(convert.lipd_extract_main(l))
    print("Process Complete")
    return


def showTso(name):
    """
    Show contents of one TimeSeries object.
    :param name:
    :return:
    """
    ts_lib.showTso(name)
    print("Process Complete")
    return


def showTsos():
    """
    Prints the names of all TimeSeries objects in the TimeSeries_Library
    :return:
    """
    ts_lib.showTsos()
    print("Process Complete")
    return


def find(expression, ts):
    """
    Find the names of the TimeSeries that match some criteria (expression)
    :return:
    """
    names = []
    expr_lst = translate_expression(expression)
    if expr_lst:
        names = get_matches(expr_lst, ts)
    print("Process Complete")
    return names


def check_ts(parameter, names, ts):
    for i in names:
        try:
            print(ts[i][parameter])
        except KeyError:
            print("ERROR: Key doesn't exist")
    return


def TS(names, ts):
    """
    Create a new TS dictionary using
    index = find(logical expression)
    newTS = TS(index)

    :param expression:
    :return:
    """
    d = {}
    for name in names:
        try:
            d[name] = ts[name]
        except KeyError:
            print("ERROR: Record not in TimeSeries")
    print("Process Complete")
    return d


def get_numpy(ts):
    """
    Get all values from a TimeSeries
    :param ts: (dict) Time Series
    :return: (list of lists)
    """
    tmp = []
    try:
        for k,v in ts.items():
            try:
                tmp.append(v['paleoData_values'])
            except KeyError:
                pass
    except AttributeError:
        print("ERROR: Invalid TimeSeries")

    print("Process Complete")
    return tmp

# CLOSING


def saveLipd(filename):
    """
    Saves changes made to the target LiPD file.
    (ex. saveLiPD NAm-ak000.lpd)
    :param filename: (str) LiPD filename
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
    :return: None
    """
    lipd_lib.removeLipd(filename)
    print("Process Complete")
    return


def removeLipds():
    """
    Remove all LiPD objects from library.
    :return: None
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


def set_source():
    """
    User sets the path to LiPD source. Local or online.
    :return: (str) Path
    """
    _path = ''
    invalid = True
    count = 0
    while invalid:
        print("Where are your files stored?\n1. Online URL\n2. Browse Computer\n3. "
              "Downloads folder\n4. Notebooks folder\n")
        option = input("Option: ")
        if option == '1':
            # Retrieve data from the online URL
            _path = input("Enter the URL: ")
        elif option == '2':
            # Open up the GUI browse dialog
            _path = browse_dialog()
            # Set the path to the local files in CLI and lipd_lib
        elif option == '3':
            # Set the path to the system downloads folder.
            _path = os.path.expanduser('~/Downloads')
        elif option == '4':
            # Set path to the Notebook folder
            _path = os.path.expanduser('~/LiPD_Notebooks')
        else:
            # Something went wrong. Prompt again. Give a couple tries before defaulting to downloads folder
            if count == 2:
                print("Defaulting to Downloads Folder.")
                _path = os.path.expanduser('~/Downloads')
            else:
                count += 1
                print("Invalid option. Try again.")
        if _path:
            invalid = False
    lipd_lib.setDir(_path)

    return _path


# GLOBALS
lipd_lib = LiPD_Library()
ts_lib = TimeSeries_Library()
convert = Convert()
path = ''
set_source()

