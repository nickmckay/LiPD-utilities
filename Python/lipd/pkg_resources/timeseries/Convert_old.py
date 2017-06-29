import copy as cp
from copy import deepcopy
import csv
import pandas as pd

from ..helpers.google import get_google_csv
from ..helpers.directory import check_file_age
from ..helpers.regexes import *
from ..helpers.blanks import *
from ..helpers.loggers import create_logger

logger_convert = create_logger('Convert')


class Convert(object):
    """
    LiPD to TIME SERIES
    TIME SERIES to LiPD
    """

    def __init__(self):

        # LiPD to TS (One file at a time)
        self.ts_root = {}  # Root metadata for current LiPD.
        self.ts_tsos = []  # Individual columns. One entry represents one TSO (to be created later)

        # TS to LiPD (Batch Process)
        self.lipd_tsos = []  # One entry for each TSO metadata dictionary
        self.lipd_master = {}  # Key: LiPD name, Value: Complete metadata dictionary (when finished)
        self.lipd_curr_tso_data = {}  # Holds metadata for current TSO being processed
        self.dataset_ext = ''  # Filename.lpd. This is what the output name will be.
        self.table = ''
        self.variableName = ''

        # TS Names validation
        self.full_list = {"root": [], "pub": [], "climateInterpretation": [], "calibration": [], "geo": [],
                          "paleoData": []}
        # full_list - All valid TS Names and synonyms. { 'category' : [ ['validTSName', 'synonym'], ... ] }
        self.quick_list = []  # All valid TS Name keys
        self.recent = {}  # Recently corrected TS names, builds with each run.

    # LiPD TO TIME SERIES

    def ts_extract_main(self, d, dfs):
        """
        LiPD Version 1.2
        Main function to initiate LiPD to TSOs conversion.
        :param dict d: Metadata for one LiPD file
        :param dict dfs: Chron data frame(s)
        """
        logger_convert.info("enter ts_extract_main")
        # Reset these each run
        self.ts_root = {}
        self.ts_tsos = []

        # Build the root level data.
        # This will serve as the template for which column data will be added onto later.
        for k, v in d.items():
            if isinstance(v, str):
                self.ts_root[k] = v
            elif k == "funding":
                self.__ts_extract_funding(v)
            elif k == "geo":
                self.__ts_extract_geo(v)
            elif k == 'pub':
                self.__ts_extract_pub(v)
            elif k == 'chronData':
                self.ts_root[k] = cp.deepcopy(v)

        # Include the chronology data frame in each time series object
        self.ts_root["chronData_df"] = dfs

        # Create tso dictionaries for each individual column (build on root data)
        self.__ts_extract_paleo(d)

        # Get TSNames and verify against TSOs in ts_tsos
        # self.__fetch_tsnames()
        # self.__verify_tsnames()
        logger_convert.info("exit ts_extract_main")
        return self.ts_tsos

    def __ts_extract_funding(self, l):
        """
        Creates flat funding dictionary.
        :param list l: Funding entries
        """
        logger_convert.info("enter ts_extract_funding")
        for idx, i in enumerate(l):
            for k, v in i.items():
                self.ts_root['funding' + str(idx+1) + '_' + k] = v
        return

    def __ts_extract_geo(self, d):
        """
        Extract geo data from input
        :param dict d: Geo
        """
        logger_convert.info("enter ts_extract_geo")
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
                                    self.ts_root[x[idx]] = 0
                            else:
                                # Set the value as a float into its entry.
                                self.ts_root[x[idx]] = float(p)
                        # Value is a normal number, or string representation of a number
                        else:
                            # Set the value as a float into its entry.
                            self.ts_root[x[idx]] = float(p)
                    except IndexError as e:
                        logger_convert.warn("ts_extract_geo: IndexError: idx: {}, val: {}, {}".format(idx, p, e))
            # Case 2: Any value that is a string can be added as-is
            elif isinstance(v, str):
                if k == 'meanElev':
                    try:
                        # Some data sets have meanElev listed under properties for some reason.
                        self.ts_root['geo_' + k] = float(v)
                    except ValueError as e:
                        # If the value is a string, then we don't want it
                        logger_convert.warn("ts_extract_geo: ValueError: meanElev is a string: {}, {}".format(v, e))
                else:
                    self.ts_root['geo_' + k] = v
            # Case 3: Nested dictionary. Recursion
            elif isinstance(v, dict):
                self.__ts_extract_geo(v)
        return

    def __ts_extract_pub(self, l):
        """
        Extract publication data from one or more publication entries.
        :param list l: Publication
        """
        logger_convert.info("enter ts_extract")
        # For each publication entry
        for idx, pub in enumerate(l):
            logger_convert.info("processing publication #: {}".format(idx))
            # Get author data first, since that's the most ambiguously structured data.
            self.__ts_extract_authors(pub, idx)
            # Go through data of this publication
            for k, v in pub.items():
                # Case 1: DOI ID. Don't need the rest of 'identifier' dict
                if k == 'identifier':
                    try:
                        self.ts_root['pub' + str(idx+1) + '_DOI'] = v[0]['id']
                    except KeyError as e:
                        logger_convert.warn("ts_extract_pub: KeyError: no doi id: {}, {}".format(v, e))
                # Case 2: All other string entries
                else:
                    if k != 'authors' and k != 'author':
                        self.ts_root['pub' + str(idx+1) + '_' + k] = v
        return

    def __ts_extract_authors(self, pub, idx):
        """
        Create a concatenated string of author names. Separate names with semi-colons.
        :param any pub: Publication author structure is ambiguous
        :param int idx: Index number of Pub
        """
        logger_convert.info("enter ts_extract_authors")
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
                logger_convert.warn("ts_extract_authors: KeyError: could not find author data, {}".format(e))

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
            self.ts_root['pub' + str(idx+1) + '_author'] = auth[:-1]
        return

    def __ts_extract_paleo(self, d):
        """
        LiPD Version 1.2
        Extract all data from a PaleoData dictionary.
        :param dict d: PaleoData dictionary
        """
        logger_convert.info("enter ts_extract_paleo")
        try:
            # For each table in paleoData
            for k, v in d['paleoData'].items():
                # Get root items for this table
                self.__ts_extract_paleo_table_root(v["paleoMeasurementTable"])
                for table_name, table_data in v["paleoMeasurementTable"].items():
                    # Add age, depth, and year columns to ts_root if available
                    self.__ts_extract_special(table_data)
                    # Start creating TSOs with dictionary copies.
                    for i, e in table_data["columns"].items():
                        # if not any(x in i for x in ('age', 'depth', 'year')):
                        #     # TSO. Add this column onto root items. Deepcopy since we need to reuse ts_root
                        #     col = self.__ts_extract_paleo_columns(e, deepcopy(self.ts_root))
                        #     try:
                        #         self.ts_tsos.append(col)
                        #     except Exception as e:
                        #         logger_convert.warn("ts_extract_paleo: KeyError: unable to append TSO, {}".format(e))

                        # TSO. Add this column onto root items. Deepcopy since we need to reuse ts_root
                        col = self.__ts_extract_paleo_columns(e, deepcopy(self.ts_root))
                        try:
                            self.ts_tsos.append(col)
                        except Exception as e:
                            logger_convert.warn("ts_extract_paleo: KeyError: unable to append TSO, {}".format(e))

        except KeyError as e:
            logger_convert.warn("ts_Extract_paleo: KeyError: paleoData/columns not found, {}".format(e))
        return

    def __ts_extract_special(self, table_data):
        """
        Extract year, age, and depth column. Add to self.ts_root
        :param dict table_data: Data at the table level
        :return none: Results set to object self
        """
        logger_convert.info("enter ts_extract_special")
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
                        self.ts_root[s] = v['values']
                    except KeyError as e:
                        # Values key was not found.
                        logger_convert.warn("ts_extract_special: KeyError: 'values' not found, {}".format(e))
                    try:
                        self.ts_root[s + 'Units'] = v['units']
                    except KeyError as e:
                        # Values key was not found.
                        logger_convert.warn("ts_extract_special: KeyError: 'units' not found, {}".format(e))

        except KeyError:
            logger_convert.debug("Convert: ts_extract_special: KeyError: didn't find 'columns'. Possible bad structure")
        except AttributeError:
            logger_convert.debug("Convert: ts_extract_special: AttributeError: 'columns' is not a dictionary. Possible bad structure")

        return

    def __ts_extract_paleo_table_root(self, d):
        """
        Extract data from the root level of a paleoData table.
        :param dict d: One paleoData table
        :return none: Results set to object self
        """
        logger_convert.info("enter ts_extract_paleo_table_root")
        for k, v in d.items():
            if isinstance(v, str):
                self.ts_root['paleoData_' + k] = v
        return

    def __ts_extract_paleo_columns(self, d, tmp_tso):
        """
        Extract data from one paleoData column
        :param dict d: Column dictionary
        :param dict tmp_tso: TSO dictionary with only root items
        :return dict: Finished TSO
        """
        logger_convert.info("enter ts_extract_paleo_columns")
        for k, v in d.items():
            if k == 'climateInterpretation':
                tmp_tso = self.__ts_extract_climate(v, tmp_tso)
            elif k == 'calibration':
                tmp_tso = self.__ts_extract_calibration(v, tmp_tso)
            else:
                # Assume if it's not a special nested case, then it's a string value
                tmp_tso['paleoData_' + k] = v
        return tmp_tso

    @staticmethod
    def __ts_extract_calibration(d, tmp_tso):
        """
        Get calibration info from column data.
        :param dict d: Calibration dictionary
        :param dict tmp_tso: Temp TSO dictionary
        :return dict: tmp_tso with added calibration entries
        """
        logger_convert.info("enter ts_extract_calibration")
        for k, v in d.items():
            tmp_tso['calibration_' + k] = v
        return tmp_tso

    @staticmethod
    def __ts_extract_climate(d, tmp_tso):
        """
        Get climate interpretation from column data.
        :param dict d: Climate Interpretation dictionary
        :param dict tmp_tso: Temp TSO dictionary
        :return dict: tmp_tso with added climateInterpretation entries
        """
        logger_convert.info("enter ts_extract_climate")
        for k, v in d.items():
            tmp_tso['climateInterpretation_' + k] = v
        return tmp_tso

    # TIME SERIES to LiPD


# todo NEEDS COMPLETE OVERHAUL now that TSOs are not named
# todo Need a way to completely restore age/year/depth columns without losing any original column info
    def lipd_extract_main(self, lipd_tsos):
        """
        Main function to initiate TimeSeries to LiPD conversion
        :param list of dict lipd_tsos: List of all TSOs
        :return:
        """
        logger_convert.info("enter lipd_extract_main")
        # Reset for each run
        self.lipd_tsos = lipd_tsos  # All TSO metadata dictionaries
        self.lipd_master = {}  # All lipds (in progress) by dataset name. Key: LiPD name, Val: JSON metadata
        self.lipd_curr_tso_data = {}  # Current TSO metadata

        # Receive list of TSO objects
        for tso in self.lipd_tsos:
            # Set current keys
            self.dataset_ext = tso['name']
            logger_convert.info("processing tso: {}".format(self.dataset_ext))
            self.lipd_curr_tso_data = tso['data']
            self.__lipd_set_current()

            # Since root items are the same in the same dataset, we only need these steps if dataset doesn't exist yet.
            if self.dataset_ext not in self.lipd_master:
                self.__lipd_extract_roots()

            # Extract PaleoData, Calibration, and Climate Interpretation
            self.__lipd_extract_paleo()
        logger_convert.info("exit lipd_extract_main")
        return self.lipd_master

    def __lipd_set_current(self):
        """
        Set keys for current TSO file
        """
        logger_convert.info("enter lipd_set_current")
        # Get key info
        try:
            self.table = self.lipd_curr_tso_data['paleoData_paleoDataTableName']
            self.variableName = self.lipd_curr_tso_data['paleoData_variableName']
        except KeyError as e:
            print("Error: failed to convert {}".format(self.dataset_ext))
            logger_convert.warn("lipd_set_current: KeyError: pd table/variable name not found, {}".format(e))
        return

    def __lipd_extract_roots(self):
        """
        Extract root from TimeSeries
        """
        logger_convert.info("enter lipd_extract_roots")
        tmp_funding = {}
        tmp_pub = {}
        tmp_master = {'pub': [], 'geo': {'geometry': {'coordinates': []}, 'properties': {}}, 'funding': [],
                      'paleoData': {}}
        p_keys = ['siteName', 'pages2kRegion']
        c_keys = ['meanLat', 'meanLon', 'meanElev']
        c_vals = [0, 0, 0]

        for k, v in self.lipd_curr_tso_data.items():
            if 'paleoData' not in k and 'calibration' not in k and 'climateInterpretation' not in k:
                if 'funding' in k:
                    # Group funding items in tmp_funding by number
                    m = re_fund_valid.match(k)
                    try:
                        tmp_funding[m.group(1)][m.group(2)] = v
                    except KeyError:
                        tmp_funding[m.group(1)] = {}
                        tmp_funding[m.group(1)][m.group(2)] = v

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
                        tmp_master['geo']['properties'][key[1]] = v
                    # All others
                    else:
                        tmp_master['geo'][key[1]] = v

                elif 'pub' in k:
                    # Group pub items in tmp_pub by number
                    m = re_pub_valid.match(k)
                    number = int(m.group(1)) - 1  # 0 indexed behind the scenes, 1 indexed to user.
                    key = m.group(2)
                    # Authors ("Pu, Y.; Nace, T.; etc..")
                    if key == 'author' or key == 'authors':
                        try:
                            tmp_pub[number]['author'] = self.__lipd_extract_author(v)
                        except KeyError as e:
                            # Dictionary not created yet. Assign one first.
                            tmp_pub[number] = {}
                            tmp_pub[number]['author'] = self.__lipd_extract_author(v)
                    # DOI ID
                    elif key == 'DOI':
                        try:
                            tmp_pub[number]['identifier'] = [{"id": v, "type": "doi", "url": "http://dx.doi.org/" + str(v)}]
                        except KeyError:
                            # Dictionary not created yet. Assign one first.
                            tmp_pub[number] = {}
                            tmp_pub[number]['identifier'] = [{"id": v, "type": "doi", "url": "http://dx.doi.org/" + str(v)}]
                    # All others
                    else:
                        try:
                            tmp_pub[number][key] = v
                        except KeyError:
                            # Dictionary not created yet. Assign one first.
                            tmp_pub[number] = {}
                            tmp_pub[number][key] = v
                else:
                    # Root
                    tmp_master[k] = v

        # Append pub and funding to master
        for k, v in tmp_pub.items():
            tmp_master['pub'].append(v)
        for k, v in tmp_funding.items():
            tmp_master['funding'].append(v)
        # Get rid of elevation coordinate if one was never added.
        if c_vals[2] == 0:
            del c_vals[2]
        tmp_master['geo']['geometry']['coordinates'] = c_vals

        # If we're getting root info, then there shouldn't be a dataset entry yet.
        # Create entry in object master, and set our new data to it.
        self.lipd_master[self.dataset_ext] = {}
        self.lipd_master[self.dataset_ext] = tmp_master
        logger_convert.info("exit lipd_extract_roots")
        return

    @staticmethod
    def __lipd_extract_author(s):
        """
        Split author string back into organized dictionary
        :param str s: Formatted names string "Last, F.; Last, F.; etc.."
        :return list of dict: One dictionary per author name
        """
        logger_convert.info("enter lipd_extract_author")
        l = []
        authors = s.split(';')
        for author in authors:
            l.append({'name': author})
        return l

    def __lipd_extract_paleo_root(self):
        """
        Create paleo table in master if it doesn't exist. Insert table root items
        """
        logger_convert.info("enter lipd_extract_paleo_root")
        try:
            # If table doesn't exist yet, create it.
            if self.table not in self.lipd_master[self.dataset_ext]['paleoData']:
                t_root_keys = ['filename', 'googleWorkSheetKey', 'paleoDataTableName']
                self.lipd_master[self.dataset_ext]['paleoData'][self.table] = {'columns': {}}
                for key in t_root_keys:
                    try:
                        # Now set the root table items in our new table
                        self.lipd_master[self.dataset_ext]['paleoData'][self.table][key] = self.lipd_curr_tso_data['paleoData_' + key]
                    except KeyError as e:
                        # That's okay. Keep trying :)
                        logger_convert.warn("lipd_extract_paleo_root: KeyError: {} not found in master, {}".format(key, e))
        except KeyError as e:
            print("Error: missing paleoData key: {}".format(self.dataset_ext))
            logger_convert.warn("lipd_extract_paleo_root: KeyError: missing paleoData/{} in {}, {}".format(self.table, self.dataset_ext, e))
        return

    def __lipd_extract_paleo(self):
        """
        Extract paleoData from tso
        :return: LiPD entry in self.lipd_master is updated
        """
        logger_convert.info("enter lipd_extract_paleo")
        tmp_clim = {}
        tmp_cal = {}
        self.__lipd_extract_paleo_root()
        try:
            # Create the column entry in the table
            self.lipd_master[self.dataset_ext]['paleoData'][self.table]['columns'][self.variableName] = {}
            # Start inserting paleoData into the table at self.lipd_master[table][column]
            for k, v in self.lipd_curr_tso_data.items():
                # ['paleoData', 'key']
                m = k.split('_')
                if 'paleoData' in m[0]:
                    self.lipd_master[self.dataset_ext]['paleoData'][self.table]['columns'][self.variableName][m[1]] = v
                elif 'calibration' in m[0]:
                    tmp_cal[m[1]] = v
                elif 'climateInterpretation' in m[0]:
                    tmp_clim[m[1]] = v
        except KeyError as e:
            print("Error: Unable to extract column data from {}, {}".format(self.dataset_ext, self.variableName))
            logger_convert.warn("lipd_extract_paleo: KeyError: {}, {}".format(self.dataset_ext, self.variableName))

        # If these sections had any items added to them, then add them to the column master.
        if tmp_clim:
            self.lipd_master[self.dataset_ext]['paleoData'][self.table]['columns'][self.variableName]['climateInterpretation'] = tmp_clim
        if tmp_cal:
            self.lipd_master[self.dataset_ext]['paleoData'][self.table]['columns'][self.variableName]['calibration'] = tmp_cal
        return

    # VALIDATING AND UPDATING TSNAMES

    def __fetch_tsnames(self):
        """
        Call down a current version of the TSNames spreadsheet from google. Convert to a structure better
        for comparisons.
        :return dict: K: Valid TSName, V: TSName synonyms
        :return list: List of valid TSnames
        """
        logger_convert.info("enter fetch_tsnames")
        # Check if it's been longer than one day since updating the TSNames.csv file.
        # If so, go fetch the file from google in case it's been updated since.
        # Or if file isn't found at all, download it also.
        if check_file_age('tsnames.csv', 1):
            # Fetch TSNames sheet from google
            logger_convert.info("fetching update for tsnames.csv")
            ts_id = '1C135kP-SRRGO331v9d8fqJfa3ydmkG2QQ5tiXEHj5us'
            get_google_csv(ts_id, 'tsnames.csv')
        try:
            # Start sorting the tsnames into an organized structure
            logger_convert.info("start sorting tsnames.csv")
            with open('tsnames.csv', 'r') as f:
                r = csv.reader(f, delimiter=',')
                for idx, line in enumerate(r):
                    # print('line[{}] = {}'.format(i, line))
                    if idx != 0:
                        # Do not record empty lines. Create list of non-empty entries.
                        line = [x for x in line if x]
                        # If line has content (i.e. not an empty line), then record it
                        if line:
                            # We don't need all the duplicates of pub and fund.
                            if "pub" in line[0] or "funding" in line[0]:
                                if re_pub_fetch.match(line[0]):
                                    self.quick_list.append(line[0])
                                    self.full_list['pub'].append(line)
                            elif re_misc_fetch.match(line[0]):
                                # Other Categories. Not special
                                self.quick_list.append(line[0])
                                cat, key = line[0].split('_')
                                self.full_list[cat].append(line)
                            else:
                                # Any of the root items
                                self.quick_list.append(line[0])
                                self.full_list["root"].append(line)
        except FileNotFoundError as e:
            print("Error: Unable to find TimeSeries lint file")
            logger_convert.debug("fetch_tsnames: FileNotFound: tsnames.csv, {}".format(e))

        return

    def __verify_tsnames(self):
        """
        Verify TSNames are current and valid. Compare to TSNames spreadsheet in Google Drive. Update where necessary.
        """
        logger_convert.info("enter verify_tsnames")
        # Temp to store incorrect keys
        bad_keys = []

        for tso in self.ts_tsos:
            # Build onto the "recent" dictionary so we have a list of keys to replace.
            for k, v in tso.items():
                # @context needs to be ignored
                if k not in self.quick_list and not re_pub_valid.match(k) and not re_fund_valid.match(k) and k != '@context':
                    # Invalid key. Store in temp for processing.
                    if k not in self.recent:
                        bad_keys.append(k)
            # Start to find replacements for empty entries in "recent"
            for incorrect in bad_keys:
                # Set incorrect name as key, and valid name as value.
                self.recent[incorrect] = self.__get_valid_tsname(incorrect)

            # Use temp to start replacing entries in d
            for invalid, valid in self.recent.items():
                try:
                    # Add new item, and remove old item in one step
                    tso[valid] = tso.pop(invalid)
                except KeyError as e:
                    logger_convert.debug("verify_tsnames: KeyError: add/drop: valid: {}, invalid: {}, {}".format(valid, invalid, e))
        return

    def __get_valid_tsname(self, invalid):
        """
        Turn a bad tsname into a valid one.
        * Note: Index[0] for each TSName is the most current, valid entry. Index[1:] are synonyms
        :param str invalid: Invalid tsname
        :return str: valid tsname
        """
        valid = ''
        invalid_l = invalid.lower()
        try:
            # PUB ENTRIES
            if re_pub_invalid.match(invalid_l):

                # Case 1: pub1_year (number and hyphen)
                if re_pub_nh.match(invalid_l):
                    s_invalid = invalid_l.split('_', 1)
                    # Check which list the key word is in
                    for line in self.full_list['pub']:
                        for key in line:
                            if s_invalid[1] in key.lower():
                                # Get the keyword from the valid entry.
                                v = line[0].split("_")
                                # Join our category with the valid keyword
                                valid = ''.join([s_invalid[0], '_', v[1]])

                # Case 2: pub_year (hyphen)
                elif re_pub_h.match(invalid_l):
                    s_invalid = invalid_l.split('_', 1)
                    # The missing pub number is the main problem, but the keyword may or may not be correct. Check.
                    for line in self.full_list['pub']:
                        for key in line:
                            if s_invalid[1] in key.lower():
                                # We're going to use the valid entry as-is, because that's what we need for this case.
                                valid = line[0]

                # Case 3: pub1year (number)
                elif re_pub_n.match(invalid_l):
                    s_invalid = re_pub_n.match(invalid_l)
                    for line in self.full_list['pub']:
                        for key in line:
                            if s_invalid.group(2) in key.lower():
                                v = line[0].split('_', 1)
                                valid = ''.join(['pub', s_invalid.group(0), v[1]])

                # Case 4: pubYear (camelcase)
                elif re_pub_cc.match(invalid_l):
                    valid = self.__iter_ts('pub', invalid_l)

            # FUNDING
            elif re_fund_invalid.match(invalid_l):
                if "grant" in invalid_l:
                    valid = 'funding1_grant'
                elif "agency" in invalid_l:
                    valid = "funding1_agency"

            # GEO
            elif re_geo_invalid.match(invalid_l):
                valid = self.__iter_ts('geo', invalid_l)

            # PALEODATA
            elif re_paleo_invalid.match(invalid_l):
                g1 = re_paleo_invalid.match(invalid_l).group(1)
                valid = self.__iter_ts('paleoData', g1)

            # CALIBRATION
            elif re_calib_invalid.match(invalid_l):
                g1 = re_calib_invalid.match(invalid_l).group(1)
                valid = self.__iter_ts('calibration', g1)

            # CLIMATE INTERPRETATION
            elif re_clim_invalid.match(invalid_l):
                g1 = re_clim_invalid.match(invalid_l).group(1)
                if 'climate' in g1:
                    g1 = re.sub('climate', '', g1)
                valid = self.__iter_ts('climateInterpretation', g1)

            else:
                # ROOT
                valid = self.__iter_ts('root', invalid_l)

            # Last chance
            # Specific case that isn't a typical format, or no match. Go through all possible entries.
            if not valid:
                valid = self.__iter_ts(None, invalid_l)

        except IndexError as e:
            logger_convert.debug("get_valid_tsname: IndexError: {}".format(e))

        if not valid:
            logger_convert.warn("get_valid_tsname: Unable to find match for term: {}".format(invalid))
            return invalid
        return valid

    def __iter_ts(self, category, invalid):
        """
        Match an invalid entry to one of the TSName synonyms.
        :param str category: Name of category being searched
        :param str invalid: Invalid tsname string
        :return str: Valid tsname
        """
        valid = ''

        # If a leading hyphen is in the string, get rid of it.
        if '_' == invalid[0]:
            invalid = invalid[1:]

        # If one specific category is passed through
        if category:
            for line in self.full_list[category]:
                for key in line:
                    if invalid in key.lower():
                        valid = line[0]
                        break
        # Entire TSNames dict is passed through (i.e. final effort, all categories have failed so far)
        else:
            for k, v in self.full_list.items():
                for line in v:
                    for key in line:
                        if invalid in key.lower():
                            valid = line[0]
                            break

        return valid
