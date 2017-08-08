from collections import OrderedDict
import csv
import re
import os
import copy

from .misc import rm_empty_doi, rm_empty_fields
from .jsons import write_json_to_file
from .bag import finish_bag
from .alternates import NOAA_KEYS_BY_SECTION, UNITS, ALTS_MV
from .regexes import re_var, re_var_split, re_name_unit, re_name_unit_range, re_doi, re_var_w_units, re_tab_split
from .blanks import NOAA_EMPTY, NOAA_DATA_LINES, NOAA_VAR_LINES, EMPTY
from .loggers import create_logger

logger_noaa_lpd = create_logger("noaa_lpd")


class NOAA_LPD(object):

    def __init__(self, dir_root, dir_tmp, dsn):
        self.dir_root = dir_root
        self.dir_tmp = dir_tmp
        self.dir_bag = os.path.join(dir_tmp, "bag")
        self.dsn = dsn
        self.filename_txt = dsn + '.txt'
        self.filename_lpd = dsn + '.lpd'
        self.metadata = {}

    def main(self):
        """
        Convert a NOAA text file into a lipds file.
        CSV files will be created if chronology or data sections are available.
        :return dict: Metadata Dictionary
        """
        logger_noaa_lpd.info("enter main")
        # Run the file through the parser
        # Sets self.metadata, Creates CSVs in dir_tmp
        os.chdir(self.dir_tmp)
        os.mkdir("bag")
        os.chdir(self.dir_root)
        self.__parse()
        os.chdir(self.dir_bag)
        # Dump Metadata JSON to dir_tmp
        write_json_to_file(self.metadata)
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
        chron_vals_on = False
        variables_on = False
        data_vals_on = False
        data_on = False

        # Lists
        lat = []
        lon = []
        elev = []
        pub = []
        funding = []
        temp_abstract = []
        temp_description = []
        data_var_names = []
        data_col_list = []
        data_tables = []

        # All dictionaries needed to create JSON structure
        temp_funding = OrderedDict()
        temp_pub = OrderedDict()
        core_len = OrderedDict()
        geo_properties = OrderedDict()
        chron_dict = OrderedDict()
        data_dict_upper = OrderedDict()
        final_dict = OrderedDict()

        try:
            # Open the text file in read mode. We'll read one line at a time until EOF
            with open(self.filename_txt, 'r') as f:
                logger_noaa_lpd.info("opened noaa file: {}".format(self.filename_txt))
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
                            if key in ("Author", "Authors"):
                                temp_pub["author"] = self.__reorganize_authors(value)
                            else:
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
                            if key.lower() in ["northernmost_latitude", "southernmost_latitude"]:
                                lat.append(self.__convert_num(value))

                            elif key.lower() in ["easternmost_longitude", "westernmost_longitude"]:
                                lon.append(self.__convert_num(value))

                            elif key.lower() in ["site_name", "location", "country", "elevation"]:
                                if key.lower() == 'elevation':
                                    val, unit = self.__split_name_unit(value)
                                    elev.append(val)
                                else:
                                    geo_properties[self.__camel_case(key)] = value

                    # CHRONOLOGY
                    elif chronology_on:
                        """
                        HOW IT WORKS:
                        Chronology will be started at "Chronology:" section header
                        Every line starting with a "#" will be ignored
                        The first line without a "#" is considered the variable header line. Variable names are parsed.
                        Each following line will be considered column data and sorted accordingly.
                        Once the "-----" barrier is reached, we exit the chronology section.
                        """
                        # When reaching the end of the chron section, set the marker to off and close the CSV file
                        if '-------' in line:
                            # Turn off markers to exit section
                            chronology_on = False
                            chron_vals_on = False
                            try:
                                # If nothing between the chronology start and the end barrier, then there won't be a CSV
                                if chron_start_line != line_num - 1:
                                    try:
                                        chron_csv.close()
                                        logger_noaa_lpd.info("parse: chronology: no data found in chronology section")
                                    except NameError:
                                        logger_noaa_lpd.debug(
                                            "parse: chronology_on: NameError: chron_csv ref before assignment, {}".format(
                                                self.filename_txt))
                                        print(
                                            "Chronology section is incorrectly formatted. "
                                            "Section data will not be converted")

                                logger_noaa_lpd.info("end section: Chronology")
                            except NameError:
                                logger_noaa_lpd.debug(
                                    "parse: chronology_on: NameError: chron_start_line ref before assignment, {}".format(
                                        self.filename_txt))
                                print("Chronology section is incorrectly formatted. Section data will not be converted")

                        # Data values line. Split, then write to CSV file
                        elif chron_vals_on:
                            values = line.split()
                            try:
                                cw.writerow(values)
                            except NameError:
                                logger_noaa_lpd.debug(
                                    "parse: chronology_on: NameError: csv writer ref before assignment, {}".format(
                                        self.filename_txt))
                                print("Chronology section is incorrectly formatted. Section data will not be converted")

                        else:
                            try:
                                # Chron variable headers line
                                if line and line[0] != "#":
                                    chron_filename = self.dsn + '.chron1.measurementTable1.csv'
                                    # Organize the var header into a dictionary
                                    variables = self.__reorganize_chron_header(line)

                                    # Create a dictionary of info for each column
                                    chron_col_list = self.__create_chron_cols(variables)
                                    chron_dict['filename'] = chron_filename
                                    chron_dict['chronTableName'] = 'Chronology'
                                    chron_dict['columns'] = chron_col_list

                                    # Open CSV for writing
                                    csv_path = os.path.join(self.dir_bag, chron_filename)
                                    chron_csv = open(csv_path, 'w+', newline='')
                                    logger_noaa_lpd.info("opened csv file: {}".format(chron_filename))
                                    cw = csv.writer(chron_csv)
                                    # Turn the marker on to start processing the values columns
                                    chron_vals_on = True
                            except IndexError:
                                logger_noaa_lpd.debug("parse: chronology: IndexError when attempting chron var header")

                    # VARIABLES
                    elif variables_on:
                        """
                        HOW IT WORKS:
                        Variable lines are the only lines that have a "##" in front of them.
                        Ignore all lines that don't match the "##" regex.
                        Once there's a match, start parsing the variable lines, and create a column entry for each line.
                        """
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
                        m = re.match(re_var, line)
                        if m:
                            process_line = True

                        # If the line isn't in the ignore list, then it's a variable line
                        if process_line:

                            # Split the line items, and cleanup
                            cleaned_line = self.__separate_data_vars(line)

                            # Add the items into a column dictionary
                            data_col_dict = self.__create_paleo_col(cleaned_line, data_col_ct)

                            # Keep a list of all variable names
                            try:
                                # Use this list later to cross check with the variable line in the Data section
                                data_var_names.append(data_col_dict['variableName'])
                            except KeyError:
                                data_var_names.append('')
                                logger_noaa_lpd.warn("parse: variables: "
                                                     "KeyError: {} not found in {}".format("variableName", "data_col_dict"))
                            # Add the column dictionary into a final dictionary
                            data_col_list.append(data_col_dict)
                            data_col_ct += 1

                    # DATA
                    # Missing Value, Create data columns, and output Data CSV
                    elif data_on:
                        """
                        HOW IT WORKS:
                        Capture the "Missing Value" entry, if it exists.
                        Data lines should not have a "#" in front of them.
                        The first line without a "#" should be the variable header line
                        All lines that follow should have column data.
                        """
                        # Do not process blank or template lines
                        process_line = True
                        for item in NOAA_DATA_LINES:
                            if item in line:
                                process_line = False
                        for item in NOAA_EMPTY:
                            if item == line:
                                process_line = False
                        for item in ALTS_MV:
                            # Missing value found. Store entry
                            if item in line.lower():
                                process_line = False
                                line = self.__str_cleanup(line)
                                key, missing_str = self.__slice_key_val(line)

                        if process_line:
                            # Split the line at each space (There SHOULD one space between each variable. Not always true)
                            values = line.split()
                            # Write all data values to CSV
                            if data_vals_on:
                                try:
                                    dw.writerow(values)
                                except NameError:
                                    logger_noaa_lpd.debug(
                                        "parse: data_on: NameError: csv writer ref before assignment, {}".format(
                                            self.filename_txt))

                            # Check for the line of variables
                            else:
                                var = self.__str_cleanup(values[0].lstrip())
                                # Check if a variable name is in the current line
                                if var.lower() in line.lower():
                                    data_vals_on = True
                                    logger_noaa_lpd.info("start section: Data_Values")
                                    # Open CSV for writing
                                    data_filename = "{}.paleoData1.measurementTable1.csv".format(self.dsn)
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
                                    logger_noaa_lpd.debug(
                                        "parse: metadata: line continuation: {} not found in {}, {}".format(old_key,
                                                                                                            "temp_funding",
                                                                                                            e))
                            else:
                                try:
                                    final_dict[old_key] = old_val + line
                                except KeyError as e:
                                    logger_noaa_lpd.debug(
                                        "parse: metadata: line continuation: {} not found in {}, {}".format(old_key,
                                                                                                            "temp_funding",
                                                                                                            e))

                        # No Line Continuation: This is the start or a new entry
                        else:
                            line = self.__str_cleanup(line)

                            # Grab the key and value from the current line
                            try:
                                # Split the line into key, value pieces
                                key, value = self.__slice_key_val(line)
                                l_key = key.lower()
                                cc_key= self.__camel_case(key)

                                # If there is no value, then we are at a section header.
                                # Data often has a blank value, so that is a special check.
                                if not value or l_key == 'data':
                                    # Turn on markers if we run into section headers
                                    if l_key == 'description_and_notes':
                                        description_on = True
                                        logger_noaa_lpd.info("reading section: Description_and_Notes")
                                    elif l_key == 'publication':
                                        publication_on = True
                                        logger_noaa_lpd.info("reading section: Publication")
                                    elif l_key == 'site_information':
                                        site_info_on = True
                                        logger_noaa_lpd.info("reading section: Site_Information")
                                    elif l_key == 'chronology':
                                        chronology_on = True
                                        logger_noaa_lpd.info("reading section: Chronology")
                                        chron_start_line = line_num
                                    elif l_key == 'variables':
                                        variables_on = True
                                        logger_noaa_lpd.info("reading section: Variables")
                                    elif l_key == 'data':
                                        data_on = True
                                        logger_noaa_lpd.info("reading section: Data")
                                # For all
                                else:
                                    # Ignore any entries that are specified in the skip list
                                    _ignore = [item.lower() for item in NOAA_KEYS_BY_SECTION["Ignore"]]
                                    if l_key not in _ignore:
                                        # There can be multiple funding agencies and grants. Keep a list of dict entries
                                        _funding = [item.lower() for item in NOAA_KEYS_BY_SECTION["Funding_Agency"]]
                                        if l_key in _funding:
                                            if l_key == 'funding_agency_name':
                                                funding_id += 1
                                                key = 'agency'
                                            elif l_key == 'grant':
                                                grant_id += 1
                                                key = 'grant'
                                            temp_funding[key] = value
                                            # If both counters are matching, we are ready to add content to the funding list
                                            if grant_id == funding_id:
                                                funding.append(temp_funding.copy())
                                                temp_funding.clear()
                                        else:
                                            # There's likely two "Online_Resource"s, and we need both, so check and concat
                                            if cc_key == "onlineResource":
                                                # If it exists, append. If not, add entry as a list
                                                if cc_key in final_dict:
                                                    final_dict[cc_key].append(value)
                                                else:
                                                    final_dict[cc_key] = [value]
                                            else:
                                                final_dict[cc_key] = value
                                        # Keep track of old key in case we have a line continuation
                                        old_key = key
                                        old_val = value.strip()
                            except TypeError as e:
                                logger_noaa_lpd.warn(
                                    "parse: TypeError: none type received from slice_key_val, {}".format(e))

            # Wait to close the data CSV until we reached the end of the text file
            try:
                data_csv.close()
                logger_noaa_lpd.info("end section: Data_Values")
                logger_noaa_lpd.info("end section: Data")
            except NameError as e:
                print("Error: NOAA text file is contains format errors. Unable to process.")
                logger_noaa_lpd.debug(
                    "parse: NameError: failed to close csv, invalid formatting in NOAA txt file, {}".format(e))

            # Piece together measurements block
            logger_noaa_lpd.info("compiling final paleoData")
            data_dict_upper['filename'] = data_filename
            data_dict_upper['paleoDataTableName'] = 'Data'
            data_dict_upper['missingValue'] = missing_str
            data_dict_upper['columns'] = data_col_list
            data_tables.append(data_dict_upper)

            # Piece together geo block
            logger_noaa_lpd.info("compiling final geo")
            geo = self.__create_coordinates(lat, lon, elev)
            geo['properties'] = geo_properties

            # Piece together final dictionary
            logger_noaa_lpd.info("compiling final master")
            final_dict['pub'] = pub
            final_dict['funding'] = funding
            final_dict['geo'] = geo
            final_dict['coreLength'] = core_len
            final_dict['chronData'] = [{"chronMeasurementTable": chron_dict}]
            final_dict['paleoData'] = data_tables
            self.metadata = final_dict
            logger_noaa_lpd.info("final dictionary compiled")

            # Start cleaning up the metadata
            logger_noaa_lpd.info("removing empty fields")
            self.metadata = rm_empty_fields(self.metadata)
            logger_noaa_lpd.info("removing empty doi")
            self.metadata = rm_empty_doi(self.metadata)
            logger_noaa_lpd.info("removing irrelevant keys")
            self.__remove_irr_fields()

        except Exception as e:
            logger_noaa_lpd.debug("parse: {}".format(e))

        logger_noaa_lpd.info("exit parse")
        return

    @staticmethod
    def __create_paleo_col(l, col_count):
        """
        Receive split list from separate_data_vars, and turn it into a dictionary for that column
        :param list l:
        :param int col_count:
        :return dict:
        """
        # Format: what, material, error, units, seasonality, archive, detail, method,
        # C or N for Character or Numeric data, direction of relation to climate (positive or negative)
        d = OrderedDict()
        d['number'] = col_count
        for idx, var_name in enumerate(NOAA_KEYS_BY_SECTION["Variables"]):
            try:
                value = l[idx]
                # These two cases are nested in the column, so treat them special
                if var_name == "seasonality":
                    d["climateInterpretation"] = {var_name: value}
                elif var_name == "uncertainty":
                    d["calibration"] = {var_name: value}
                # All other cases are root items in the column, so add normally
                else:
                    d[var_name] = value
            except IndexError as e:
                logger_noaa_lpd.debug("create_var_col: IndexError: var: {}, {}".format(var_name, e))
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
            m = re.match(re_var_split, line)
            if m:
                combine.append(m.group(1))
                attr = m.group(2).split(',')
                combine += attr
                for index, string in enumerate(combine):
                    combine[index] = string.strip()
                # for i, s in enumerate(combine):
                #     if not s or s in NOAA_EMPTY:
                #         del combine[i]
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
        :return str str:
        """
        value = ""
        unit = ""
        r = re.findall(re_name_unit, word)
        try:
            value = r[0][0]
        except IndexError as e:
            logger_noaa_lpd.warn("name_unit_regex: IndexError: value: {}, {}, {}".format(word, r, e))
        try:
            unit = r[0][1]
            # Replace unit with correct synonym.
            if unit.lower() in UNITS:
                unit = UNITS[unit]
        except IndexError as e:
            logger_noaa_lpd.warn("name_unit_regex: IndexError: unit: {}, {}, {}".format(word, r, e))
        if value:
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
        vals = []
        unit = ''
        if line != '' or line != ' ':
            # If there are parenthesis, remove them
            line = line.replace('(', '').replace(')', '')
            # When value and units are a range (i.e. '100 m - 200 m').
            if re.match(re_name_unit_range, line):
                m = re.findall(re_name_unit_range, line)
                if m:
                    for group in m:
                        for item in group:
                            try:
                                val = float(item)
                                vals.append(val)
                            except ValueError:
                                if item:
                                    unit = item
                # Piece the number range back together.
                if len(vals) == 1:
                    value = vals[0]
                else:
                    value = str(vals[0]) + ' to ' + str(vals[1])
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
        if '#' in line:
            line = line.replace("#", "")
            line = line.strip()
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
            value = line[position + 1:]
            value = value.lstrip()
            return key, value
        else:
            key = line
            value = None
            return key, value

    def __create_coordinates(self, lat, lon, elev):
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
                geo_dict = self.__geo_point(lat, lon, elev)
            # 4 unique coordinates
            else:
                logger_noaa_lpd.info("coordinates found: {}".format("4"))
                geo_dict = self.__geo_multipoint(lat, lon, elev)
        # 2 coordinate values
        elif len(lat) == 1 and len(lon) == 1:
            logger_noaa_lpd.info("coordinates found: {}".format("2"))
            geo_dict = self.__geo_point(lat, lon, elev)
        # 0 coordinate values
        elif not lat and not lon:
            logger_noaa_lpd.info("coordinates found: {}".format("0"))
        else:
            geo_dict = {}
            logger_noaa_lpd.info("coordinates found: {}".format("too many"))
        return geo_dict

    @staticmethod
    def __geo_multipoint(lat, lon, elev):
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
        if elev:
            coordinates = coordinates + elev
        # Create geometry block
        geometry_dict['type'] = 'Polygon'
        geometry_dict['coordinates'] = coordinates
        # Create geo block
        geo_dict['type'] = 'Feature'
        # geo_dict['bbox'] = bbox
        geo_dict['geometry'] = geometry_dict

        return geo_dict

    @staticmethod
    def __geo_point(lat, lon, elev):
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
        if elev:
            coordinates = coordinates + elev
        geometry_dict['type'] = 'Point'
        geometry_dict['coordinates'] = coordinates
        geo_dict['type'] = 'Feature'
        geo_dict['geometry'] = geometry_dict
        return geo_dict

    @staticmethod
    def __reorganize_doi(temp_pub):
        """
        Create a valid bib json entry for the DOI information.
        "DOI" is technically the only valid DOI key, but there are sometimes a doi_id and doi_url entry.
        Check for all three and compare them, then keep whichever seems best.
        :param dict temp_pub:
        :return dict:
        """
        doi_out = ""
        doi_list = []
        rm = ["doiId", "doi", "doiUrl"]
        # Check if both entries exist
        if "doi" and "doiId" in temp_pub:
            if temp_pub["doi"] == temp_pub["doiId"]:
                # If the entries are the same, then pick one to use
                doi_out = temp_pub["doiId"]
            else:
                # If entries are not the same, check if it matches the regex pattern.
                if re_doi.findall(temp_pub["doiId"]):
                    doi_out = temp_pub["doiId"]
                # If it doesnt match the regex, just use the "doi" entry as-is
                else:
                    doi_out = temp_pub["doi"]
        # Check if "doiId" entry exists. Most common entry.
        elif "doiId" in temp_pub:
            doi_out = temp_pub["doiId"]
        # Check if "doi" entry exists. Fallback.
        elif "doi" in temp_pub:
            doi_out = temp_pub["doi"]
        # It's unlikely that ONLY the doi_url exists, but check if no doi found so far
        elif "doiUrl" in temp_pub:
            doi_out = temp_pub["doiUrl"]

        # Log if the DOI is invalid or not.
        if not re_doi.match(doi_out):
            logger_noaa_lpd.info("reorganize_doi: invalid doi input from NOAA file")

        # Get a list of all DOIs found in the string
        matches = re.findall(re_doi, doi_out)
        logger_noaa_lpd.info("reorganize_dois: found {} dois: {}".format(len(matches), doi_out))

        # Add identifier block to publication dictionary
        for doi in matches:
            doi_list.append({"type": "doi", "id": doi})

        # Remove the other DOI entries
        for k in rm:
            try:
                del temp_pub[k]
            except KeyError:
                # If there's a KeyError, don't worry about it. It's likely that only one of these keys will be present.
                pass

        temp_pub["identifier"] = doi_list
        return temp_pub

    def __remove_irr_fields(self):
        """
        Remove NOAA keys that don't have a place in the LiPD schema
        :return:
        """
        for key in NOAA_KEYS_BY_SECTION["Ignore"]:
            try:
                del self.metadata[key]
            except KeyError:
                # Key wasn't found. That's okay. No need for handling
                pass
        return



    @staticmethod
    def __create_chron_cols(metadata):
        """
        Use to collected chron metadata to create the chron columns
        :param dict metadata: key: variable, val: unit (optional)
        :return list: list of one dict per column
        """
        chron_col_list = []
        chron_col_ct = 1
        for variableName, unit in metadata.items():
            temp_dict = OrderedDict()
            temp_dict['column'] = chron_col_ct
            temp_dict['variableName'] = variableName
            temp_dict['unit'] = unit
            chron_col_list.append(copy.deepcopy(temp_dict))
            chron_col_ct += 1

        return chron_col_list

    @staticmethod
    def __reorganize_chron_header(line):
        """
        Reorganize the list of variables. If there are units given, log them.
        :param str line:
        :return dict: key: variable, val: units (optional)
        """
        d = {}
        # Header variables should be tab-delimited. Use regex to split by tabs
        m = re.split(re_tab_split, line)
        # If there was an output match from the line, then keep going
        if m:
            # Loop once for each variable in the line
            for s in m:
                # Match the variable to the 'variable (units)' regex to look for units
                m2 = re.match(re_var_w_units, s)
                # If there was a match
                if m2:
                    # If no units were found, set to blank
                    if m2.group(2) is None:
                        d[m2.group(1)] = ""
                    # Units were found
                    else:
                        # Set both values
                        d[m2.group(1)] = m2.group(2)
        return d

    @staticmethod
    def __reorganize_authors(authors):
        """
        Separate the string of authors and put it into a BibJSON compliant list
        :param str authors:
        :return list: List of dictionaries of author names.
        """
        # String SHOULD be semi-colon separated names.
        l = []
        s = authors.split(";")
        for author in s:
            try:
                l.append({"name": author.strip()})
            except AttributeError:
                logger_noaa_lpd.warning("reorganize_authors: AttributeError: authors incorrectly formatted")
        return l
