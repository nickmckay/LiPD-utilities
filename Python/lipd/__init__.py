import copy
from time import clock

from .pkg_resources.lipds.LiPD_Library import *
from .pkg_resources.timeseries.Convert import *
from .pkg_resources.timeseries.TimeSeries_Library import *
from .pkg_resources.doi.doi_main import doi_main
from .pkg_resources.excel.excel_main import excel_main
from .pkg_resources.noaa.noaa_main import noaa_prompt, noaa_to_lpd, lpd_to_noaa
from .pkg_resources.helpers.ts import translate_expression, get_matches
from .pkg_resources.helpers.dataframes import *
from .pkg_resources.helpers.directory import get_src_or_dst, list_files
from .pkg_resources.helpers.loggers import create_logger, log_benchmark, create_benchmark
from .pkg_resources.helpers.misc import path_type, load_fn_matches_ext
from .pkg_resources.helpers.ensembles import create_ensemble, insert_ensemble
from .pkg_resources.helpers.validator_api import get_validator_results, display_results
from .pkg_resources.helpers.alternates import FILE_TYPE_MAP


# READ


def run():
    """
    Initialize and start objects. This is called automatically when importing the package.
    :return none:
    """
    # GLOBALS
    global cwd, lipd_lib, ts_lib, convert, files, logger_start, logger_benchmark, verbose
    verbose = True
    cwd = os.getcwd()
    # creating the LiPD Library also creates the Tmp sys folder where the files will be stored later.
    lipd_lib = LiPD_Library()
    ts_lib = TimeSeries_Library()
    convert = Convert()
    # print(cwd)
    # logger created in whatever directory lipd is called from
    logger_start = create_logger("start")
    logger_benchmark = create_benchmark("benchmarks", "benchmark.log")
    files = {".txt": [], ".lpd": [], ".xls": []}

    return


def readLipd(usr_path=""):
    """
    Wrapper function: LiPD file read
    :param str usr_path: Path to file (optional)
    :return str cwd: Current Working Directory
    """
    global cwd
    start = time.clock()
    __read(usr_path, ".lpd")
    end = time.clock()
    logger_benchmark.info(log_benchmark("readLipd", start, end))
    return cwd


def readExcel(usr_path=""):
    """
    Wrapper function: Excel file read
    :param str usr_path: Path to file (optional)
    :return str cwd: Current Working Directory
    """
    global cwd
    start = time.clock()
    __read(usr_path, ".xls")
    end = time.clock()
    logger_benchmark.info(log_benchmark("readExcel", start, end))
    return cwd


def readNoaa(usr_path=""):
    """
    Wrapper function: NOAA file read
    :param str usr_path: Path to file
    :return str cwd: Current Working Directory
    """
    global cwd
    start = time.clock()
    __read(usr_path, ".txt")
    end = time.clock()
    logger_benchmark.info(log_benchmark("readNoaa", start, end))
    return cwd


def readAll(usr_path=""):
    """
    Wrapper function: Read all file types at once
    :param str usr_path: Path to directory
    :return str cwd: Current Working Directory
    """
    global cwd
    start = time.clock()
    if not usr_path:
        usr_path, src_files = get_src_or_dst("read", "directory")
    __read_directory(usr_path, ".lpd")
    __read_directory(usr_path, ".xls")
    __read_directory(usr_path, ".xlsx")
    __read_directory(usr_path, ".txt")
    end = time.clock()
    logger_benchmark.info(log_benchmark("readAll", start, end))
    return cwd


def excel():
    """
    Wrapper function: Convert Excel files to LiPD files
    :return none:
    """
    global files, cwd, verbose
    start = time.clock()
    # Convert excel files to LiPD
    excel_main(files)
    end = time.clock()
    logger_start.info(log_benchmark("excel", start, end))
    # Turn off verbose. We don't want to clutter the console with extra reading/writing output statements
    verbose = False
    for file in files[".xls"]:
        try:
            readLipd(os.path.join(file["dir"], file["filename_no_ext"] + ".lpd"))
        except Exception as e:
            logger_start.debug("excel: Converted excel to lipd file, but unable readLipd(): {}, {}".format(file["filename_ext"], e))
    try:
        writeLipd(usr_path=cwd)
        print("Reminder! Use lipd.validate() or www.LiPD.net/validator "
              "to ensure that your new LiPD file(s) are valid")
    except Exception as e:
        logger_start.debug("excel: Unable to writeLipds with new lipd files, {}".format(e))
    end = time.clock()
    logger_benchmark.info(log_benchmark("readAll", start, end))
    # Turn on verbose. Back to normal mode when this function is finished.
    verbose = True
    return


def noaa():
    """
    Wrapper function: Convert between NOAA and LiPD files
    :return none:
    """
    global files, lipd_lib, cwd
    # When going from NOAA to LPD, use the global "files" variable.
    # When going from LPD to NOAA, use the data from the LiPD Library.

    # Choose the mode
    _mode = noaa_prompt()
    start = time.clock()
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
        writeLipd(usr_path=cwd)

    # NOAA mode: Convert NOAA files to LiPD files
    elif _mode == "2":
        # Pass through the global files list. Use NOAA files directly on disk.
        noaa_to_lpd(files)

    else:
        print("Invalid input. Try again.")
    end = time.clock()
    logger_benchmark.info(log_benchmark("noaa", start, end))
    return


def doi():
    """
    Wrapper function: Update publication information using data DOIs
    :return:
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
    start = time.clock()
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
    end = time.clock()
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


def extractTs():
    """
    Create a time series using the LiPD library
    :return list l: Time series
    """
    l = []
    start = time.clock()
    try:
        # Loop over the LiPD files in the LiPD_Library
        for k, v in lipd_lib.get_master().items():
            try:
                # Get metadata from this LiPD object. Convert.
                # Receive a time series (list of time series objects) and add it to what we currently have.
                # Continue building time series until all datasets are processed.
                print("extracting: {}".format(k))
                l += (convert.ts_extract_main(v.get_master(), v.get_dfs_chron()))
            except Exception as e:
                print("Error: Skipping {}: {}".format(k, e))
                logger_start.debug("extractTs: Exception: {}".format(e))
        print("Finished time series: {} objects".format(len(l)))
    except KeyError as e:
        print("Error: Unable to extractTimeSeries")
        logger_start.debug("extractTimeSeries() failed at {}".format(e))

    end = time.clock()
    logger_benchmark.info(log_benchmark("extractTs", start, end))
    return l


def collapseTs():
    """
    Export TimeSeries back to LiPD Library. Updates information in LiPD objects.
    :return none:
    """
    l = []
    # Get all TSOs from TS_Library, and add them to a list
    for k, v in ts_lib.get_master().items():
        l.append({'name': v.get_lpd_name(), 'data': v.get_master()})
    # Send the TSOs list through to be converted. Then let the LiPD_Library load the metadata into itself.
    try:
        lipd_lib.load_tsos(convert.lipd_extract_main(l))
    except Exception:
        print("Error: Unable to convert time series to LiPD")
        logger_start.debug("collapseTs failed")
    return


def find(expression, ts):
    """
    Find the names of the TimeSeries that match some criteria (expression)
    ex: find("geo_elevation == 1500", ts)
    ex: find("paleoData_variablename == sst", ts)
    :param str expression: The filter expression to apply to the time series
    :param list ts: Time series
    :return list new_ts: Filtered time series that matches the expression
    """
    new_ts = []
    expr_lst = translate_expression(expression)
    if expr_lst:
        new_ts = get_matches(expr_lst, ts)
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
    Display the filenames in the LiPD library
    :return none:
    """
    lipd_lib.show_lipds()
    return


def showMetadata(filename):
    """
    Display the contents of the specified LiPD file in the library.
    (ex. displayLiPD NAm-ak000.lpd)
    :param str filename: LiPD filename
    :return none:
    """
    lipd_lib.show_metadata(filename)
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

def getLipdNames():
    """
    Get a list of all LiPD names in the library
    :return list f_list: File list
    """
    f_list = []
    try:
        f_list = lipd_lib.get_lipd_names()
    except Exception:
        pass
    return f_list


def getMetadata(filename):
    """
    Get metadata from a LiPD file
    :param str filename: LiPD filename
    :return dict d: Metadata
    """
    d = {}
    try:
        d = lipd_lib.get_metadata(filename)
    except KeyError:
        print("Error: Unable to find LiPD file")
        logger_start.warn("KeyError: Unable to find record {}".format(filename))
    # print("Process Complete")
    return d


def getCsv(filename):
    """
    Get CSV from a  LiPD file
    :param str filename: LiPD filename
    :return dict d: CSV
    """
    d = {}
    try:
        d = lipd_lib.get_csv(filename)
    except KeyError:
        print("Error: Unable to find record")
        logger_start.warn("Unable to find record {}".format(filename))
    return d


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


def writeLipd(usr_path="", filename=""):
    """
    Write out LiPD file(s)
    :param str filename: LiPD filename (optional)
    :param str usr_path: Target directory destination (optional)
    :return none:
    """
    global verbose
    start = time.clock()
    __write_lipd(usr_path, filename)
    end = time.clock()
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


def quit():
    """
    Quit and exit the program. Cleans up temporary space (Does not save changes)
    :return none:
    """
    lipd_lib.cleanup()
    print("Quitting LiPD Utilities...")
    exit(0)


# HELPERS


def __universal_read(file_path, file_type):
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
            print("finding more excel")
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
        # Filename is given, write out one file
        if filename:
            lipd_lib.write_lipd(usr_path, filename)
            if verbose:
                print("writing: {}".format(filename))
        # Filename is not given, write out whole library
        else:
            _lib = list(lipd_lib.get_master().keys())
            if _lib:
                for filename in _lib:
                    lipd_lib.write_lipd(usr_path, filename)
                    if verbose:
                        print("writing: {}".format(filename))
    return


# GLOBALS
run()

