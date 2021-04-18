from lipd.lipd_io import lipd_read, lipd_write
from lipd.timeseries import extract, collapse, mode_ts, translate_expression, get_matches
from lipd.doi_main import doi_main
from lipd.csvs import get_csv_from_metadata
from lipd.excel import excel_main
from lipd.noaa import noaa_prompt, noaa_to_lpd, lpd_to_noaa, noaa_prompt_1
from lipd.dataframes import *
from lipd.directory import get_src_or_dst, list_files, collect_metadata_file
from lipd.loggers import create_logger, log_benchmark, create_benchmark
from lipd.misc import path_type, load_fn_matches_ext, rm_values_fields, get_dsn, rm_empty_fields, print_filename, rm_wds_url, rm_od_url
from lipd.tables import addModel, addTable
from lipd.validator_api import call_validator_api, display_results, get_validator_format
from lipd.alternates import FILE_TYPE_MAP
from lipd.regexes import re_url
from lipd.fetch_doi import update_dois
from lipd.download_lipd import download_from_url, get_download_path
from lipd.directory import _go_to_package

import re
from time import process_time as clock
import os
import json
import copy
from collections import OrderedDict
import subprocess


# READ
def run():
    """
    Initialize and start objects. This is called automatically when importing the package.

    :return none:
    """
    # GLOBALS
    global cwd, files, logger_start, logger_benchmark, settings, _timeseries_data
    _timeseries_data = {}
    # files = {".lpd": [ {"full_path", "filename_ext", "filename_no_ext", "dir"} ], ".xls": [...], ".txt": [...]}
    settings = {"note_update": True, "note_validate": True, "verbose": True}
    cwd = os.getcwd()
    # logger created in whatever directory lipd is called from
    logger_start = create_logger("start")
    files = {".txt": [], ".lpd": [], ".xls": []}

    return


def readLipd(usr_path="", remote_file_save=False):
    """
    Read LiPD file(s).
    Enter a file path, directory path, or leave args blank to trigger gui.

    :param str usr_path: Path to file / directory (optional)
    :return dict _d: Metadata
    """
    global cwd, settings, files
    try:
        if settings["verbose"]:
            __disclaimer(opt="update")
        files[".lpd"] = []
        __read(usr_path, ".lpd")
        _d = __read_lipd_contents(usr_path, remote_file_save)
        # Clear out the lipd files metadata. We're done loading, we dont need it anymore.
        files[".lpd"] = []
    except Exception as e:
        pass
        # Placeholder to catch errors so we can always chdir back to cwd
    os.chdir(cwd)
    return _d


def readExcel(usr_path=""):
    """
    Read Excel file(s)
    Enter a file path, directory path, or leave args blank to trigger gui.

    :param str usr_path: Path to file / directory (optional)
    :return str cwd: Current working directory
    """
    global cwd, files
    try:
        files[".xls"] = []
        __read(usr_path, ".xls")

    except Exception as e:
        pass
        # Placeholder to catch errors so we can always chdir back to cwd

    os.chdir(cwd)
    return cwd


def readNoaa(usr_path=""):
    """
    Read NOAA file(s)
    Enter a file path, directory path, or leave args blank to trigger gui.

    :param str usr_path: Path to file / directory (optional)
    :return str cwd: Current working directory
    """
    global cwd, files
    try:
        files[".txt"] = []
        __read(usr_path, ".txt")
    except Exception as e:
        pass
        # Placeholder to catch errors so we can always chdir back to cwd
    os.chdir(cwd)
    return cwd


def readAll(usr_path=""):
    """
    Read all approved file types at once.
    Enter a file path, directory path, or leave args blank to trigger gui.

    :param str usr_path: Path to file / directory (optional)
    :return str cwd: Current working directory
    """
    print("readAll: This function no longer exists. Sorry! :(")
    # global cwd, files
    # start = clock()
    # files = {".txt": [], ".lpd": [], ".xls": []}
    # if not usr_path:
    #     usr_path, src_files = get_src_or_dst("read", "directory")
    # __read_directory(usr_path, ".lpd")
    # __read_directory(usr_path, ".xls")
    # __read_directory(usr_path, ".xlsx")
    # __read_directory(usr_path, ".txt")
    # end = clock()
    # logger_benchmark.info(log_benchmark("readAll", start, end))
    # return cwd


def excel():
    """
    Convert Excel files to LiPD files. LiPD data is returned directly from this function.

    | Example
    | 1: lipd.readExcel()
    | 2: D = lipd.excel()

    :return dict _d: Metadata
    """
    global files, cwd, settings
    _d = {}
    # Turn off verbose. We don't want to clutter the console with extra reading/writing output statements
    settings["verbose"] = False

    try:
        # Find excel files
        print("Found " + str(len(files[".xls"])) + " Excel files")
        logger_start.info("found excel files: {}".format(len(files[".xls"])))
        # Loop for each excel file
        for file in files[".xls"]:
            # Convert excel file to LiPD
            dsn = excel_main(file)
            try:
                # Read the new LiPD file back in, to get fixes, inferred calculations, updates, etc.
                _d[dsn] = readLipd(os.path.join(file["dir"], dsn + ".lpd"))
                # Write the modified LiPD file back out again.
                writeLipd(_d[dsn], cwd)
            except Exception as e:
                logger_start.error("excel: Unable to read new LiPD file, {}".format(e))
                print("Error: Unable to read new LiPD file: {}, {}".format(dsn, e))


    except Exception as e:
        pass
    # Start printing stuff again.
    settings["verbose"] = True
    os.chdir(cwd)
    return _d


def noaa(D="", path="", wds_url="", lpd_url="", version=""):
    """
    Convert between NOAA and LiPD files

    | Example: LiPD to NOAA converter
    | 1: L = lipd.readLipd()
    | 2: lipd.noaa(L, "/Users/someuser/Desktop", "https://www1.ncdc.noaa.gov/pub/data/paleo/pages2k/NAm2kHydro-2017/noaa-templates/data-version-1.0.0", "https://www1.ncdc.noaa.gov/pub/data/paleo/pages2k/NAm2kHydro-2017/data-version-1.0.0", "v1-1.0.0")

    | Example: NOAA to LiPD converter
    | 1: lipd.readNoaa()
    | 2: lipd.noaa()

    :param dict D: Metadata
    :param str path: Path where output files will be written to
    :param str wds_url: WDSPaleoUrl, where NOAA template file will be stored on NOAA's FTP server
    :param str lpd_url: URL where LiPD file will be stored on NOAA's FTP server
    :param str version: Version of the dataset
    :return none:
    """
    global files, cwd

    try:
        # When going from NOAA to LPD, use the global "files" variable.
        # When going from LPD to NOAA, use the data from the LiPD Library.

        # Choose the mode
        _mode = noaa_prompt()
        # LiPD mode: Convert LiPD files to NOAA files
        if _mode == "1":
            # _project, _version = noaa_prompt_1()
            if not version or not lpd_url:
                print("Missing parameters: Please try again and provide all parameters.")
                return
            if not D:
                print("Error: LiPD data must be provided for LiPD -> NOAA conversions")
            else:
                try:
                    os.mkdir("noaa_files")
                except FileExistsError:
                    pass
                if "paleoData" in D:
                    _d = copy.deepcopy(D)
                    D = lpd_to_noaa(_d, wds_url, lpd_url, version, path)
                else:
                    # For each LiPD file in the LiPD Library
                    for dsn, dat in D.items():
                        _d = copy.deepcopy(dat)
                        # Process this data through the converter
                        _d = lpd_to_noaa(_d, wds_url, lpd_url, version, path)
                        # Overwrite the data in the LiPD object with our new data.
                        D[dsn] = _d
                # If no wds url is provided, then remove instances from jsonld metadata
                if not wds_url:
                    D = rm_wds_url(D)
                # Write out the new LiPD files, since they now contain the new NOAA URL data
                if(path):
                    writeLipd(D, path)
                else:
                    print("Path not provided. Writing to CWD...")
                    writeLipd(D, cwd)

        # NOAA mode: Convert NOAA files to LiPD files
        elif _mode == "2":
            # Pass through the global files list. Use NOAA files directly on disk.
            noaa_to_lpd(files)

        else:
            print("Invalid input. Try again.")
    except Exception as e:
        pass
        # Placeholder to catch errors so we can always chdir back to cwd

    os.chdir(cwd)
    return


def doi(D, force=False):
    """
    Use the DOI id stored in the LiPD publication data to fetch new information from the DOI.org using their API.
    Merge the results with the existing data. This process will open the LiPD files on your computer, and overwrite them
    when done. This will not affect LiPD data currently loaded into memory.

    | Example
    | 1: D = lipd.readLipd()
    | 2: D = lipd.doi(D)
    |
    | DOI location : D["pub"][0]["doi"]

    :param  dict D: Metadata, either a single dataset or multiple datasets sorted by dataset name.
    :param bool force: Force DOIs to update even if they have previously been processed. Default is False.
    :return dict D: Metadata, with all publication data updated where possible

    """
    global cwd
    try:
        D = doi_main(D, force)
    except Exception as e:
        pass

    os.chdir(cwd)
    return D


def fetchDoiWithCsv(csv_source, write_file=True):
    """
    Retrieve DOI publication data for a list of DOI IDs that are stored in a CSV file. No LiPD files needed.
    This process uses the DOI.org API for data.

    :param str csv_source: The path to the CSV file stored on your computer
    :param bool write_file: Write the results to a JSON file (default) or print the results to the console.
    :return none:
    """
    global cwd
    try:
        update_dois(csv_source, write_file)
    except Exception as e:
        pass
        # Placeholder to catch errors so we can always chdir back to cwd

    os.chdir(cwd)
    return


def validate(D, detailed=True):
    """
    Use the Validator API for lipd.net to validate all LiPD files in the LiPD Library.
    Display the PASS/FAIL results. Display detailed results if the option is chosen.

    :param dict D: Metadata (single or multiple datasets)
    :param bool detailed: Show or hide the detailed results of each LiPD file. Shows warnings and errors
    :return none:
    """

    print("\n")
    # Fetch new results by calling lipd.net/api/validator (costly, may take a while)
    print("Fetching results from validator at lipd.net/validator... this may take a few moments.\n")
    try:
        results = []
        # Get the validator-formatted data for each dataset.
        if "paleoData" in D:
            _api_data = get_validator_format(D)
            # A list of lists of LiPD-content metadata
            results.append(call_validator_api(D["dataSetName"], _api_data))
        else:
            for dsn, dat in D.items():
                _api_data = get_validator_format(dat)
                # A list of lists of LiPD-content metadata
                results.append(call_validator_api(dsn, _api_data))
        display_results(results, detailed)
    except Exception as e:
        print("Error: validate: {}".format(e))

    __move_to_cwd()
    return


# def viewLipd(D):
#
#     try:
#         # Move to py package dir, so we can relative reference json_viewer.py
#         _go_to_package()
#         # Open viewer in subprocess, so it's contained and closed in a new py process
#         subprocess.call(('python', 'json_viewer.py', json.dumps(D)))
#     except Exception as e:
#         pass
#         # Placeholder to catch errors so we can always chdir back to cwd
#
#     __move_to_cwd()
#     return


# PUT


# def addEnsemble(D, dsn, ensemble):
#     """
#     Create ensemble entry and then add it to the specified LiPD dataset.
#
#     :param dict D: LiPD data
#     :param str dsn: Dataset name
#     :param list ensemble: Nested numpy array of ensemble column data.
#     :return dict D: LiPD data
#     """
#
#     # Check that the given filename exists in the library
#     if dsn in D:
#         meta = D[dsn]
#         # Create an ensemble dictionary entry
#         ens = create_ensemble(ensemble)
#         # If everything above worked, then there should be formatted ensemble data now.
#         if ens:
#             # Insert the formatted ensemble data into the master lipd library
#             meta = insert_ensemble(meta, ens)
#             # Set meta into lipd object
#             D[dsn] = meta
#     else:
#         print("Error: This dataset was not found in your LiPD data: {}".format(dsn))
#     return D


# DATA FRAMES


def ensToDf(ensemble):
    """
    Create an ensemble data frame from some given nested numpy arrays

    :param list ensemble: Ensemble data
    :return obj df: Pandas dataframe
    """
    try:
        df = create_dataframe(ensemble)
    except Exception as e:
        pass
    __move_to_cwd()
    return df


# TODO Not adapted to objectless utilties. Does it need an update?
# def lipdToDf(D, dsn):
#     """
#     Get LiPD data frames from LiPD object
#     :param dict D: LiPD data
#     :param str dsn: Dataset name
#     :return dict dfs: Pandas dataframes
#     """
#     try:
#         dfs = lipd_lib.get_dfs(dsn)
#     except KeyError:
#         print("Error: Unable to find LiPD file")
#         logger_start.warn("lipd_to_df: KeyError: missing lipds {}".format(filename))
#         dfs = None
#     return dfs


def tsToDf(tso):
    """
    Create Pandas DataFrame from TimeSeries object.
    Use: Must first extractTs to get a time series. Then pick one item from time series and pass it through

    :param dict tso: Time series entry
    :return dict dfs: Pandas dataframes
    """
    dfs = {}
    try:
        dfs = ts_to_df(tso)
    except Exception as e:
        print("Error: Unable to create data frame")
        logger_start.warn("ts_to_df: tso malformed: {}".format(e))
    __move_to_cwd()
    return dfs


# TODO Not adapted to objectless utilties. Does it need an update?
# def filterDfs(expr):
#     """
#     Get data frames based on some criteria. i.e. all measurement tables or all ensembles.
#     :param str expr: Search expression. (i.e. "paleo measurement tables")
#     :return dict dfs: Data frames indexed by filename
#     """
#     dfs = {}
#     try:
#         dfs = get_filtered_dfs(lipd_lib.get_master(), expr)
#     except Exception:
#         logger_dataframes.info("filter_dfs: Unable to filter data frames for expr: {}".format(expr))
#         print("Error: unable to filter dataframes")
#     return dfs


# ANALYSIS - TIME SERIES


def extractTs(d, whichtables="meas", mode="paleo"):
    """
    Create a time series using LiPD data (uses paleoData by default)

    | Example : (default) paleoData and meas tables
    | 1. D = lipd.readLipd()
    | 2. ts = lipd.extractTs(D)

    | Example : chronData and all tables
    | 1. D = lipd.readLipd()
    | 2. ts = lipd.extractTs(D, "all", "chron")

    :param dict d: Metadata
    :param str whichtables: "all", "summ", "meas", "ens" - The tables that you would like in the timeseries
    :param str mode: "paleo" or "chron" mode
    :return list l: Time series
    """
    # instead of storing each raw dataset per tso, store it once in the global scope. saves memory
    global _timeseries_data
    start = clock()
    _l = []
    try:
        if not d:
            print("Error: LiPD data not provided. Pass LiPD data into the function.")
        else:
            print(mode_ts("extract", mode))
            if "paleoData" in d:
                # One dataset: Process directly on file, don't loop
                try:
                    _dsn = get_dsn(d)
                    _timeseries_data[start] = {}
                    _timeseries_data[start][_dsn] = d
                    # Use the LiPD data given to start time series extract
                    print("extracting: {}".format(_dsn))
                    # Copy, so we don't affect the original data
                    _v = copy.deepcopy(d)
                    # Start extract...
                    _l = (extract(_v, whichtables, mode, start))
                except Exception as e:
                    print("Error: Unable to extractTs for dataset: {}: {}".format(_dsn, e))
                    logger_start.debug("extractTs: Exception: {}, {}".format(_dsn, e))

            else:
                _timeseries_data[start] = d
                # Multiple datasets: Loop and append for each file
                for k, v in d.items():
                    try:
                        # Use the LiPD data given to start time series extract
                        print("extracting: {}".format(k))
                        # Copy, so we don't affect the original data
                        _v = copy.deepcopy(v)
                        # Start extract...
                        _l += (extract(_v, whichtables, mode, start))
                    except Exception as e:
                        print("Error: Unable to extractTs for dataset: {}: {}".format(k, e))
                        logger_start.debug("extractTs: Exception: {}".format(e))
            print("Created time series: {} entries".format(len(_l)))
    except Exception as e:
        print("Error: Unable to extractTs: {}".format(e))
        logger_start.error("extractTs: Exception: {}".format(e))
    __move_to_cwd()
    return _l


def collapseTs(ts=None):
    """
    Collapse a time series back into LiPD record form.

    | Example
    | 1. D = lipd.readLipd()
    | 2. ts = lipd.extractTs(D)
    | 3. New_D = lipd.collapseTs(ts)

    _timeseries_data is sorted by time_id, and then by dataSetName
    _timeseries_data[10103341]["ODP1098B"] = {data}

    :param list ts: Time series
    :return dict: Metadata
    """
    # Retrieve the associated raw data according to the "time_id" found in each object. Match it in _timeseries_data
    global _timeseries_data
    _d = {}
    try:
        if not ts:
            print("Error: Time series data not provided. Pass time series into the function.")
        else:
            # Send time series list through to be collapsed.
            try:
                _raw = _timeseries_data[ts[0]["time_id"]]
                print(mode_ts("collapse", mode="", ts=ts))
                _d = collapse(ts, _raw)
                _d = rm_empty_fields(_d)
            except Exception as e:
                print("Error: Unable to collapse the time series: {}".format(e))
                logger_start.error("collapseTs: unable to collapse the time series: {}".format(e))
    except Exception as e:
        pass
    __move_to_cwd()
    return _d


def filterTs(ts, expressions):
    """
    Create a new time series that only contains entries that match the given expression.

    | Example:
    | D = lipd.loadLipd()
    | ts = lipd.extractTs(D)
    | new_ts = filterTs(ts, "archiveType == marine sediment")
    | new_ts = filterTs(ts, ["paleoData_variableName == sst", "archiveType == marine sediment"])
    | Expressions should use underscores to denote data nesting.
    | Ex: paleoData_hasResolution_hasMedian or

    :param list OR str expressions: Expressions
    :param list ts:                 Time series
    :return list new_ts:            Filtered time series that matches the expression
    """

    try:
        # Make a copy of the ts. We're going to work directly on it.
        new_ts = ts[:]

        # User provided a single query string
        if isinstance(expressions, str):
            # Use some magic to turn the given string expression into a machine-usable comparative expression.
            expr_lst = translate_expression(expressions)
            # Only proceed if the translation resulted in a usable expression.
            if expr_lst:
                # Return the new filtered time series. This will use the same time series
                # that filters down each loop.
                new_ts, _idx = get_matches(expr_lst, new_ts)

        # User provided a list of multiple queries
        elif isinstance(expressions, list):
            # Loop for each query
            for expr in expressions:
                # Use some magic to turn the given string expression into a machine-usable comparative expression.
                expr_lst = translate_expression(expr)
                # Only proceed if the translation resulted in a usable expression.
                if expr_lst:
                    # Return the new filtered time series. This will use the same time series
                    # that filters down each loop.
                    new_ts, _idx = get_matches(expr_lst, new_ts)
    except Exception as e:
        pass

    __move_to_cwd()
    return new_ts


def queryTs(ts, expression):
    """
    Find the indices of the time series entries that match the given expression.

    | Example:
    | D = lipd.loadLipd()
    | ts = lipd.extractTs(D)
    | matches = queryTs(ts, "archiveType == marine sediment")
    | matches = queryTs(ts, "geo_meanElev <= 2000")

    :param str expression: Expression
    :param list ts: Time series
    :return list _idx: Indices of entries that match the criteria
    """
    try:
        # Make a copy of the ts. We're going to work directly on it.
        _idx = []

        # User provided a single query string
        if isinstance(expression, str):
            # Use some magic to turn the given string expression into a machine-usable comparative expression.
            expr_lst = translate_expression(expression)
            # Only proceed if the translation resulted in a usable expression.
            if expr_lst:
                # Return the new filtered time series. This will use the same time series
                # that filters down each loop.
                new_ts, _idx = get_matches(expr_lst, ts)

        # User provided a list of multiple queries
        elif isinstance(expression, list):
            # Loop for each query
            for expr in expression:
                # Use some magic to turn the given string expression into a machine-usable comparative expression.
                expr_lst = translate_expression(expr)
                # Only proceed if the translation resulted in a usable expression.
                if expr_lst:
                    # Return the new filtered time series. This will use the same time series
                    # that filters down each loop.
                    new_ts, _idx = get_matches(expr_lst, ts)
    except Exception as e:
        pass
    __move_to_cwd()
    return _idx


def viewTs(ts):
    """
    View the contents of one time series entry in a nicely formatted way

    | Example
    | 1. D = lipd.readLipd()
    | 2. ts = lipd.extractTs(D)
    | 3. viewTs(ts[0])

    :param dict ts: One time series entry
    :return none:
    """
    try:
        _ts = ts
        if isinstance(ts, list):
            _ts = ts[0]
            print("It looks like you input a full time series. It's best to view one entry at a time.\n"
                  "I'll show you the first entry...")
        _tmp_sort = OrderedDict()
        _tmp_sort["ROOT"] = {}
        _tmp_sort["PUBLICATION"] = {}
        _tmp_sort["GEO"] = {}
        _tmp_sort["OTHERS"] = {}
        _tmp_sort["DATA"] = {}

        # Organize the data by section
        for k,v in _ts.items():
            if not any(i == k for i in ["paleoData", "chronData", "mode", "@context"]):
                if k in ["archiveType", "dataSetName", "googleSpreadSheetKey", "metadataMD5", "tagMD5", "googleMetadataWorksheet", "lipdVersion"]:
                    _tmp_sort["ROOT"][k] = v
                elif "pub" in k:
                    _tmp_sort["PUBLICATION"][k] = v
                elif "geo" in k:
                    _tmp_sort["GEO"][k] = v
                elif "paleoData_" in k or "chronData_" in k:
                    if isinstance(v, list) and len(v) > 2:
                        _tmp_sort["DATA"][k] = "[{}, {}, {}, ...]".format(v[0], v[1], v[2])
                    else:
                        _tmp_sort["DATA"][k] = v
                else:
                    if isinstance(v, list) and len(v) > 2:
                        _tmp_sort["OTHERS"][k] = "[{}, {}, {}, ...]".format(v[0], v[1], v[2])
                    else:
                        _tmp_sort["OTHERS"][k] = v

        # Start printing the data to console
        for k1, v1 in _tmp_sort.items():
            print("\n{}\n===============".format(k1))
            for k2, v2 in v1.items():
                print("{} : {}".format(k2, v2))
    except Exception as e:
        pass
    __move_to_cwd()
    return

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

    | Example
    | lipd.showLipds(D)

    :pararm dict D: LiPD data
    :return none:
    """
    try:
        if not D:
            print("Error: LiPD data not provided. Pass LiPD data into the function.")
        else:
            print(json.dumps(D.keys(), indent=2))
    except Exception as e:
        pass
    __move_to_cwd()
    return


def showMetadata(dat):
    """
    Display the metadata specified LiPD in pretty print

    | Example
    | showMetadata(D["Africa-ColdAirCave.Sundqvist.2013"])

    :param dict dat: Metadata
    :return none:
    """
    try:
        _tmp = rm_values_fields(copy.deepcopy(dat))
        print(json.dumps(_tmp, indent=2))
    except Exception as e:
        pass
    __move_to_cwd()
    return


def showDfs(d):
    """
    Display the available data frame names in a given data frame collection

    :param dict d: Dataframe collection
    :return none:
    """
    try:
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
    except Exception as e:
        pass
    __move_to_cwd()
    return


# GET

def getLipdNames(D=None):
    """
    Get a list of all LiPD names in the library

    | Example
    | names = lipd.getLipdNames(D)

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
    __move_to_cwd()
    return _names


def getMetadata(L):
    """
    Get metadata from a LiPD data in memory

    | Example
    | m = lipd.getMetadata(D["Africa-ColdAirCave.Sundqvist.2013"])

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
    Get CSV from LiPD metadata

    | Example
    | c = lipd.getCsv(D["Africa-ColdAirCave.Sundqvist.2013"])

    :param dict L: One LiPD record
    :return dict d: CSV data
    """
    _c = {}
    try:
        if not L:
            print("Error: LiPD data not provided. Pass LiPD data into the function.")
        else:
            _j, _c = get_csv_from_metadata(L["dataSetName"], L)
    except KeyError as ke:
        print("Error: Unable to get data. Please check that input is one LiPD dataset: {}".format(ke))
    except Exception as e:
        print("Error: Unable to get data. Something went wrong: {}".format(e))
        logger_start.warn("getCsv: Exception: Unable to process lipd data: {}".format(e))
    return _c


# WRITE

def writeLipd(dat, path=""):
    """
    Write LiPD data to file(s)

    :param dict dat: Metadata
    :param str path: Destination (optional)
    :return none:
    """
    global settings
    __write_lipd(dat, path)
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

    try:
        # check that we are using the correct function to load this file type. (i.e. readNoaa for a .txt file)
        correct_ext = load_fn_matches_ext(file_path, file_type)

        # Check that this path references a file
        valid_path = path_type(file_path, "file")

        # is the path a file?
        if valid_path and correct_ext:

            # get file metadata for one file
            file_meta = collect_metadata_file(file_path)

            # append to global files, then load in D
            if file_type == ".lpd":
                # add meta to global file meta
                files[".lpd"].append(file_meta)
            # append to global files
            elif file_type in [".xls", ".xlsx"]:
                print("reading: {}".format(print_filename(file_meta["full_path"])))
                files[".xls"].append(file_meta)
            # append to global files
            elif file_type == ".txt":
                print("reading: {}".format(print_filename(file_meta["full_path"])))
                files[".txt"].append(file_meta)


            # we want to move around with the files we load
            # change dir into the dir of the target file
            cwd = file_meta["dir"]
            if cwd:
                os.chdir(cwd)
    except Exception as e:
        pass
        # Placeholder to catch errors so we can always chdir back to cwd

    os.chdir(cwd)
    return


def __read(usr_path, file_type):
    """
    Determine what path needs to be taken to read in file(s)

    :param str usr_path: Path  (optional)
    :param str file_type: File type to read
    :return none:
    """
    global cwd

    try:
        # is there a file path specified ?
        if usr_path:
            # Is this a URL? Download the file and return the local path
            is_url = re.match(re_url, usr_path)
            if is_url:
                # The usr_path will now be a local path to a single file. It will trigger the "elif" statement below
                usr_path = download_from_url(usr_path)
            # Directory path
            if os.path.isdir(usr_path):
                __read_directory(usr_path, file_type)
            # File path
            elif os.path.isfile(usr_path):
                __read_file(usr_path, file_type)
            # Invalid path given
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
    except Exception as e:
        pass
        # Placeholder to catch errors so we can always chdir back to cwd

    os.chdir(cwd)

    return


def __read_lipd_contents(usr_path, remote_file_save):
    """
    Use the file metadata to read in the LiPD file contents as a dataset library

    :return dict: Metadata
    """
    global files, settings
    _d = {}
    try:
        # Read in one file, set data directly into dictionary
        if len(files[".lpd"]) == 1:
            _d = lipd_read(files[".lpd"][0]["full_path"])
            # Remove any files that were downloaded remotely and user doesn't want to save
            is_url = re.match(re_url, usr_path)
            if not remote_file_save and is_url:
                try:
                    os.remove(files[".lpd"][0]["full_path"])
                except FileNotFoundError:
                    print("Unable to delete locally saved remote file")
            if settings["verbose"]:
                print("Finished read: 1 record")
        # Read in multiple files, organize data by dataSetName (one extra layer)
        else:
            for file in files[".lpd"]:
                _contents = lipd_read(file["full_path"])
                _d[_contents["dataSetName"]] = _contents
            if settings["verbose"]:
                print("Finished read: {} records".format(len(_d)))
    except Exception as e:
        print("Error: read_lipd_contents: {}".format(e))
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
        if src_files:
            for file_path in src_files:
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


def __write_lipd(dat, usr_path):
    """
    Write LiPD data to file, provided an output directory and dataset name.

    :param dict dat: Metadata
    :param str usr_path: Destination path
    :param str dsn: Dataset name of one specific file to write
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
        if "paleoData" in dat:
            try:
                if settings["verbose"]:
                    print("writing: {}".format(dat["dataSetName"]))
                lipd_write(dat, usr_path)
            except KeyError as ke:
                print("Error: Unable to write file: unknown, {}".format(ke))
            except Exception as e:
                print("Error: Unable to write file: {}, {}".format(dat["dataSetName"], e))
        # Filename is not given, write out whole library
        else:
            if dat:
                for name, lipd_dat in dat.items():
                    try:
                        if settings["verbose"]:
                            print("writing: {}".format(name))
                        lipd_write(lipd_dat, usr_path)
                    except Exception as e:
                        print("Error: Unable to write file: {}, {}".format(name, e))

    return


def __disclaimer(opt=""):
    """
    Print the disclaimers once. If they've already been shown, skip over.

    :return none:
    """
    global settings
    if opt == "update":
        print("Disclaimer: LiPD files may be updated and modified to adhere to standards\n")
        settings["note_update"] = False
    if opt == "validate":
        print("Note: Use lipd.validate() or www.LiPD.net/create "
              "to ensure that your new LiPD file(s) are valid")
        settings["note_validate"] = False
    return


def __move_to_cwd():
    global cwd
    os.chdir(cwd)
    return

# GLOBALS
run()

