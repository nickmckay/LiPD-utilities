import copy

from .pkg_resources.lipds.LiPD_Library import *
from .pkg_resources.timeseries.Convert import *
from .pkg_resources.timeseries.TimeSeries_Library import *
from .pkg_resources.doi.doi_main import doi_main
from .pkg_resources.excel.excel_main import excel_main
from .pkg_resources.noaa.noaa_main import noaa_prompt, noaa_to_lpd, lpd_to_noaa
from .pkg_resources.helpers.ts import translate_expression, get_matches
from .pkg_resources.helpers.dataframes import *
from .pkg_resources.helpers.directory import get_src_or_dst, collect_metadata_files, list_files
from .pkg_resources.helpers.loggers import create_logger
from .pkg_resources.helpers.misc import path_type, load_fn_matches_ext
from .pkg_resources.helpers.ensembles import create_ensemble, insert_ensemble
from .pkg_resources.helpers.validator_api import get_validator_results, display_results

# READ


def run():
    """
    Initialize and start objects
    :return:
    """
    # GLOBALS
    global cwd, lipd_lib, ts_lib, convert, files, logger_start, verbose
    verbose = True
    cwd = os.getcwd()
    # creating the LiPD Library also creates the Tmp sys folder where the files will be stored later.
    lipd_lib = LiPD_Library()
    ts_lib = TimeSeries_Library()
    convert = Convert()
    # print(cwd)
    # logger created in whatever directory lipd is called from
    logger_start = create_logger("start")
    files = {".txt": [], ".lpd": [], ".xls": []}
    return


def readLipd(usr_path=""):
    """
    Wrapper function for LiPD file read.
    :param str usr_path: Path to file
    :return none:
    """
    global cwd
    __read_file(usr_path, ".lpd")
    return cwd


def readLipds(usr_path=""):
    """
    Wrapper function for LiPD directory read.
    :param str usr_path: Path to directory
    :return none:
    """
    global cwd
    __read_directory(usr_path, ".lpd", "LiPD")
    # Turned off until LiPD.net is updated to accept Validator API requests
    # validator()
    return cwd


def readExcel(usr_path=""):
    """
    Wrapper function for Excel file read.
    :param str usr_path: Path to file
    :return none:
    """
    global cwd
    __read_file(usr_path, ".xls")
    return cwd


def readExcels(usr_path=""):
    """
    Wrapper function for Excel directory read.
    :param str usr_path: Path to directory
    :return none:
    """
    global cwd
    if not usr_path:
        usr_path, src_files = get_src_or_dst("read", "directory")
    __read_directory(usr_path, ".xls", "Excel (.xls)")
    __read_directory(usr_path, ".xlsx", "Excel (.xlsx)")
    return cwd


def readNoaa(usr_path=""):
    """
    Wrapper function for NOAA file read.
    :param str usr_path: Path to file
    :return none:
    """
    global cwd
    __read_file(usr_path, ".txt")
    return cwd


def readNoaas(usr_path=""):
    """
    Wrapper function for NOAA directory read.
    :param str usr_path: Path to directory
    :return none:
    """
    global cwd
    __read_directory(usr_path, ".txt", "NOAA")
    return cwd


def readAll(usr_path=""):
    """
    Wrapper function for reading ALL file types in a given directory.
    :param str usr_path: Path to directory
    :return none:
    """
    global cwd
    if not usr_path:
        usr_path, src_files = get_src_or_dst("read", "directory")
    __read_directory(usr_path, ".lpd", "LiPD")
    __read_directory(usr_path, ".xls", "Excel (xls)")
    __read_directory(usr_path, ".xlsx", "Excel (xlsx)")
    __read_directory(usr_path, ".txt", "NOAA")
    return cwd


def excel():
    """
    User facing call to the excel function
    :return none:
    """
    global files, cwd, verbose
    excel_main(files)
    # Turn off verbose. We don't want to clutter the console with extra reading/writing output statements
    verbose = False
    for file in files[".xls"]:
        try:
            readLipd(os.path.join(file["dir"], file["filename_no_ext"] + ".lpd"))
        except Exception as e:
            logger_start.debug("excel: Converted excel to lipd file, but unable readLipd(): {}, {}".format(file["filename_ext"], e))
    try:
        writeLipds(cwd)
    except Exception as e:
        logger_start.debug("excel: Unable to writeLipds with new lipd files, {}".format(e))
    # Turn on verbose. Back to normal mode when this function is finished.
    verbose = True
    return


def noaa():
    """
    User facing call to noaa function
    :return none:
    """
    global files, lipd_lib, cwd
    # When going from NOAA to LPD, use the global "files" variable.
    # When going from LPD to NOAA, use the data from the LiPD Library.

    # Choose the mode
    _mode = noaa_prompt()

    # LiPD mode: Convert LiPD files to NOAA files
    if _mode == "1":

        _lib = lipd_lib.get_master()

        # For each LiPD file in the LiPD Library
        for filename, obj in _lib.items():
            # Get the LiPD object data
            # _obj = dict(obj)
            # Process this data through the converter
            _obj_modified = lpd_to_noaa(obj)
            # Overwrite the data in the LiPD object with our new data.
            _lib[filename] = _obj_modified
        # Replace the data in the LiPD Library master
        lipd_lib.put_master(_lib)
        # Write out the new LiPD files, since they now contain the NOAA URL data
        writeLipds(cwd)

    # NOAA mode: Convert NOAA files to LiPD files
    elif _mode == "2":
        # For each NOAA txt file in the global "files" list, Run the converter
        #todo This is just a concept of how it should work. Not currently working.
        for file in files[".txt"]:
            _data = noaa_to_lpd(files)
            #todo Use the parsed NOAA data to create a LiPD object in the library
            #todo Use writeLipd to create a LiPD file using the object.
            pass

    else:
        print("Invalid input. Try again.")

    # LIPD TO NOAA IS THE ONLY CONVERSION CURRENTLY WORKING.
    # MAKE IT THE ONLY OPTION FOR NOW.
    # For each LiPD file in the LiPD Library
        # Get the LiPD object data
        # Process this data through the converter
        # Overwrite the data in the LiPD object with our new data.
        # Write the new LiPD file back out to disk.
    return


def doi():
    """
    User facing call to doi function
    :return:
    """
    global files
    doi_main(files)
    return


def validator(detailed=False):
    """
    Use the Validator API for lipd.net to validate all LiPD files in the LiPD Library.
    Display the PASS/FAIL results. Display detailed results if the option is chosen.
    :param bool detailed: Show or hide the detailed results of each LiPD file. Shows warnings and errors.
    :return none:
    """
    # Get the validator-formatted data for each LiPD file in the LiPD Library. A list of lists of LiPD-content metadata
    d = lipd_lib.get_data_for_validator()
    results = get_validator_results(d)
    display_results(results, detailed)
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
            lib[filename].put_metadata(meta)
            # Set the new master data back into the lipd library
            lipd_lib.put_master(lib)
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


# todo this function no longer works. time series objects are not referenced by name. TS is a list of TSOs
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
    :return list: TimeSeries_Library
    """
    l = []
    try:
        # Loop over the LiPD files in the LiPD_Library
        for k, v in lipd_lib.get_master().items():
            # Get metadata from this LiPD object. Convert.
            # Receive a time series (list of time series objects) and add it to what we currently have.
            # Continue building time series until all datasets are processed.
            print("extracting: {}".format(k))
            l += (convert.ts_extract_main(v.get_master(), v.get_dfs_chron()))
        print("Finished time series: {} objects".format(len(l)))
    except KeyError as e:
        print("Error: Unable to extractTimeSeries")
        logger_start.debug("extractTimeSeries() failed at {}".format(e))

    print("Process Complete")
    return l


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
    new_ts = []
    # filtered_ts = {}
    expr_lst = translate_expression(expression)
    if expr_lst:
        new_ts = get_matches(expr_lst, ts)
        # filtered_ts = _createTs(names, ts)
    print("Process Complete")
    return new_ts


# DEPRECATED - TS no longer uses dictionaries or names.
# def _createTs(names, ts):
#     """
#     Create a new TS dictionary using
#     index = find(logical expression)
#     newTS = TS(index)
#     :param str expression:
#     :return dict:
#     """
#     d = {}
#     for name in names:
#         try:
#             d[name] = ts[name]
#         except KeyError as e:
#             logger_start.warn("TS: KeyError: {} not in timeseries, {}".format(name, e))
#     return d


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


def showTso(tso):
    """
    Show contents of one TimeSeries object.
    :param str name: TimeSeries Object name
    :return None:
    """
    try:
        for key, value in sorted(tso.items()):
            print("{0:20}: {1}".format(key, value))
    except Exception as e:
        print("Unable to list contents: {}".format(e))
    print("Process Complete")
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

def getLipdNames():
    """
    Get a list of all lipd dataset names in the library
    :return list:
    """
    f_list = []
    f_list = lipd_lib.get_lipd_names()
    return f_list


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


# WRITE


def writeLipd(filename, usr_path=""):
    """
    Write out one specific LiPD file
    :param str filename: LiPD filename ("somefile.lpd")
    :param str usr_path: Target directory destination (optional)
    :return none:
    """
    global verbose
    # no path provided. start gui browse
    if not usr_path:
        # got dir path
        usr_path, _ignore = get_src_or_dst("write", "directory")
    __write_lipd(usr_path, filename)
    return


def writeLipds(usr_path=""):
    """
    Save changes made to all LiPD files in the workspace.
    Files are created in current working directory if path is not provided.
    :param str usr_path: Target directory destination (optional)
    """
    global verbose
    # no path provided. start gui browse
    if not usr_path:
        # got dir path
        usr_path, _ignore = get_src_or_dst("write", "directory")
    _lib = list(lipd_lib.get_master().keys())
    if _lib:
        for filename in _lib:
            __write_lipd(usr_path, filename)
    if verbose:
        print("Process Complete")
    return


def removeLipd(filename):
    """
    Remove LiPD object from library
    :return None:
    """
    lipd_lib.remove_lipd(filename)
    return


def removeLipds():
    """
    Remove all LiPD objects from library.
    :return None:
    """
    lipd_lib.remove_lipds()
    return


def quit():
    """
    Quit and exit the program. (Does not save changes)
    """
    lipd_lib.cleanup()
    print("Quitting LiPD Utilities...")
    exit(0)


# HELPERS


def __universal_load(file_path, file_type):
    """
    Use a file path to create file metadata and load a file in the appropriate way, according to the provided file type.
    :param str file_path: Path to file
    :param str file_type: One of approved file types: xls, xlsx, txt, lpd
    :return none:
    """
    global files, lipd_lib, cwd, verbose

    # check that we are using the correct function to load this file type. (i.e. readNoaa for a .txt file)
    correct_ext = load_fn_matches_ext(file_path, file_type)

    # Check that this path references a file
    valid_path = path_type(file_path, "file")

    # is the path a file?
    if valid_path and correct_ext:

        # get file metadata for one file
        file_meta = collect_metadata_file(file_path)
        if verbose:
            print("reading: {}".format(file_meta["filename_ext"]))

        # append to global files, then load in lipd_lib
        if file_type == ".lpd":
            # add meta to global file meta
            files[".lpd"].append(file_meta)
            # yes, go ahead and load in the file
            lipd_lib.read_lipd(file_meta)
        # append to global files
        elif file_type in (".xls", ".xlsx"):
            files[".xls"].append(file_meta)
        # append to global files
        elif file_type == ".txt":
            files[".txt"].append(file_meta)

        # we want to move around with the files we load
        # change dir into the dir of the target file
        cwd = file_meta["dir"]
        os.chdir(cwd)

    return


def __read_file(usr_path, file_type):
    """
    Universal read file. Given a path and a type, it will do the appropriate read actions
    :param str usr_path: Path to file
    :param str file_type: One of approved file types: xls, xlsx, txt, lpd
    :return none:
    """
    global files

    # no path provided. start gui browse
    if not usr_path:
        # src files could be a list of one, or a list of many. depending how many files the user selects
        src_dir, src_files = get_src_or_dst("read", "file")
        # check if src_files is a list of multiple files
        if len(src_files) > 1:
            for file_path in src_files:
                __universal_load(file_path, file_type)
        # one file chosen
        elif src_files:
            file_path = src_files[0]
            __universal_load(file_path, file_type)
        else:
            print("No file(s) chosen")
    else:
        __universal_load(usr_path, file_type)

    return


def __read_directory(usr_path, file_type, file_type_print):
    """
    Universal read directory. Given a path and a type, it will do the appropriate read actions
    :param str usr_path: Path to directory
    :param str file_type: One of approved file types: xls, xlsx, txt, lpd
    :return none:
    """
    # no path provided. start gui browse
    if not usr_path:
        # got dir path
        usr_path, src_files = get_src_or_dst("read", "directory")

    # Check if this is a valid directory path
    valid_path = path_type(usr_path, "directory")

    # If dir path is valid
    if valid_path:
        # List all files of target type in dir
        files_found = list_files(file_type, usr_path)
        # notify how many files were found
        print("Found: {} {} file(s)".format(len(files_found), file_type_print))
        # Loop for each file found
        for file_path in files_found:
            # Call read lipd for each file found
            __read_file(file_path, file_type)
    else:
        print("Directory path is not valid: {}".format(usr_path))
    return


def __write_lipd(usr_path, filename):
    """
    Write LiPD data to file, provided an output directory and filename.
    :param str usr_path: Directory destination
    :param str filename: Target file
    :return none:
    """
    global verbose
    # no path provided. start gui browse
    if not usr_path:
        # got dir path
        usr_path, _ignore = get_src_or_dst("write", "directory")
    # Check if this is a valid directory path
    valid_path = path_type(usr_path, "directory")
    # If dir path is valid
    if valid_path:
        if verbose:
            print("writing: {}".format(filename))
        lipd_lib.write_lipd(usr_path, filename)

    return


# GLOBALS
run()

