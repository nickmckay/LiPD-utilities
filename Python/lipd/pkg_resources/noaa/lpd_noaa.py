import os
import shutil
from collections import defaultdict, OrderedDict

# NOAA SECTIONS is for writing keys in order, and for mapping keys to their proper sections
# NOAA KEYS is for converting keys from LPD to NOAA
from ..helpers.csvs import read_csv_from_file
from ..helpers.alternates import NOAA_KEYS_BY_SECTION, LIPD_NOAA_MAP_FLAT, LIPD_NOAA_MAP_BY_SECTION
from ..helpers.loggers import create_logger
from ..helpers.misc import clean_doi, generate_timestamp, get_authors_as_str

logger_lpd_noaa = create_logger("lpd_noaa")


class LPD_NOAA(object):
    """
    Creates a NOAA object that contains all the functions needed to write out a LiPD file as a NOAA text file.
    Supports
    LiPD Version: v1.2
    NOAA txt template: v3.0

    :return none: Writes NOAA text to file in local storage
    """

    def __init__(self, dir_root, name, lipd_dict, data_csv):
        """
        :param str dir_root: Path to dir containing all .lpd files
        :param str name: Name of current .lpd file
        :param dict root_dict: Full dict loaded from jsonld file
        """
        # Directory where this LiPD file was read from
        self.dir_root = dir_root
        # LiPD dataset name
        self.name = name
        # Dataset name with LiPD extension
        self.name_lpd = name + ".lpd"
        # Dataset name with TXT extension
        self.name_txt = name + '.txt'
        # List of filenames to write out. One .txt file per data table set.
        self.output_filenames = []
        # Amount of .txt files to be written
        self.output_file_ct = 0
        # The current .txt file writer object that is open.
        self.noaa_txt = None
        # Archive type for this dataset, used in multiple locations
        self.archive_type = ""
        # NOAA url, to landing page where this dataset will be stored on NOAA's servers
        self.noaa_url = "https://www1.ncdc.noaa.gov/pub/data/paleo/pages2k/pages2k-temperature-v2-2017/{}".format(self.name_txt)
        # List of all DOIs found in this dataset
        self.doi = []
        # Avoid writing identical pub citations. Store here as intermediate check.
        self.data_citation = {}
        # noaa dict has all metadata with noaa keys
        self.noaa_data = lipd_dict
        # the raw dictionary imported from jsonld file
        self.lipd_data = lipd_dict
        # jsonld data sorted according to noaa d sections
        self.noaa_data_sorted = {
            "Top": {},
            "Contribution_Date": {},
            "File_Last_Modified_Date": {},
            "Title": {},
            "Investigators": {},
            "Description_Notes_and_Keywords": {},
            "Publication": {},
            "Funding_Agency": {},
            "Site_Information": {},
            "Data_Collection": {},
            "Species": {},
            # these are sections, but i'm approaching them differently instead of storing them in the sorted data dict.
            # "Chronology_Information": {},
            # "Variables": {},
            # store all table PAIRS here. (chron + paleo @ same idx)
            "Data": [],
            # These are keys that do not currently have NOAA - LPD mappings
            "Ignore": {},
        }
        self.noaa_geo = {
        }
        # CSV data for this LiPD file. Taken from LiPD object.
        self.data_csv = data_csv
        # Paleo and Chron tables
        self.data_paleos = []
        self.data_chrons = []

    # MAIN

    def main(self):
        """
        Load in the template file, and run through the parser
        :return none:
        """
        logger_lpd_noaa.info("enter main")
        # Starting Directory: dir_tmp/dir_bag/data/

        # convert all lipd keys to noaa keys
        # timestamp the conversion of the file
        self.noaa_data_sorted["File_Last_Modified_Date"]["Modified_Date"] = generate_timestamp()

        # Get measurement tables from metadata, and sort into object self
        self.__put_tables_in_self(["paleo","paleoData", "paleoMeasurementTable"])
        self.__put_tables_in_self(["chron", "chronData", "chronMeasurementTable"])

        # how many measurement tables exist? this will tell use how many noaa files to create
        self.__get_table_pairs()

        # reorganize data into noaa sections
        self.__reorganize()

        # special case: earliest_year, most_recent_year, and time unit
        self.__check_time_unit()

        # Use data in steps_dict to write to
        # self.noaa_data_sorted = self.__key_conversion(self.noaa_data_sorted)
        self.__write_file()
        logger_lpd_noaa.info("exit main")
        return

    # MISC

    def get_wdc_paleo_url(self):
        """
        When a NOAA file is created, it creates a URL link to where the dataset will be hosted in NOAA's archive
        Retrieve and add this link to the original LiPD file, so we can trace the dataset to NOAA.
        :return str:
        """
        return self.noaa_url

    @staticmethod
    def __csv_found(filename):
        """
        Check for CSV file. Make sure it exists before we try to open it.
        :param str filename: Name of the file to open.
        :return none:
        """
        found = False
        # Current Directory
        # tmp/filename/data (access to jsonld, changelog, csv, etc
        try:
            # Attempt to open csv
            if open(filename):
                found = True
        except FileNotFoundError as e:
            logger_lpd_noaa.debug("csv_found: FileNotFound: no csv file, {}".format(e))
        return found

    @staticmethod
    def __split_path(string):
        """
        Used in the path_context function. Split the full path into a list of steps
        :param str string: Path string ("geo-elevation-height")
        :return list out: Path as a list of strings. One entry per path step.(["geo", "elevation", "height"])
        """
        out = []
        position = string.find(':')
        if position != -1:
            # A position of 0+ means that ":" was found in the string
            key = string[:position]
            val = string[position+1:]
            out.append(key)
            out.append(val)
            if ('-' in key) and ('Funding' not in key) and ('Grant' not in key):
                out = key.split('-')
                out.append(val)
        return out

    @staticmethod
    def __create_blanks(section_name, d):
        """
        All keys need to be written to the output, with or without a value. Furthermore, only keys that have values
        exist at this point. We need to manually insert the other keys with a blank value. Loop through the global list
        to see what's missing in our dict.
        :param str section_name: Retrieve data from global dict for this section
        :return none:
        """
        try:
            for key in NOAA_KEYS_BY_SECTION[section_name]:
                if key not in d:
                    # Key not in our dict. Create the blank entry.
                    d[key] = ""

        except Exception:
            logger_lpd_noaa.error("lpd_noaa: create_blanks: must section: {}, key".format(section_name, key))
        return d

    @staticmethod
    def __convert_keys_2(header, d):
        """
        Convert lpd to noaa keys for this one section
        :param str header: Section header
        :param dict d: Metadata
        :return dict:  Metadata w/ converted keys
        """
        d_out = {}
        try:
            for k, v in d.items():
                try:
                    noaa_key = LIPD_NOAA_MAP_BY_SECTION[header][k]
                    d_out[noaa_key] = v
                except Exception:
                    logger_lpd_noaa.warn("lpd_noaa: convert_keys_section: ran into an error converting {}".format(k))
        except KeyError:
            logger_lpd_noaa.warn("lpd_noaa: convert_keys_section: KeyError: header key {} is not in NOAA_ALL_DICT".format(header))
        except AttributeError:
            logger_lpd_noaa.warn("lpd_noaa: convert_keys_section: AttributeError: metdata is wrong data type".format(header))
            return d
        return d_out

    def __convert_keys_1(self, header, d):
        """
        Loop over keys in a dictionary and replace the lipd keys with noaa keys
        :return:
        """
        d2 = {}
        try:
            for k, v in d.items():
                try:
                    d2[self.__get_noaa_key_w_context(header, k)] = v
                except KeyError:
                    pass
        except Exception:
            return d
        return d2

    def __parse_dois(self, x):
        """
        Parse the Dataset_DOI field. Could be one DOI string, or a list of DOIs
        :param any x: Str or List of DOI ids
        :return none: list is set to self
        """
        # datasetDOI is a string. parse, validate and return a list of DOIs
        if isinstance(x, str):
            # regex cleans string, and returns a list with 1 entry for each regex doi match
            m = clean_doi(x)
            # make sure m is not an empty list
            if m:
                # set list directly into self
                self.doi = m

        # datasetDOI is a list. use regex to validate each doi entry.
        elif isinstance(x, list):
            for entry in x:
                # regex cleans string, and returns a list with 1 entry for each regex doi match
                m = clean_doi(entry)
                # make sure m is not an empty list
                if m:
                    # combine lists with existing self list
                    self.doi += m
        return

    def __flatten_col(self, d):
        """
        Flatten column so climateInterpretation and calibration are not nested.
        :param d:
        :return:
        """

        try:
            for entry in ["climateInterpretation", "calibration"]:
                if entry in d:
                    for k, v in d[entry].items():
                        d[k] = v
                    del d[entry]
        except AttributeError:
            pass

        return d

    def __check_time_unit(self):
        """
        If earliest_year, and most_recent_year exist, and time_unit does NOT exist, then default time_unit = "AD"
        :return none:
        """
        if "Earliest_Year" in self.noaa_data_sorted["Data_Collection"] and \
            "Most_Recent_Year" in self.noaa_data_sorted["Data_Collection"] and \
            "Time_Unit" not in self.noaa_data_sorted["Data_Collection"]:
            self.noaa_data_sorted["Data_Collection"]["Time_Unit"] = "AD"
        return

    def __put_sensor_species(self, value):
        """
        Two possible cases:
        Species_code = 4 character string
        Species_name =  all other cases
        :param str value:
        :return none:
        """
        if len(value) == 4:
            self.noaa_data_sorted["Species"]["Species_Code"] = value
        else:
            self.noaa_data_sorted["Species"]["Species_Name"] = value
        return

    @staticmethod
    def __put_names_on_csv_cols(names, cols):
        """
        Put the variableNames with the corresponding column data.
        :param list names: variableNames
        :param list cols: List of Lists of column data
        :return dict:
        """
        _combined = {}
        for idx, name in enumerate(names):
            # Use the variableName, and the column data from the same index
            _combined[name] = cols[idx]



        return _combined

    @staticmethod
    def __rm_names_on_csv_cols(d):
        """
        Remove the variableNames from the columns.
        :param dict d: Named csv data
        :return list list: One list for names, one list for column data
        """
        _names = []
        _data = []
        for name, data in d.items():
            _names.append(name)
            _data.append(data)
        return _names, _data

    @staticmethod
    def __put_year_col_first(d):
        """
        Always write year column first. Reorder dictionary so that year is first
        :param dict d: data
        :return dict: Reordered data
        """
        if "year" in d:
            D = OrderedDict()
            # store the year column first
            D["year"] = d["year"]
            for k,v in d.items():
                if k != "year":
                    # store the other columns
                    D[k] = v
            return D
        else:
            # year is not found, return data as-is
            return d

    # REORGANIZE

    def __reorganize(self):
        """
        Reorganize the keys into their proper section order for the NOAA output file
        DO NOT parse data tables (paleoData or chronData). We will do those separately.
        :param str key:
        :param any value:
        :return none:
        """
        logger_lpd_noaa.info("enter reorganize")
        # NOAA files are organized in sections differently than NOAA. try to translate these sections.
        for key, value in self.lipd_data.items():
            # if this key has a noaa match, it'll be returned. otherwise, empty string for no match
            noaa_key = self.__get_noaa_key(key)
            # check if this lipd key is in the NOAA_KEYS conversion dictionary.
            # if it's not, then stash it in our ignore list.
            if key not in LIPD_NOAA_MAP_FLAT:
                self.noaa_data_sorted["Ignore"][noaa_key] = value
            # studyName is placed two times in file. Line #1, and under the 'title' section
            elif noaa_key == "Study_Name":
                # study name gets put in two locations
                self.noaa_data_sorted["Top"][noaa_key] = value
                self.noaa_data_sorted["Title"][noaa_key] = value
            # put archiveType in self, because we'll reuse it later for the 9-part-variables as well
            elif noaa_key == "Archive_Type":
                self.archive_type = value
            # Dataset_DOI is a repeatable element. the key could be a single DOI, or a list of DOIs.
            elif noaa_key == "Dataset_DOI":
                self.__parse_dois(value)
            # sensorSpecies may map to two different keys: Species_code, or species_name. Determine the proper mapping
            elif key == "sensorSpecies":
                self.__put_sensor_species(value)

            # all other keys. determine which noaa section they belong in.
            else:
                # noaa keys are sorted by section.
                for header, content in NOAA_KEYS_BY_SECTION.items():
                    try:
                        # if our key is a noaa header key, then that means it's the ONLY key in the section.
                        # set value directly
                        if noaa_key == header:
                            self.noaa_data_sorted[header] = value
                        # all other cases, the key is part of the section
                        elif noaa_key in content:
                            self.noaa_data_sorted[header][noaa_key] = value
                    except KeyError:
                        # this shouldn't ever really happen, but just in case
                        logger_lpd_noaa.warn("lpd_noaa: reorganize: KeyError: {}".format(noaa_key))
        return

    def __reorganize_geo(self):
        """
        Concat geo value and units, and reorganize the rest
        References geo data from self.noaa_data_sorted
        Places new data into self.noaa_geo temporarily, and then back into self.noaa_data_sorted.
        :return:
        """
        logger_lpd_noaa.info("enter reorganize_geo")

        try:
            # Geo -> Properties
            for k, v in self.noaa_data_sorted["Site_Information"]['properties'].items():
                noaa_key = self.__get_noaa_key(k)
                self.noaa_geo[noaa_key] = v
        except KeyError:
            logger_lpd_noaa.info("reorganize_geo: KeyError: geo properties")
        try:
            # Geo -> Geometry
            self.__reorganize_coordinates()
        except Exception:
            logger_lpd_noaa.warning("reorganize_geo: Exception: missing required data: coordinates")

        # put the temporarily organized data into the self.noaa_data_sorted
        self.noaa_data_sorted["Site_Information"] = self.noaa_geo
        return

    def __reorganize_coordinates(self):
        """
        GEOJSON FORMAT :  [ LONGITUDE, LATITUDE, ELEVATION]
        Reorganize coordinates based on how many values are available.
        :return:
        """
        try:
            l = self.noaa_data_sorted["Site_Information"]['geometry']['coordinates']
            locations = ["Northernmost_Latitude", "Southernmost_Latitude", "Easternmost_Longitude",
                         "Westernmost_Longitude", "Elevation"]
            logger_lpd_noaa.info("coordinates: {} coordinates found".format(len(l)))

            # Amount of coordinates in the list
            _len_coords = len(l)

            # Odd number of coordinates. Elevation value exists
            if _len_coords % 2 == 1:
                # Store the elevation, which is always the last value in the list
                self.noaa_geo["Elevation"] = l[-1]
                # If elevation, then subtract one from the length
                _len_coords -= 1

            # Start compiling the lat lon coordinates

            # 0 coordinate values. fill in locations with empty values
            if _len_coords == 0:
                for location in locations:
                    self.noaa_geo[location] = ' '
            # 2 coordinates values. duplicate to fill 4 location slots.
            elif _len_coords == 2:
                self.noaa_geo[locations[0]] = l[1]
                self.noaa_geo[locations[1]] = l[1]
                self.noaa_geo[locations[2]] = l[0]
                self.noaa_geo[locations[3]] = l[0]

            # 4 coordinate values. put each in its correct location slot.
            elif _len_coords == 4:
                for index, location in enumerate(locations):
                    self.noaa_geo[locations[index]] = l[index]
            else:
                logger_lpd_noaa.info("coordinates: too many coordinates given")
        except KeyError:
            logger_lpd_noaa.info("lpd_noaa: coordinates: no coordinate information")
        except Exception:
            logger_lpd_noaa.error("lpd_noaa: coordinates: unknown exception")

        return

    # PUT

    def __put_dois(self):
        """
        Put the DOIs into their proper sections
        :return:
        """
        # todo: fn may not be necessary. I image pub DOIs and dataset_DOIs are mutually exclusive.
        # todo: therefore, collecting DOIs from pubs to put into the dataset_DOI is probably wrong.
        pass

    # REMOVE

    def __rm_duplicate_citation_2(self, key):
        """
        Remove exact duplicate entries for abstract or citation fields. Check all publication entries.
        :return:
        """
        citations = []
        # Before writing, remove any duplicate "Full_Citations" that are found
        for idx, pub in enumerate(self.noaa_data_sorted["Publication"]):
            try:
                citations.append(pub[key])
            except KeyError:
                # Key was not found. Enter a blank entry in citations list
                citations.append("")

        # Create a backwards dictionary, that lists which indexes are duplicates
        d = defaultdict(list)
        for i, item in enumerate(citations):
            d[item].append(i)
        d = {k: v for k, v in d.items() if len(v) > 1}
        # Duplicates indexes are listed like so:
        # {"full citation info here": [0, 2, 5]}

        # Loop over duplicate indexes
        for citation, idxs in d.items():
            # do not process any duplicate entries that were initially blanks.
            if citation:
                # Loop for [1:], since we want to keep the first citation and remove the rest.
                for idx in idxs[1:]:
                    # Set citation to blank
                    self.noaa_data_sorted["Publication"][idx][key] = ""

    def __rm_duplicate_citation_1(self):
        """
        If there are multiple publications, and there are two duplicate "Full_Citation" entries, then keep only one
        of the Full_Citation entries and remove the others.
        :return none:
        """
        # Loop through and collect all citations
        # Then, see if any citations are duplicates (excluding blank entry)
        # Keep the first entry,
        # then set subsequent duplicate citations to blank for corresponding publications indexes
        for key in ["abstract", "citation"]:
            self.__rm_duplicate_citation_2(key)

        return

    # GET

    @staticmethod
    def __get_pub_type(pub):
        """
        Check this publication to see if it is a data citation.
        :param dict pub: Publication
        :return bool: True, if data citation, False, if not data citation.
        """
        try:
            # The given publication IS a data citation.
            if pub["type"] == "dataCitation":
                return True
        except KeyError:
            # Publication is missing "type" field. Assume that publication IS NOT a data citation.
            pass
        return False

    @staticmethod
    def __get_filename(table):
        """
        Get filename from a data table
        :param dict table:
        :return str:
        """
        try:
            filename = table['filename']
        except KeyError as e:
            filename = ""
            logger_lpd_noaa.warning("get_filename: KeyError: Table missing filename, {}".format(e))
        except TypeError:
            try:
                filename = table[0]["filename"]
            except Exception as e:
                filename = ""
                logger_lpd_noaa.warning("get_filename: Generic: Unable to get filename from table, {}".format(e))
        return filename

    @staticmethod
    def __get_doi(pub):
        """
        Get DOI from this ONE publication entry.
        :param dict pub: Single publication entry
        :return:
        """
        doi = ""
        # Doi location: d["pub"][idx]["identifier"][0]["id"]
        try:
            doi = pub["DOI"][0]["id"]
            doi = clean_doi(doi)
        except KeyError:
            logger_lpd_noaa.info("get_dois: KeyError: missing a doi key")
        except Exception:
            logger_lpd_noaa.info("get_dois: Exception: something went wrong")

        # if we received a doi that's a list, we want to concat into a single string
        if isinstance(doi, list):
            if len(doi) == 1:
                doi = doi[0]
            else:
                ", ".join(doi)
        return doi

    @staticmethod
    def __get_mv(d):
        """
        Get missing value from root of data table dictionary.
        :param dict d: Data table
        :return str: Missing value or empty str.
        """
        if 'missingValue' in d:
            return d['missingValue']
        return ''

    @staticmethod
    def __get_noaa_key(lipd_key):
        """
        Switch a LiPD key into its NOAA equivalent
        :param str lipd_key: LiPD Key
        :return str: NOAA key
        """
        try:
            noaa_key = LIPD_NOAA_MAP_FLAT[lipd_key]
        except KeyError:
            logger_lpd_noaa.warning("lpd_noaa: map_key: unable to find noaa mapping for lipd key: {}".format(lipd_key))
            return lipd_key
        return noaa_key

    @staticmethod
    def __get_noaa_key_w_context(header, lipd_key):
        """
        Use the section header and key to get the proper noaa key.
        :param str header:
        :param str lipd_key:
        :return:
        """
        try:
            noaa_key = LIPD_NOAA_MAP_BY_SECTION[header][lipd_key]
        except KeyError:
            return lipd_key
        return noaa_key

    def __get_data_citation(self, l):
        """
        If originalDataURL / investigators not in root data, check for a dataCitation pub entry.
        :return:
        """
        # loop once for each publication entry
        for pub in l:
            try:
                # at the moment, these are the only keys of interest inside of dataCitation. Check each.
                for key in ["url", "investigators"]:
                    if pub["type"] == "dataCitation" and key in pub:
                        noaa_key = self.__get_noaa_key(key)
                        self.data_citation[noaa_key] = pub[key]
            except KeyError:
                # no "type" key in pub
                logger_lpd_noaa.info("lpd_noaa: get_data_citation: KeyError: pub is missing 'type'")
        return

    def __get_output_filenames(self):
        """
        Set up the output filenames. If more than one file is being written out, we need appended filenames.
        :return:
        """
        # if there is only one file, use the normal filename with nothing appended.
        if len(self.noaa_data_sorted["Data"]) == 1:
            self.output_filenames.append(self.name_txt)

        # if there are multiple files that need to be written out, (multiple data table pairs), then append numbers
        elif len(self.noaa_data_sorted["Data"]) > 1:
            for i in range(0, self.output_file_ct):
                tmp_name = "{}-{}.txt".format(self.name, i+1)
                self.output_filenames.append(tmp_name)
        return

    def __get_table_pairs(self):
        """
        Use the tables in self.paleos and self.chrons (sorted by idx) to put in self.noaa_data_sorted.
        :return:
        """
        try:
            for _idx, _p in enumerate(self.data_paleos):
                _c = {}
                try:
                    _c = self.data_chrons[_idx]
                except IndexError:
                    pass
                # create entry in self object collection of data tables
                self.noaa_data_sorted["Data"].append({"paleo": _p, "chron": _c})
        except KeyError:
            logger_lpd_noaa.warning("lpd_noaa: get_meas_table: 0 paleo data tables")

        self.output_file_ct = len(self.noaa_data_sorted["Data"])
        return

    def __put_tables_in_self(self, keys):
        """
        Metadata is sorted-by-name. Use this to put the table data into the object self.
        :param list keys: Paleo or Chron keys
        :return none:
        """
        try:
            for pd_name, pd_data in self.lipd_data[keys[1]].items():
                for table_name, table_data in pd_data[keys[2]].items():
                    if keys[0] == "paleo":
                        self.data_paleos.append(table_data)
                    else:
                        self.data_chrons.append(table_data)
        except Exception:
            pass

        return

    # WRITE

    def __write_file(self):
        """
        Open text file. Write one section at a time. Close text file. Move completed file to dir_root/noaa/
        :return none:
        """
        logger_lpd_noaa.info("enter write_file")

        self.__get_output_filenames()

        for idx, filename in enumerate(self.output_filenames):
            try:
                self.noaa_txt = open(filename, "w+")
                print("writing: {}".format(filename))
                logger_lpd_noaa.info("write_file: opened output txt file")
            except Exception as e:
                logger_lpd_noaa.debug("write_file: failed to open output txt file, {}".format(e))
                return

            self.__write_top()
            self.__write_generic('Contribution_Date')
            self.__write_generic('File_Last_Modified_Date')
            self.__write_generic('Title')
            self.__write_generic('Investigators')
            self.__write_generic('Description_Notes_and_Keywords')
            self.__write_pub()
            self.__write_funding()
            self.__write_geo()
            self.__write_generic('Data_Collection')
            self.__write_generic('Species')
            self.__write_data(idx)

            self.noaa_txt.close()
            logger_lpd_noaa.info("closed output text file")
            # shutil.copy(os.path.join(os.getcwd(), filename), self.dir_root)
            logger_lpd_noaa.info("exit write_file")
        return

    def __write_top(self):
        """
        Write the top section of the txt file.
        :param int section_num: Section number
        :return none:
        """
        logger_lpd_noaa.info("writing section: {}".format("top"))
        self.__create_blanks("Top", self.noaa_data_sorted["Top"])

        # Start writing the NOAA file section by section, starting at the very top of the template.
        self.noaa_txt.write("# {}".format(self.noaa_data_sorted["Top"]['Study_Name']))
        self.__write_template_top()
        # We don't know what the full online resource path will be yet, so leave the base path only
        self.__write_k_v("Online_Resource", "https://www1.ncdc.noaa.gov/pub/data/paleo/pages2k/pages2k-temperature-v2-2017/{}".format(self.name_txt), top=True)
        self.__write_k_v("Online_Resource_Description", "Online_Resource_Description: NOAA WDS Paleo formatted metadata and data", indent=True)
        self.__write_k_v("Online_Resource", "https://www1.ncdc.noaa.gov/pub/data/paleo/pages2k/pages2k-temperature-v2-2017/supplemental/{}".format(self.name_lpd), top=True)
        self.__write_k_v("Online_Resource_Description", "Linked Paleo Data (LiPD) file", indent=True)
        self.__write_k_v("Original_Source_URL", self.noaa_data_sorted["Top"]['Original_Source_URL'], top=True)
        self.noaa_txt.write("\n# Description/Documentation lines begin with #\n# Data lines have no #\n#")
        self.__write_k_v("Archive", self.noaa_data_sorted["Top"]['Archive'])
        # get the doi from the pub section of self.steps_dict[6]
        # doi = self.__get_doi()
        self.__write_k_v("Dataset_DOI",  ', '.join(self.doi), False, True, False, False)
        # self.__write_k_v("Parameter_Keywords", self.steps_dict[section_num]['parameterKeywords'])
        self.__write_divider()
        logger_lpd_noaa.info("exit write_top")
        return

    def __write_generic(self, header, d=None):
        """
        Write a generic section to the .txt. This function is reused for multiple sections.
        :param str header: Header title for this section
        :param int section_num:
        :param dict d: Section from steps_dict
        :return none:
        """
        logger_lpd_noaa.info("writing section: {}".format(header))
        if not d:
            d = self.noaa_data_sorted[header]
        d = self.__create_blanks(header, d)
        self.__write_header_name(header)
        for key in NOAA_KEYS_BY_SECTION[header]:
            key = self.__get_noaa_key_w_context(header, key)
            # NOAA writes value and units on one line. Build the string here.
            # if key == 'coreLength':
            #     value, unit = self.__get_corelength(val)
            #     val = str(value) + " " + str(unit)
            # DOI  id is nested in "identifier" block. Retrieve it.
            if key == "DOI":
                val = self.__get_doi(d)
                # Don't write out an empty DOI list. Write out empty string instead.
                if not val:
                    val = ""
            elif key == "Investigators":
                # Investigators is a section by itself. "d" should be a direct list
                val = get_authors_as_str(d)
            # lipd uses a singular "author" key, while NOAA uses plural "authors" key.
            elif key in ["Author", "Authors"]:
                # "d" has all publication data, so only pass through the d["Authors"] piece
                val = get_authors_as_str(d[key])
            else:
                val = d[key]

            # Write the output line
            self.__write_k_v(str(self.__get_noaa_key(key)), val, indent=True)
        # Don't write a divider if there isn't a Chron section after species. It'll make a double.
        # if header == "Species" and not self.noaa_data_sorted["Species"]:
        #     return
        self.__write_divider()
        return

    def __write_pub(self):
        """
        Write pub section. There may be multiple, so write a generic section for each one.
        :return none:
        """
        try:

            # Check all publications, and remove possible duplicate Full_Citations
            self.__rm_duplicate_citation_1()

            for idx, pub in enumerate(self.noaa_data_sorted["Publication"]):
                logger_lpd_noaa.info("publication: {}".format(idx))
                # Do not write out Data Citation publications. Check, and skip if necessary
                is_data_citation = self.__get_pub_type(pub)
                if not is_data_citation:
                    pub = self.__convert_keys_1("Publication", pub)
                    self.__write_generic('Publication', pub)
        except KeyError:
            logger_lpd_noaa.info("write_pub: KeyError: pub section not found")
        except TypeError:
            logger_lpd_noaa.debug("write_pub: TypeError: pub not a list type")

        return

    def __write_funding(self):
        """
        Write funding section. There are likely multiple entries.
        :param dict d:
        :return none:
        """
        # todo: CODE BREAKING HERE
        for idx, entry in enumerate(self.noaa_data_sorted["Funding_Agency"]):
            logger_lpd_noaa.info("funding: {}".format(idx))
            self.__write_generic('Funding_Agency', entry)
        return

    def __write_geo(self):
        """
        Write geo section. Organize before writing to file.
        :param dict d:
        :return none:
        """
        self.__reorganize_geo()
        self.__write_generic('Site_Information')
        return

    def __write_data(self, idx):
        """
        Write out the measurement tables found in paleoData and chronData
        :return:
        """
        pair = self.noaa_data_sorted["Data"][idx]
        # Run once for each pair (paleo+chron) of tables that was gathered earlier.
        # for idx, pair in enumerate(self.noaa_data_sorted["Data"]):

        # loop once for paleo, once for chron
        for name, table in pair.items():
            # safeguard in case the table is an empty set.
            if table:
                # self.__write_divider(top=False)
                self.__write_variables_1(table)
                self.__write_divider()
                self.__write_columns(table)

    def __write_variables_1(self, table):
        """
        Retrieve variables from data table(s) and write to Variables section of txt file.
        :param dict table: Paleodata
        :return none:
        """
        logger_lpd_noaa.info("writing section: {}".format("Variables"))

        # Write the template lines first
        self.__write_template_variable(self.__get_filename(table))

        # Start going through columns and writing out data
        try:
            self.noaa_txt.write('#')

            # Special NOAA Request: Write the "year" column first always, if available
            # write year data first, when available
            for name, data in table["columns"].items():
                if name == "year":
                    # write first line in variables section here
                    self.__write_variables_2(data)
                    # leave the loop, because this is all we needed to accomplish
                    break

            # all other cases
            for name, data in table["columns"].items():
                # we already wrote out the year column, so don't duplicate.
                if name != "year":
                    self.__write_variables_2(data)

        except KeyError as e:
            logger_lpd_noaa.warn("write_variables: KeyError: {} not found".format(e))
        return

    def __write_variables_2(self, col):
        """
        Use one column of data, to write one line of data in the variables section.
        :return none:
        """
        col = self.__convert_keys_1("Variables", col)

        # Write one line for each column. One line has all metadata for one column.
        for entry in NOAA_KEYS_BY_SECTION["Variables"]:
            # May need a better way of handling this in the future. Need a strict list for this section.
            try:
                # First entry: Add extra hash and tab
                if entry == 'shortname':
                    # DEPRECATED: Fixed spacing for variable names.
                    # self.noaa_txt.write('{:<20}'.format('#' + str(col[entry])))
                    # Fluid spacing for variable names. Spacing dependent on length of variable names.
                    self.noaa_txt.write('{}\t'.format('#' + str(col[entry])))
                # Last entry: No space or comma
                elif entry == 'notes':
                    self.noaa_txt.write('{:<0}'.format(str(col[entry])))
                else:
                    # This is for any entry that is not first or last in the line ordering
                    # Account for nested entries.
                    if entry == "uncertainty":
                        try:
                            e = str(col["calibration"][entry])
                        except KeyError:
                            e = ""
                    elif entry == "seasonality":
                        try:
                            e = str(col["climateInterpretation"][entry])
                        except KeyError:
                            e = ""
                    elif entry == "archive":
                        e = self.archive_type
                    else:
                        e = str(col[entry])
                    e = e.replace(",", ";")
                    self.noaa_txt.write('{:<0}'.format(e + ','))
            except KeyError as e:
                self.noaa_txt.write('{:<0}'.format(','))
                logger_lpd_noaa.info("write_variables: KeyError: missing {}".format(e))
        self.noaa_txt.write('\n#')
        return

    def __write_columns(self, table):
        """
        Read numeric data from csv and write to the bottom section of the txt file.
        :param dict table: Paleodata dictionary
        :return none:
        """
        logger_lpd_noaa.info("writing section: data, csv values from file")
        # get filename for this table's csv data
        filename = self.__get_filename(table)
        # filename =
        logger_lpd_noaa.info("processing csv file: {}".format(filename))
        # get missing value for this table
        # mv = self.__get_mv(table)
        # write template lines
        # self.__write_template_paleo(mv)
        self.__write_template_paleo("NaN")

        # continue if csv exists
        if filename in self.data_csv:
            logger_lpd_noaa.info("_write_columns: csv data exists: {}".format(filename))

            # sort the dictionary so the year column is first
            _csv_data_by_name = self.__put_year_col_first(self.data_csv[filename])

            # now split the sorted dictionary back into two lists (easier format to write to file)
            _names, _data = self.__rm_names_on_csv_cols(_csv_data_by_name)

            # write column variableNames
            self.__write_data_col_header(_names)

            # write data columns index by index
            self.__write_data_col_vals(_data)

        return

    def __write_template_top(self):
        """
        Write the template info for top section
        :return none:
        """
        self.noaa_txt.write(
            "\n#-----------------------------------------------------------------------\
            \n#                World Data Service for Paleoclimatology, Boulder\
            \n#                                  and\
            \n#                     NOAA Paleoclimatology Program\
            \n#             National Centers for Environmental Information (NCEI)\
            \n#-----------------------------------------------------------------------\
            \n# Template Version 3.0\
            \n# Encoding: UTF-8\
            \n# NOTE: Please cite Publication, and Online_Resource and date accessed when using these data. \
            \n# If there is no publication information, please cite Investigators, Title, and Online_Resource and date accessed."
            )
        return

    def __write_template_variable(self, filename):
        """
        Write the template info for the variable section
        :param str filename:
        :return none:
        """
        self.noaa_txt.write('# Variables\n#\
        \n# Filename: {}\
        \n#\n# Data variables follow that are preceded by "##" in columns one and two.\
        \n# Data line variables format:  Variables list, one per line, shortname-tab-longname-tab-longname components '
        '( 9 components: what, material, error, units, seasonality, archive, detail, method, C or N for Character or '
        'Numeric data, notes)\n#\n'.format(filename))
        return

    def __write_template_paleo(self, mv):
        """
        Write the template info for the paleo section
        :param str mv: Missing Value
        :return none:
        """
        self.noaa_txt.write('# Data:\
        \n# Data lines follow (have no #)\
        \n# Data line format - tab-delimited text, variable short name as header)\
        \n# Missing_Values: {}\n#\n'.format(mv))
        return

    def __write_k_v(self, k, v, top=False, bot=False, multi=False, indent=False):
        """
        Write a key value pair to the output file. If v is a list, write multiple lines.
        :param k: Key
        :param v: Value
        :param bool top: Write preceding empty line
        :param bool bot: Write following empty line
        :param bool multi: v is a list
        :return none:
        """
        if top:
            self.noaa_txt.write("\n#")
        if multi:
            for item in v:
                if indent:
                    self.noaa_txt.write("\n#     {}: {}".format(str(k), str(item)))
                else:
                    self.noaa_txt.write("\n# {}: {}".format(str(k), str(item)))
        else:
            if indent:
                self.noaa_txt.write("\n#     {}: {}".format(str(k), str(v)))
            else:
                self.noaa_txt.write("\n# {}: {}".format(str(k), str(v)))
        if bot:
            self.noaa_txt.write("\n#")
        return

    def __write_header_name(self, name):
        """
        Write the title line for the section
        :return none:
        """
        self.noaa_txt.write("# {}".format(name))
        return

    def __write_divider(self, top=False, bot=False):
        """
        Write a divider line
        :return none:
        """
        if top:
            self.noaa_txt.write("\n#")
        self.noaa_txt.write("\n#------------------\n")
        if bot:
            self.noaa_txt.write("\n#")
        return

    def __write_data_col_header(self, l):
        """
        Write the variableNames that are the column header in the "Data" section
        :param list l: variableNames
        :return none:
        """
        count = len(l)
        for name in l:
            # last column - spacing not important
            if count == 1:
                self.noaa_txt.write("{:<0}".format(name))
            # all [:-1] columns - fixed spacing to preserve alignment
            else:
                self.noaa_txt.write("{:<15}".format(name))
                count -= 1
        self.noaa_txt.write('\n')

    def __write_data_col_vals(self, ll):
        """
        Loop over value arrays and write index by index, to correspond to the rows of a txt file
        :param list ll: List of lists, column data
        :return:
        """

        # all columns should have the same amount of values. grab that number
        try:
            _items_in_cols = len(ll[0])
            for idx in range(0, _items_in_cols):
                # amount of columns
                _count = len(ll)
                for col in ll:
                    # last item in array: fixed spacing not needed
                    if _count == 1:
                        self.noaa_txt.write("{:<0}".format(str(col[idx])))
                    # all [:-1] items. maintain fixed spacing
                    else:
                        self.noaa_txt.write("{:<15.10}".format(str(col[idx])))
                    _count -= 1
                self.noaa_txt.write('\n')

        except IndexError:
            logger_lpd_noaa("_write_data_col_vals: IndexError: couldn't get length of columns")

        return