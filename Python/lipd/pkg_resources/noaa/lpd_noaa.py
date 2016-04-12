import os
import shutil

from ..helpers.alternates import *
from ..helpers.regexes import *


class LPD_NOAA(object):
    """
    Creates a NOAA object that contains all the functions needed to write out a LiPD file as a NOAA text file.
    :return: (txt) NOAA File
    """

    def __init__(self, dir_root, name, root_dict):
        """
        :param dir_root: (str) Path to dir containing all .lpd files
        :param name: (str) Name of current .lpd file
        :param root_dict: (dict) Full dict loaded from jsonld file
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
        :param filename: (str) Name of the file to open.
        :return: none
        """
        found = False

        # Current Directory
        # tmp/filename/data (access to jsonld, changelog, csv, etc)

        try:
            # Attempt to open csv
            if open(filename):
                found = True
                # print("{0} - found {1} csv".format(filename, datatype))
        except FileNotFoundError:
            # print("{0} - no {1} csv".format(filename, datatype))
            pass
        return found

    @staticmethod
    def __get_mv(d):
        """
        Get missing value from root of data table dictionary.
        :param d: (dict) Data table
        :return: (str) Missing value or empty str.
        """
        if 'missingValue' in d:
            return d['missingValue']
        return ''

    @staticmethod
    def __underscore(key):
        """
        Convert camelCase to underscore
        :param key: (str) Key or title name
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
        :param string: (str) Path string ("geo-elevation-height")
        :return out: (list) Path as a list of strings. One entry per path step.(["geo", "elevation", "height"])
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
        :param d:
        :return val, unit:(int) Value (str) Unit
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
        :param d: (list) Identifier list. (Should only have one dictionary in it)
        :return: (str) DOI id, (str) DOI url
        """
        if not isinstance(d, str):
            try:
                doi_id = d[0]['id']
            except KeyError:
                doi_id = ''
            try:
                doi_url = d[0]['url']
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
        :param section_num: (int) Retrieve data from global dict for this number.
        :param d: (dict) Section of steps_dict
        :return: none
        """
        for key in NOAA_ORDERING[section_num]:
            if key not in d and key not in NOAA_SECTIONS[13]:
                # Key not in our dict. Create the blank entry.
                d[key] = ''
        return

    @staticmethod
    def __get_filename(table):
        try:
            filename = table['filename']
        except KeyError:
            filename = ''
        return filename

    @staticmethod
    def __coordinates(l, d):
        """
        Reorganize coordinates based on how many values are available.
        :param l: (list of float) Coordinate values
        :param d: (dict) Location with cooresponding values
        :return:
        """

        length = len(l)
        locations = ['northernmostLatitude', 'easternmostLongitude', 'southernmostLatitude', 'westernmostLongitude']

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

        return d

    def main(self):
        """
        Load in the template file, and run through the parser
        :return:
        """

        # Starting Directory: dir_tmp/dir_bag/data/

        # NOAA files are organized in sections, but jld is not. Reorganize to match NOAA template.
        for k, v in self.root_dict.items():
            self.__reorganize(k, v)

        # Use data in steps_dict to write to
        self.__write_file()

        return

    def __write_file(self):
        """
        Open text file. Write one section at a time. Close text file. Move completed file to dir_root/noaa/
        :return: none
        """

        noaa_txt = open(self.name_txt, "w+")
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
        shutil.copy(os.path.join(os.getcwd(), self.name_txt), self.dir_root)
        return

    def __write_top(self, noaa_txt, section_num):
        """
        Write the top section of the txt file.
        :param noaa_txt: (obj) Output .txt file that is being written to.
        :param section_num: (int) Section number
        :return: none
        """
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

        return

    def __write_generic(self, noaa_txt, header, section_num, d):
        """
        Write a generic section to the .txt. This function is reused for multiple sections.
        :param noaa_txt: (obj) Output .txt file that is being written to.
        :param header: (str) Header title for this section
        :param section_num: (int)
        :param d: (dict) Section from steps_dict
        :return: none
        """
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
        :param noaa_txt: (obj) Output .txt file that is being written to.
        :param pub_root: (list) One or more pub dictionaries.
        :return: none
        """
        for pub in pub_root:
            self.__write_generic(noaa_txt, 'Publication', 6, pub)
        return

    def __write_funding(self, noaa_txt, d):
        """

        :param noaa_txt:
        :param d:
        :return:
        """
        for key, fund_list in d.items():
            for fund in fund_list:
                self.__write_generic(noaa_txt, 'Funding_Agency', 7, fund)
        return

    def __write_geo(self, noaa_txt, d):
        """

        :param noaa_txt:
        :param d:
        :return:
        """
        for k, v in d.items():
            d = self.__reorganize_geo(v)
        self.__write_generic(noaa_txt, 'Site_Information', 8, d)
        return

    def __write_chron(self, noaa_txt, d):
        """

        :param file_in:
        :param noaa_txt:
        :param d:
        :return:
        """
        noaa_txt.write('# Chronology:\n#\n')

        if self.__csv_found('chron'):
            cols = d['chronology']['columns']
            # Write variables line from dict_in
            for index, col in enumerate(cols):
                if index == 0:
                    noaa_txt.write('#       ' + col['parameter'] + ' (' + col['units'] + ')  | ')
                elif index == len(cols)-1:
                    noaa_txt.write(col['parameter'] + ' (' + col['units'] + ')\n')
                else:
                    noaa_txt.write(col['parameter'] + ' (' + col['units'] + ')  | ')
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
        :param noaa_txt:(obj) Output text file
        :param table: (dict) Paleodata dictionary
        :return: none
        """

        filename = self.__get_filename(table)
        mv = self.__get_mv(table)
        noaa_txt.write('# Data:\
        \n# Data lines follow (have no #)\
        \n# Data line format - tab-delimited text, variable short name as header)\
        \n# Missing_Values: ' + mv + '\n#\n')

        if self.__csv_found(filename):
            # Write variables line from dict_in
            count = len(table['columns'])
            for col in table['columns']:
                try:
                    param = col['parameter']
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
        :param noaa_txt:(obj) Output text file
        :param table: (dict) Paleodata dictionary
        :return: none
        """
        filename = self.__get_filename(table)
        noaa_txt.write('# Variables\n#\
            \n# Filename: ' + filename +
            '\n#\n# Data variables follow that are preceded by "##" in columns one and two.\
            \n# Data line variables format:  Variables list, one per line, shortname-tab-longname-tab-longname components ( 9 components: what, material, error, units, seasonality, archive, detail, method, C or N for Character or Numeric data)\n#\n')
        for col in table['columns']:
            # Write one line for each column. One line has all metadata for one column.
            for entry in NOAA_ORDERING[11]:
                # ---FIX--------FIX--------FIX--------FIX--------FIX-----
                # May need a better way of handling this in the future. Need a strict list for this section.
                try:
                    if entry == 'parameter':
                        # First entry: Double hash and tab
                        noaa_txt.write('{:<20}'.format('##' + col[entry]))
                    elif entry == 'dataType':
                        # Last entry: No space or comma
                        noaa_txt.write('{:<0}'.format(col[entry]))
                    else:
                        # Space and comma after middle entries
                        noaa_txt.write('{:<3}'.format(col[entry] + ', '))
                except KeyError:
                    noaa_txt.write('{:<3}'.format(', '))
            noaa_txt.write('\n')
        noaa_txt.write('#\n#------------------\n')
        return

    def __reorganize_geo(self, d):
        """
        Concat geo value and units, and reorganize the rest
        :param d:
        :return:
        """

        # The new dict that will be returned
        d_tmp = {}

        # Properties
        try:
            for k, v in d['properties'].items():
                if k == 'elevation':
                    d_tmp['elevation'] = str(v['value']) + ' ' + str(v['unit'])
                else:
                    d_tmp[k] = v
            # Geometry
            d_tmp = self.__coordinates(d['geometry']['coordinates'], d_tmp)

        except KeyError:
            d_tmp = {}

        return d_tmp

    def __reorganize(self, key, value):
        """

        :param dict_in:
        :param key:
        :param value:
        :return:
        """

        # If the key isn't in any list, stash it in number 13 for now
        number = 13

        if key in NOAA_SECTIONS[1]:
            # StudyName only triggers once, append to section 3 also
            if key == 'studyName':
                self.steps_dict[3][key] = value
            number = 1
        elif key in NOAA_SECTIONS[2]:
            number = 2
        elif key in NOAA_SECTIONS[4]:
            number = 4
        elif key in NOAA_SECTIONS[5]:
            number = 5
        elif key in NOAA_SECTIONS[6]:
            number = 6
        elif key in NOAA_SECTIONS[7]:
            number = 7
        elif key in NOAA_SECTIONS[8]:
            number = 8
        elif key in NOAA_SECTIONS[9]:
            number = 9
        elif key in NOAA_SECTIONS[10]:
            number = 10
        elif key in NOAA_SECTIONS[11]:
            number = 11
        elif key in NOAA_SECTIONS[12]:
            number = 12
        self.steps_dict[number][key] = value

        return

    def __path_context(self, flat_file):
        """
        Turns the flattened json list back in to a usable dictionary structure
        :param flat_file:
        :return:
        """

        new_dict = {}

        # Lists to recompile Values and Units
        elev = []
        core = []

        # Print out each item in the list for debugging
        for item in flat_file:
            split_list = self.__split_path(item)
            lst_len = len(split_list)
            value = split_list[lst_len-1]

            if 'Latitude' in split_list:
                if 'Max' in split_list:
                    new_dict['Northernmost_Latitude'] = value

                elif 'Min' in split_list:
                    new_dict['Southernmost_Latitude'] = value

            elif 'Longitude' in split_list:
                if 'Max' in split_list:
                    new_dict['Easternmost_Longitude'] = value

                elif 'Min' in split_list:
                    new_dict['Westernmost_Longitude'] = value

            elif 'Elevation' in split_list:
                elev.append(value)

            elif 'CoreLength' in split_list:
                core.append(value)

            else:
                if len(split_list) > 2:
                    key = lst_len - 2
                    new_dict[split_list[key]] = value

                else:
                    new_dict[split_list[0]] = split_list[1]

        if core:
            new_dict['Core_Length'] = self.concat_units(core)
        if elev:
            new_dict['Elevation'] = self.concat_units(elev)

        return new_dict
