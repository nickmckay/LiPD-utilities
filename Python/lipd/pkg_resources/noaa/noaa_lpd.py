from collections import OrderedDict
import os
import csv
import copy

from ..helpers.jsons import *
from ..helpers.bag import *
from ..helpers.alternates import *
from ..helpers.regexes import *
from ..helpers.blanks import *


class NOAA_LPD(object):

    def __init__(self, dir_root, dir_tmp, name):
        self.dir_root = dir_root
        self.dir_tmp = dir_tmp
        self.dir_bag = os.path.join(dir_tmp, name)
        self.name = name
        self.name_txt = name + '.txt'
        self.name_lpd = name + '.lpd'
        self.metadata = {}

    def main(self):
        """
        Convert a NOAA text file into a lipd file. CSV files will be created if chronology or data sections are available.
        :return: (dict) Metadata Dictionary
        """
        # Run the file through the parser
        # Sets self.metadata, Creates CSVs in dir_tmp
        os.chdir(self.dir_tmp)
        os.mkdir(self.name)
        os.chdir(self.dir_root)
        self.__parse()
        os.chdir(self.dir_bag)

        # Dump Metadata JSON to dir_tmp
        write_json_to_file(self.name + '.jsonld', self.metadata)

        # Create a bagit bag
        new_bag = create_bag(self.dir_bag)
        open_bag(self.dir_bag)
        new_bag.save(manifests=True)

        return

    def __parse(self):
        """
        Main parser
        Accept the text file. We'll open it, read it, and return a compiled dictionary to write to a json file
        May write a chronology CSV and a data CSV if those sections are available
        :param file (str):
        :param path (str):
        :param filename (str):
        :return:
        """
        # Strings
        last_insert = None
        missing_str = ''
        data_filename = ''

        # Counters
        grant_id = 0
        funding_id = 0
        data_col_ct = 1
        line_num = 0

        # Boolean markers
        description_on = False
        publication_on = False
        abstract_on = False
        site_info_on = False
        chronology_on = False
        chron_vars_start = True
        variables_on = False
        data_vals_on = False
        data_on = False

        # Lists
        lat = []
        lon = []
        pub = []
        funding = []
        temp_abstract = []
        temp_description = []
        chron_col_list = []
        data_var_names = []
        data_col_list = []
        data_tables = []

        # All dictionaries needed to create JSON structure
        temp_funding = OrderedDict()
        temp_pub = OrderedDict()
        vars_dict = OrderedDict()
        core_len = OrderedDict()
        geo_properties = OrderedDict()
        chron_dict = OrderedDict()
        data_dict_upper = OrderedDict()
        data_dict_lower = OrderedDict()
        final_dict = OrderedDict()

        # Open the text file in read mode. We'll read one line at a time until EOF
        with open(self.name_txt, 'r') as f:
            for line in iter(f):
                line_num += 1

                # PUBLICATION
                # There can be multiple publications. Create a dictionary for each one.
                if publication_on:

                    # End of the section. Add the dictionary for this one publication to the overall list
                    if '-----' in line:
                        temp_pub['abstract'] = ''.join(temp_abstract)
                        pub.append(temp_pub.copy())
                        temp_abstract.clear()
                        temp_pub.clear()
                        abstract_on = False
                        publication_on = False

                    elif abstract_on:
                        temp_abstract.append(self.__str_cleanup(line))

                    # Add all info into the current publication dictionary
                    else:
                        line = self.__str_cleanup(line)
                        key, value = self.__slice_key_val(line)
                        temp_pub[self.__camel_case(key)] = value
                        if key == 'Abstract':
                            abstract_on = True
                            temp_abstract.append(value)

                # DESCRIPTION
                # Descriptions are often long paragraphs spanning multiple lines, but don't follow the key/value format
                elif description_on:

                    # End of the section. Turn marker off and combine all the lines in the section
                    if '-------' in line:
                        description_on = False
                        value = ''.join(temp_description)
                        final_dict['description'] = value

                    # The first line in the section. Split into key, value
                    elif 'Description:' in line:
                        key, val = self.__slice_key_val(line)
                        temp_description.append(val)

                    # Keep a running list of all lines in the section
                    else:
                        line = self.__str_cleanup(line)
                        temp_description.append(line)

                # SITE INFORMATION (Geo)
                elif site_info_on:

                    if '-------' in line:
                        site_info_on = False

                    else:
                        line = self.__str_cleanup(line)
                        key, value = self.__slice_key_val(line)
                        if key.lower() in NOAA_SITE_INFO['lat']:
                            lat.append(self.__convert_num(value))

                        elif key.lower() in NOAA_SITE_INFO['lon']:
                            lon.append(self.__convert_num(value))

                        elif key.lower() in NOAA_SITE_INFO['properties']:
                            if key.lower() == 'elevation':
                                val, unit = self.__split_name_unit(value)
                                geo_properties['elevation'] = {'value': self.__convert_num(val), 'unit': unit}
                            else:
                                geo_properties[self.__camel_case(key)] = value

                # CHRONOLOGY
                elif chronology_on:

                    # When reaching the end of the chron section, set the marker to off and close the CSV file
                    if '-------' in line:
                        chronology_on = False

                        # If nothing between the chronology start and the end barrier, then there won't be a CSV
                        if chron_start_line != line_num-1:
                            chron_csv.close()

                    # Special case for first line in chron section. Grab variables and open a new CSV file
                    elif chron_vars_start:
                        chron_vars_start = False

                        # Open CSV for writing
                        chron_filename = self.name + '-chronology.csv'
                        csv_path = os.path.join(self.dir_bag, chron_filename)
                        chron_csv = open(csv_path, 'w+', newline='')
                        cw = csv.writer(chron_csv)

                        # Split the line into a list of variables
                        chron_col_ct = 1
                        line = line.lstrip()
                        variables = line.split('|')

                        # Create a dictionary of info for each column
                        for index, var in enumerate(variables):
                            temp_dict = OrderedDict()
                            temp_dict['column'] = chron_col_ct
                            name, unit = self.__split_name_unit(var.replace('\n', '').lstrip().rstrip())
                            temp_dict['parameter'] = name
                            temp_dict['units'] = unit
                            chron_col_list.append(temp_dict)
                            chron_col_ct += 1
                        chron_dict['filename'] = chron_filename
                        chron_dict['chronTableName'] = 'Chronology'
                        chron_dict['columns'] = chron_col_list

                    # Split the line of data values, then write to CSV file
                    else:
                        values = line.split()
                        cw.writerow(values)

                # VARIABLES
                # Variables are the only lines that have a double # in front
                elif variables_on:

                    process_line = False

                    # End of the section. Turn marker off
                    if "------" in line:
                        variables_on = False
                    for item in NOAA_VAR_LINES:
                        if item.lower() in line.lower():
                            process_line = False
                    for item in NOAA_EMPTY:
                        if item == line:
                            process_line = False
                    m = re.match(RE_VAR, line)
                    if m:
                        process_line = True

                    # If the line isn't in the ignore list, then it's a variable line
                    if process_line:
                        # Split the line items, and cleanup
                        cleaned_line = self.__separate_data_vars(line)

                        # Add the items into a column dictionary
                        data_col_dict = self.__create_var_col(cleaned_line, data_col_ct)

                        # Keep a list of all variable names
                        try:
                            data_var_names.append(data_col_dict['parameter'])
                        except KeyError:
                            data_var_names.append('')

                        # Add the column dictionary into a final dictionary
                        data_col_list.append(data_col_dict)
                        data_col_ct += 1

                # DATA
                # Missing Value, Create data columns, and output Data CSV
                elif data_on:

                    # Do not process lines that are blank, template lines, or missing value
                    process_line = True

                    for item in NOAA_DATA_LINES:
                        if item in line:
                            process_line = False
                    for item in NOAA_EMPTY:
                        if item == line:
                            process_line = False
                    for item in ALTS_MV:
                        if item in line.lower():
                            process_line = False
                            line = self.__str_cleanup(line)
                            key, missing_str = self.__slice_key_val(line)

                    if process_line:
                        # Split the line at each space (There's one space between each data item)
                        values = line.split()

                        # Write all data values to CSV
                        if data_vals_on:
                            dw.writerow(values)

                        # Check for the line of variables
                        else:

                            var = self.__str_cleanup(values[0].lstrip())
                            # Check if a variable name is in the current line
                            if var.lower() == data_var_names[0].lower():
                                data_vals_on = True

                                # Open CSV for writing
                                data_filename = self.name + '-data.csv'
                                csv_path = os.path.join(self.dir_bag, data_filename)
                                data_csv = open(csv_path, 'w+', newline='')
                                dw = csv.writer(data_csv)

                # METADATA
                else:
                    # Line Continuation: Sometimes there are items that span a few lines.
                    # If this happens, we want to combine them all properly into one entry.
                    if '#' not in line and line not in NOAA_EMPTY and old_val:
                        try:
                            if old_key in ('funding', 'agency'):
                                temp_funding[old_key] = old_val + line
                            else:
                                    final_dict[old_key] = old_val + line
                        except KeyError:
                            pass

                    # No Line Continuation: This is the start or a new entry
                    else:
                        line = self.__str_cleanup(line)

                        # Grab the key and value from the current line
                        try:
                            # Split the line into key, value pieces
                            key, value = self.__slice_key_val(line)
                            lkey = key.lower()

                            # If there is no value, then we are at a section header.
                            # Data often has a blank value, so that is a special check.
                            if value is None or lkey == 'data':

                                # Turn on markers if we run into section headers
                                if lkey == 'description_and_notes':
                                    description_on = True
                                elif lkey == 'publication':
                                    publication_on = True
                                elif lkey == 'site_information':
                                    site_info_on = True
                                elif lkey == 'chronology':
                                    chronology_on = True
                                    chron_start_line = line_num
                                elif lkey == 'variables':
                                    variables_on = True
                                elif lkey == 'data':
                                    data_on = True

                            # For all
                            else:

                                # Ignore any entries that are specified in the skip list
                                if lkey not in NOAA_KEYS:

                                    if lkey == 'core_length':
                                        val, unit = self.__split_name_unit(value)
                                        core_len['value'] = self.__convert_num(val)
                                        core_len['unit'] = unit
                                        last_insert = core_len

                                    # There can be multiple funding agencies and grants. Keep a list of dict entries
                                    elif lkey in FUNDING_LIST:
                                        if lkey == 'funding_agency_name':
                                            funding_id += 1
                                            key = 'agency'
                                        elif lkey == 'grant':
                                            grant_id += 1
                                            key = 'grant'
                                        temp_funding[key] = value

                                        # If both counters are matching, we are ready to add content to the funding list
                                        if grant_id == funding_id:
                                            funding.append(temp_funding.copy())
                                            temp_funding.clear()

                                    else:
                                        final_dict[self.__camel_case(key)] = value

                                    # Keep track of old key in case we have a line continuation
                                    old_key = key
                                    old_val = value.rstrip()
                        # Ignore any errors from NoneTypes that are returned from slice_key_val
                        except TypeError:
                            pass

        # Wait to close the data CSV until we reached the end of the text file
        try:
            data_csv.close()
        except NameError:
            print("Couldn't close Data CSV. Invalid formatting of variables/data sections in NOAA txt file")

        # Piece together measurements block
        data_dict_upper['filename'] = data_filename
        data_dict_upper['paleoDataTableName'] = 'Data'
        data_dict_upper['missingValue'] = missing_str
        data_dict_upper['columns'] = data_col_list
        data_tables.append(data_dict_upper)

        # Piece together geo block
        geo = self.__create_coordinates(lat, lon)
        geo['properties'] = geo_properties

        # Piece together final dictionary
        final_dict['pub'] = pub
        final_dict['funding'] = funding
        final_dict['geo'] = geo
        final_dict['coreLength'] = core_len
        final_dict['chronology'] = chron_dict
        final_dict['paleoData'] = data_tables

        # Insert the data dictionaries into the final dictionary
        for k, v in vars_dict.items():
            data_dict_lower[k] = v

        # Set final_dict to self.
        self.metadata = remove_empty_fields(final_dict)

        return

    @staticmethod
    def __create_var_col(l, col_count):
        """
        Receive split list from separate_data_vars, and turn it into a dictionary for that column
        :param l (list):
        :param col_count (int):
        :return: (dict) d
        """
        # Format: what, material, error, units, seasonality, archive, detail, method,
        # C or N for Character or Numeric data, direction of relation to climate (positive or negative)
        d = OrderedDict()
        d['column'] = col_count
        for index, item in enumerate(l):
            if index == 0:
                d['parameter'] = item
            elif index == 1:
                d['description'] = item
            elif index == 2:
                d['material'] = item
            elif index == 3:
                d['error'] = item
            elif index == 4:
                d['units'] = item
            elif index == 5:
                d['seasonality'] = item
            elif index == 6:
                d['archive'] = item
            elif index == 7:
                d['detail'] = item
            elif index == 8:
                d['method'] = item
            elif index == 9:
                d['dataType'] = item
            elif index == 10:
                d['direction'] = item
        return d

    @staticmethod
    def __separate_data_vars(line):
        """
        For the variables section, clean up the line and return a list of each of the 10 items
        :param line (str):
        :return: (str)
        """
        combine = []
        if '#' in line:
            line = line.replace("#", "")
            line = line.lstrip()
        if line not in NOAA_EMPTY and line not in EMPTY:

            m = re.match(RE_VAR_SPLIT, line)
            if m:
                combine.append(m.group(1))
                attr = m.group(3).split(',')
                combine += attr
                for index, string in enumerate(combine):
                    combine[index] = string.lstrip().rstrip()
                for i, s in enumerate(combine):
                    if not s or s in NOAA_EMPTY:
                        del combine[i]
        return combine

    @staticmethod
    def __convert_num(number):
        """
        All path items are automatically strings. If you think it's an int or float, this attempts to convert it.
        :param number (str):
        :return: (float)
        """
        try:
            return float(number)
        except ValueError:
            return number

    @staticmethod
    def __camel_case(word):
        """
        Convert underscore naming into camel case naming
        :param word (str):
        :return: (str)
        """
        word = word.lower()
        if '_' in word:
            split_word = word.split('_')
        else:
            split_word = word.split()
        if len(split_word) > 0:
            for i, word in enumerate(split_word):
                if i > 0:
                    split_word[i] = word.title()
        strings = ''.join(split_word)
        return strings

    @staticmethod
    def __name_unit_regex(word):
        """
        Split a name and unit that are bunched together (i.e. '250m')
        :param word (str):
        :return:
        """
        r = re.findall(r'(\d+)(\w+?)', word)
        value = r[0][0]
        unit = r[0][1]
        try:
            value = float(value)
        except ValueError:
            pass
        return value, unit

    @staticmethod
    def __contains_digits(word):
        """
        Check if the string contains digits
        :param word (str):
        :return:
        """
        return any(i.isdigit() for i in word)

    def __split_name_unit(self, line):
        """
        Split a string that has value and unit as one.
        :param line (str):
        :return:
        """
        if line != '' or line != ' ':
            # If there are parenthesis, remove them
            line = line.replace('(', '').replace(')', '')
            # When value and units are a range (i.e. '100 m - 200 m').
            if ' to ' in line or ' - ' in line:
                line = line.replace('to', '').replace('-', '')
                val_list = [int(s) for s in line.split() if s.isdigit()]
                unit_list = [s for s in line.split() if not s.isdigit()]
                # For items that did not split properly. Need regex split.
                for item in unit_list:
                    if self.__contains_digits(item):
                        unit_list = []
                        i, v = self.__name_unit_regex(item)
                        val_list.append(i)
                        unit_list.append(v)
                # Piece the number range back together.
                value = str(val_list[0]) + ' to ' + str(val_list[1])
                unit = unit_list[0]
            else:
                # Normal case. Value and unit separated by a space.
                if ' ' in line:
                    line = line.split()
                    value = line[0]
                    unit = ' '.join(line[1:])
                # No Value. Line only contains a unit.
                elif not self.__contains_digits(line):
                    value = 'n/a'
                    unit = line
                # Value and unit bunched together ('100m'). Use regex to identify groups.
                else:
                    value, unit = self.__name_unit_regex(line)
            return value, unit

    @staticmethod
    def __str_cleanup(line):
        """
        Remove the unnecessary characters in the line that we don't want
        :param line (str):
        :return: (str)
        """
        line = line.rstrip()
        if '#' in line:
            line = line.replace("#", "")
            line = line.lstrip()
        if '-----------' in line:
            line = ''

        return line

    @staticmethod
    def __slice_key_val(line):
        """
        Get the key and value items from a line by looking for and lines that have a ":"
        :param line (str):
        :return: (str) Key, (str) Value
        """
        position = line.find(":")
        # If value is -1, that means the item was not found in the string.
        if position != -1:
            key = line[:position]
            value = line[position+1:]
            value = value.lstrip()
            return key, value
        else:
            key = line
            value = None
            return key, value

    def __create_coordinates(self, lat, lon):
        """
        GeoJSON standard:
        Use to determine 2-point or 4-point coordinates
        :param lat (float):
        :param lon (float):
        :return: (dict)
        """

        # Sort lat an lon in numerical order
        lat.sort()
        lon.sort()
        # 4 coordinate values
        if len(lat) == 2 and len(lon) == 2:
            geo_dict = self.__geo_multipoint(lat, lon)
        # 2 coordinate values
        elif len(lat) == 1 and len(lon) == 1:
            geo_dict = self.__geo_point(lat, lon)
        else:
            geo_dict = {}
            print("More than 4 coordinates")
        return geo_dict

    def __geo_multipoint(self, lat, lon):
        """
        GeoJSON standard:
        Create a geoJson MultiPoint-type dictionary
        :param lat (float):
        :param lon (float):
        :return:
        """
        geo_dict = OrderedDict()
        geometry_dict = OrderedDict()
        coordinates = []
        # bbox = []
        temp = [None, None]

        # if the value pairs are matching, then it's not a real MultiPoint type. Send to other method
        if lat[0] == lat[1] and lon[0] == lon[1]:
            lat.pop()
            lon.pop()
            geo_dict = self.__geo_point(lat, lon)

        # 4 unique values
        else:
            # # Creates bounding box
            # for index, point in enumerate(lat):
            #     bbox.append(lat[index])
            #     bbox.append(lon[index])

            # Creates coordinates list
            for i in lat:
                temp[0] = i
                for j in lon:
                    temp[1] = j
                    coordinates.append(copy.copy(temp))

            # Create geometry block
            geometry_dict['type'] = 'Polygon'
            geometry_dict['coordinates'] = coordinates

            # Create geo block
            geo_dict['type'] = 'Featured'
            # geo_dict['bbox'] = bbox
            geo_dict['geometry'] = geometry_dict

        return geo_dict

    @staticmethod
    def __geo_point(lat, lon):
        """
        GeoJSON standard:
        Create a geoJson Point-type dictionary
        :param lat:
        :param lon:
        :return:
        """
        coordinates = []
        geo_dict = OrderedDict()
        geometry_dict = OrderedDict()
        for index, point in enumerate(lat):
            coordinates.append(lat[index])
            coordinates.append(lon[index])
        geometry_dict['type'] = 'Point'
        geometry_dict['coordinates'] = coordinates
        geo_dict['type'] = 'Feature'
        geo_dict['geometry'] = geometry_dict
        return geo_dict

