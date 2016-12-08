import os
import shutil

# NOAA SECTIONS is for writing keys in order, and for mapping keys to their proper sections
# NOAA KEYS is for converting keys from LPD to NOAA
from ..helpers.alternates import NOAA_ALL, NOAA_KEYS, NOAA_ALL_DICT
from ..helpers.loggers import create_logger
from ..helpers.misc import clean_doi, generate_timestamp

logger_lpd_noaa = create_logger("lpd_noaa")


class LPD_NOAA(object):
    """
    Creates a NOAA object that contains all the functions needed to write out a LiPD file as a NOAA text file.
    Supports
    LiPD Version: v1.2
    NOAA txt template: v3.0

    :return none: Writes NOAA text to file in local storage
    """

    def __init__(self, dir_root, name, lipd_dict):
        """
        :param str dir_root: Path to dir containing all .lpd files
        :param str name: Name of current .lpd file
        :param dict root_dict: Full dict loaded from jsonld file
        """
        self.dir_root = dir_root
        self.name = name
        # output filename
        self.name_txt = name + '.txt'
        self.output_filenames = []
        self.output_file_ct = 0
        self.noaa_txt = None
        self.archive_type = ""
        self.doi = []
        self.data_citation = {}
        # noaa dict has all metadata with noaa keys
        self.noaa_data = lipd_dict
        # the raw dictionary imported from jsonld file
        self.lipd_data = lipd_dict
        # jsonld data sorted according to noaa sections
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
            for key in NOAA_ALL[section_name]:
                if key not in d:
                    # Key not in our dict. Create the blank entry.
                    d[key] = ""

        except Exception:
            logger_lpd_noaa.error("lpd_noaa: create_blanks: must section: {}, key".format(section_name, key))
        return d

    @staticmethod
    def __reorganize_authors(d):
        """
        Create a combined string of authors from the pub list of authors
        :param dict d: One Publication metadata entry
        :return:
        """
        s = ""
        try:
            l = d["Author"]
        except KeyError:
            logger_lpd_noaa.debug("reorganize_authors: KeyError: missing author keys")
            return s
        if l:
            for idx, author in enumerate(l):
                try:
                    if idx == len(l)-1:
                        s += "{}".format(author["name"])
                    else:
                        s += "{}; ".format(author["name"])
                except KeyError:
                    logger_lpd_noaa.debug("reorganize_authors: KeyError: missing 'name'")
        return s

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
            self.__coordinates()
        except Exception:
            logger_lpd_noaa.warning("reorganize_geo: Exception: missing required data: coordinates")

        # put the temporarily organized data into the self.noaa_data_sorted
        self.noaa_data_sorted["Site_Information"] = self.noaa_geo
        return

    def __reorganize(self):
        """
        Reorganize the keys into their proper section order for the NOAA output file
        DO NOT parse data tables (paleoData or chronData). We will do those separately.
        :param str key:
        :param any value:
        :return none:
        """
        logger_lpd_noaa.info("enter reorganize")
        # NOAA files are organized in sections, but jld is not. Reorganize to match NOAA template.
        for key, value in self.lipd_data.items():
            # if this key has a noaa match, it'll be returned. otherwise, empty string for no match
            noaa_key = self.__get_noaa_key(key)
            # check if this lipd key is in the NOAA_KEYS conversion dictionary.
            # if it's not, then stash it in our ignore list.
            if key not in NOAA_KEYS:
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
            # all other keys. determine which noaa section they belong in.
            else:
                # noaa keys are sorted by section.
                for header, content in NOAA_ALL.items():
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

    @staticmethod
    def __convert_keys_section(header, d):
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
                    noaa_key = NOAA_ALL_DICT[header][k]
                    d_out[noaa_key] = v
                except Exception:
                    logger_lpd_noaa.warn("lpd_noaa: convert_keys_section: ran into an error converting {}".format(k))
        except KeyError:
            logger_lpd_noaa.warn("lpd_noaa: convert_keys_section: KeyError: header key {} is not in NOAA_ALL_DICT".format(header))
        except AttributeError:
            logger_lpd_noaa.warn("lpd_noaa: convert_keys_section: AttributeError: metdata is wrong data type".format(header))
            return d
        return d_out

    def __convert_keys_dict(self, header, d):
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

    def __coordinates(self):
        """
        Reorganize coordinates based on how many values are available.
        :return:
        """
        try:
            l = self.noaa_data_sorted["Site_Information"]['geometry']['coordinates']
            locations = ["Northernmost_Latitude", "Southernmost_Latitude", "Easternmost_Longitude",
                         "Westernmost_Longitude", "Elevation"]
            logger_lpd_noaa.info("coordinates: {} coordinates found".format(len(l)))

            # Odd number of coordinates. Elevation value exists
            if len(l) % 2 == 1:
                # Store the elevation, which is always the last value in the list
                self.noaa_geo["Elevation"] = l.pop()

            # Start compiling the lat lon coordinates

            # 0 coordinate values. fill in locations with empty values
            if len(l) == 0:
                for location in locations:
                    self.noaa_geo[location] = ' '
            # 2 coordinates values. duplicate to fill 4 location slots.
            elif len(l) == 2:
                self.noaa_geo[locations[0]] = l[0]
                self.noaa_geo[locations[1]] = l[1]
                self.noaa_geo[locations[2]] = l[0]
                self.noaa_geo[locations[3]] = l[1]

            # 4 coordinate values. put each in its correct location slot.
            elif len(l) == 4:
                for index, location in enumerate(locations):
                    self.noaa_geo[locations[index]] = l[index]
            else:
                logger_lpd_noaa.info("coordinates: too many coordinates given")
        except KeyError:
            logger_lpd_noaa.info("lpd_noaa: coordinates: no coordinate information")
        except Exception:
            logger_lpd_noaa.error("lpd_noaa: coordinates: unknown exception")

        return

    def __put_dois(self):
        """
        Put the DOIs into their proper sections
        :return:
        """
        # todo: fn may not be necessary. I image pub DOIs and dataset_DOIs are mutually exclusive.
        # todo: therefore, collecting DOIs from pubs to put into the dataset_DOI is probably wrong.
        pass

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
    def __get_investigators(x):
        """
        Get the investigators info. Sometimes a string, sometimes a dictionary with the string in it.
        :param any x:
        :return str: investigators string
        """
        val = ""
        if isinstance(x, dict):
            try:
                val = x["Investigators"]
            except KeyError:
                # not really concerned about this
                pass
        elif isinstance(x, str):
            val = x
        return val

    @staticmethod
    def __get_noaa_key(lipd_key):
        """
        Switch a LiPD key into its NOAA equivalent
        :param str lipd_key: LiPD Key
        :return str: NOAA key
        """
        try:
            noaa_key = NOAA_KEYS[lipd_key]
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
            noaa_key = NOAA_ALL_DICT[header][lipd_key]
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

    def __get_meas_table_chron(self, idx1, idx2):
        """
        Look for a chron meas table to match the paleo meas table we just added.
        :param int idx1: chronData[idx1]
        :param int idx2: chronData[idx1]["chronMeasurementTable"][idx2]
        :return:
        """
        try:
            # this will always be called right after a paleoData table
            self.noaa_data_sorted["Data"][len(self.noaa_data_sorted["Data"]) - 1]["chron"] = self.lipd_data["chronData"][idx1]["chronMeasurementTable"][idx2]
        except KeyError:
            logger_lpd_noaa.info("lpd_noaa: get_meas_table_chron: No matching chron table")
        except IndexError:
            # there are more paleo tables than chron tables. this is okay, keep going
            pass
        return

    def __get_meas_tables(self):
        """
        Count the number of measurement tables in the Paleo/Chron tables
        :return:
        """
        # todo: is this going to be a problem if there is a chronData table but no paleoData table?
        try:
            for idx1, pd in enumerate(self.lipd_data["paleoData"]):
                for idx2, pmt in enumerate(self.lipd_data["paleoData"][idx1]["paleoMeasurementTable"]):
                    # create entry in self object collection of data tables
                    self.noaa_data_sorted["Data"].append({"paleo": pmt, "chron": {}})
                    # look for a matching chron table at the same index
                    self.__get_meas_table_chron(idx1, idx2)
        except KeyError:
            logger_lpd_noaa.warning("lpd_noaa: get_meas_table: 0 paleo data tables")

        self.output_file_ct = len(self.noaa_data_sorted["Data"])
        return

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

        # how many measurement tables exist? this will tell use how many noaa files to create
        self.__get_meas_tables()

        # collect all doi ids
        # self.__get_dois()
        # self.__put_dois()

        # reorganize data into noaa sections
        self.__reorganize()

        # Use data in steps_dict to write to
        # self.noaa_data_sorted = self.__key_conversion(self.noaa_data_sorted)
        self.__write_file()
        logger_lpd_noaa.info("exit main")
        return

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
            shutil.copy(os.path.join(os.getcwd(), filename), self.dir_root)
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
        self.__write_k_v("Online_Resource", "http://www1.ncdc.noaa.gov/pub/data/paleo/pages2k/pages2k-temperature-v2-2017/", top=True)
        self.__write_k_v("Online_Resource_Description", self.noaa_data_sorted["Top"]['Online_Resource_Description'], indent=True)
        self.__write_k_v("Online_Resource", "http://www1.ncdc.noaa.gov/pub/data/paleo/pages2k/pages2k-temperature-v2-2017/supplemental/{}".format(self.name), top=True)
        self.__write_k_v("Online_Resource_Description", self.noaa_data_sorted["Top"]['Online_Resource_Description'], indent=True)
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
        for key in NOAA_ALL[header]:
            key = self.__get_noaa_key_w_context(header, key)
            # NOAA writes value and units on one line. Build the string here.
            # if key == 'coreLength':
            #     value, unit = self.__get_corelength(val)
            #     val = str(value) + " " + str(unit)
            # DOI  id is nested in "identifier" block. Retrieve it.
            if key == "DOI":
                val = self.__get_doi(d)
            elif key == "Investigators":
                val = self.__get_investigators(d)
            elif key in ["Author", "Authors"]:
                val = self.__reorganize_authors(d)
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
            for idx, pub in enumerate(self.noaa_data_sorted["Publication"]):
                logger_lpd_noaa.info("publication: {}".format(idx))
                pub = self.__convert_keys_dict("Publication", pub)
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

    def __write_columns(self, table):
        """
        Read numeric data from csv and write to the bottom section of the txt file.
        :param dict table: Paleodata dictionary
        :return none:
        """
        logger_lpd_noaa.info("writing section: data, csv values from file")
        filename = self.__get_filename(table)
        logger_lpd_noaa.info("processing csv file: {}".format(filename))
        mv = self.__get_mv(table)
        self.__write_template_paleo(mv)
        if self.__csv_found(filename):
            logger_lpd_noaa.info("found csv file: {}".format(filename))
            # Write variables line from dict_in
            count = len(table['columns'])
            for col in table['columns']:
                col = self.__convert_keys_dict("Variables", col)
                try:
                    param = col['shortname']
                except KeyError:
                    param = 'N/A'
                if count == 1:
                    self.noaa_txt.write("{:<0}".format(param))
                else:
                    self.noaa_txt.write("{:<15}".format(param))
                    count -= 1
            self.noaa_txt.write('\n')
            # Iter over CSV and write line for line
            with open(filename, 'r') as f:
                logger_lpd_noaa.info("opened csv file: {}".format(filename))
                for line in iter(f):
                    line = line.split(',')
                    for idx, value in enumerate(line):
                        if idx == len(line) - 1:
                            self.noaa_txt.write("{:<0}".format(str(value)))
                        else:
                            self.noaa_txt.write("{:<15.10}".format(str(value)))
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
                self.__write_variables(table)
                self.__write_divider()
                self.__write_columns(table)

    def __write_variables(self, table):
        """
        Retrieve variables from data table(s) and write to Variables section of txt file.
        :param dict table: Paleodata dictionary
        :return none:
        """
        logger_lpd_noaa.info("writing section: {}".format("Variables"))

        # Write the template lines first
        self.__write_template_variable(self.__get_filename(table))

        # Start going through columns and writing out data
        try:
            self.noaa_txt.write('#')
            for col in table['columns']:
                col = self.__convert_keys_dict("Variables", col)

                # Write one line for each column. One line has all metadata for one column.
                for entry in NOAA_ALL["Variables"]:
                    # May need a better way of handling this in the future. Need a strict list for this section.
                    try:
                        # First entry: Add extra hash and tab
                        if entry == 'shortname':
                            self.noaa_txt.write('{:<20}'.format('#' + str(col[entry])))
                        # Last entry: No space or comma
                        elif entry == 'dataType':
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
        except KeyError as e:
            logger_lpd_noaa.warn("write_variables: KeyError: {} not found".format(e))
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
        'Numeric data)\n#\n'.format(filename))
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


# @staticmethod
# def __get_corelength(d):
#     """
#     Get the value and unit to write the Core Length line
#     :param dict d:
#     :return int str: Value, Unit
#     """
#     # If d is a string, it'll throw a type error
#     if not isinstance(d, str):
#         try:
#             val = d['coreLength']['value']
#         except KeyError:
#             val = ''
#         try:
#             unit = d['coreLength']['unit']
#         except KeyError:
#             unit = ''
#         return val, unit
#     return '', ''



# def __write_chron(self, d):
#     """
#     Write chronology section.
#     :param dict d:
#     :return none:
#     """
#     # ChronData is a list of dictionaries
#     logger_lpd_noaa.info("writing section: {}".format("chronology"))
#     try:
#         # Loop for one or more chronologies
#         for chron in d["chronData"]:
#             try:
#                 # todo STRUCTURE: there is a discrepancy here.
#                 # LPD files created from noaa -> LPD converter work here (bad structure): chron["chronMeasurementTable"]
#                 # Normal, good LPD files fail here because there is another level of structure. : chron["chronMeasurementTable"][0]
#
#                 table = chron["chronMeasurementTable"]
#             except KeyError:
#                 logger_lpd_noaa.warn("write_chron: KeyError: missing chronMeasurementTable, ()".format(self.name))
#                 break
#             # Get the csv filename from the current table
#             filename = self.__get_filename(table)
#             self.noaa_txt.write('# Chronology:\n#\n')
#             if self.__csv_found(filename):
#                 logger_lpd_noaa.info("found csv file: {}".format(filename))
#                 try:
#                     cols = table["columns"]
#                 except KeyError:
#                     logger_lpd_noaa.warn("write_chron: KeyError: missing chron columns, {}".format(filename))
#                 # Loop for each column in the table
#                 for idx, col in enumerate(cols):
#                     try:
#                         units = "({})".format(str(col["units"]))
#                     except KeyError:
#                         # No units are okay. No handling.
#                         units = ""
#                     if idx == len(cols)-1:
#                         self.noaa_txt.write("{:<0}".format(col['variableName'], units))
#                     else:
#                         self.noaa_txt.write("{:<15}".format(col['variableName'], units))
#                 self.noaa_txt.write("\n")
#                 # Write each line from the csv file
#                 with open(filename, 'r') as f:
#                     for line in iter(f):
#                         line = line.split(',')
#                         for idx, value in enumerate(line):
#                             if idx == len(line) - 1:
#                                 self.noaa_txt.write("{:<0}".format(str(value)))
#                             else:
#                                 self.noaa_txt.write("{:<15.10}".format(str(value)))
#         self.noaa_txt.write("#")
#     except KeyError:
#         logger_lpd_noaa.info("write_chron: KeyError: missing chronData key")
#     return

# def __key_conversion(self, d):
#     """
#     Convert entire lipd metadata into noaa keys
#     :return dict: noaa dictionary
#     """
#
#     if isinstance(d, str):
#         return self.__get_noaa_key(d)
#
#     elif isinstance(d, list):
#         for idx, i in enumerate(d):
#             d[idx] = self.__key_conversion(i)
#
#     elif isinstance(d, dict):
#         tmp = {}
#         for k, v in d.items():
#             if k != "Ignore":
#                 # get the new noaa key
#                 noaa_key = self.__get_noaa_key(k)
#                 # swap the keys
#                 tmp[noaa_key] = v
#                 # recursive dive
#                 tmp[noaa_key] = self.__key_conversion(v)
#         d = tmp
#     return d
