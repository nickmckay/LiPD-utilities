from .pkg_resources.lipds.LiPD import lipd_read, lipd_write
from .pkg_resources.timeseries.timeseries import extract, collapse, mode_ts
from .pkg_resources.doi.doi_main import doi_main
from .pkg_resources.helpers.csvs import get_csv_from_metadata
from .pkg_resources.excel.excel_main import excel_main
from .pkg_resources.noaa.noaa_main import noaa_prompt, noaa_to_lpd, lpd_to_noaa
from .pkg_resources.helpers.ts import translate_expression, get_matches
from .pkg_resources.helpers.dataframes import *
from .pkg_resources.helpers.directory import get_src_or_dst, list_files, collect_metadata_file
from .pkg_resources.helpers.loggers import create_logger, log_benchmark, create_benchmark
from .pkg_resources.helpers.misc import path_type, load_fn_matches_ext, rm_values_fields, get_dsn, rm_empty_fields
from .pkg_resources.helpers.ensembles import create_ensemble, insert_ensemble
from .pkg_resources.helpers.validator_api import get_validator_results, display_results
from .pkg_resources.helpers.alternates import FILE_TYPE_MAP

from time import clock
import os
import json
import copy
# READ


def run():
    """
    Initialize and start objects. This is called automatically when importing the package.
    :return none:
    """
    # GLOBALS
    global cwd, files, logger_start, logger_benchmark, settings
    # files = {".lpd": [ {"full_path", "filename_ext", "filename_no_ext", "dir"} ], ".xls": [...], ".txt": [...]}
    settings = {"note_update": True, "note_validate": True, "verbose": True}
    cwd = os.getcwd()
    # logger created in whatever directory lipd is called from
    logger_start = create_logger("start")
    logger_benchmark = create_benchmark("benchmarks", "benchmark.log")
    files = {".txt": [], ".lpd": [], ".xls": []}

    return


def readLipd(usr_path=""):
    """
    Wrapper function: LiPD file read
    :param str usr_path: Path to file (optional)
    :return dict _d: LiPD data
    """
    global cwd, settings
    if settings["verbose"]:
        __disclaimer(opt="update")
    start = clock()
    __read(usr_path, ".lpd")
    _d = __read_lipd_contents()
    end = clock()
    print("Finished read: {} records".format(len(_d)))
    logger_benchmark.info(log_benchmark("readLipd", start, end))
    return _d


def readExcel(usr_path=""):
    """
    Wrapper function: Excel file read
    :param str usr_path: Path to file (optional)
    :return str cwd: Current Working Directory
    """
    global cwd
    start = clock()
    __read(usr_path, ".xls")
    end = clock()
    logger_benchmark.info(log_benchmark("readExcel", start, end))
    return cwd


def readNoaa(usr_path=""):
    """
    Wrapper function: NOAA file read
    :param str usr_path: Path to file
    :return str cwd: Current Working Directory
    """
    global cwd
    start = clock()
    __read(usr_path, ".txt")
    end = clock()
    logger_benchmark.info(log_benchmark("readNoaa", start, end))
    return cwd


def readAll(usr_path=""):
    """
    Wrapper function: Read all file types at once
    :param str usr_path: Path to directory
    :return str cwd: Current Working Directory
    """
    global cwd
    start = clock()
    if not usr_path:
        usr_path, src_files = get_src_or_dst("read", "directory")
    __read_directory(usr_path, ".lpd")
    __read_directory(usr_path, ".xls")
    __read_directory(usr_path, ".xlsx")
    __read_directory(usr_path, ".txt")
    end = clock()
    logger_benchmark.info(log_benchmark("readAll", start, end))
    return cwd


def excel():
    """
    Convert Excel files to LiPD files. LiPD data is returned directly from this function.

    Example
    1: lipd.readExcel()
    2: D = lipd.excel()

    :return dict _d: LiPD data
    """
    global files, cwd, settings
    _d = {}
    # Turn off verbose. We don't want to clutter the console with extra reading/writing output statements
    settings["verbose"] = False
    # Find excel files
    print("Found " + str(len(files[".xls"])) + " Excel files")
    logger_start.info("found excel files: {}".format(len(files[".xls"])))
    # Start the clock
    start = clock()
    # Loop for each excel file
    for file in files[".xls"]:
        # Convert excel file to LiPD
        filename = excel_main(file)
        try:
            # Read the new LiPD file back in, to get fixes, inferred calculations, updates, etc.
            _d[filename] = readLipd(os.path.join(file["dir"], filename))
            # Write the modified LiPD file back out again.
            writeLipd(_d, cwd, filename)
        except Exception as e:
            logger_start.error("excel: Unable to read/write new LiPD file, {}".format(e))
            print("Error: Unable to process new LiPD file: {}, {}".format(filename, e))
    # Time!
    end = clock()
    logger_benchmark.info(log_benchmark("excel", start, end))
    # Start printing stuff again.
    settings["verbose"] = True
    return _d


def noaa(d=None):
    """
    Wrapper function: Convert between NOAA and LiPD files

    Example: LiPD to NOAA converter
    1: D = lipd.readLipd()
    2: lipd.noaa(D)

    Example: NOAA to LiPD converter
    1: readNoaa()
    2: lipd.noaa()

    :return none:
    """
    global files, lipd_lib, cwd
    # When going from NOAA to LPD, use the global "files" variable.
    # When going from LPD to NOAA, use the data from the LiPD Library.

    # Choose the mode
    _mode = noaa_prompt()
    start = clock()
    # LiPD mode: Convert LiPD files to NOAA files
    if _mode == "1":
        if not d:
            print("Error: LiPD data must be provided for LiPD -> NOAA conversions")
        else:
            # For each LiPD file in the LiPD Library
            for dsn, dat in d.items():
                _l = copy.deepcopy(dat)
                # Process this data through the converter
                _l_modified = lpd_to_noaa(_l)
                # Overwrite the data in the LiPD object with our new data.
                d[dsn] = _l_modified
            # Write out the new LiPD files, since they now contain the new NOAA URL data
            writeLipd(d, cwd)

    # NOAA mode: Convert NOAA files to LiPD files
    elif _mode == "2":
        # Pass through the global files list. Use NOAA files directly on disk.
        noaa_to_lpd(files)

    else:
        print("Invalid input. Try again.")
    end = clock()
    logger_benchmark.info(log_benchmark("noaa", start, end))
    return


def doi():
    """
    Update publication information using data DOIs. Updates LiPD files on disk, not in memory.

    Example
    1: lipd.readLipd()
    2: lipd.doi()

    :return none:
    """
    global files
    doi_main(files)
    return


def validate(detailed=True, fetch_new_results=True):
    """
    Use the Validator API for lipd.net to validate all LiPD files in the LiPD Library.
    Display the PASS/FAIL results. Display detailed results if the option is chosen.
    :param bool detailed: Show or hide the detailed results of each LiPD file. Shows warnings and errors.
    :param bool fetch_new_results: Defaults to fetching new validation results each call
    :return none:
    """
    start = clock()
    print("\n")
    # Fetch new results by calling lipd.net/api/validator (costly, may take a while)
    if fetch_new_results:
        print("Fetching results from validator at lipd.net/validator... this may take a few moments.\n")
        # Get the validator-formatted data for each LiPD file in the LiPD Library.
        # A list of lists of LiPD-content metadata
        d = lipd_lib.get_data_for_validator()
        results = get_validator_results(d)
        display_results(results, detailed)
        # Set the results inside of each LiPD object
        for entry in results:
            lipd_lib.put_validator_results(entry)
    # Check for previous validator results. Display those rather than running the validator again. (faster)
    else:
        results = lipd_lib.get_validator_results()
        display_results(results, detailed)
    end = clock()
    logger_benchmark.info(log_benchmark("validate", start, end))
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
    return


# DATA FRAMES


def ensToDf(ensemble):
    """
    Create an ensemble data frame from some given nested numpy arrays
    :param list ensemble: Ensemble data
    :return obj df: Pandas dataframe
    """
    df = create_dataframe(ensemble)
    return df


def lipdToDf(filename):
    """
    Get LiPD data frames from LiPD object
    :param str filename:
    :return dict dfs: Pandas dataframes
    """
    try:
        dfs = lipd_lib.get_dfs(filename)
    except KeyError:
        print("Error: Unable to find LiPD file")
        logger_start.warn("lipd_to_df: KeyError: missing lipds {}".format(filename))
        dfs = None
    return dfs


def tsToDf(tso):
    """
    Create Pandas DataFrame from TimeSeries object.
    Use: Must first extractTimeSeries to get a time series. Then pick one item from time series and pass it through
    :param dict tso: Time series object
    :return dict dfs: Pandas dataframes
    """
    dfs = {}
    try:
        dfs = ts_to_df(tso)
    except Exception as e:
        print("Error: Unable to create data frame")
        logger_start.warn("ts_to_df: tso malformed: {}".format(e))
    return dfs


def filterDfs(expr):
    """
    Get data frames based on some criteria. i.e. all measurement tables or all ensembles.
    :param str expr: Search expression. (i.e. "paleo measurement tables")
    :return dict dfs: Data frames indexed by filename
    """
    dfs = {}
    try:
        dfs = get_filtered_dfs(lipd_lib.get_master(), expr)
    except Exception:
        logger_dataframes.info("filter_dfs: Unable to filter data frames for expr: {}".format(expr))
        print("Error: unable to filter dataframes")
    return dfs


# ANALYSIS - TIME SERIES


def extractTs(d, chron=False):
    """
    Create a time series using LiPD data

    Example
    1. D = lipd.readLipd()
    2. ts = lipd.extractTs(D)

    :return list l: Time series
    """
    _l = []
    start = clock()
    try:
        if not d:
            print("Error: LiPD data not provided. Pass LiPD data into the function.")
        else:
            print(mode_ts("extract", b=chron))
            if "paleoData" in d:
                # One dataset: Process directly on file, don't loop
                try:
                    _dsn = get_dsn(d)
                    # Use the LiPD data given to start time series extract
                    print("extracting: {}".format(_dsn))
                    # Copy, so we don't affect the original data
                    _v = copy.deepcopy(d)
                    # Start extract...
                    _l = (extract(_v, chron))
                except Exception as e:
                    print("Error: Unable to extractTs for dataset: {}: {}".format(_dsn, e))
                    logger_start.debug("extractTs: Exception: {}, {}".format(_dsn, e))

            else:
                # Multiple datasets: Loop and append for each file
                for k, v in d.items():
                    try:
                        # Use the LiPD data given to start time series extract
                        print("extracting: {}".format(k))
                        # Copy, so we don't affect the original data
                        _v = copy.deepcopy(v)
                        # Start extract...
                        _l += (extract(_v, chron))
                    except Exception as e:
                        print("Error: Unable to extractTs for dataset: {}: {}".format(k, e))
                        logger_start.debug("extractTs: Exception: {}".format(e))
            print("Created time series: {} entries".format(len(_l)))
    except Exception as e:
        print("Error: Unable to extractTs: {}".format(e))
        logger_start.error("extractTs: Exception: {}".format(e))
    end = clock()
    logger_benchmark.info(log_benchmark("extractTs", start, end))
    return _l


def collapseTs(ts=None):
    """
    Collapse a time series back into LiPD record form.

    Example
    1. D = lipd.readLipd()
    2. ts = lipd.extractTs(D)
    3. New_D = lipd.collapseTs(ts)

    :param list ts: Time series
    :return dict: LiPD data
    """
    _d = {}
    if not ts:
        print("Error: Time series data not provided. Pass time series into the function.")
    else:
        # Send time series list through to be collapsed.
        try:
            print(mode_ts("collapse", ts=ts))
            _d = collapse(ts)
            _d = rm_empty_fields(_d)
            print("Created LiPD data: {} entries".format(len(_d)))

        except Exception as e:
            print("Error: Unable to collapse the time series: {}".format(e))
            logger_start.error("collapseTs: unable to collapse the time series: {}".format(e))
    return _d


def filterTs(ts, expression):
    """
    Create a new time series that only contains entries that match the given expression.

    Example:
    D = lipd.loadLipd()
    ts = lipd.extractTs(D)
    new_ts = filterTs(ts, "archiveType == marine sediment")
    new_ts = filterTs(ts, "paleoData_variableName == sst")

    :param str expression: Expression
    :param list ts: Time series
    :return list new_ts: Filtered time series that matches the expression
    """
    new_ts = []
    # Use some magic to turn the given string expression into a machine-usable comparative expression.
    expr_lst = translate_expression(expression)
    # Only proceed if the translation resulted in a usable expression.
    if expr_lst:
        new_ts, _idx = get_matches(expr_lst, ts)
    return new_ts


def queryTs(ts, expression):
    """
    Find the indices of the time series entries that match the given expression.

    Example:
    D = lipd.loadLipd()
    ts = lipd.extractTs(D)
    matches = queryTs(ts, "archiveType == marine sediment")
    matches = queryTs(ts, "geo_meanElev <= 2000")

    :param str expression: Expression
    :param list ts: Time series
    :return list _idx: Indices of entries that match the criteria
    """
    _idx = []
    # Use some magic to turn the given string expression into a machine-usable comparative expression.
    expr_lst = translate_expression(expression)
    # Only proceed if the translation resulted in a usable expression.
    if expr_lst:
        new_ts, _idx = get_matches(expr_lst, ts)
    return _idx

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


def showLipds(D=None):
    """
    Display the dataset names of a given LiPD data

    Example
    lipd.showLipds(D)

    :pararm dict D: LiPD data
    :return none:
    """

    if not D:
        print("Error: LiPD data not provided. Pass LiPD data into the function.")
    else:
        print(json.dumps(D.keys(), indent=2))

    return


def showMetadata(dat):
    """
    Display the metadata specified LiPD in pretty print

    Example
    showMetadata(D["Africa-ColdAirCave.Sundqvist.2013"])

    :param dict dat: Metadata
    :return none:
    """
    _tmp = rm_values_fields(copy.deepcopy(dat))
    print(json.dumps(_tmp, indent=2))
    return


def showCsv(filename):
    """
    Display CSV data for a LiPD file
    :param str filename: LiPD filename
    :return none:
    """
    lipd_lib.show_csv(filename)
    return


def showTso(tso):
    """
    Display contents of one time series entry.
    :param str tso: Time series entry
    :return none:
    """
    try:
        for key, value in sorted(tso.items()):
            print("{0:20}: {1}".format(key, value))
    except Exception as e:
        print("Unable to list contents: {}".format(e))
    # print("Process Complete")
    return


def showDfs(d):
    """
    Display the available data frame names in a given data frame collection
    :param dict d: Dataframe collection
    :return none:
    """
    if "metadata" in d:
        print("metadata")
    if "paleoData" in d:
        try:
            for k, v in d["paleoData"].items():
                print(k)
        except KeyError:
            pass
        except AttributeError:
            pass
    if "chronData" in d:
        try:
            for k, v in d["chronData"].items():
                print(k)
        except KeyError:
            pass
        except AttributeError:
            pass
    # print("Process Complete")
    return


# GET

def getLipdNames(D=None):
    """
    Get a list of all LiPD names in the library

    Example
    names = lipd.getLipdNames(D)

    :return list f_list: File list
    """
    _names = []
    try:
        if not D:
            print("Error: LiPD data not provided. Pass LiPD data into the function.")
        else:
            _names = D.keys()
    except Exception:
        pass
    return _names


def getMetadata(L):
    """
    Get metadata from a LiPD data in memory

    Example
    m = lipd.getMetadata(D["Africa-ColdAirCave.Sundqvist.2013"])

    :param dict L: One LiPD record
    :return dict d: LiPD record (metadata only)
    """
    _l = {}
    try:
        # Create a copy. Do not affect the original data.
        _l = copy.deepcopy(L)
        # Remove values fields
        _l = rm_values_fields(_l)
    except Exception as e:
        # Input likely not formatted correctly, though other problems can occur.
        print("Error: Unable to get data. Please check that input is LiPD data: {}".format(e))
    return _l


def getCsv(L=None):
    """
    Get CSV from LiPD data

    Example
    c = lipd.getCsv(D["Africa-ColdAirCave.Sundqvist.2013"])

    :param dict L: One LiPD record
    :return dict d: CSV data
    """
    _c = {}
    try:
        if not L:
            print("Error: LiPD data not provided. Pass LiPD data into the function.")
        else:
            _l = copy.deepcopy(L)
            _j, _c = get_csv_from_metadata(_l["dataSetName"], _l)
    except KeyError as ke:
        print("Error: Unable to get data. Please check that input is LiPD data: {}".format(ke))
    except Exception as e:
        print("Error: Unable to get data. Something went wrong: {}".format(e))
        logger_start.warn("getCsv: Exception: Unable to process lipd data: {}".format(e))
    return _c


def getLibrary():
    """
    Get LiPD library as a dictionary. Intended for use in pickling library data.
    :return dict D: Library
    """
    D = {}
    try:
        D = lipd_lib.get_lib_as_dict()
    except Exception as e:
        print("Error: Unable to retrieve library: {}".format(e))
        logger_start.debug("getLibrary: {}".format(e))
    return D


# WRITE


def writeLipd(dat, usr_path="", filename=""):
    """
    Write LiPD data to file(s)
    :param dict dat: LiPD data
    :param str usr_path: Destination (optional)
    :param str filename: LiPD filename, for writing one specific file (optional)
    :return none:
    """
    global settings
    start = clock()
    __write_lipd(dat, usr_path, filename)
    end = clock()
    logger_benchmark.info(log_benchmark("writeLipd", start, end))
    return


def removeLipd(filename):
    """
    Remove LiPD file from library
    :return none:
    """
    lipd_lib.remove_lipd(filename)
    return


def removeLipds():
    """
    Remove all LiPD files from library.
    :return none:
    """
    lipd_lib.remove_lipds()
    return


# HELPERS


def __universal_read(file_path, file_type):
    """
    Use a file path to create file metadata and load a file in the appropriate way, according to the provided file type.
    :param str file_path: Path to file
    :param str file_type: One of approved file types: xls, xlsx, txt, lpd
    :return none:
    """
    global files, cwd, settings

    # check that we are using the correct function to load this file type. (i.e. readNoaa for a .txt file)
    correct_ext = load_fn_matches_ext(file_path, file_type)

    # Check that this path references a file
    valid_path = path_type(file_path, "file")

    # is the path a file?
    if valid_path and correct_ext:

        # get file metadata for one file
        file_meta = collect_metadata_file(file_path)
        if settings["verbose"]:
            print("reading: {}".format(file_meta["filename_ext"]))

        # append to global files, then load in lipd_lib
        if file_type == ".lpd":
            # add meta to global file meta
            files[".lpd"].append(file_meta)
        # append to global files
        elif file_type in [".xls", ".xlsx"]:
            files[".xls"].append(file_meta)
        # append to global files
        elif file_type == ".txt":
            files[".txt"].append(file_meta)

        # we want to move around with the files we load
        # change dir into the dir of the target file
        cwd = file_meta["dir"]
        os.chdir(cwd)

    return


def __read(usr_path, file_type):
    """
    Determine what path needs to be taken to read in file(s)
    :param str usr_path: Path  (optional)
    :param str file_type: File type to read
    :return none:
    """
    # is there a file path specified ?
    if usr_path:
        if os.path.isdir(usr_path):
            __read_directory(usr_path, file_type)
        elif os.path.isfile(usr_path):
            __read_file(usr_path, file_type)
        else:
            print("Error: Path given is invalid")

    # no path specified. ask if they want to load dir or file
    else:
        choice = ""
        count = 3
        while not choice:
            try:
                print("Choose a read option:\n1. One file\n2. Multi-file select\n3. Directory")
                choice = input("Option: ")
                print("\n")
                # now use the given file type and prompt answer to call _read_file or _read_dir
                if choice in ["1", "2", "3"]:
                    # open directory picker
                    if choice == "3":
                        __read_directory(usr_path, file_type)
                    else:
                        # open a file picker
                        __read_file(usr_path, file_type)
                    break
                else:
                    count -= 1
                if count == 0:
                    print("Error: Too many failed attempts")
                    break
            except Exception as e:
                print("Error: Invalid input: {}".format(e))
    return


def __read_lipd_contents():
    """
    Use the file metadata to read in the LiPD file contents as a dictionary "library"
    :return dict: LiPD data
    """
    global files
    _d = {}
    for file in files[".lpd"]:
        _d[file["filename_no_ext"]] = lipd_read(file["full_path"])
    return _d


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
                __universal_read(file_path, file_type)
        # one file chosen
        elif src_files:
            file_path = src_files[0]
            __universal_read(file_path, file_type)
        else:
            print("No file(s) chosen")
    else:
        __universal_read(usr_path, file_type)

    return


def __read_directory(usr_path, file_type):
    """
    Universal read directory. Given a path and a type, it will do the appropriate read actions
    :param str usr_path: Path to directory
    :param str file_type: .xls, .xlsx, .txt, .lpd
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
        files_found = []
        # Extra case for xlsx excel files
        if file_type == ".xls":
            files_found += list_files(".xlsx", usr_path)
        files_found += list_files(file_type, usr_path)
        # notify how many files were found
        print("Found: {} {} file(s)".format(len(files_found), FILE_TYPE_MAP[file_type]["file_type"]))
        # Loop for each file found
        for file_path in files_found:
            # Call read lipd for each file found
            __read_file(file_path, file_type)
    else:
        print("Directory path is not valid: {}".format(usr_path))
    return


def __write_lipd(dat, usr_path, filename):
    """
    Write LiPD data to file, provided an output directory and filename.
    :param dict dat: LiPD data
    :param str usr_path: Directory destination
    :param str filename: Target file
    :return none:
    """
    global settings
    # no path provided. start gui browse
    if not usr_path:
        # got dir path
        usr_path, _ignore = get_src_or_dst("write", "directory")
    # Check if this is a valid directory path
    valid_path = path_type(usr_path, "directory")
    # If dir path is valid
    if valid_path:
        # Filename is given, write out one file
        if filename:
            try:
                if settings["verbose"]:
                    print("writing: {}".format(filename))
                lipd_write(dat[filename], usr_path, filename)
            except Exception as e:
                print("Error: Unable to write file: {}, {}".format(filename, e))
        # Filename is not given, write out whole library
        else:
            if dat:
                for name, lipd_dat in dat.items():
                    try:
                        if settings["verbose"]:
                            print("writing: {}".format(name))
                        lipd_write(lipd_dat, usr_path, name)
                    except Exception as e:
                        print("Error: Unable to write file: {}, {}".format(name, e))

    return


def __disclaimer(opt=""):
    """
    Print the disclaimers once. If they've already been shown, skip over.
    :return none:
    """
    global settings
    if opt is "update":
        print("Disclaimer: LiPD files may be updated and modified to adhere to standards\n")
        settings["note_update"] = False
    if opt is "validate":
        print("Note: Use lipd.validate() or www.LiPD.net/create "
              "to ensure that your new LiPD file(s) are valid")
        settings["note_validate"] = False
    return

# GLOBALS
run()

