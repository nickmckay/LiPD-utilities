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
            logger_lpd_noaa.debug("csv_found: FileNotFound: no csv/couldn't open file, {}".format(e))
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
    def __get_identifier(l):
        """
        Get DOI id and url from identifier dictionary.
        :param list l: Identifier list. (Should only have one dictionary in it)
        :return str str: DOI id, DOI url
        """
        if not isinstance(l, str):
            try:
                doi_id = l[0]['id']
            except KeyError:
                doi_id = ''
            try:
                doi_url = l[0]['url']
            except KeyError:
                doi_url = ''
            return doi_id, doi_url
        return '', ''

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
                d[key] = ''
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
            filename = ''
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
        if length == 0:
            for location in locations:
                d[location] = ' '
        elif length == 2:
            d[locations[0]] = l[0]
            d[locations[1]] = l[1]
            d[locations[2]] = l[0]
            d[locations[3]] = l[1]
        elif length == 4:
            for index, location in enumerate(locations):
                d[locations[index]] = l[index]
        else:
            logger_lpd_noaa.info("coordinates: Too many coordinates given")
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
        noaa_txt = None
        try:
            noaa_txt = open(self.name_txt, "w+")
            logger_lpd_noaa.info("opened output txt file")
        except Exception as e:
            logger_lpd_noaa.debug("write_file: Failed to open output txt file, {}".format(e))

        if noaa_txt:
            self.__write_top(noaa_txt, 1)
            self.__write_generic(noaa_txt, 'Contribution_Date', 2, self.steps_dict[2])
            self.__write_generic(noaa_txt, 'Title', 3, self.steps_dict[3])
            self.__write_generic(noaa_txt, 'Investigators', 4, self.steps_dict[4])
            self.__write_generic(noaa_txt, 'Description_Notes_and_Keywords', 5, self.steps_dict[5])
            self.__write_pub(noaa_txt, self.steps_dict[6]['pub'])
            self.__write_funding(noaa_txt, self.steps_dict[7])
            self.__write_geo(noaa_txt, self.steps_dict[8])
            self.__write_generic(noaa_txt, 'Data_Collection', 9, self.steps_dict[9])
            self.__write_generic(noaa_txt, 'Species', 10, self.steps_dict[10])
            # self.write_chron(noaa_txt, self.steps_dict[11])

        # Run once for each table. Keep variables and related data grouped
        for table in self.steps_dict[12]['paleoData']:
            self.__write_variables(noaa_txt, table)
            self.__write_numbers(noaa_txt, table)
        noaa_txt.close()
        logger_lpd_noaa.info("closed output text file")
        shutil.copy(os.path.join(os.getcwd(), self.name_txt), self.dir_root)
        logger_lpd_noaa.info("exit write_file")
        return

    def __write_top(self, noaa_txt, section_num):
        """
        Write the top section of the txt file.
        :param obj noaa_txt: Output .txt file that is being written to.
        :param int section_num: Section number
        :return none:
        """
        logger_lpd_noaa.info("writing section: {}".format("top"))
        self.__create_blanks(section_num, self.steps_dict[section_num])
        noaa_txt.write(
            '# ' + self.steps_dict[section_num]['studyName'] +
            '\n#-----------------------------------------------------------------------\
            \n#                World Data Service for Paleoclimatology, Boulder\
            \n#                                  and\
            \n#                     NOAA Paleoclimatology Program\
            \n#             National Centers for Environmental Information (NCEI)\
            \n#-----------------------------------------------------------------------\
            \n# Template Version 2.0\
            \n# NOTE: Please cite Publication, and Online_Resource and date accessed when using these data.\
            \n# If there is no publication information, please cite Investigators, Title, and Online_Resource and date accessed.\
            \n# Online_Resource: ' + self.steps_dict[section_num]['onlineResource'] + '\
            \n#\
            \n# Original_Source_URL: ' + self.steps_dict[section_num]['originalSourceUrl'] + '\
            \n#\
            \n# Description/Documentation lines begin with #\
            \n# Data lines have no #\
            \n#\
            \n# Archive: ' + self.steps_dict[section_num]['archive'] + '\
            \n#\
            \n# Parameter_Keywords: ' + self.steps_dict[section_num]['parameterKeywords'] + '\
            \n#--------------------\n')
        logger_lpd_noaa.info("exit write_top")
        return

    def __write_generic(self, noaa_txt, header, section_num, d):
        """
        Write a generic section to the .txt. This function is reused for multiple sections.
        :param obj noaa_txt: Output .txt file that is being written to.
        :param str header: Header title for this section
        :param int section_num:
        :param dict d: Section from steps_dict
        :return none:
        """
        logger_lpd_noaa.info("writing section: {}".format(header))
        self.__create_blanks(section_num, d)
        noaa_txt.write('# ' + header + ' \n')
        for entry in NOAA_ORDERING[section_num]:
            if entry == 'coreLength':
                val, unit = self.__get_corelength(d[entry])
                noaa_txt.write('#   ' + self.__underscore(entry) + ': ' + str(val) + ' ' + str(unit) + '\n')
            elif entry == 'identifier':
                doi_id, doi_url = self.__get_identifier(d[entry])
                noaa_txt.write('#   DOI_id: ' + doi_id + '\n')
                noaa_txt.write('#   DOI_url: ' + doi_url + '\n')
            else:
                noaa_txt.write('#   ' + self.__underscore(entry) + ': ' + str(d[entry]) + '\n')
        noaa_txt.write('#------------------\n')
        return

    def __write_pub(self, noaa_txt, pub_root):
        """
        Write pub section. There may be multiple, so write a generic section for each one.
        :param obj noaa_txt: Output .txt file that is being written to.
        :param list pub_root: One or more pub dictionaries.
        :return none:
        """
        for idx, pub in enumerate(pub_root):
            logger_lpd_noaa.info("publication: {}".format(idx))
            self.__write_generic(noaa_txt, 'Publication', 6, pub)
        return

    def __write_funding(self, noaa_txt, d):
        """
        Write funding section. There are likely multiple entries.
        :param obj noaa_txt:
        :param dict d:
        :return none:
        """
        for key, fund_list in d.items():
            for idx, fund in enumerate(fund_list):
                logger_lpd_noaa.info("funding: {}".format(idx))
                self.__write_generic(noaa_txt, 'Funding_Agency', 7, fund)
        return

    def __write_geo(self, noaa_txt, d):
        """
        Write geo section. Organize before writing to file.
        :param obj noaa_txt:
        :param dict d:
        :return none:
        """
        for k, v in d.items():
            d = self.__reorganize_geo(v)
        self.__write_generic(noaa_txt, 'Site_Information', 8, d)
        return

    def __write_chron(self, noaa_txt, d):
        """
        Write chronology section.
        :param obj noaa_txt:
        :param dict d:
        :return none:
        """
        logger_lpd_noaa.info("writing section: {}".format("chronology"))
        noaa_txt.write('# Chronology:\n#\n')
        if self.__csv_found('chron'):
            cols = d['chronology']['columns']
            # Write variables line from dict_in
            for index, col in enumerate(cols):
                if index == 0:
                    noaa_txt.write('#       ' + col['variableName'] + ' (' + col['units'] + ')  | ')
                elif index == len(cols)-1:
                    noaa_txt.write(col['variableName'] + ' (' + col['units'] + ')\n')
                else:
                    noaa_txt.write(col['variableName'] + ' (' + col['units'] + ')  | ')
            # Iter over CSV and write line for line
            with open(self.name + '-chronology.csv', 'r') as f:
                for line in iter(f):
                    line = line.split(',')
                    for index, value in enumerate(line):
                        if index == 0:
                            noaa_txt.write('#          ' + str(value) + '              ')
                        elif index == len(line) - 1:
                            noaa_txt.write(str(value))
                        else:
                            noaa_txt.write(str(value) + '                 ')
        noaa_txt.write('#------------------\n')
        return

    def __write_numbers(self, noaa_txt, table):
        """
        Read numeric data from csv and write to the bottom section of the txt file.
        :param obj noaa_txt: Output text file
        :param dict table: Paleodata dictionary
        :return none:
        """
        logger_lpd_noaa.info("writing section: data, csv values from file")
        filename = self.__get_filename(table)
        logger_lpd_noaa.info("processing csv file: {}".format(filename))
        mv = self.__get_mv(table)
        noaa_txt.write('# Data:\
        \n# Data lines follow (have no #)\
        \n# Data line format - tab-delimited text, variable short name as header)\
        \n# Missing_Values: ' + mv + '\n#\n')

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
                    noaa_txt.write("{:<0}".format(param))
                else:
                    noaa_txt.write("{:<15}".format(param))
                    count -= 1
            noaa_txt.write('\n')
            # Iter over CSV and write line for line
            with open(filename, 'r') as f:
                logger_lpd_noaa.info("opened csv file: {}".format(filename))
                for line in iter(f):
                    line = line.split(',')
                    for index, value in enumerate(line):
                        if index == len(line) - 1:
                            noaa_txt.write("{:<0}".format(str(value)))
                        else:
                            noaa_txt.write("{:<15.10}".format(str(value)))
        noaa_txt.write('\n#\n#------------------\n')
        return

    def __write_variables(self, noaa_txt, table):
        """
        Retrieve variables from data table(s) and write to Variables section of txt file.
        :param obj noaa_txt: Output text file
        :param dict table: Paleodata dictionary
        :return none:
        """
        logger_lpd_noaa.info("writing section: {}".format("Variables"))
        filename = self.__get_filename(table)
        noaa_txt.write('# Variables\n#\
            \n# Filename: ' + filename +
            '\n#\n# Data variables follow that are preceded by "##" in columns one and two.\
            \n# Data line variables format:  Variables list, one per line, shortname-tab-longname-tab-longname components ( 9 components: what, material, error, units, seasonality, archive, detail, method, C or N for Character or Numeric data)\n#\n')
        try:
            for col in table['columns']:
                # Write one line for each column. One line has all metadata for one column.
                for entry in NOAA_ORDERING[11]:
                    # ---FIX--------FIX--------FIX--------FIX--------FIX-----
                    # May need a better way of handling this in the future. Need a strict list for this section.
                    try:
                        if entry == 'variableName':
                            # First entry: Double hash and tab
                            noaa_txt.write('{:<20}'.format('##' + col[entry]))
                        elif entry == 'dataType':
                            # Last entry: No space or comma
                            noaa_txt.write('{:<0}'.format(col[entry]))
                        else:
                            # Space and comma after middle entries
                            noaa_txt.write('{:<3}'.format(col[entry] + ', '))
                    except KeyError as e:
                        noaa_txt.write('{:<3}'.format(', '))
                        logger_lpd_noaa.warn("write_variables: KeyError: {} not found".format(e))
                noaa_txt.write('\n')
        except KeyError as e:
            logger_lpd_noaa.warn("write_variables: KeyError: {} not found".format(e))
        noaa_txt.write('#\n#------------------\n')
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
                if k == 'elevation':
                    d_tmp['elevation'] = str(v['value']) + ' ' + str(v['unit'])
                else:
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
            if key in v:
                if key == 'studyName':
                    self.steps_dict[3][key] = value
                number = k
        self.steps_dict[number][key] = value
        return

    # DEPRECATED

    # def __path_context(self, flat_file):
    #     """
    #     Turns the flattened json list back in to a usable dictionary structure
    #     :param list flat_file:
    #     :return dict:
    #     """
    #     new_dict = {}
    #     # Lists to recompile Values and Units
    #     elev = []
    #     core = []
    #     # Print out each item in the list for debugging
    #     for item in flat_file:
    #         split_list = self.__split_path(item)
    #         lst_len = len(split_list)
    #         value = split_list[lst_len-1]
    #         if 'Latitude' in split_list:
    #             if 'Max' in split_list:
    #                 new_dict['Northernmost_Latitude'] = value
    #             elif 'Min' in split_list:
    #                 new_dict['Southernmost_Latitude'] = value
    #         elif 'Longitude' in split_list:
    #             if 'Max' in split_list:
    #                 new_dict['Easternmost_Longitude'] = value
    #             elif 'Min' in split_list:
    #                 new_dict['Westernmost_Longitude'] = value
    #         elif 'Elevation' in split_list:
    #             elev.append(value)
    #
    #         elif 'CoreLength' in split_list:
    #             core.append(value)
    #         else:
    #             if len(split_list) > 2:
    #                 key = lst_len - 2
    #                 new_dict[split_list[key]] = value
    #             else:
    #                 new_dict[split_list[0]] = split_list[1]
    #     if core:
    #         new_dict['Core_Length'] = self.concat_units(core)
    #     if elev:
    #         new_dict['Elevation'] = self.concat_units(elev)
    #     return new_dict
