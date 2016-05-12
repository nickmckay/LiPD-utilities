from collections import OrderedDict
import os
import csv
import copy

from ..helpers.jsons import *
from ..helpers.bag import *
from ..helpers.alternates import *
from ..helpers.regexes import *
from ..helpers.blanks import *
from ..helpers.loggers import create_logger

logger_noaa_lpd = create_logger("noaa_lpd")


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
        :return dict: Metadata Dictionary
        """
        logger_noaa_lpd.info("enter main")
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
        finish_bag(self.dir_bag)
        logger_noaa_lpd.info("exit main")
        return

    def __parse(self):
        """
        Parse
        Accept the text file. We'll open it, read it, and return a compiled dictionary to write to a json file
        May write a chronology CSV and a data CSV if those sections are available
        :return:
        """
        logger_noaa_lpd.info("enter parse")
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
            logger_noaa_lpd.info("opened noaa file: {}".format(self.name_txt))
            for line in iter(f):
                line_num += 1

                # PUBLICATION
                # There can be multiple publications. Create a dictionary for each one.
                if publication_on:
                    # End of the section. Add the dictionary for this one publication to the overall list
                    if '-----' in line:
                        temp_pub = self.__reorganize_doi(temp_pub)
                        pub.append(temp_pub.copy())
                        temp_abstract.clear()
                        temp_pub.clear()
                        publication_on = False
                        logger_noaa_lpd.info("end section: Publication")
                    elif abstract_on:
                        # End of abstract: possibly more variables after.
                        if "#" in line:
                            abstract_on = False
                            temp_pub['abstract'] = ''.join(temp_abstract)
                            logger_noaa_lpd.info("end section: Abstract")
                            line = self.__str_cleanup(line)
                            key, value = self.__slice_key_val(line)
                            temp_pub[self.__camel_case(key)] = value
                        else:
                            temp_abstract.append(self.__str_cleanup(line))

                    # Add all info into the current publication dictionary
                    else:
                        line = self.__str_cleanup(line)
                        key, value = self.__slice_key_val(line)
                        temp_pub[self.__camel_case(key)] = value
                        if key == 'Abstract':
                            logger_noaa_lpd.info("reading section: Abstract")
                            abstract_on = True
                            temp_abstract.append(value)

                # DESCRIPTION AND NOTES
                # Descriptions are often long paragraphs spanning multiple lines, but don't follow the key/value format
                elif description_on:

                    # End of the section. Turn marker off and combine all the lines in the section
                    if '-------' in line:
                        description_on = False
                        value = ''.join(temp_description)
                        final_dict['description'] = value
                        logger_noaa_lpd.info("end section: Description_and_Notes")

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
                        logger_noaa_lpd.info("end section: Site_Information")

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
                            logger_noaa_lpd.info("parse: chronology: no data found in chronology section")
                        logger_noaa_lpd.info("end section: Chronology")

                    # Special case for first line in chron section. Grab variables and open a new CSV file
                    elif chron_vars_start:
                        chron_vars_start = False

                        # Open CSV for writing
                        chron_filename = self.name + '-chronology.csv'
                        csv_path = os.path.join(self.dir_bag, chron_filename)
                        chron_csv = open(csv_path, 'w+', newline='')
                        logger_noaa_lpd.info("opened csv file: {}".format(chron_filename))
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
                        logger_noaa_lpd.info("end section: Variables")
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
                            data_var_names.append(data_col_dict['variableName'])
                        except KeyError:
                            data_var_names.append('')
                            logger_noaa_lpd.warn("parse: variables: KeyError: {} not found in {}, {}".format("variableName", "data_col_dict", e))
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
                                logger_noaa_lpd.info("start section: Data_Values")
                                # Open CSV for writing
                                data_filename = self.name + '-data.csv'
                                csv_path = os.path.join(self.dir_bag, data_filename)
                                data_csv = open(csv_path, 'w+', newline='')
                                logger_noaa_lpd.info("opened csv file: {}".format(data_filename))
                                dw = csv.writer(data_csv)

                # METADATA
                else:
                    # Line Continuation: Sometimes there are items that span a few lines.
                    # If this happens, we want to combine them all properly into one entry.
                    if '#' not in line and line not in NOAA_EMPTY and old_val:
                        if old_key in ('funding', 'agency'):
                            try:
                                temp_funding[old_key] = old_val + line
                            except KeyError as e:
                                logger_noaa_lpd.debug("parse: metadata: line continuation: {} not found in {}, {}".format(old_key, "temp_funding", e))
                        else:
                            try:
                                final_dict[old_key] = old_val + line
                            except KeyError as e:
                                logger_noaa_lpd.debug("parse: metadata: line continuation: {} not found in {}, {}".format(old_key, "temp_funding", e))

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
                                    logger_noaa_lpd.info("reading section: Description_and_Notes")
                                elif lkey == 'publication':
                                    publication_on = True
                                    logger_noaa_lpd.info("reading section: Publication")
                                elif lkey == 'site_information':
                                    site_info_on = True
                                    logger_noaa_lpd.info("reading section: Site_Information")
                                elif lkey == 'chronology':
                                    chronology_on = True
                                    logger_noaa_lpd.info("reading section: Chronology")
                                    chron_start_line = line_num
                                elif lkey == 'variables':
                                    variables_on = True
                                    logger_noaa_lpd.info("reading section: Variables")
                                elif lkey == 'data':
                                    data_on = True
                                    logger_noaa_lpd.info("reading section: Data")
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
                        except TypeError as e:
                            logger_noaa_lpd.warn("parse: TypeError: none type received from slice_key_val, {}".format(e))

        # Wait to close the data CSV until we reached the end of the text file
        try:
            data_csv.close()
            logger_noaa_lpd.info("end section: Data_Values")
            logger_noaa_lpd.info("end section: Data")
        except NameError as e:
            print("Error: Invalid formatting in NOAA txt")
            logger_noaa_lpd.debug("parse: NameError: failed to close csv, invalid formatting in NOAA txt file, {}".format(e))

        # Piece together measurements block
        logger_noaa_lpd.info("compiling final paleoData")
        data_dict_upper['filename'] = data_filename
        data_dict_upper['paleoDataTableName'] = 'Data'
        data_dict_upper['missingValue'] = missing_str
        data_dict_upper['columns'] = data_col_list
        data_tables.append(data_dict_upper)

        # Piece together geo block
        logger_noaa_lpd.info("compiling final geo")
        geo = self.__create_coordinates(lat, lon)
        geo['properties'] = geo_properties

        # Piece together final dictionary
        logger_noaa_lpd.info("compiling final master")
        final_dict['pub'] = pub
        final_dict['funding'] = funding
        final_dict['geo'] = geo
        final_dict['coreLength'] = core_len
        final_dict['chronology'] = chron_dict
        final_dict['paleoData'] = data_tables
        logger_noaa_lpd.info("final dictionary compiled")

        # Insert the data dictionaries into the final dictionary
        # for k, v in vars_dict.items():
        #     data_dict_lower[k] = v

        # Set final_dict to self.
        logger_noaa_lpd.info("removing empty fields")
        self.metadata = remove_empty_fields(final_dict)
        logger_noaa_lpd.info("exit parse")
        return

    @staticmethod
    def __create_var_col(l, col_count):
        """
        Receive split list from separate_data_vars, and turn it into a dictionary for that column
        :param list l:
        :param int col_count:
        :return dict:
        """
        # Format: what, material, error, units, seasonality, archive, detail, method,
        # C or N for Character or Numeric data, direction of relation to climate (positive or negative)
        d = OrderedDict()
        d['column'] = col_count
        for idx, var_data in enumerate(l):
            try:
                var = NOAA_VAR_COLS[idx]
                # These two cases are nested in the column, so treat them special
                if var == "seasonality":
                    d["climateInterpretation"] = {var: var_data}
                elif var == "uncertainty":
                    d["calibration"] = {var: var_data}
                # All other cases are root items in the column, so add normally
                else:
                    d[var] = var_data
            except IndexError as e:
                logger_noaa_lpd.debug("create_var_col: IndexError: var: {}, {}".format(var_data, e))
        return d

    @staticmethod
    def __separate_data_vars(line):
        """
        For the variables section, clean up the line and return a list of each of the 10 items
        :param str line:
        :return str:
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
        :param str number:
        :return float or str:
        """
        try:
            return float(number)
        except ValueError as e:
            logger_noaa_lpd.warn("convert_num: ValueError: {}".format(e))
            return number

    @staticmethod
    def __camel_case(word):
        """
        Convert underscore naming into camel case naming
        :param str word:
        :return str:
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
        :param str word:
        :return:
        """
        r = re.findall(r'(\d+)(\w+?)', word)
        try:
            value = r[0][0]
            unit = r[0][1]
        except IndexError as e:
            logger_noaa_lpd.warn("name_unit_regex: IndexError: {}, {}".format(r, e))
        try:
            value = float(value)
        except ValueError as e:
            logger_noaa_lpd.warn("name_unit_regex: ValueError: val: {}, {}".format(value, e))
        return value, unit

    @staticmethod
    def __contains_digits(word):
        """
        Check if the string contains digits
        :param str word:
        :return:
        """
        return any(i.isdigit() for i in word)

    def __split_name_unit(self, line):
        """
        Split a string that has value and unit as one.
        :param str line:
        :return str str:
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
        :param str line:
        :return str:
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
        :param str line:
        :return str str: Key, Value
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
        :param list lat:
        :param list lon:
        :return dict:
        """
        # Sort lat an lon in numerical order
        lat.sort()
        lon.sort()
        geo_dict = {}
        # 4 coordinate values
        if len(lat) == 2 and len(lon) == 2:
            # Matching coordinate pairs. Not 4 unique values.
            if lat[0] == lat[1] and lon[0] == lon[1]:
                logger_noaa_lpd.info("coordinates found: {}".format("2"))
                lat.pop()
                lon.pop()
                geo_dict = self.__geo_point(lat, lon)
            # 4 unique coordinates
            else:
                logger_noaa_lpd.info("coordinates found: {}".format("4"))
                geo_dict = self.__geo_multipoint(lat, lon)
        # 2 coordinate values
        elif len(lat) == 1 and len(lon) == 1:
            logger_noaa_lpd.info("coordinates found: {}".format("2"))
            geo_dict = self.__geo_point(lat, lon)
        # 0 coordinate values
        elif not lat and not lon:
            logger_noaa_lpd.info("coordinates found: {}".format("0"))
        else:
            geo_dict = {}
            logger_noaa_lpd.info("coordinates found: {}".format("too many"))
        return geo_dict

    @staticmethod
    def __geo_multipoint(lat, lon):
        """
        GeoJSON standard:
        Create a geoJson MultiPoint-type dictionary
        :param list lat:
        :param list lon:
        :return dict:
        """
        logger_noaa_lpd.info("enter geo_multipoint")
        geo_dict = OrderedDict()
        geometry_dict = OrderedDict()
        coordinates = []
        # bbox = []
        temp = [None, None]
        # 4 unique values
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
        geo_dict['type'] = 'Feature'
        # geo_dict['bbox'] = bbox
        geo_dict['geometry'] = geometry_dict

        return geo_dict

    @staticmethod
    def __geo_point(lat, lon):
        """
        GeoJSON standard:
        Create a geoJson Point-type dictionary
        :param list lat:
        :param list lon:
        :return dict:
        """
        logger_noaa_lpd.info("enter geo_point")
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

    @staticmethod
    def __reorganize_doi(temp_pub):
        """
        Create a valid bib json entry for the DOI information.
        :param dict temp_pub:
        :return dict:
        """
        doi_out = ''
        rm = ["doiId", "doi", "doiUrl"]
        # Check if both entries exist
        if "doi" and "doiId" in temp_pub:
            if temp_pub["doi"] == temp_pub["doiId"]:
                # If the entries are the same, then pick one to use
                doi_out = temp_pub["doi"]
            else:
                # If entries are not the same, check if it matches the regex pattern.
                if DOI.match(temp_pub["doiId"]):
                    doi_out = temp_pub["doiId"]
                # If it doesnt match the regex, just use the "doi" entry as-is
                else:
                    doi_out = temp_pub["doi"]
        # Check if "doi" entry exists
        elif "doi" in temp_pub:
            doi_out = temp_pub["doi"]
        # Check if "doiId" entry exists
        elif "doiId" in temp_pub:
            doi_out = temp_pub["doiId"]

        # Log if the DOI is invalid or not.
        if not DOI.match(doi_out):
            logger_noaa_lpd.info("reorganize_doi: invalid doi input from NOAA file")
        # Add identifier block to publication dictionary
        temp_pub["identifier"] = [{"type": "doi", "id": doi_out}]
        # Remove the other DOI entries
        for k in rm:
            try:
                del temp_pub[k]
            except KeyError:
                # If there's a KeyError, don't worry about it. It's likely that only one of these keys will be present.
                pass
        return temp_pub
