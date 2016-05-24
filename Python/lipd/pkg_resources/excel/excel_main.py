import csv

import xlrd

from ..doi.doi_resolver import *
from ..helpers.bag import *
from ..helpers.directory import *
from ..helpers.zips import *
from ..helpers.blanks import *
from ..helpers.loggers import *
from ..helpers.alternates import *


logger_excel = create_logger('excel_main')


def excel():
    """
    Parse data from Excel spreadsheets into LiPD files.
    :return:
    """
    dir_root = os.getcwd()
    # Ask user if they want to run the Chronology sheets or flatten the JSON files.
    # This is an all or nothing choice
    # need_response = True
    # while need_response:
    #     chron_run = input("Run Chronology? (y/n)\n")
    #     if chron_run == 'y' or 'n':
    #         flat_run = input("Flatten JSON? (y/n)\n")
    #         if flat_run == 'y' or 'n':
    #             need_response = False

    # For testing, assume we don't want to run these to make things easier for now.
    chron_run = 'n'
    flat_run = 'n'

    # Find excel files
    f_list = list_files('.xls') + list_files('.xlsx')
    print("Found " + str(len(f_list)) + " Excel files")
    logger_excel.info("found excel files: {}".format(len(f_list)))

    # Run once for each file
    for name_ext in f_list:

        # Filename without extension
        name = os.path.splitext(name_ext)[0]
        name_lpd = name + '.lpd'
        print("processing: {}".format(name_ext))
        logger_excel.info("processing: {}".format(name_ext))

        # Create a temporary folder and set paths
        dir_tmp = create_tmp_dir()
        dir_bag = os.path.join(dir_tmp, name)
        dir_data = os.path.join(dir_bag, 'data')

        # Make folders in tmp
        os.mkdir(os.path.join(dir_bag))
        os.mkdir(os.path.join(dir_data))

        data_sheets = []
        chron_sheets = []
        chron_combine = []
        data_combine = []
        final_dict = OrderedDict()
        logger_excel.info("variables initialized")

        # Open excel workbook with filename
        try:
            workbook = xlrd.open_workbook(name_ext)
            logger_excel.info("opened XLRD workbook")

        except Exception as e:
            # There was a problem opening a file with XLRD
            print("Failed to open Workbook: {}".format(name))
            logger_excel.debug("excel: xlrd failed to open workbook: {}, {}".format(name, e))

        if workbook:
            # Check what worksheets are available, so we know how to proceed.
            for sheet in workbook.sheet_names():
                if 'Metadata' in sheet:
                    metadata_str = 'Metadata'
                elif 'Chronology' in sheet:
                    chron_sheets.append(sheet)
                elif 'Data' in sheet:
                    data_sheets.append(sheet)

            # METADATA WORKSHEETS
            # Parse Metadata sheet and add to output dictionary
            if metadata_str:
                logger_excel.info("parsing metadata worksheets")
                cells_dn_meta(workbook, metadata_str, 0, 0, final_dict)

            # DATA WORKSHEETS
            for sheet_str in data_sheets:
                # Parse each Data sheet. Combine into one dictionary
                logger_excel.info("parsing data worksheets")
                sheet_str = cells_dn_ds(name, workbook, sheet_str, 2, 0)
                data_combine.append(sheet_str)

            # Add data dictionary to output dictionary
            final_dict['paleoData'] = data_combine

            # CHRONOLOGY WORKSHEETS
            chron_dict = OrderedDict()
            if chron_run == 'y':
                logger_excel.info("parsing chronology worksheets")
                for sheet_str in chron_sheets:
                    # Parse each chronology sheet. Combine into one dictionary
                    temp_sheet = workbook.sheet_by_name(sheet_str)
                    chron_dict['filename'] = str(name) + '-' + str(sheet_str) + '.csv'

                    # Create a dictionary that has a list of all the columns in the sheet
                    start_row = traverse_to_chron_var(temp_sheet)
                    columns_list_chron = get_chron_var(temp_sheet, start_row)
                    chron_dict['columns'] = columns_list_chron
                    chron_combine.append(chron_dict)

                # Add chronology dictionary to output dictionary
                final_dict['chronData'] = chron_combine

            # OUTPUT

            # Create new files and dump data in dir_data
            os.chdir(dir_data)

            # CSV - DATA
            for sheet_str in data_sheets:
                logger_excel.info("output to csv: data: {}".format(sheet_str))
                write_csv_ds(workbook, sheet_str, name)
            del data_sheets[:]

            # CSV - CHRONOLOGY
            if chron_run == 'y':
                for sheet_str in chron_sheets:
                    logger_excel.info("output to csv: chronology: {}".format(sheet_str))
                    write_csv_chron(workbook, sheet_str, name)

            # JSON-LD
            # Invoke DOI Resolver Class to update publisher data
            try:
                logger_excel.info("invoking doi resolver")
                final_dict = DOIResolver(dir_root, name, final_dict).main()
            except Exception as e:
                print("Error: doi resolver failed: {}".format(name))
                logger_excel.debug("excel: doi resolver failed: {}, {}".format(name, e))

            # Dump final_dict to a json file.
            write_json_to_file(name + '.jsonld', final_dict)

            # JSON FLATTEN code would go here.

            # Move files to bag root for re-bagging
            # dir : dir_data -> dir_bag
            logger_excel.info("start cleanup")
            dir_cleanup(dir_bag, dir_data)

            # Create a bag for the 3 files
            finish_bag(dir_bag)

            # dir: dir_tmp -> dir_root
            os.chdir(dir_root)

            # Check if same lpd file exists. If so, delete so new one can be made
            if os.path.isfile(name_lpd):
                os.remove(name_lpd)

            # Zip dir_bag. Creates in dir_root directory
            logger_excel.info("re-zip and rename")
            re_zip(dir_tmp, name, name_lpd)
            os.rename(name_lpd + '.zip', name_lpd)

        # Move back to dir_root for next loop.
        os.chdir(dir_root)

        # Cleanup and remove tmp directory
        shutil.rmtree(dir_tmp)

    print("Process Complete")
    return


def write_csv_ds(workbook, sheet, name):
    """
    Write datasheet columns to a csv file
    :param obj workbook:
    :param str sheet:
    :param str name:
    :return: none
    """
    logger_excel.info("enter write_csv_ds")
    temp_sheet = workbook.sheet_by_name(sheet)

    # Create CSV file and open
    file_csv = open(str(name) + '-' + str(sheet) + '.csv', 'w', newline='')
    w = csv.writer(file_csv)
    logger_excel.info("start parsing sheet: {}".format(sheet))

    try:
        # Loop to find starting variable name
        # Try to find if there are variable headers or not
        ref_first_var = traverse_short_row_str(temp_sheet)

        # Traverse down to the "Missing Value" cell to get us near the data we want.
        missing_val_row = traverse_mv(temp_sheet)

        # Get the missing val for search-and-replace later
        missing_val = get_mv(temp_sheet)

        # Loop for 5 times past "Missing Value" to see if we get a match on the variable header
        # Don't want to loop for too long, or we're wasting our time.
        position_start = var_headers_check(temp_sheet, missing_val_row, ref_first_var)
        data_cell_start = traverse_headers_to_data(temp_sheet, position_start)

        # Loop over all variable names, and count how many there are. We need to loop this many times.
        first_short_cell = traverse_short_row_int(temp_sheet)
        var_limit = count_vars(temp_sheet, first_short_cell)

        # Until we reach the bottom worksheet
        current_row = data_cell_start
        while current_row < temp_sheet.nrows:
            data_list = []

            # Move down a row and go back to column 0
            current_column = 0

            # Until we reach the right side worksheet
            while current_column < var_limit:
                # Increment to column 0, and grab the cell content
                cell_value = replace_mvs(temp_sheet.cell_value(current_row, current_column), missing_val)
                data_list.append(cell_value)
                current_column += 1
            data_list = replace_mvs(data_list, missing_val)
            w.writerow(data_list)
            current_row += 1

    except IndexError as e:
        logger_excel.warn("write_csv_ds: IndexError while parsing: {}".format(e))
    file_csv.close()
    logger_excel.info("exit write_csv_ds")
    return


def write_csv_chron(workbook, sheet, name):
    """
    Output the data columns from chronology sheet to csv file
    :param obj workbook:
    :param str sheet:
    :param str name:
    :return: none
    """
    logger_excel.info("enter write_csv_chron")
    temp_sheet = workbook.sheet_by_name(sheet)

    # Create CSV file and open
    file_csv = open(str(name) + '-' + str(sheet) + '.csv', 'w', newline='')
    w = csv.writer(file_csv)
    logger_excel.info("start parsing sheet")
    try:
        total_vars = count_chron_variables(temp_sheet)
        row = traverse_to_chron_data(temp_sheet)

        while row < temp_sheet.nrows:
            data_list = get_chron_data(temp_sheet, row, total_vars)
            w.writerow(data_list)
            row += 1

    except IndexError as e:
        logger_excel.info("write_csv_chron: IndexError while parsing: {}".format(e))

    file_csv.close()
    logger_excel.info("exit write_csv_chron")
    return


# GEO DATA METHODS

def geometry_linestring(lat, lon, elev):
    """
    GeoJSON Linestring. Latitude and Longitude have 2 values each.
    :param list lat: Latitude values
    :param list lon:  Longitude values
    :return dict:
    """
    logger_excel.info("enter geometry_linestring")
    d = OrderedDict()
    coordinates = []
    temp = ["", ""]

    # Point type, Matching pairs.
    if lat[0] == lat[1] and lon[0] == lon[1]:
        logger_excel.info("matching geo coordinate")
        lat.pop()
        lon.pop()
        d = geometry_point(lat, lon, elev)

    else:
        # Creates coordinates list
        logger_excel.info("unique geo coordinates")
        for i in lat:
            temp[0] = i
            for j in lon:
                temp[1] = j
                coordinates.append(copy.copy(temp))
        if elev:
            for i in coordinates:
                i.append(elev)
        # Create geometry block
        d['type'] = 'Linestring'
        d['coordinates'] = coordinates
    logger_excel.info("exit geometry_linestring")
    return d


def geometry_point(lat, lon, elev):
    """
    GeoJSON point. Latitude and Longitude only have one value each
    :param list lat: Latitude values
    :param list lon: Longitude values
    :return dict:
    """
    logger_excel.info("enter geometry_point")
    coordinates = []
    point_dict = OrderedDict()
    for idx, val in enumerate(lat):
        try:
            coordinates.append(lat[idx])
            coordinates.append(lon[idx])
        except IndexError as e:
            print("Error: Invalid geo coordinates")
            logger_excel.debug("geometry_point: IndexError: lat: {}, lon: {}, {}".format(lat, lon, e))

    coordinates.append(elev)
    point_dict['type'] = 'Point'
    point_dict['coordinates'] = coordinates
    logger_excel.info("exit geometry_point")
    return point_dict


def compile_geometry(lat, lon, elev):
    """
    Take in lists of lat and lon coordinates, and determine what geometry to create
    :param list lat: Latitude values
    :param list lon: Longitude values
    :param float elev: Elevation value
    :return dict:
    """
    logger_excel.info("enter compile_geometry")
    lat = _remove_geo_placeholders(lat)
    lon = _remove_geo_placeholders(lon)

    # 4 coordinate values
    if len(lat) == 2 and len(lon) == 2:
        logger_excel.info("found 4 coordinates")
        geo_dict = geometry_linestring(lat, lon, elev)

        # # 4 coordinate values
        # if (lat[0] != lat[1]) and (lon[0] != lon[1]):
        #     geo_dict = geometry_polygon(lat, lon)
        # # 3 unique coordinates
        # else:
        #     geo_dict = geometry_multipoint(lat, lon)
        #

    # 2 coordinate values
    elif len(lat) == 1 and len(lon) == 1:
        logger_excel.info("found 2 coordinates")
        geo_dict = geometry_point(lat, lon, elev)

    # Too many points, or no points
    else:
        geo_dict = {}
        logger_excel.warn("compile_geometry: invalid coordinates: lat: {}, lon: {}".format(lat, lon))
        print("Error: Invalid geo coordinates")
    logger_excel.info("exit compile_geometry")
    return geo_dict


def compile_geo(d):
    """
    Compile top-level Geography dictionary.
    :param d:
    :return:
    """
    logger_excel.info("enter compile_geo")
    d2 = OrderedDict()
    d2['type'] = 'Feature'
    # If the necessary keys are missing, put in placeholders so there's no KeyErrors.
    for key in EXCEL_GEO:
        if key not in d:
            d[key] = ""
    # Compile the geometry based on the info available.
    d2['geometry'] = compile_geometry([d['latMin'], d['latMax']], [d['lonMin'], d['lonMax']], d['elevation'])
    try:
        d2['properties'] = {'siteName': d['siteName']}
    except KeyError as e:
        logger_excel.warn("compile_geo: KeyError: {}, {}".format("siteName", e))

    logger_excel.info("exit compile_geo")
    return d2


def compile_authors(cell):
    """
    Split the string of author names into the BibJSON format.
    :param str cell: Data from author cell
    :return: (list of dicts) Author names
    """
    logger_excel.info("enter compile_authors")
    author_lst = []
    s = cell.split(';')
    for w in s:
        author_lst.append(w.lstrip())
    logger_excel.info("exit compile_authors")
    return author_lst


# MISC HELPER METHODS


def compile_temp(d, key, value):
    """
    Compiles temporary dictionaries for metadata. Adds a new entry to an existing dictionary.
    :param dict d:
    :param str key:
    :param any value:
    :return dict:
    """
    if not value:
        d[key] = None
    elif len(value) == 1:
        d[key] = value[0]
    else:
        d[key] = value
    return d


def compile_fund(workbook, sheet, row, col):
    """
    Compile funding entries. Iter both rows at the same time. Keep adding entries until both cells are empty.
    :param obj workbook:
    :param str sheet:
    :param int row:
    :param int col:
    :return list of dict: l
    """
    logger_excel.info("enter compile_fund")
    l = []
    temp_sheet = workbook.sheet_by_name(sheet)
    while col < temp_sheet.ncols:
        col += 1
        try:
            agency = temp_sheet.cell_value(row, col)
            grant = temp_sheet.cell_value(row+1, col)
            if (agency != xlrd.empty_cell and agency not in EMPTY) or (grant != xlrd.empty_cell and grant not in EMPTY):
                if agency in EMPTY:
                    l.append({'grant': grant})
                elif grant in EMPTY:
                    l.append({'agency': agency})
                else:
                    l.append({'agency': agency, 'grant': grant})
        except IndexError as e:
            logger_excel.debug("compile_fund: IndexError: sheet:{} row:{} col:{}, {}".format(sheet, row, col, e))
    logger_excel.info("exit compile_fund")
    return l


def cell_occupied(temp_sheet, row, col):
    """
    Check if there is content in this cell
    :param obj temp_sheet:
    :param int row:
    :param int col:
    :return bool:
    """
    try:
        if temp_sheet.cell_value(row, col) != ("N/A" and " " and xlrd.empty_cell and ""):
            return True
    except IndexError as e:
        logger_excel.debug("cell_occupied: IndexError: row:{} col:{}, {}".format(row, col, e))
    return False


def name_to_jsonld(title_in):
    """
    Convert formal titles to camelcase json_ld text that matches our context file
    Keep a growing list of all titles that are being used in the json_ld context
    :param str title_in:
    :return str:
    """
    title_out = ''
    try:
        title_in = title_in.lower()
        title_out = ALTS_JSONLD[title_in]
    except (KeyError, AttributeError) as e:
        for k, v in ALTS_JSONLD.items():
            if title_in == k:
                title_out = v
            elif k in title_in:
                title_out = v
    if not title_out:
        logger_excel.debug("name_to_jsonld: No match found: {}".format(title_in))
    return title_out


def get_data_type(temp_sheet, colListNum):
    """
    Find out what type of values are stored in a specific column in data sheet (best guess)
    :param obj temp_sheet:
    :param int colListNum:
    :return str:
    """
    short = traverse_short_row_str(temp_sheet)
    mv_cell = traverse_mv(temp_sheet)
    row = var_headers_check(temp_sheet, mv_cell, short)
    temp = temp_sheet.cell_value(row, colListNum - 1)

    # Make sure we are not getting the dataType of a "NaN" item
    while (temp == 'NaN') and (row < temp_sheet.nrows):
        row += 1

    # If we find a value before reaching the end of the column, determine the dataType
    if row < temp_sheet.nrows:
        # Determine what type the item is
        str_type = instance_str(temp_sheet.cell_value(row, colListNum - 1))

    # If the whole column is NaN's, then there is no dataType
    else:
        str_type = 'None'

    return str_type


def instance_str(cell):
    """
    Match data type and return string
    :param any cell:
    :return str:
    """
    if isinstance(cell, str):
        return 'str'
    elif isinstance(cell, int):
        return 'int'
    elif isinstance(cell, float):
        return 'float'
    else:
        return 'unknown'


def replace_mvs(cell_entry, missing_val):
    """
    The missing value standard is "NaN". If there are other missing values present, we need to swap them.
    :param str cell_entry: Contents of target cell
    :param str missing_val:
    :return str:
    """
    if isinstance(cell_entry, str):
        missing_val_list = ['none', 'na', '', '-', 'n/a']
        if missing_val.lower() not in missing_val_list:
            missing_val_list.append(missing_val)
        try:
            if cell_entry.lower() in missing_val_list:
                cell_entry = 'NaN'
        except (TypeError, AttributeError) as e:
            logger_excel.debug("replace_missing_vals: Type/AttrError: cell: {}, mv: {} , {}".format(cell_entry, missing_val, e))
    return cell_entry


def extract_units(string_in):
    """
    Extract units from parenthesis in a string. i.e. "elevation (meters)"
    :param str string_in:
    :return str:
    """
    start = '('
    stop = ')'
    return string_in[string_in.index(start) + 1:string_in.index(stop)]


def extract_short(string_in):
    """
    Extract the short name from a string that also has units.
    :param str string_in:
    :return str:
    """
    stop = '('
    return string_in[:string_in.index(stop)]


# DATA WORKSHEET HELPER METHODS


def count_vars(temp_sheet, first_short):
    """
    Starts at the first short name, and counts how many variables are present
    :param obj temp_sheet:
    :param int first_short:
    :return int: Number of variables
    """
    count = 0
    # If we hit a blank cell, or the MV / Data cells, then stop
    while cell_occupied(temp_sheet, first_short, 0) and temp_sheet.cell_value(first_short, 0) != ("Missing" and "Data"):
        count += 1
        first_short += 1
    return count


def get_mv(temp_sheet):
    """
    Look for what missing value is being used.
    :param obj temp_sheet:
    :return str: Missing value
    """
    row = traverse_mv(temp_sheet)
    # There are two blank cells to check for a missing value
    empty = ''
    missing_val = temp_sheet.cell_value(row, 1)
    missing_val2 = temp_sheet.cell_value(row, 2)
    if cell_occupied(temp_sheet, row, 1):
        if isinstance(missing_val, str):
            missing_val = missing_val.lower()
        logger_excel.info("missing value: {}".format(missing_val))
        return missing_val
    elif cell_occupied(temp_sheet, row, 2):
        if isinstance(missing_val2, str):
            missing_val2 = missing_val2.lower()
        logger_excel.info("missing value: {}".format(missing_val))
        return missing_val2
    logger_excel.info("missing value is empty")
    return empty


def traverse_short_row_int(temp_sheet):
    """
    Traverse to short name cell in data sheet. Get the row number.
    :param obj temp_sheet:
    :return int: Current row
    """
    for i in range(0, temp_sheet.nrows):
        # We need to keep the first variable name as a reference.
        # Then loop down past "Missing Value" to see if there is a matching variable header
        # If there's not match, then there must not be a variable header row.
        if 'Short' in temp_sheet.cell_value(i, 0):
            current_row = i + 1
            return current_row
    return


def traverse_short_row_str(temp_sheet):
    """
    Traverse to short name cell in data sheet
    :param obj temp_sheet:
    :return str: Name of first variable, if we find one
    """
    for i in range(0, temp_sheet.nrows):

        # We need to keep the first variable name as a reference.
        # Then loop down past "Missing Value" to see if there is a matching variable header
        # If there's not match, then there must not be a variable header row.
        if 'Short' in temp_sheet.cell_value(i, 0):
            current_row = i + 1
            ref_first_var = temp_sheet.cell_value(current_row, 0)
            return ref_first_var
    return


def traverse_mv(temp_sheet):
    """
    Traverse to missing value cell in data sheet
    :param obj temp_sheet:
    :return int: Only returns int if it finds a missing value
    """
    logger_excel.info("enter traverse_missing_values")
    # Traverse down to the "Missing Value" cell. This gets us near the data we want.
    for i in range(0, temp_sheet.nrows):
        # Loop down until you hit the "Missing Value" cell, and then move down one more row
        try:
            cell = temp_sheet.cell_value(i, 0)
            if 'Missing' in cell:
                missing_row_num = i
                logger_excel.info("exit traverse_missing_values")
                return missing_row_num
        except TypeError as e:
            logger_excel.debug("traverse_mv: TypeError: row:{} col: {}, {}".format(i, "0", e))
    logger_excel.info("exit traverse_missing_values")
    return


def traverse_headers_to_data(temp_sheet, start_cell):
    """
    Traverse to the first cell that has data
    If the cell on Col 0 has content, check 5 cells to the right for content also. (fail-safe)
    :param obj temp_sheet:
    :param int start_cell: Start of variable headers
    :return int : First cell that contains numeric data
    """
    # Start at the var_headers row, and try to find the start of the data cells
    # Loop for 5 times. It's unlikely that there are more than 5 blank rows between the var_header row and
    # the start of the data cells. Usually it's 1 or 2 at most.
    while not cell_occupied(temp_sheet, start_cell, 0):
        start_cell += 1
    return start_cell


def traverse_mv_to_headers(temp_sheet, start):
    """
    Traverse from the missing value cell to the first occupied cell
    :param obj temp_sheet:
    :param int start: var_headers start row
    :return int: start cell
    """
    # Start at the var_headers row, and try to find the start of the data cells
    # Loop for 5 times. It's unlikely that there are more than 5 blank rows between the var_header row and
    # the start of the data cells. Usually it's 1 or 2 at most.
    start += 1
    # Move past the empty cells
    while not cell_occupied(temp_sheet, start, 0):
        start += 1
    # Check if there is content in first two cols
    # Move down a row, check again. (Safety check)
    num = 0
    for i in range(0, 2):
        if cell_occupied(temp_sheet, start, i):
            num += 1
    start += 1
    for i in range(0, 2):
        if cell_occupied(temp_sheet, start, i):
            num += 1
    return start


def var_headers_check(temp_sheet, missing_val_row, ref_first_var):
    """
    Check for matching variables first. If match, return var_header cell int.
    If no match, check the first two rows to see if one is all strings, or if there's some discrepancy
    :param obj temp_sheet:
    :param int missing_val_row:
    :param str ref_first_var:
    :return int: start cell
    """
    start = traverse_mv_to_headers(temp_sheet, missing_val_row)
    # If we find a match, then Variable headers exist for this file
    if temp_sheet.cell_value(start, 0) == ref_first_var:
        return start + 1
    # No var match, start to manually check the first two rows and make a best guess
    else:
        col = 0
        str_row1 = 0
        str_row2 = 0

        # Row 1
        while col < temp_sheet.ncols:
            if isinstance(temp_sheet.cell_value(start, col), str):
                str_row1 += 1
            col += 1

        # Reset variables
        col = 0
        start += 1

        # Row 2
        while col < temp_sheet.ncols:
            if isinstance(temp_sheet.cell_value(start, col), str):
                str_row2 += 1
            col += 1

        # If the top row has more strings than the bottom row, then the top row must be the header
        if str_row1 > str_row2:
            return start
        # If not, then we probably don't have a header, so move back up one row
        else:
            return start - 1
    # If we still aren't sure, traverse one row down from the MV box and start from there
    # UNREACHABLE
    # return traverse_missing_value(temp_sheet) + 1


def cells_rt_meta_pub(workbook, sheet, row, col, pub_qty):
    """
    Publication section is special. It's possible there's more than one publication.
    :param obj workbook:
    :param str sheet:
    :param int row:
    :param int col:
    :param int pub_qty: Number of distinct publication sections in this file
    :return list: Cell data for a specific row
    """
    logger_excel.info("enter cells_rt_meta_pub")
    col_loop = 0
    cell_data = []
    temp_sheet = workbook.sheet_by_name(sheet)
    while col_loop < pub_qty:
        col += 1
        col_loop += 1
        cell_data.append(temp_sheet.cell_value(row, col))
    logger_excel.info("exit cells_rt_meta_pub")
    return cell_data


def cells_rt_meta(workbook, sheet, row, col):
    """
    Traverse all cells in a row. If you find new data in a cell, add it to the list.
    :param obj workbook:
    :param str sheet:
    :param int row:
    :param int col:
    :return list: Cell data for a specific row
    """
    logger_excel.info("enter cells_rt_meta")
    col_loop = 0
    cell_data = []
    temp_sheet = workbook.sheet_by_name(sheet)
    while col_loop < temp_sheet.ncols:
        col += 1
        col_loop += 1
        try:
            if temp_sheet.cell_value(row, col) != xlrd.empty_cell and temp_sheet.cell_value(row, col) != '':
                cell_data.append(temp_sheet.cell_value(row, col))
        except IndexError as e:
            logger_excel.warn("cells_rt_meta: IndexError: sheet: {}, row: {}, col: {}, {}".format(sheet, row, col, e))
    logger_excel.info("exit cells_right_meta")
    return cell_data


def cells_dn_meta(workbook, sheet, row, col, final_dict):
    """
    Traverse all cells in a column moving downward. Primarily created for the metadata sheet, but may use elsewhere.
    Check the cell title, and switch it to.
    :param obj workbook:
    :param str sheet:
    :param int row:
    :param int col:
    :param dict final_dict:
    :return: none
    """
    logger_excel.info("enter cells_dn_meta")
    row_loop = 0
    pub_cases = ['id', 'year', 'author', 'journal', 'issue', 'volume', 'title', 'pages',
                 'reportNumber', 'abstract', 'alternateCitation']
    geo_cases = ['latMin', 'lonMin', 'lonMax', 'latMax', 'elevation', 'siteName', 'location']

    # Temp
    pub_qty = 0
    geo_temp = {}
    general_temp = {}
    pub_temp = []
    funding_temp = []

    temp_sheet = workbook.sheet_by_name(sheet)

    # Loop until we hit the max rows in the sheet
    while row_loop < temp_sheet.nrows:
        try:
            # If there is content in the cell...
            if temp_sheet.cell_value(row, col) != xlrd.empty_cell and temp_sheet.cell_value(row, col) not in EMPTY:

                # Convert title to correct format, and grab the cell data for that row
                title_formal = temp_sheet.cell_value(row, col)
                title_json = name_to_jsonld(title_formal)

                # If we don't have a title for it, then it's not information we want to grab
                if title_json:

                    # Geo
                    if title_json in geo_cases:
                        cell_data = cells_rt_meta(workbook, sheet, row, col)
                        geo_temp = compile_temp(geo_temp, title_json, cell_data)

                    # Pub
                    # Create a list of dicts. One for each pub column.
                    elif title_json in pub_cases:

                        # Authors seem to be the only consistent field we can rely on to determine number of Pubs.
                        if title_json == 'author':
                            cell_data = cells_rt_meta(workbook, sheet, row, col)
                            pub_qty = len(cell_data)
                            for i in range(pub_qty):
                                author_lst = compile_authors(cell_data[i])
                                pub_temp.append({'author': author_lst, 'pubDataUrl': 'Manually Entered'})
                        else:
                            cell_data = cells_rt_meta_pub(workbook, sheet, row, col, pub_qty)
                            for pub in range(pub_qty):
                                if title_json == 'id':
                                    pub_temp[pub]['identifier'] = [{"type": "doi", "id": cell_data[pub]}]
                                else:
                                    pub_temp[pub][title_json] = cell_data[pub]
                    # Funding
                    elif title_json == 'agency':
                        funding_temp = compile_fund(workbook, sheet, row, col)

                    # All other cases do not need fancy structuring
                    else:
                        cell_data = cells_rt_meta(workbook, sheet, row, col)
                        general_temp = compile_temp(general_temp, title_json, cell_data)

        except IndexError as e:
            logger_excel.debug("cells_dn_datasheets: IndexError: sheet: {}, row: {}, col: {}, {}".format(sheet, row, col, e))
        row += 1
        row_loop += 1

    # Compile the more complicated items
    geo = compile_geo(geo_temp)

    logger_excel.info("compile metadata dictionary")
    # Insert into final dictionary
    final_dict['@context'] = "context.jsonld"
    final_dict['pub'] = pub_temp
    final_dict['funding'] = funding_temp
    final_dict['geo'] = geo

    # Add remaining general items
    for k, v in general_temp.items():
        final_dict[k] = v
    logger_excel.info("exit cells_dn_meta")
    return


def cells_rt_ds(workbook, sheet, row, col, col_list_num):
    """
    Traverse right datasheet cells. Collect metadata for one column in the datasheet
    :param obj workbook:
    :param str sheet:
    :param int row:
    :param int col:
    :param int col_list_num:
    :return dict: (Attributes Dictionary
    """
    logger_excel.info("enter cells_rt_ds")
    temp_sheet = workbook.sheet_by_name(sheet)

    # Iterate over all attributes, and add them to the column if they are not empty
    attr_dict = OrderedDict()
    attr_dict['number'] = col_list_num

    # Get the data type for this column
    attr_dict['dataType'] = str(get_data_type(temp_sheet, col_list_num))

    # Separate dict for climateInterp block
    climate_int_dict = {}

    try:
        # Loop until we hit the right-side boundary
        while col < temp_sheet.ncols:
            cell = temp_sheet.cell_value(row, col)

            # If the cell contains any data, grab it
            if cell not in (EMPTY, xlrd.empty_cell) and "Note:" not in cell:

                title_in = name_to_jsonld(temp_sheet.cell_value(1, col))

                # Special case if we need to split the climate interpretation string into 3 parts
                if title_in == 'climateInterpretation':
                    if cell in (EMPTY, xlrd.empty_cell):
                        climate_int_dict['parameter'] = ''
                        climate_int_dict['parameterDetail'] = ''
                        climate_int_dict['interpDirection'] = ''
                    else:
                        cicSplit = cell.split('.')
                        climate_int_dict['climateParameter'] = cicSplit[0]
                        climate_int_dict['climateParameterDetail'] = cicSplit[1]
                        climate_int_dict['interpDirection'] = cicSplit[2]

                # Special case to add these two categories to climateInterpretation
                elif title_in == 'seasonality' or title_in == 'basis':
                    climate_int_dict[title_in] = temp_sheet.cell_value(row, col)

                # If the key is null, then this is a not a cell we want to add
                # We also don't want Data Type, because we manually check for the content data type later
                # Don't want it to overwrite the other data type.
                # Happens when we get to the cells that are filled with formatting instructions
                # Ex. "Climate_interpretation_code has 3 fields separated by periods..."
                elif title_in is (None or 'dataType'):
                    pass

                # Catch all other cases
                else:
                    attr_dict[title_in] = cell
            col += 1

    except IndexError as e:
        logger_excel.debug("cell_rt_ds: IndexError: sheet: {}, row: {}, col:{}, {}".format(sheet, row, col, e))

    # Only add if there's data
    if climate_int_dict:
        attr_dict['climateInterpretation'] = climate_int_dict
    logger_excel.info("exit cells_rt_ds")
    return attr_dict


def cells_dn_ds(filename, workbook, sheet, row, col):
    """
    Traverse down datasheet cells. Add measurement table data to the final dictionary
    :param str filename:
    :param obj workbook:
    :param str sheet:
    :param int row:
    :param int col:
    :return dict:
    """
    logger_excel.info("enter cells_dn_ds")
    # Create a dictionary to hold each column as a separate entry
    paleoDataTableDict = OrderedDict()

    # Iterate over all the short_name variables until we hit the "Data" cell, or until we hit an empty cell
    # If we hit either of these, that should mean that we found all the variables
    # For each short_name, we should create a column entry and match all the info for that column
    temp_sheet = workbook.sheet_by_name(sheet)
    columnsTop = []
    commentList = []
    colListNum = 1
    iter_var = True

    # Loop for all variables in top section
    try:
        while iter_var:

            cell = temp_sheet.cell_value(row, col).lstrip().rstrip()
            if (cell == 'Data') or (cell == 'Missing Value') \
                    or (cell == 'The value or character string used as a placeholder for missing values'):
                break
            else:
                variable = name_to_jsonld(temp_sheet.cell_value(row, col))

                # If the cell isn't blank or empty, then grab the data
                # Special case for handling comments since we want to stop them from being inserted at column level
                if variable == 'comments':
                    for i in range(1, 3):
                        if cell_occupied(temp_sheet, row, i):
                            commentList.append(temp_sheet.cell_value(row, i))

                # All other cases, create a list of columns, one dictionary per column
                elif temp_sheet.cell_value(row, col) != ('' and xlrd.empty_cell):
                    columnsTop.append(cells_rt_ds(workbook, sheet, row, col, colListNum))
                    colListNum += 1
                row += 1

    except IndexError as e:
        logger_excel.debug("cells_dn_ds: IndexError: sheet: {}, row: {}, col: {}, {}".format(sheet, row, col, e))

    # Add all our data pieces for this column into a new entry in the Measurement Table Dictionary
    logger_excel.info("compile paleoDataTableDict")
    paleoDataTableDict['paleoDataTableName'] = sheet
    paleoDataTableDict['filename'] = str(filename) + '-' + str(sheet) + ".csv"
    paleoDataTableDict['missingValue'] = 'NaN'

    # If comments exist, insert them at table level
    if commentList:
        paleoDataTableDict['comments'] = commentList[0]
    paleoDataTableDict['columns'] = columnsTop

    # Reset list back to null for next loop
    commentList = []
    logger_excel.info("exit cells_dn_ds")
    return paleoDataTableDict

# CHRONOLOGY HELPER METHODS


def count_chron_variables(temp_sheet):
    """
    Count the number of chron variables
    :param obj temp_sheet:
    :return int: variable count
    """
    total_count = 0
    start_row = traverse_to_chron_var(temp_sheet)
    while temp_sheet.cell_value(start_row, 0) != '':
        total_count += 1
        start_row += 1
    return total_count


def get_chron_var(temp_sheet, start_row):
    """
    Capture all the vars in the chron sheet (for json-ld output)
    :param obj temp_sheet:
    :param int start_row:
    :return: (list of dict) column data
    """
    col_dict = OrderedDict()
    out_list = []
    column = 1

    while (temp_sheet.cell_value(start_row, 0) != '') and (start_row < temp_sheet.nrows):
        short_cell = temp_sheet.cell_value(start_row, 0)
        units_cell = temp_sheet.cell_value(start_row, 1)
        long_cell = temp_sheet.cell_value(start_row, 2)

        # Fill the dictionary for this column
        col_dict['number'] = column
        col_dict['parameter'] = short_cell
        col_dict['description'] = long_cell
        col_dict['units'] = units_cell
        out_list.append(col_dict.copy())
        start_row += 1
        column += 1

    return out_list


def traverse_to_chron_data(temp_sheet):
    """
    Traverse down to the first row that has chron data
    :param obj temp_sheet:
    :return int: traverse_row
    """
    traverse_row = traverse_to_chron_var(temp_sheet)
    reference_var = temp_sheet.cell_value(traverse_row, 0)

    # Traverse past all the short_names, until you hit a blank cell (the barrier)
    while temp_sheet.cell_value(traverse_row, 0) != '':
        traverse_row += 1
    # Traverse past the empty cells until we hit the chron data area
    while temp_sheet.cell_value(traverse_row, 0) == '':
        traverse_row += 1

    # Check if there is a header row. If there is, move past it. We don't want that data
    if temp_sheet.cell_value(traverse_row, 0) == reference_var:
        traverse_row += 1
    logger_excel.info("traverse_to_chron_data: row:{}".format(traverse_row))
    return traverse_row


def traverse_to_chron_var(temp_sheet):
    """
    Traverse down to the row that has the first variable
    :param obj temp_sheet:
    :return int:
    """
    row = 0
    while row < temp_sheet.nrows - 1:
        if 'Parameter' in temp_sheet.cell_value(row, 0):
            row += 1
            break
        row += 1
    logger_excel.info("traverse_to_chron_var: row:{}".format(row))
    return row


def get_chron_data(temp_sheet, row, total_vars):
    """
    Capture all data in for a specific chron data row (for csv output)
    :param obj temp_sheet:
    :param int row:
    :param int total_vars:
    :return list: data_row
    """
    data_row = []
    missing_val_list = ['none', 'na', '', '-']
    for i in range(0, total_vars):
        cell = temp_sheet.cell_value(row, i)
        if isinstance(cell, str):
            cell = cell.lower()
        if cell in missing_val_list:
            cell = 'NaN'
        data_row.append(cell)
    return data_row


# DEPRECATED


def single_item(arr):
    """
    DEPRECATED.
    Check an array to see if it is a single item or not
    :param list arr:
    :return bool:
    """
    if len(arr) == 1:
        return True
    return False


def blind_data_capture(temp_sheet):
    """
    DEPRECATED
    This was the temporary, inconsistent way to get chron data as a whole chunk.
    :param temp_sheet: (obj)
    :return: (dict)
    """
    chronology = OrderedDict()
    start_row = traverse_to_chron_var(temp_sheet)
    for row in range(start_row, temp_sheet.nrows):
        key = str(row)
        row_list = []
        for col in range(0, temp_sheet.ncols):
            row_list.append(temp_sheet.cell_value(row, col))
        chronology[key] = row_list

    return chronology


def _remove_geo_placeholders(l):
    """
    Remove placeholders from coordinate lists and sort
    :param list l: Lat or long list
    :return list: Modified list
    """
    for i in l:
        if not i:
            l.remove(i)
    l.sort()
    return l


if __name__ == '__main__':
    excel()
