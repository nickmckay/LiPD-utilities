__author__ = 'chrisheiser1'
from collections import OrderedDict
import json
import os
import csv
import re
import copy

"""
README

Accepts files with UTF-8 encoding.
Convert a NOAA text file into a lipd file. CSV files will output if chronology or data sections are available.

How to use:
 1. Run the program
 2. Select directory on your computer that contains NOAA text files
 3. The console will show all files that are being processed
 4. When complete, the output files are in the directory you selected in an "output" folder.
"""

"""
CHANGE LOG

    Revision 0
    DONE - Strip the # and the white space on the left and right of strings
    DONE - Try to capture all the info with ":", because that's data we want
    DONE - Figure out how to capture the data cols and maybe put it in a list(?)
    DONE - do you need to lowercase all the strings?
    DONE - Piece together all the dictionaries into the final dictionaries
    DONE - Determine which info from the NOAA text file that we want to keep (waiting on Nick)
    DONE - get rid of K-V's that are in the dictionary blocks. It's adding duplicates at the root level.
    DONE - Get rid of blank values. Stop them from adding to the dictionary
    DONE - Figure out what to do with coreLength val and unit

    Revision 1
    DONE - Decide what to do with Chron data columns
    DONE - Capture variables section and use it later to cross-check the data section
    DONE - Output Data columns to CSV
    DONE - Strip '\n' from lines, and rstrip() also
    DONE - Data columns are overwriting each other
    DONE - Convert all names to JSONLD naming (method to convert to camel casing)
    DONE - Fix case where Variables section doesn't have double ## marks
    DONE - update to have same measurements columns as old format
    DONE - update to have consistent naming as old format
    DONE - add meastablename and filename (csv) fields
    DONE - change the formatting for the funding block. new structure
    DONE - description and notes section needs special parsing
    DONE - yamalia - fix values that span multiple lines (i.e. abstract, description and notes)
    DONE - account for elevations that are a range and not just a single number
    DONE - parse lat and long data into the new geojson format, include point and multiPoint cases
    DONE - handle multiple publication sections
    DONE - Test compatibility on all LMR files
    DONE - make sure number values are being converted from str to float
    - remove "in" when units are in format "in cm" to make it look cleaner


    # How to properly loop with enumerate
    for index, val in enumerate(values):
        values[index] = val.lstrip()

"""


# Receive split list from separate_data_vars, and turn it into a dictionary for that column
# Accept list, return dictionary
def create_var_col(list_in, col_count):
    # Format: what, material, error, units, seasonality, archive, detail, method,
    # C or N for Character or Numeric data, direction of relation to climate (positive or negative)
    dict_out = OrderedDict()
    dict_out['column'] = col_count
    for index, item in enumerate(list_in):
        if index == 0:
            dict_out['parameter'] = item
        elif index == 1:
            dict_out['description'] = item
        elif index == 2:
            dict_out['material'] = item
        elif index == 3:
            dict_out['error'] = item
        elif index == 4:
            dict_out['units'] = item
        elif index == 5:
            dict_out['seasonality'] = item
        elif index == 6:
            dict_out['archive'] = item
        elif index == 7:
            dict_out['detail'] = item
        elif index == 8:
            dict_out['method'] = item
        elif index == 9:
            dict_out['dataType'] = item
        elif index == 10:
            dict_out['direction'] = item
    return dict_out


# For the variables section, clean up the line and return a list of each of the 10 items
# Accepts string, returns list
def separate_data_vars(line):
    if '#' in line:
        line = line.replace("#", "")
        line = line.lstrip()
    a = line.split('\t')
    b = a[1].split(',')
    a.pop()
    c = a + b
    for index, string in enumerate(c):
        c[index] = string.lstrip().rstrip()
    return c


# All path items are automatically strings. If you think it's an int or float, this attempts to convert it.
# Accept string, return float
def convert_num(number):
    try:
        return float(number)
    except ValueError:
        return number


# Convert underscore naming into camel case naming
# Accept string, return string
def camelCase(word):
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


# Split a name and unit that are bunched together (i.e. '250m')
def name_unit_regex(word):
    r = re.findall(r'(\d+)(\w+?)', word)
    value = r[0][0]
    unit = r[0][1]
    return value, unit


# Check if the string contains digits
def contains_digits(word):
    return any(i.isdigit() for i in word)


# Split a string that has value and unit as one.
def split_name_unit(line):
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
                if contains_digits(item):
                    unit_list = []
                    i, v = name_unit_regex(item)
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
            elif not contains_digits(line):
                value = 'n/a'
                unit = line
            # Value and unit bunched together ('100m'). Use regex to identify groups.
            else:
                value, unit = name_unit_regex(line)
        return value, unit


# Remove the unnecessary characters in the line that we don't want
# Accept string, return string
def str_cleanup(line):
    line = line.rstrip()
    if '#' in line:
        line = line.replace("#", "")
        line = line.lstrip()
    if '-----------' in line:
        line = ''

    return line


# Get the key and value items from a line by looking for and lines that have a ":"
# Accepts string, return two strings
def slice_key_val(line):
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


# Use to determine 2-point or 4-point coordinates
# Return geometry dict, and (multipoint/bbox or point) type
def create_coordinates(lat, lon):

    # Sort lat an lon in numerical order
    lat.sort()
    lon.sort()
    # 4 coordinate values
    if len(lat) == 2 and len(lon) == 2:
        geo_dict = geo_multipoint(lat, lon)
    # 2 coordinate values
    elif len(lat) == 1 and len(lon) == 1:
        geo_dict = geo_point(lat,lon)
    else:
        geo_dict = {}
        print("More than 4 coordinates")
    return geo_dict


# Create a geoJson MultiPoint-type dictionary
def geo_multipoint(lat, lon):

    geo_dict = OrderedDict()
    geometry_dict = OrderedDict()
    coordinates = []
    # bbox = []
    temp = [None, None]

    # if the value pairs are matching, then it's not a real MultiPoint type. Send to other method
    if lat[0] == lat[1] and lon[0] == lon[1]:
        lat.pop()
        lon.pop()
        geo_dict = geo_point(lat, lon)

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


# Create a geoJson Point-type dictionary
def geo_point(lat, lon):

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


# Main parser.
# Accept the text file. We'll open it, read it, and return a compiled dictionary to write to a json file
# May write a chronology CSV and a data CSV if those sections are available
def parse(file, path, filename):

    # Strings
    last_insert = None
    missing_str = ''

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
    coreLen = OrderedDict()
    geo_properties = OrderedDict()
    chron_dict = OrderedDict()
    data_dict_upper = OrderedDict()
    data_dict_lower = OrderedDict()
    final_dict = OrderedDict()

    # List of items that we don't want to output
    ignore_keys = ['earliest_year', 'most_recent_year', 'note']
    ignore_var_lines = ['have no #', 'variables',
                        'lines begin with #',
                        'double marker',
                        'line variables format',
                        'line format',
                        'c or n for character or numeric',
                        'preceded by'
                        ]
    ignore_data_lines = ['have no #',
                         'tab-delimited text',
                         'age ensembles archived']
    ignore_blanks = ['\n', '', '#\n', '# \n', ' ']

    # Missing value name appears as many variations. Try to account for all of them
    missing_val_alts = ['missing value', 'missing values', 'missingvalue', 'missingvalues', 'missing_values',
                        'missing variables', 'missing_variables', 'missingvariables']

    # Lists for what keys go in specific dictionary blocks
    site_info = {'lat': ['northernmostlatitude', 'northernmost latitude', 'northernmost_latitude',
                         'southernmostlatitude', 'southernmost latitude', 'southernmost_latitude'],
                 'lon': ['easternmostlongitude', 'easternmost longitude', 'easternmost_longitude',
                         'westernmostlongitude', 'westernmost longitude', 'westernmost_longitude'],
                 'properties': ['location', 'country', 'elevation', 'site_name', 'region'],
                 }
    funding_lst = ['funding_agency_name', 'grant']

    # Open the text file in read mode. We'll read one line at a time until EOF
    with open(file, 'r') as f:

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
                    temp_abstract.append(str_cleanup(line))

                # Add all info into the current publication dictionary
                else:
                    line = str_cleanup(line)
                    key, value = slice_key_val(line)
                    temp_pub[camelCase(key)] = value
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
                    key, val = slice_key_val(line)
                    temp_description.append(val)

                # Keep a running list of all lines in the section
                else:
                    line = str_cleanup(line)
                    temp_description.append(line)

            # SITE INFORMATION (Geo)
            elif site_info_on:

                if '-------' in line:
                    site_info_on = False

                else:
                    line = str_cleanup(line)
                    key, value = slice_key_val(line)
                    if key.lower() in site_info['lat']:
                        lat.append(convert_num(value))

                    elif key.lower() in site_info['lon']:
                        lon.append(convert_num(value))

                    elif key.lower() in site_info['properties']:
                        if key.lower() == 'elevation':
                            val, unit = split_name_unit(value)
                            geo_properties['elevation'] = {'value': convert_num(val), 'unit': unit}
                        else:
                            geo_properties[camelCase(key)] = value

            # CHRONOLOGY
            elif chronology_on:

                # When reaching the end of the chron section, set the marker to off and close the CSV file
                if '-------' in line:
                    chronology_on = False

                    # If there is nothing between the chronology start and the end barrier, then there won't be a CSV
                    if chron_start_line != line_num-1:
                        chron_csv.close()

                # Special case for first line in chron section. Grab variables and open a new CSV file
                elif chron_vars_start:
                    chron_vars_start = False

                    # Open CSV for writing
                    chron_filename = filename + '-chronology.csv'
                    csv_path = path + '/' + chron_filename
                    chron_csv = open(csv_path, 'w', newline='')
                    cw = csv.writer(chron_csv)

                    # Split the line into a list of variables
                    chron_col_ct = 1
                    line = line.lstrip()
                    variables = line.split('|')

                    # Create a dictionary of info for each column
                    for index, var in enumerate(variables):
                        temp_dict = OrderedDict()
                        temp_dict['column'] = chron_col_ct
                        name, unit = split_name_unit(var.replace('\n', '').lstrip().rstrip())
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

                process_line = True

                # End of the section. Turn marker off
                if "------" in line:
                    variables_on = False
                    process_line = False

                for item in ignore_var_lines:
                    if item.lower() in line.lower():
                        process_line = False
                for item in ignore_blanks:
                    if item == line:
                        process_line = False

                # If the line isn't in the ignore list, then it's a variable line
                if process_line:

                    # Split the line items, and cleanup
                    cleaned_line = separate_data_vars(line)

                    # Add the items into a column dictionary
                    data_col_dict = create_var_col(cleaned_line, data_col_ct)

                    # Keep a list of all variable names
                    data_var_names.append(data_col_dict['parameter'])

                    # Add the column dictionary into a final dictionary
                    data_col_list.append(data_col_dict)
                    data_col_ct += 1

            # DATA
            # Missing Value, Create data columns, and output Data CSV
            elif data_on:

                # Do not process lines that are blank, template lines, or missing value
                process_line = True

                for item in ignore_data_lines:
                    if item in line:
                        process_line = False
                for item in ignore_blanks:
                    if item == line:
                        process_line = False
                for item in missing_val_alts:
                    if item in line.lower():
                        process_line = False
                        line = str_cleanup(line)
                        key, missing_str = slice_key_val(line)

                if process_line:
                    # Split the line at each space (There's one space between each data item)
                    values = line.split()

                    # Write all data values to CSV
                    if data_vals_on:
                        dw.writerow(values)

                    # Check for the line of variables
                    else:

                        var = str_cleanup(values[0].lstrip())
                        # Check if a variable name is in the current line
                        if var.lower() == data_var_names[0].lower():
                            data_vals_on = True

                            # Open CSV for writing
                            data_filename = filename + '-data.csv'
                            csv_path = path + '/' + data_filename
                            data_csv = open(csv_path, 'w', newline='')
                            dw = csv.writer(data_csv)

            # METADATA
            else:
                # Line Continuation: Sometimes there are items that span a few lines.
                # If this happens, we want to combine them all properly into one entry.
                if '#' not in line and line not in ignore_blanks and last_insert is not None:
                    old_val = last_insert[old_key]
                    last_insert[old_key] = old_val + line

                # No Line Continuation: This is the start or a new entry
                else:
                    line = str_cleanup(line)

                    # Grab the key and value from the current line
                    try:
                        # Split the line into key, value pieces
                        key, value = slice_key_val(line)
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
                            if lkey not in ignore_keys:

                                if lkey == 'core_length':
                                    val, unit = split_name_unit(value)
                                    coreLen['value'] = convert_num(val)
                                    coreLen['unit'] = unit
                                    last_insert = coreLen

                                # There can be multiple funding agencies and grants. Keep a list of dictionary entries
                                elif lkey in funding_lst:
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
                                    final_dict[camelCase(key)] = value
                                    last_insert = final_dict

                                # Keep track of old key in case we have a line continuation
                                old_key = key

                    # Ignore any errors from NoneTypes that are returned from slice_key_val
                    except TypeError:
                        pass

    # Wait to close the data CSV until we reached the end of the text file
    try:
        data_csv.close()
    except NameError:
        print("Couldn't close Data CSV")

    # Piece together measurements block
    data_dict_upper['filename'] = data_filename
    data_dict_upper['paleoDataTableName'] = 'Data'
    data_dict_upper['missingValue'] = missing_str
    data_dict_upper['columns'] = data_col_list
    data_tables.append(data_dict_upper)

    # Piece together geo block
    geo = create_coordinates(lat, lon)
    geo['properties'] = geo_properties

    # Piece together final dictionary
    final_dict['pub'] = pub
    final_dict['funding'] = funding
    final_dict['geo'] = geo
    final_dict['coreLength'] = coreLen
    final_dict['chronology'] = chron_dict
    final_dict['paleoData'] = data_tables

     # Insert the data dictionaries into the final dictionary
    for k, v in vars_dict.items():
        data_dict_lower[k] = v

    # Return one complete dictionary per text file
    return final_dict


# Main function takes in file name, and outputs new jsonld file
def main():

    # Store a list of all the txt files in the specified directory. This is what we'll process.
    file_list = []
    # os.chdir('/Users/chrisheiser1/Desktop/')
    os.chdir('/Users/chrisheiser1/Dropbox/GeoChronR/noaa_lipd_files/lmr')
    for file in os.listdir():
        if file.endswith('.txt') and file != 'noaa-template.txt':
            file_list.append(file)

    for txts in file_list:

        # Print to user which file we're currently processing
        print(txts)

        # Cut the extension from the file name
        name = os.path.splitext(txts)[0]

        # Creates the directory 'output' if it does not already exist
        path = 'output/'
        if not os.path.exists(path):
              os.makedirs(path)

        # Run the file through the parser
        dict_out = parse(txts, path, name)

        # LPD file output
        out_name = name + '.lipd'
        file_jsonld = open(path + '/' + out_name, 'w')

        # Write finalDict to json-ld file with dump. Dump outputs into a human-readable json hierarchy
        json.dump(dict_out, file_jsonld, indent=4)

    return

main()