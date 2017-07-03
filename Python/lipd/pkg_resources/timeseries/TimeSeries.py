import copy

# from ..helpers.google import get_google_csv
# from ..helpers.directory import check_file_age
from ..helpers.regexes import re_pandas_x_und, re_fund_valid, re_pub_valid
from ..helpers.blanks import EMPTY
from ..helpers.loggers import create_logger

logger_timeseries = create_logger('time_series')


############################## EXTRACT

def extract(d, chron):
    """
    LiPD Version 1.3
    Main function to initiate LiPD to TSOs conversion.
    :param dict d: Metadata for one LiPD file
    :param bool chron: Paleo mode (default) or Chron mode
    :return list _ts: Time series
    """
    logger_timeseries.info("enter extract_main")
    _root = {}
    _ts = {}
    _switch = {"paleoData": "chronData", "chronData": "paleoData"}
    _pc = "paleoData"
    if chron:
        _pc = "chronData"
    try:
        # Build the root level data.
        # This will serve as the template for which column data will be added onto later.
        for k, v in d.items():
            if isinstance(v, str):
                _root[k] = v
            elif k == "funding":
                _root = _extract_fund(v, _root)
            elif k == "geo":
                _root = _extract_geo(v, _root)
            elif k == 'pub':
                _root = _extract_pub(v, _root)
            elif k == _switch[_pc]:
                # Whatever mode we're in, store the opposite raw data.
                # e.g. If we're making a paleo time series, store the raw chronData
                _root[_switch[_pc]] = copy.deepcopy(v)

        # Create tso dictionaries for each individual column (build on root data)
        _ts = _extract_pc(d, _root, _pc)
    except Exception as e:
        logger_timeseries.error("extract: Exception: {}".format(e))
        print("extract: Exception: {}".format(e))

    logger_timeseries.info("exit extract_main")
    return _ts


def _extract_fund(l, _root):
    """
    Creates flat funding dictionary.
    :param list l: Funding entries
    """
    logger_timeseries.info("enter _extract_funding")
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
    logger_timeseries.info("enter ts_extract_geo")
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
                    logger_timeseries.warn("_extract_geo: IndexError: idx: {}, val: {}, {}".format(idx, p, e))
        # Case 2: Any value that is a string can be added as-is
        elif isinstance(v, str):
            if k == 'meanElev':
                try:
                    # Some data sets have meanElev listed under properties for some reason.
                    _root['geo_' + k] = float(v)
                except ValueError as e:
                    # If the value is a string, then we don't want it
                    logger_timeseries.warn("_extract_geo: ValueError: meanElev is a string: {}, {}".format(v, e))
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
    logger_timeseries.info("enter _extract_pub")
    # For each publication entry
    for idx, pub in enumerate(l):
        logger_timeseries.info("processing publication #: {}".format(idx))
        # Get author data first, since that's the most ambiguously structured data.
        _root = _extract_authors(pub, idx, _root)
        # Go through data of this publication
        for k, v in pub.items():
            # Case 1: DOI ID. Don't need the rest of 'identifier' dict
            if k == 'identifier':
                try:
                    _root['pub' + str(idx + 1) + '_DOI'] = v[0]['id']
                except KeyError as e:
                    logger_timeseries.warn("_extract_pub: KeyError: no doi id: {}, {}".format(v, e))
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
    logger_timeseries.info("enter _extract_authors")
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
            logger_timeseries.warn("_extract_authors: KeyError: could not find author data, {}".format(e))

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


def _extract_pc(d, root, pc):
    """
    Extract all data from a PaleoData dictionary.
    :param dict d: PaleoData dictionary
    :param dict root: Time series root data
    :param str pc: paleoData or chronData
    :param list _ts: Time series
    """
    logger_timeseries.info("enter extract_pc")
    _ts = []
    try:
        # For each table in pc
        for k, v in d[pc].items():
            for _table_name, _table_data in v["measurementTable"].items():
                _tmp_root = copy.deepcopy(root)
                _ts = _extract_table(_table_data, _tmp_root, pc, _ts)
            if "model" in v:
                _tmp_root = copy.deepcopy(root)
                for _entry in v["model"]:
                    if "summaryTable" in _entry:
                        # todo this needs to be switched over once "summaryTable" becomes a list of multiples
                        _ts = _extract_table(_entry["summaryTable"], _tmp_root, pc, _ts)
                        # for _table_name, _table_data in _entry["summaryTable"].items():
                        #     _ts = _extract_table(_table_data, _table_tmp, pc, _ts)
    except KeyError as e:
        logger_timeseries.warn("extract_pc: KeyError: paleoData/columns not found, {}".format(e))

    return _ts


def _extract_special(table_data, current):
    """
    Extract year, age, and depth column from table data
    :param dict table_data: Data at the table level
    :param dict current: Current data
    :return dict current:
    """
    logger_timeseries.info("enter extract_special")
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
                    logger_timeseries.warn("extract_special: KeyError: 'values' not found, {}".format(e))
                try:
                    current[s + 'Units'] = v['units']
                except KeyError as e:
                    # Values key was not found.
                    logger_timeseries.warn("extract_special: KeyError: 'units' not found, {}".format(e))

    except KeyError as ke:
        logger_timeseries.error("extract_special: KeyError: didn't find 'columns', {}",format(ke))
    except AttributeError as ae:
        logger_timeseries.error(
            "extract_special: AttributeError: 'columns' is not a dictionary, {}".format(ae))
    except Exception as e:
        logger_timeseries.error("extract_special: Exception: {}".format(e))

    return current


def _extract_table_root(d, current, pc):
    """
    Extract data from the root level of a paleoData table.
    :param dict d: paleoData table
    :param dict current: Current data
    :param str pc: paleoData or chronData
    :return dict current:
    """
    logger_timeseries.info("enter extract_table_root")
    for k, v in d.items():
        if isinstance(v, str):
            current[pc + '_' + k] = v
    return current


def _extract_table(table_data, tmp_root, pc, ts):
    """
    Use the given table data to create a time series entry for each column in the table.
    :param dict table_data: Table data
    :param dict tmp_root: LiPD root data
    :param str pc: paleoData or chronData
    :param list ts: Time series (so far)
    :return list ts: Time series (so far)
    """
    # Get root items for this table
    # todo create fields for the table name and table index in the ts entry.
    _table_tmp = _extract_table_root(table_data, tmp_root, pc)
    # Add age, depth, and year columns to root if available
    _table_tmp = _extract_special(tmp_root, _table_tmp)
    # Start creating entries using dictionary copies.
    for i, e in table_data["columns"].items():
        # Add column data onto root items. Copy so we don't ruin original data
        col = _extract_columns(e, copy.deepcopy(_table_tmp), pc)
        try:
            ts.append(col)
        except Exception as e:
            logger_timeseries.warn("extract_table: Exception: Unable to create ts entry, {}".format(e))
    return ts


def _extract_columns(d, tmp_tso, pc):
    """
    Extract data from one paleoData column
    :param dict d: Column dictionary
    :param dict tmp_tso: TSO dictionary with only root items
    :return dict: Finished TSO
    """
    logger_timeseries.info("enter extract_columns")
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
    logger_timeseries.info("enter extract_calibration")
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
    logger_timeseries.info("enter extract_climate")
    for k, v in d.items():
        tmp_tso['climateInterpretation_' + k] = v
    return tmp_tso


############################################## COLLAPSE


def collapse(l):
    """
    LiPD Version 1.2
    Main function to initiate TimeSeries to LiPD conversion
    :param list l: Time series
    :return dict _master: LiPD data, sorted by dataset name
    """
    logger_timeseries.info("enter collapse")
    # LiPD data (in progress) by dataset name
    _master = {}
    # Current time series entry
    _current= {}

    # Receive list of TSO objects
    for entry in l:
        # Get notable keys
        dsn = entry['dataSetName']
        logger_timeseries.info("processing: {}".format(dsn))
        _current = entry

        # Since root items are the same in each column of the same dataset, we only need these steps the first time.
        if dsn not in _master:
            _master, _current = _collapse_root(_master, _current, dsn)

        # Collapse paleoData, calibration, and climate interpretation
        _master = _collapse_paleo(_master, _current, dsn)

    logger_timeseries.info("exit collapse")
    return _master


def _get_current(current, dsn):
    """
    Get the table name and variable name from the given time series entry
    :param dict current: Time series entry
    :return str _table_name:
    :return str _variable_name:
    """
    logger_timeseries.info("enter get_current")
    _table_name = ""
    _variable_name = ""
    # Get key info
    try:
        _table_name = current['paleoData_paleoDataTableName']
        _variable_name = current['paleoData_variableName']
    except KeyError as ke:
        print("Error: time series entry is missing a required key: {}, {}".format(dsn, ke))
        logger_timeseries.error("get_current: KeyError: pd table/variable name not found, {}".format(ke))
    except Exception as e:
        print("Error: Unable to collapse time series: {}, {}".format(dsn, e))
        logger_timeseries.error("get_current: Exception: {}, {}".format(dsn, e))
    return _table_name, _variable_name


def _collapse_root(master, current, dsn):
    """
    Collapse the root items of the current time series entry
    :param dict master: LiPD data (so far)
    :param dict current: Current time series entry
    :param str dsn: Dataset name
    :return dict master:
    :return dict current:
    """
    logger_timeseries.info("enter collapse_root")
    _tmp_fund = {}
    _tmp_pub = {}
    _tmp_master = {'pub': [], 'geo': {'geometry': {'coordinates': []}, 'properties': {}}, 'funding': [],
                  'paleoData': {}}
    p_keys = ['siteName', 'pages2kRegion']
    c_keys = ['meanLat', 'meanLon', 'meanElev']
    c_vals = [0, 0, 0]

    for k, v in current.items():
        if 'paleoData' not in k and 'calibration' not in k and \
                        'climateInterpretation' not in k and "chronData" not in k:
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

            elif 'geo' in k:
                key = k.split('_')
                # Coordinates - [LON, LAT, ELEV]
                if key[1] in c_keys:
                    if key[1] == 'meanLon':
                        c_vals[0] = v
                    elif key[1] == 'meanLat':
                        c_vals[1] = v
                    elif key[1] == 'meanElev':
                        c_vals[2] = v
                # Properties
                elif key[1] in p_keys:
                    _tmp_master['geo']['properties'][key[1]] = v
                # All others
                else:
                    _tmp_master['geo'][key[1]] = v

            elif 'pub' in k:
                # Group pub items in tmp_pub by number
                m = re_pub_valid.match(k)
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
            else:
                # Root
                _tmp_master[k] = v

    # Append pub and funding to master
    for k, v in _tmp_pub.items():
        _tmp_master['pub'].append(v)
    for k, v in _tmp_fund.items():
        _tmp_master['funding'].append(v)
    # Get rid of elevation coordinate if one was never added.
    if c_vals[2] == 0:
        del c_vals[2]
    _tmp_master['geo']['geometry']['coordinates'] = c_vals

    # If we're getting root info, then there shouldn't be a dataset entry yet.
    # Create entry in object master, and set our new data to it.
    master[dsn] = _tmp_master
    logger_timeseries.info("exit collapse_root")
    return master, current


def _collapse_author(s):
    """
    Split author string back into organized dictionary
    :param str s: Formatted names string "Last, F.; Last, F.; etc.."
    :return list of dict: One dictionary per author name
    """
    logger_timeseries.info("enter collapse_author")
    l = []
    authors = s.split(';')
    for author in authors:
        l.append({'name': author})
    return l


def _collapse_paleo(master, current, dsn):
    """
    Collapse the paleoData for the current time series entry
    :param dict master: LiPD data (so far)
    :param dict current: Current time series entry
    :param str dsn: Dataset name
    :return dict master:
    """
    logger_timeseries.info("enter collapse_paleo")
    _table_name, _variable_name = _get_current(current, dsn)
    tmp_clim = {}
    tmp_cal = {}
    master, current = _collapse_paleo_root(master, current, dsn)
    try:
        # Create the column entry in the table
        master[dsn]['paleoData'][_table_name]['columns'][_variable_name] = {}
        # Start inserting paleoData into the table at self.lipd_master[table][column]
        for k, v in current.items():
            # ['paleoData', 'key']
            m = k.split('_')
            if 'paleoData' in m[0]:
                master[dsn]['paleoData'][_table_name]['columns'][_variable_name][m[1]] = v
            elif 'calibration' in m[0]:
                tmp_cal[m[1]] = v
            elif 'climateInterpretation' in m[0]:
                tmp_clim[m[1]] = v
    except KeyError as ke:
        print("Error: Unable to collapse column data: {}, {}, {}".format(dsn, _variable_name, ke))
        logger_timeseries.warn("collapse_paleo: KeyError: {}, {}, {}".format(dsn, _variable_name, ke))
    except Exception as e:
        print("Error: Unable to collapse column data: {}, {}".format(dsn, e))
        logger_timeseries.error("collapse_paleo: Exception: {}, {}, {}".format(dsn, _variable_name, e))

    # If these sections had any items added to them, then add them to the column master.
    if tmp_clim:
        master[dsn]['paleoData'][_table_name]['columns'][_variable_name]['climateInterpretation'] = tmp_clim
    if tmp_cal:
        master[dsn]['paleoData'][_table_name]['columns'][_variable_name]['calibration'] = tmp_cal
    return master


def _collapse_paleo_root(master, current, dsn):
    """
    Create paleo table in master if it doesn't exist. Insert table root items
    """
    logger_timeseries.info("enter collapse_paleo_root")
    _table_name, _variable_name = _get_current(current, dsn)

    try:
        # If table doesn't exist yet, create it.
        if _table_name not in master[dsn]['paleoData']:
            t_root_keys = ['filename', 'googleWorkSheetKey', 'paleoDataTableName']
            master[dsn]['paleoData'][_table_name] = {'columns': {}}
            for key in t_root_keys:
                try:
                    # Now set the root table items in our new table
                    master[dsn]['paleoData'][_table_name][key] = current['paleoData_' + key]
                except KeyError as e:
                    # That's okay. Keep trying :)
                    logger_timeseries.warn("lipd_extract_paleo_root: KeyError: {} not found in master, {}".format(key, e))
    except KeyError as ke:
        print("Error: Missing a paleoData root key: {}, {}".format(dsn, ke))
        logger_timeseries.error("collapse_paleo_root: KeyError: missing paleoData {}, {}, {}".format(_table_name, dsn, ke))
    except Exception as e:
        print("Error: Unable to collapse: {}, {}".format(dsn, e))
        logger_timeseries.error("collapse_paleo_root: Exception: Unable to collapse: {}, {}, {}".format(_table_name, dsn, e))

    return master, current
