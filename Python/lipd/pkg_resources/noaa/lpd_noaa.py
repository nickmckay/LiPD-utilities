import os
import shutil

from ..helpers.alternates import *
from ..helpers.regexes import *
from ..helpers.loggers import create_logger

logger_lpd_noaa = create_logger("lpd_noaa")


class LPD_NOAA(object):
    """
    Creates a NOAA object that contains all the functions needed to write out a LiPD file as a NOAA text file.
    :return str: NOAA text file
    """

    def __init__(self, dir_root, name, root_dict):
        """
        :param str dir_root: Path to dir containing all .lpd files
        :param str name: Name of current .lpd file
        :param dict root_dict: Full dict loaded from jsonld file
        """
        self.dir_root = dir_root
        self.name = name
        self.root_dict = root_dict
        self.steps_dict = {1:{},2:{},3:{},4:{},5:{},6:{},7:{},8:{},9:{},10:{},11:{},12:{},13:{}}
        self.name_txt = name + '.txt'
        self.noaa_txt = None

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
    def __underscore(key):
        """
        Convert camelCase to underscore
        :param str key: Key or title name
        """
        # Special keys that need a specific key change
        if key == 'doi':
            key_o = 'DOI'

        elif key == 'agency':
            key_o = 'Funding_Agency_Name'

        elif key == 'originalSourceURL':
            key_o = 'Original_Source_URL'

        # Use regex to split and add underscore at each capital letter
        else:
            s = first_cap_re.sub(r'\1_\2', key)
            key_o = all_cap_re.sub(r'\1_\2', s).title()

        return key_o

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
    def __get_corelength(d):
        """
        Get the value and unit to write the Core Length line
        :param dict d:
        :return int str: Value, Unit
        """
        # If d is a string, it'll throw a type error
        if not isinstance(d, str):
            try:
                val = d['coreLength']['value']
            except KeyError:
                val = ''
            try:
                unit = d['coreLength']['unit']
            except KeyError:
                unit = ''
            return val, unit
        return '', ''

    @staticmethod
    def __get_identifier(d):
        """
        Get DOI id and url from identifier dictionary.
        :param dict d: Pub metadata.
        :return str str: DOI id
        """
        doi_id = ""
        for pub in d["identifier"]:
            try:
                doi_id += pub['id']
            except KeyError:
                # Don't care if it fails. It will return an empty string or what's been found so far.
                pass
        return doi_id

    @staticmethod
    def __create_blanks(section_num, d):
        """
        All keys need to be written to the output, with or without a value. Furthermore, only keys that have values
        exist at this point. We need to manually insert the other keys with a blank value. Loop through the global list
        to see what's missing in our dict.
        :param int section_num: Retrieve data from global dict for this number.
        :param dict d: Section of steps_dict
        :return none:
        """
        for key in NOAA_ORDERING[section_num]:
            if key not in d and key not in NOAA_SECTIONS[13]:
                # Key not in our dict. Create the blank entry.
                d[key] = ""
        return

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
        return filename

    @staticmethod
    def __coordinates(l, d):
        """
        Reorganize coordinates based on how many values are available.
        :param list of float l: Coordinate values
        :param dict d: Location with corresponding values
        :return dict:
        """
        length = len(l)
        locations = ['northernmostLatitude', 'easternmostLongitude', 'southernmostLatitude', 'westernmostLongitude']
        logger_lpd_noaa.info("coordinates: {} coordinates found".format(length))

        # Odd number of coordinates. Elevation value exists
        if len(l) % 2 == 1:
            # Store the elevation, which is always the last value in the list
            d["elevation"] = l.pop()

        # Start compiling the lat lon coordinates
        if len(l) == 0:
            for location in locations:
                d[location] = ' '
        elif len(l) == 2:
            d[locations[0]] = l[0]
            d[locations[1]] = l[1]
            d[locations[2]] = l[0]
            d[locations[3]] = l[1]
        elif len(l) == 4:
            for index, location in enumerate(locations):
                d[locations[index]] = l[index]
        else:
            logger_lpd_noaa.info("coordinates: too many coordinates given")

        return d

    def main(self):
        """
        Load in the template file, and run through the parser
        :return none:
        """
        logger_lpd_noaa.info("enter main")
        # Starting Directory: dir_tmp/dir_bag/data/
        # NOAA files are organized in sections, but jld is not. Reorganize to match NOAA template.
        for k, v in self.root_dict.items():
            self.__reorganize(k, v)
        # Use data in steps_dict to write to
        self.__write_file()
        logger_lpd_noaa.info("exit main")
        return

    def __write_file(self):
        """
        Open text file. Write one section at a time. Close text file. Move completed file to dir_root/noaa/
        :return none:
        """
        logger_lpd_noaa.info("enter write_file")
        try:
            self.noaa_txt = open(self.name_txt, "w+")
            logger_lpd_noaa.info("write_file: opened output txt file")
        except Exception as e:
            logger_lpd_noaa.debug("write_file: failed to open output txt file, {}".format(e))
            return

        self.__write_top(1)
        self.__write_generic('Contribution_Date', 2, self.steps_dict[2])
        self.__write_generic('Title', 3, self.steps_dict[3])
        self.__write_generic('Investigators', 4, self.steps_dict[4])
        self.__write_generic('Description_Notes_and_Keywords', 5, self.steps_dict[5])
        self.__write_pub()
        self.__write_funding(self.steps_dict[7])
        self.__write_geo(self.steps_dict[8])
        self.__write_generic('Data_Collection', 9, self.steps_dict[9])
        self.__write_generic('Species', 10, self.steps_dict[10])
        self.__write_chron(self.steps_dict[11])

        # Run once for each table. Keep variables and related data grouped
        for table in self.steps_dict[12]['paleoData']:
            self.__write_divider()
            self.__write_variables(table)
            self.__write_divider()
            self.__write_paleo(table)
        self.noaa_txt.close()
        logger_lpd_noaa.info("closed output text file")
        shutil.copy(os.path.join(os.getcwd(), self.name_txt), self.dir_root)
        logger_lpd_noaa.info("exit write_file")
        return

    def __write_top(self, section_num):
        """
        Write the top section of the txt file.
        :param int section_num: Section number
        :return none:
        """
        logger_lpd_noaa.info("writing section: {}".format("top"))
        self.__create_blanks(section_num, self.steps_dict[section_num])

        # Start writing the top section line by line
        self.noaa_txt.write("# {}".format(self.steps_dict[section_num]['studyName']))
        self.__write_template_top()
        self.__write_k_v("Online_Resource", self.steps_dict[section_num]['onlineResource'], True, True, True, False)
        self.__write_k_v("Original_Source_URL", self.steps_dict[section_num]['originalSourceUrl'], tab=False)
        self.noaa_txt.write("\n# Description/Documentation lines begin with #\n# Data lines have no #\n#")
        self.__write_k_v("Archive", self.steps_dict[section_num]['archive'], tab=False)
        # self.__write_k_v("Parameter_Keywords", self.steps_dict[section_num]['parameterKeywords'])
        self.__write_divider()
        logger_lpd_noaa.info("exit write_top")
        return

    def __write_generic(self, header, section_num, d):
        """
        Write a generic section to the .txt. This function is reused for multiple sections.
        :param str header: Header title for this section
        :param int section_num:
        :param dict d: Section from steps_dict
        :return none:
        """
        logger_lpd_noaa.info("writing section: {}".format(header))
        self.__create_blanks(section_num, d)
        self.__write_header_name(header)
        for key in NOAA_ORDERING[section_num]:
            val = d[key]
            # NOAA writes value and units on one line. Build the string here.
            if key == 'coreLength':
                value, unit = self.__get_corelength(val)
                val = str(value) + " " + str(unit)
            # DOI  id is nested in "identifier" block. Retrieve it.
            elif key == "doi":
                val = self.__get_identifier(d)
            elif key in ("author", "authors"):
                val = self.__reorganize_authors(d)
                key = "authors"
            # Write the output line
            self.__write_k_v(str(self.__underscore(key)), val)
        # Don't write a divider if there isn't a Chron section after species. It'll make a double.
        if header == "Species" and not self.steps_dict[11]:
            return
        self.__write_divider()
        return

    def __write_pub(self):
        """
        Write pub section. There may be multiple, so write a generic section for each one.
        :return none:
        """
        try:
            for idx, pub in enumerate(self.steps_dict[6]["pub"]):
                logger_lpd_noaa.info("publication: {}".format(idx))
                self.__write_generic('Publication', 6, pub)
        except KeyError:
            logger_lpd_noaa.info("write_pub: KeyError: pub section not found")
        except TypeError:
            logger_lpd_noaa.debug("write_pub: TypeError: pub not a list type")

        return

    def __write_funding(self, d):
        """
        Write funding section. There are likely multiple entries.
        :param dict d:
        :return none:
        """
        for key, fund_list in d.items():
            for idx, fund in enumerate(fund_list):
                logger_lpd_noaa.info("funding: {}".format(idx))
                self.__write_generic('Funding_Agency', 7, fund)
        return

    def __write_geo(self, d):
        """
        Write geo section. Organize before writing to file.
        :param dict d:
        :return none:
        """
        for k, v in d.items():
            d = self.__reorganize_geo(v)
        self.__write_generic('Site_Information', 8, d)
        return

    def __write_chron(self, d):
        """
        Write chronology section.
        :param dict d:
        :return none:
        """
        # ChronData is a list of dictionaries
        logger_lpd_noaa.info("writing section: {}".format("chronology"))
        try:
            # Loop for one or more chronologies
            for chron in d["chronData"]:
                try:
                    table = chron["chronMeasurementTable"]
                except KeyError:
                    logger_lpd_noaa.warn("write_chron: KeyError: missing chronMeasurementTable, ()".format(self.name))
                    break
                # Get the csv filename from the current table
                filename = self.__get_filename(table)
                self.noaa_txt.write('# Chronology:\n#\n')
                if self.__csv_found(filename):
                    logger_lpd_noaa.info("found csv file: {}".format(filename))
                    try:
                        cols = table["columns"]
                    except KeyError:
                        logger_lpd_noaa.warn("write_chron: KeyError: missing chron columns, {}".format(filename))
                    # Loop for each column in the table
                    for idx, col in enumerate(cols):
                        try:
                            units = "({})".format(str(col["units"]))
                        except KeyError:
                            # No units are okay. No handling.
                            units = ""
                        if idx == len(cols)-1:
                            self.noaa_txt.write("{:<0}".format(col['variableName'], units))
                        else:
                            self.noaa_txt.write("{:<15}".format(col['variableName'], units))
                    self.noaa_txt.write("\n")
                    # Write each line from the csv file
                    with open(filename, 'r') as f:
                        for line in iter(f):
                            line = line.split(',')
                            for idx, value in enumerate(line):
                                if idx == len(line) - 1:
                                    self.noaa_txt.write("{:<0}".format(str(value)))
                                else:
                                    self.noaa_txt.write("{:<15.10}".format(str(value)))
            self.noaa_txt.write("#")
        except KeyError:
            logger_lpd_noaa.info("write_chron: KeyError: missing chronData key")
        return

    def __write_paleo(self, table):
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
                try:
                    param = col['variableName']
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
            for col in table['columns']:
                # Write one line for each column. One line has all metadata for one column.
                for entry in NOAA_ORDERING[11]:
                    # May need a better way of handling this in the future. Need a strict list for this section.
                    try:
                        if entry == 'variableName':
                            # First entry: Double hash and tab
                            self.noaa_txt.write('{:<20}'.format('##' + str(col[entry])))
                        elif entry == 'dataType':
                            # Last entry: No space or comma
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
                            else:
                                e = str(col[entry])
                            self.noaa_txt.write('{:<0}'.format(e + ','))
                    except KeyError as e:
                        self.noaa_txt.write('{:<0}'.format(','))
                        logger_lpd_noaa.info("write_variables: KeyError: missing {}".format(e))
                self.noaa_txt.write('\n#')
        except KeyError as e:
            logger_lpd_noaa.warn("write_variables: KeyError: {} not found".format(e))
        return

    def __reorganize_geo(self, d):
        """
        Concat geo value and units, and reorganize the rest
        :param dict d:
        :return dict:
        """
        logger_lpd_noaa.info("enter reorganize_geo")
        d_tmp = {}
        try:
            for k, v in d['properties'].items():
                d_tmp[k] = v
            # Geometry
            d_tmp = self.__coordinates(d['geometry']['coordinates'], d_tmp)
        except KeyError as e:
            d_tmp = {}
            logger_lpd_noaa.debug("reorganize_geo: KeyError: improper format, {}".format(e))
        return d_tmp

    def __reorganize(self, key, value):
        """
        Reorganize the keys into their proper section order for the NOAA output file
        :param str key:
        :param any value:
        :return none:
        """
        logger_lpd_noaa.info("enter reorganize")
        # If the key isn't in any list, stash it in number 13 for now
        number = 13
        for k, v in NOAA_SECTIONS.items():
            if key == "studyName":
                self.steps_dict[1][key] = value
                self.steps_dict[3][key] = value
            else:
                if key in v:
                    number = k
                self.steps_dict[number][key] = value
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
            \n# Template Version 2.0\
            \n# NOTE: Please cite Publication, Online_Resource and date accessed when using these data.\
            \n# If there is no publication information, please cite Investigators, Title, and Online_Resource "
            "and date accessed."
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

    def __write_k_v(self, k, v, top=False, bot=False, multi=False, tab=True):
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
                if tab:
                    self.noaa_txt.write("\n#     {}: {}".format(str(k), str(item)))
                else:
                    self.noaa_txt.write("\n# {}: {}".format(str(k), str(item)))
        else:
            if tab:
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

    @staticmethod
    def __reorganize_authors(d):
        """
        Create a combined string of authors from the pub list of authors
        :param dict d: Publication metadata
        :return:
        """
        s = ""
        # "author" is the correct key, but check for "authors" just in case.
        if "author" in d:
            key = "author"
        elif "authors" in d:
            key = "authors"
        try:
            l = d[key]
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
