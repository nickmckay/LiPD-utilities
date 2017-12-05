import copy
import re

from .alternates import COMPARISONS
from .misc import match_operators, cast_float
from .regexes import re_pandas_x_und, re_fund_valid, re_pub_valid, re_sheet_w_number, re_sheet, re_filter_expr
from .blanks import EMPTY
from .loggers import create_logger

logger_ts = create_logger('time_series')


# EXTRACT

def extract(d, whichtables, mode, time):
    """
    LiPD Version 1.3
    Main function to initiate LiPD to TSOs conversion.

    Each object has a
    "paleoNumber" or "chronNumber"
    "tableNumber"
    "modelNumber"
    "time_id"
    "mode" - chronData or paleoData
    "tableType" - "meas" "ens" "summ"


    :param dict d: Metadata for one LiPD file
    :param str whichtables: all, meas, summ, or ens
    :param str mode: paleo or chron mode
    :return list _ts: Time series
    """
    logger_ts.info("enter extract_main")
    _root = {}
    _ts = {}
    # _switch = {"paleoData": "chronData", "chronData": "paleoData"}
    _pc = "paleoData"
    if mode == "chron":
        _pc = "chronData"
    _root["mode"] = _pc
    _root["time_id"] = time
    try:
        # Build the root level data.
        # This will serve as the template for which column data will be added onto later.
        for k, v in d.items():
            if k == "funding":
                _root = _extract_fund(v, _root)
            elif k == "geo":
                _root = _extract_geo(v, _root)
            elif k == 'pub':
                _root = _extract_pub(v, _root)
            # elif k in ["chronData", "paleoData"]:
            #     # Store chronData and paleoData as-is. Need it to collapse without data loss.
            #     _root[k] = copy.deepcopy(v)
            else:
                if k not in ["chronData", "paleoData"]:
                    _root[k] = v
        # Create tso dictionaries for each individual column (build on root data)
        _ts = _extract_pc(d, _root, _pc, whichtables)
    except Exception as e:
        logger_ts.error("extract: Exception: {}".format(e))
        print("extract: Exception: {}".format(e))

    logger_ts.info("exit extract_main")
    return _ts


def _extract_fund(l, _root):
    """
    Creates flat funding dictionary.
    :param list l: Funding entries
    """
    logger_ts.info("enter _extract_funding")
    for idx, i in enumerate(l):
        for k, v in i.items():
            _root['funding' + str(idx + 1) + '_' + k] = v
    return _root


def _extract_geo(d, _root):
    """
    Extract geo data from input
    :param dict d: Geo
    :return dict _root: Root data
    """
    logger_ts.info("enter ts_extract_geo")
    # May not need these if the key names are corrected in the future.
    # COORDINATE ORDER: [LON, LAT, ELEV]
    x = ['geo_meanLon', 'geo_meanLat', 'geo_meanElev']
    # Iterate through geo dictionary
    for k, v in d.items():
        # Case 1: Coordinates special naming
        if k == 'coordinates':
            for idx, p in enumerate(v):
                try:
                    # Check that our value is not in EMPTY.
                    if isinstance(p, str):
                        if p.lower() in EMPTY:
                            # If elevation is a string or 0, don't record it
                            if idx != 2:
                                # If long or lat is empty, set it as 0 instead
                                _root[x[idx]] = 0
                        else:
                            # Set the value as a float into its entry.
                            _root[x[idx]] = float(p)
                    # Value is a normal number, or string representation of a number
                    else:
                        # Set the value as a float into its entry.
                        _root[x[idx]] = float(p)
                except IndexError as e:
                    logger_ts.warn("_extract_geo: IndexError: idx: {}, val: {}, {}".format(idx, p, e))
        # Case 2: Any value that is a string can be added as-is
        elif isinstance(v, str):
            if k == 'meanElev':
                try:
                    # Some data sets have meanElev listed under properties for some reason.
                    _root['geo_' + k] = float(v)
                except ValueError as e:
                    # If the value is a string, then we don't want it
                    logger_ts.warn("_extract_geo: ValueError: meanElev is a string: {}, {}".format(v, e))
            else:
                _root['geo_' + k] = v
        # Case 3: Nested dictionary. Recursion
        elif isinstance(v, dict):
            _root = _extract_geo(v, _root)
    return _root


def _extract_pub(l, _root):
    """
    Extract publication data from one or more publication entries.
    :param list l: Publication
    :return dict _root: Root data
    """
    logger_ts.info("enter _extract_pub")
    # For each publication entry
    for idx, pub in enumerate(l):
        logger_ts.info("processing publication #: {}".format(idx))
        # Get author data first, since that's the most ambiguously structured data.
        _root = _extract_authors(pub, idx, _root)
        # Go through data of this publication
        for k, v in pub.items():
            # Case 1: DOI ID. Don't need the rest of 'identifier' dict
            if k == 'identifier':
                try:
                    _root['pub' + str(idx + 1) + '_DOI'] = v[0]['id']
                except KeyError as e:
                    logger_ts.warn("_extract_pub: KeyError: no doi id: {}, {}".format(v, e))
            # Case 2: All other string entries
            else:
                if k != 'authors' and k != 'author':
                    _root['pub' + str(idx + 1) + '_' + k] = v
    return _root


def _extract_authors(pub, idx, _root):
    """
    Create a concatenated string of author names. Separate names with semi-colons.
    :param any pub: Publication author structure is ambiguous
    :param int idx: Index number of Pub
    """
    logger_ts.info("enter extract_authors")
    try:
        # DOI Author data. We'd prefer to have this first.
        names = pub['author']
    except KeyError as e:
        try:
            # Manually entered author data. This is second best.
            names = pub['authors']
        except KeyError as e:
            # Couldn't find any author data. Skip it altogether.
            names = False
            logger_ts.info("extract_authors: KeyError: author data not provided, {}".format(e))

    # If there is author data, find out what type it is
    if names:
        # Build author names onto empty string
        auth = ''
        # Is it a list of dicts or a list of strings? Could be either
        # Authors: Stored as a list of dictionaries or list of strings
        if isinstance(names, list):
            for name in names:
                if isinstance(name, str):
                    auth += name + ';'
                elif isinstance(name, dict):
                    for k, v in name.items():
                        auth += v + ';'
        elif isinstance(names, str):
            auth = names
        # Enter finished author string into target
        _root['pub' + str(idx + 1) + '_author'] = auth[:-1]
    return _root


def _extract_pc(d, root, pc, whichtables):
    """
    Extract all data from a PaleoData dictionary.
    :param dict d: PaleoData dictionary
    :param dict root: Time series root data
    :param str pc: paleoData or chronData
    :param str whichtables: all, meas, summ, or ens
    :return list _ts: Time series
    """
    logger_ts.info("enter extract_pc")
    _ts = []
    try:
        # For each table in pc
        for k, v in d[pc].items():
            if whichtables == "all" or whichtables == "meas":
                for _table_name1, _table_data1 in v["measurementTable"].items():
                    _ts = _extract_table(_table_data1, copy.deepcopy(root), pc, _ts, "meas")
            if whichtables != "meas":
                if "model" in v:
                    for _table_name1, _table_data1 in v["model"].items():
                        # get the method info for this model. This will be paired to all summ and ens table data
                        _method = _extract_method(_table_data1["method"])
                        if whichtables == "all" or whichtables == "summ":
                            if "summaryTable" in _table_data1:
                                for _table_name2, _table_data2 in _table_data1["summaryTable"].items():
                                    # take a copy of this tso root
                                    _tso = copy.deepcopy(root)
                                    # add in the method details
                                    _tso.update(_method)
                                    # add in the table details
                                    _ts = _extract_table(_table_data2, _tso, pc, _ts, "summ")
                        if whichtables == "all" or whichtables == "ens":
                            if "ensembleTable" in _table_data1:
                                for _table_name2, _table_data2 in _table_data1["ensembleTable"].items():
                                    _tso = copy.deepcopy(root)
                                    _tso.update(_method)
                                    _ts = _extract_table(_table_data2, _tso, pc, _ts, "ens")

    except Exception as e:
        logger_ts.warn("extract_pc: Exception: {}".format(e))
    return _ts


def _extract_method(method):
    """
    Make a timeseries-formatted version of model method data

    :param dict method: Method data
    :return dict _method: Method data, formatted
    """
    _method = {}
    for k,v in method.items():
        _method["method_" + k] = v
    return _method


def _extract_special(current, table_data):
    """
    Extract year, age, and depth column from table data
    :param dict table_data: Data at the table level
    :param dict current: Current data
    :return dict current:
    """
    logger_ts.info("enter extract_special")
    try:
        # Add age, year, and depth columns to ts_root where possible
        for k, v in table_data['columns'].items():
            s = ""

            # special case for year bp, or any variation of it. Translate key to "age""
            if "bp" in k.lower():
                s = "age"

            # all other normal cases. clean key and set key.
            elif any(x in k.lower() for x in ('age', 'depth', 'year', "yr", "distance_from_top", "distance")):
                # Some keys have units hanging on them (i.e. 'year_ad', 'depth_cm'). We don't want units on the keys
                if re_pandas_x_und.match(k):
                    s = k.split('_')[0]
                elif "distance" in k:
                    s = "depth"
                else:
                    s = k

            # create the entry in ts_root.
            if s:
                try:
                    current[s] = v['values']
                except KeyError as e:
                    # Values key was not found.
                    logger_ts.warn("extract_special: KeyError: 'values' not found, {}".format(e))
                try:
                    current[s + 'Units'] = v['units']
                except KeyError as e:
                    # Values key was not found.
                    logger_ts.warn("extract_special: KeyError: 'units' not found, {}".format(e))

    except Exception as e:
        logger_ts.error("extract_special: {}".format(e))

    return current


def _extract_table_root(d, current, pc):
    """
    Extract data from the root level of a paleoData table.
    :param dict d: paleoData table
    :param dict current: Current root data
    :param str pc: paleoData or chronData
    :return dict current: Current root data
    """
    logger_ts.info("enter extract_table_root")
    try:
        for k, v in d.items():
            if isinstance(v, str):
                current[pc + '_' + k] = v
    except Exception as e:
        logger_ts.error("extract_table_root: {}".format(e))
    return current


def _extract_table_model(table_data, current, tt):
    """
    Add in modelNumber and summaryNumber fields if this is a summary table

    :param dict table_data: Table data
    :param dict current: LiPD root data
    :param str tt: Table type "summ", "ens", "meas"
    :return dict current: Current root data
    """
    try:
        if tt in ["summ", "ens"]:
            m = re.match(re_sheet, table_data["tableName"])
            if m:
                _pc_num= m.group(1) + "Number"
                current[_pc_num] = m.group(2)
                current["modelNumber"] = m.group(4)
                current["tableNumber"] = m.group(6)
            else:
                logger_ts.error("extract_table_summary: Unable to parse paleo/model/table numbers")
    except Exception as e:
        logger_ts.error("extract_table_summary: {}".format(e))
    return current


def _extract_table(table_data, current, pc, ts, tt):
    """
    Use the given table data to create a time series entry for each column in the table.

    :param dict table_data: Table data
    :param dict current: LiPD root data
    :param str pc: paleoData or chronData
    :param list ts: Time series (so far)
    :param bool summary: Summary Table or not
    :return list ts: Time series (so far)
    """
    current["tableType"] = tt
    # Get root items for this table
    current = _extract_table_root(table_data, current, pc)
    # Add in modelNumber and tableNumber if this is "ens" or "summ" table
    current = _extract_table_model(table_data, current, tt)
    # Add age, depth, and year columns to root if available
    _table_tmp = _extract_special(current, table_data)
    try:
        # Start creating entries using dictionary copies.
        for _col_name, _col_data in table_data["columns"].items():
            # Add column data onto root items. Copy so we don't ruin original data
            _col_tmp = _extract_columns(_col_data, copy.deepcopy(_table_tmp), pc)
            try:
                ts.append(_col_tmp)
            except Exception as e:
                logger_ts.warn("extract_table: Unable to create ts entry, {}".format(e))
    except Exception as e:
        logger_ts.error("extract_table: {}".format(e))
    return ts


def _extract_columns(d, tmp_tso, pc):
    """
    Extract data from one paleoData column
    :param dict d: Column dictionary
    :param dict tmp_tso: TSO dictionary with only root items
    :return dict: Finished TSO
    """
    logger_ts.info("enter extract_columns")
    for k, v in d.items():
        if k == 'climateInterpretation':
            tmp_tso = _extract_climate(v, tmp_tso)
        elif k == 'calibration':
            tmp_tso = _extract_calibration(v, tmp_tso)
        else:
            # Assume if it's not a special nested case, then it's a string value
            tmp_tso[pc + '_' + k] = v
    return tmp_tso


def _extract_calibration(d, tmp_tso):
    """
    Get calibration info from column data.
    :param dict d: Calibration dictionary
    :param dict tmp_tso: Temp TSO dictionary
    :return dict: tmp_tso with added calibration entries
    """
    logger_ts.info("enter extract_calibration")
    for k, v in d.items():
        tmp_tso['calibration_' + k] = v
    return tmp_tso


def _extract_climate(d, tmp_tso):
    """
    Get climate interpretation from column data.
    :param dict d: Climate Interpretation dictionary
    :param dict tmp_tso: Temp TSO dictionary
    :return dict: tmp_tso with added climateInterpretation entries
    """
    logger_ts.info("enter extract_climate")
    for k, v in d.items():
        tmp_tso['climateInterpretation_' + k] = v
    return tmp_tso


# COLLAPSE


def collapse(l, raw):
    """
    LiPD Version 1.3
    Main function to initiate time series to LiPD conversion

    Each object has a:
    "paleoNumber" or "chronNumber"
    "tableNumber"
    "modelNumber"
    "time_id"
    "mode" - chronData or paleoData
    "tableType" - "meas" "ens" "summ"

    :param list l: Time series
    :return dict _master: LiPD data, sorted by dataset name
    """
    logger_ts.info("enter collapse")
    # LiPD data (in progress), sorted dataset name
    _master = {}
    _dsn = ""

    try:
        # Determine if we're collapsing a paleo or chron time series
        _pc = l[0]["mode"]

        # Loop the time series
        for entry in l:
            # Get notable keys
            dsn = entry['dataSetName']
            _dsn = dsn
            _current = entry

            # Since root items are the same in each column of the same dataset, we only need these steps the first time.
            if dsn not in _master:
                logger_ts.info("collapsing: {}".format(dsn))
                print("collapsing: {}".format(dsn))
                _master, _current = _collapse_root(_master, _current, dsn, _pc)
                try:
                    _master[dsn]["paleoData"] = raw[dsn]["paleoData"]
                    if "chronData" in raw[dsn]:
                        _master[dsn]["chronData"] = raw[dsn]["chronData"]
                except KeyError as e:
                    print("collapse: Could not collapse an object the dataset: {}, {}".format(dsn, e))

            # Collapse pc, calibration, and interpretation
            _master = _collapse_pc(_master, _current, dsn, _pc)

        # The result combined into a single dataset. Remove the extra layer on the data.
        if len(_master) == 1:
            _master = _master[_dsn]
            print("Created LiPD data: 1 dataset")
        else:
            print("Created LiPD data: {} datasets".format(len(_master)))

    except Exception as e:
        print("Error: Unable to collapse time series, {}".format(e))
        logger_ts.error("collapse: Exception: {}".format(e))

    logger_ts.info("exit collapse")
    return _master


def _get_current_names(current, dsn, pc):
    """
    Get the table name and variable name from the given time series entry

    :param dict current: Time series entry
    :param str pc: paleoData or chronData
    :return str _table_name:
    :return str _variable_name:
    """
    _table_name = ""
    _variable_name = ""
    # Get key info
    try:
        _table_name = current['{}_tableName'.format(pc)]
        _variable_name = current['{}_variableName'.format(pc)]
    except Exception as e:
        print("Error: Unable to collapse time series: {}, {}".format(dsn, e))
        logger_ts.error("get_current: {}, {}".format(dsn, e))
    return _table_name, _variable_name


def _collapse_root(master, current, dsn, pc):
    """
    Collapse the root items of the current time series entry

    :param dict master: LiPD data (so far)
    :param dict current: Current time series entry
    :param str dsn: Dataset name
    :param str pc: paleoData or chronData (mode)
    :return dict master:
    :return dict current:
    """
    logger_ts.info("enter collapse_root")
    _tmp_fund = {}
    _tmp_pub = {}
    # The tmp lipd data that we'll place in master later
    _tmp_master = {'pub': [], 'geo': {'geometry': {'coordinates': []}, 'properties': {}}, 'funding': [],
                   'paleoData': {}, "chronData": {}}
    # _raw = _switch[pc]
    _c_keys = ['meanLat', 'meanLon', 'meanElev']
    _c_vals = [0, 0, 0]
    _p_keys = ['siteName', 'pages2kRegion']
    try:
        # For all keys in the current time series entry
        for k, v in current.items():
            # Here are all the keys that we don't want in the root.
            if any(i in k for i in ["funding", "pub", "geo", "lipdVersion", "dataSetName", "metadataMD5", "googleMetadataWorksheet",
                     "googleSpreadSheetKey", "tagMD5", "@context", "archiveType"]):
                # FUNDING
                if 'funding' in k:
                    # Group funding items in tmp_funding by number
                    m = re_fund_valid.match(k)
                    try:
                        _tmp_fund[m.group(1)][m.group(2)] = v
                    except Exception:
                        try:
                            # If the first layer is missing, create it and try again
                            _tmp_fund[m.group(1)] = {}
                            _tmp_fund[m.group(1)][m.group(2)] = v
                        except Exception:
                            # Still not working. Give up.
                            pass

                # GEO
                elif 'geo' in k:
                    key = k.split('_')
                    # Coordinates - [LON, LAT, ELEV]
                    if key[1] in _c_keys:
                        if key[1] == 'meanLon' or key[1] == "longitude":
                            _c_vals[0] = v
                        elif key[1] == 'meanLat' or key[1] == "latitude":
                            _c_vals[1] = v
                        elif key[1] == 'meanElev' or key[1] == "elevation":
                            _c_vals[2] = v
                    # Properties
                    elif key[1] in _p_keys:
                        _tmp_master['geo']['properties'][key[1]] = v
                    # All others
                    else:
                        _tmp_master['geo'][key[1]] = v

                # PUBLICATION
                elif 'pub' in k:
                    # Group pub items in tmp_pub by number
                    m = re_pub_valid.match(k.lower())
                    if m:
                        number = int(m.group(1)) - 1  # 0 indexed behind the scenes, 1 indexed to user.
                        key = m.group(2)
                        # Authors ("Pu, Y.; Nace, T.; etc..")
                        if key == 'author' or key == 'authors':
                            try:
                                _tmp_pub[number]['author'] = _collapse_author(v)
                            except KeyError as e:
                                # Dictionary not created yet. Assign one first.
                                _tmp_pub[number] = {}
                                _tmp_pub[number]['author'] = _collapse_author(v)
                        # DOI ID
                        elif key == 'DOI':
                            try:
                                _tmp_pub[number]['identifier'] = [{"id": v, "type": "doi", "url": "http://dx.doi.org/" + str(v)}]
                            except KeyError:
                                # Dictionary not created yet. Assign one first.
                                _tmp_pub[number] = {}
                                _tmp_pub[number]['identifier'] = [{"id": v, "type": "doi", "url": "http://dx.doi.org/" + str(v)}]
                        # All others
                        else:
                            try:
                                _tmp_pub[number][key] = v
                            except KeyError:
                                # Dictionary not created yet. Assign one first.
                                _tmp_pub[number] = {}
                                _tmp_pub[number][key] = v
                # ALL OTHER KEYS THAT AREN'T YET ACCOUNTED FOR : md5, googleSheetKey, etc.
                else:
                    # Root
                    _tmp_master[k] = v

        # Append the compiled data into the master dataset data
        for k, v in _tmp_pub.items():
            _tmp_master['pub'].append(v)
        for k, v in _tmp_fund.items():
            _tmp_master['funding'].append(v)

        # Get rid of elevation coordinate if one was never added.
        if _c_vals[2] == 0:
            del _c_vals[2]
        _tmp_master['geo']['geometry']['coordinates'] = _c_vals

        # Create entry in object master, and set our new data to it.
        master[dsn] = _tmp_master
    except Exception as e:
        logger_ts.error("collapse_root: Exception: {}, {}".format(dsn, e))
    logger_ts.info("exit collapse_root")
    return master, current


def _collapse_author(s):
    """
    Split author string back into organized dictionary
    :param str s: Formatted names string "Last, F.; Last, F.; etc.."
    :return list of dict: One dictionary per author name
    """
    logger_ts.info("enter collapse_author")
    l = []
    authors = s.split(';')
    for author in authors:
        l.append({'name': author})
    return l


def _collapse_pc(master, current, dsn, pc):
    """
    Collapse the paleo or chron for the current time series entry

    :param dict master: LiPD data (so far)
    :param dict current: Current time series entry
    :param str dsn: Dataset name
    :param str pc: paleoData or chronData
    :return dict master:
    """
    logger_ts.info("enter collapse_paleo")
    _table_name, _variable_name = _get_current_names(current, dsn, pc)

    try:
        # Get the names we need to build the hierarchy
        _m = re.match(re_sheet_w_number, _table_name)

        # Is this a summary table or a measurement table?
        _switch = {"meas": "measurementTable", "summ": "summaryTable", "ens": "ensembleTable"}
        _ms = _switch[current["tableType"]]

        # This is a measurement table. Put it in the correct part of the structure
        # master[datasetname][chronData][chron0][measurementTable][chron0measurement0]
        if _ms == "measurementTable":

            # master[dsn] = _collapse_build_skeleton(master(dsn), _ms, _m)

            # Collapse the keys in the table root if a table does not yet exist
            if _table_name not in master[dsn][pc][_m.group(1)][_ms]:
                _tmp_table = _collapse_table_root(current, dsn, pc)
                master[dsn][pc][_m.group(1)][_ms][_table_name] = _tmp_table

            # Collapse the keys at the column level, and return the column data
            _tmp_column = _collapse_column(current, pc)
            # Create the column entry in the table
            master[dsn][pc][_m.group(1)][_ms][_table_name]['columns'][_variable_name] = _tmp_column

        # This is a summary table. Put it in the correct part of the structure
        # master[datasetname][chronData][chron0][model][chron0model0][summaryTable][chron0model0summary0]
        elif _ms in ["ensembleTable", "summaryTable"]:
            # Collapse the keys in the table root if a table does not yet exist
            if _table_name not in master[dsn][pc][_m.group(1)]["model"][_m.group(1) + _m.group(2)][_ms]:
                _tmp_table = _collapse_table_root(current, dsn, pc)
                master[dsn][pc][_m.group(1)]["model"][_m.group(1) + _m.group(2)][_ms][_table_name] = _tmp_table

            # Collapse the keys at the column level, and return the column data
            _tmp_column = _collapse_column(current, pc)
            # Create the column entry in the table
            master[dsn][pc][_m.group(1)]["model"][_m.group(1) + _m.group(2)][_ms][_table_name]["columns"][_variable_name] = _tmp_column

    except Exception as e:
        print("Error: Unable to collapse column data: {}, {}".format(dsn, e))
        logger_ts.error("collapse_paleo: {}, {}, {}".format(dsn, _variable_name, e))

    # If these sections had any items added to them, then add them to the column master.

    return master


def _collapse_table_root(current, dsn, pc):
    """
    Create a table with items in root given the current time series entry
    :param dict current: Current time series entry
    :param str dsn: Dataset name
    :param str pc: paleoData or chronData
    :return dict _tmp_table: Table data
    """
    logger_ts.info("enter collapse_table_root")
    _table_name, _variable_name = _get_current_names(current, dsn, pc)
    _tmp_table = {'columns': {}}

    try:
        for k, v in current.items():
            # These are the main table keys that we should be looking for
            for i in ['filename', 'googleWorkSheetKey', 'tableName', "missingValue", "tableMD5", "dataMD5"]:
                if i in k:
                    try:
                        _tmp_table[i] = v
                    except Exception:
                        # Not all keys are available. It's okay if we hit a KeyError.
                        pass
    except Exception as e:
        print("Error: Unable to collapse: {}, {}".format(dsn, e))
        logger_ts.error("collapse_table_root: Unable to collapse: {}, {}, {}".format(_table_name, dsn, e))

    return _tmp_table


def _collapse_column(current, pc):
    """
    Collapse the column data and
    :param current:
    :param pc:
    :return:
    """
    _tmp_column = {}
    _tmp_interp = {}
    _tmp_calib = {}
    try:
        for k, v in current.items():
            try:
                # We do not want to store these table keys at the column level.
                if not any(i in k for i in ["tableName", "google", "filename", "md5", "MD5"]):
                    # ['paleoData', 'key']
                    m = k.split('_')
                    # Is this a chronData or paleoData key?
                    if pc in m[0] and len(m) >= 2:
                        # Use the key after the underscore and add the data to the column
                        _tmp_column[m[1]] = v
                    elif 'calibration' in m[0]:
                        _tmp_calib[m[1]] = v
                    elif 'interpretation' in m[0]:
                        _tmp_interp[m[1]] = v
            except Exception as e:
                logger_ts.error("collapse_column: loop: {}".format(e))
    except Exception as e:
        logger_ts.error("collapse_column: {}".format(e))

    # Add the interpretation and calibration data
    if _tmp_interp:
        _tmp_column['interpretation'] = _tmp_interp
    if _tmp_calib:
        _tmp_column['calibration'] = _tmp_calib
    return _tmp_column


# HELPERS


def mode_ts(ec, mode="", ts=None):
    """
    Get string for the mode
    :param str ec: extract or collapse
    :param str mode: "paleo" or "chron" mode
    :param list ts: Time series (for collapse)
    :return str phrase: Phrase
    """
    phrase = ""
    if ec == "extract":
        if mode=="chron":
            phrase = "extracting chronData..."
        else:
            phrase = "extracting paleoData..."
    elif ec == "collapse":
        if ts[0]["mode"] == "chronData":
            phrase = "collapsing chronData"
        else:
            phrase = "collapsing paleoData..."
    return phrase


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
            if tmp[1] in COMPARISONS:
                tmp[1] = COMPARISONS[tmp[1]]
            tmp[0] = cast_float(tmp[0])
            tmp[2] = cast_float(tmp[2])
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
    :param list ts: TimeSeries
    :return list new_ts: Matched time series objects
    :return list idxs: Indices of matched objects
    """
    logger_ts.info("enter get_matches")
    new_ts = []
    idxs = []
    match = False
    try:
        for idx, ts_data in enumerate(ts):
            for expr in expr_lst:
                try:
                    val = ts_data[expr[0]]
                    # Check what comparison operator is being used
                    if expr[1] == 'in':
                        # "IN" operator can't be used in get_truth. Handle first.
                        if expr[2] in val:
                            match = True
                    elif match_operators(val, expr[1], expr[2]):
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
                idxs.append(idx)
                new_ts.append(ts_data)
    except AttributeError as e:
        logger_ts.debug("get_matches: AttributeError: unable to get expression matches, {},  {}".format(type(ts), e))
        print("Error: Timeseries is an invalid data type")
    if not new_ts:
        print("No matches found for that expression")
    else:
        print("Found {} matches".format(len(new_ts)))
    logger_ts.info("exit get_matches")
    return new_ts, idxs
