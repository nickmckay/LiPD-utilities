import csv

from ..helpers.loggers import *
from ..helpers.misc import cast_values_csvs, cast_int

logger_csvs = create_logger("csvs")


# Merge CSV and Metadata


def merge_csv_metadata(d):
    """
    Using the given metadata dictionary, retrieve CSV data from CSV files, and insert the CSV
    values into their respective metadata columns. Checks for both paleoData and chronData tables.
    :param dict d: Metadata
    :return dict: Modified metadata dictionary
    """
    logger_csvs.info("enter merge_csv_metadata")

    # Add CSV to paleoData
    if "paleoData" in d:
        d["paleoData"] = _merge_csv_section(d["paleoData"], "paleo")

    # Add CSV to chronData
    if "chronData" in d:
        d["chronData"] = _merge_csv_section(d["chronData"], "chron")

    logger_csvs.info("exit merge_csv_metadata")
    return d


def _merge_csv_section(section_data, pc):
    """
    Add csv data to all paleo data tables
    :param dict section_data: Metadata
    :return dict: Modified metadata
    """
    logger_csvs.info("enter  merge_csv_section: {}".format(pc))

    try:
        # Loop through each table_data in paleoData
        for table_name, table_data in section_data.items():

            if "{}MeasurementTable".format(pc) in table_data:
                # Send whole table_data through. Adds csv data to columns
                for table_name2, table_data2 in table_data["{}MeasurementTable".format(pc)].items():
                    crumbs = "{}.{}.{}.{}".format(pc, table_name, "MeasurementTable", table_name2)
                    table_data["{}MeasurementTable".format(pc)][table_name2] = _add_csv_to_columns(table_data2, crumbs)

            if "{}Model".format(pc) in table_data:
                crumbs = "".format(pc, table_name, "Model")
                table_data["{}Model".format(pc)] = _merge_csv_model(table_data["{}Model".format(pc)], pc, crumbs)

    except AttributeError:
        print("Error: {} section must be a dictionary data type".format(pc))

    logger_csvs.info("exit  merge_csv_section: {}".format(pc))
    return section_data


def _merge_csv_model(models, pc, crumbs):
    """
    Add csv data to each column in chron model
    :param list models: Metadata
    :param str pc: Paleo or chron
    :param str crumbs: Hierarchy crumbs
    :return dict: Modified metadata
    """
    logger_csvs.info("enter merge_csv_model: {}".format(pc))

    try:
        for model in models:

            if "summaryTable" in model:
                crumbs2 = "{}.{}".format(crumbs, "summaryTable")
                model["summaryTable"] = _add_csv_to_columns(model["summaryTable"], crumbs2)

            if "{}ModelTable".format(pc) in model:
                crumbs2 = "{}.{}".format(crumbs, "ModelTable")
                model["{}ModelTable".format(pc)] = _add_csv_to_columns(model["{}ModelTable".format(pc)], crumbs2)

            if "ensembleTable" in model:
                crumbs2 = "{}.{}".format(crumbs, "ensembleTable")
                model["ensembleTable"] = _add_csv_to_columns(model["ensembleTable"], crumbs2)

            # Check for calibratedAges (old format) and distributionTable (current format)
            if "calibratedAges" in model:
                model["distributionTable"] = {}
                # Calibrated age tables are nested. Go down an extra layer.
                for k, v in model["calibratedAges"].items():
                    crumbs2 = "{}.{}.{}".format(crumbs, "distributionTable", k)
                    model["distributionTable"][k] = _add_csv_to_columns(v, crumbs2)
            elif "distributionTable" in model:
                for k, v in model["distributionTable"].items():
                    crumbs2 = "{}.{}.{}".format(crumbs, "distributionTable", k)
                    model["distributionTable"][k] = _add_csv_to_columns(v, crumbs2)
    except AttributeError:
        print("Error: Model section must be a list data type")

    logger_csvs.info("exit merge_csv_model: {}".format(pc))
    return models


def _add_csv_to_columns(table, crumbs):
    """
    Add csv data to each column in a list of columns
    :param dict table: Table metadata
    :param str crumbs: Hierarchy crumbs
    :return dict: Table metadata with csv "values" entry
    """
    # Get the filename or this table
    filename = _get_filename(table, crumbs)

    # If there's no filename, bypass whole process because there's no way to know which file to open
    if filename:
        # Call read_csv_to_columns for this filename. csv_data is list of lists.
        csv_data = _read_csv_from_file(filename)

        # Start putting CSV data into corresponding column "values" key
        try:
            for col_name, col in table['columns'].items():
                # The "number" entry in the ensemble table is a list of columns, instead of an int.
                # In this case, just store all the csv data as a batch.
                if isinstance(col["number"], list):
                    col["values"] = csv_data
                # For all other cases, "number" is a single int, and "values" should hold one column list.
                else:
                    col_num = cast_int(col["number"])
                    col['values'] = csv_data[col_num - 1]
        except IndexError:
            logger_csvs.warning("add_csv_to_columns: IndexError: index out of range of csv_data list")
        except KeyError:
            logger_csvs.debug("add_csv_to_columns: KeyError: missing columns key")
        except Exception as e:
            logger_csvs.debug("add_csv_to_columns: Unknown Error:  {}".format(e))
    return table


def _read_csv_from_file(filename):
    """
    Opens the target CSV file and creates a dictionary with one list for each CSV column.
    :param str filename:
    :return list of lists: column values
    """
    logger_csvs.info("enter read_csv_from_file")
    d = {}
    l = []
    try:
        with open(filename, 'r') as f:
            r = csv.reader(f, delimiter=',')

            # Create a dict with X lists corresponding to X columns
            for idx, col in enumerate(next(r)):
                d[idx] = []
                d = cast_values_csvs(d, idx, col)

            # Start iter through CSV data
            for row in r:
                for idx, col in enumerate(row):
                    # Append the cell to the correct column list
                    d = cast_values_csvs(d, idx, col)

        # Make a list of lists out of the dictionary instead
        for idx, col in d.items():
            l.append(col)
    except FileNotFoundError as e:
        print('CSV FileNotFound: ' + filename)
        logger_csvs.warn("read_csv_to_columns: FileNotFound: {}, {}".format(filename, e))
    logger_csvs.info("exit read_csv_from_file")
    return l


# SKIM CSV


def get_csv_from_metadata(name, metadata):
    """
    Two goals. Get all csv from metadata, and return new metadata with generated filenames to match files.
    :param str name: LiPD dataset name
    :param dict metadata: Metadata
    :return dict: Csv Data
    """
    logger_csvs.info("enter get_csv_from_metadata")

    _csv = {}
    _meta = metadata
    # crumbs = _get_dataset_name(metadata)

    if "paleoData" in metadata:
        # start building crumbs. This will be used to create new filenames.
        crumbs_tmp = "{}.Paleo".format(name)
        # Process paleoData section
        pd_meta, pd_csv = _get_csv_section(metadata["paleoData"], crumbs_tmp, "paleo")
        # Build up out master csv output data with our skimmed values
        _csv.update(pd_csv)
        # Set the new metadata in the output meta
        _meta["paleoData"] = pd_meta

    if "chronData" in metadata:
        crumbs_tmp = "{}.Chron".format(name)
        cd_meta, cd_csv = _get_csv_section(metadata["chronData"], crumbs_tmp, "chron")
        _csv.update(cd_csv)
        _meta["chronData"] = cd_meta

    logger_csvs.info("exit get_csv_from_metadata")
    return _meta, _csv


def _get_csv_section(_meta, crumbs, pc):
    """
    Get table name, variable name, and column values from paleo metadata
    :param dict _meta: Metadata
    :param str crumbs: Table name crumbs
    :param str pc: Paleo or chron
    :return dict: Metadata
    """
    logger_csvs.info("enter get_csv_section: {}".format(pc))
    _csv = {}
    s_idx = 1
    try:
        # Process the tables in section
        for name_table, data_table in _meta.items():
            # crumbs_tmp = "{}{}".format(crumbs, str(name_table))
            crumbs_tmp = "{}{}".format(crumbs, s_idx)

            # Process each entry sub-table below if they exist
            if "{}MeasurementTable".format(pc) in data_table:
                idx = 1
                for name_pmt, dat in data_table["{}MeasurementTable".format(pc)].items():
                    # String together the final pieces of the crumbs filename
                    filename = "{}.{}{}.csv".format(crumbs_tmp, "measurementTable", idx)
                    # Set the filename inside the metadata also, so our _csv and _meta will match
                    dat = _set_filename(dat, filename)
                    # Get a nested list of table values
                    out = _search_table_for_vals(dat, filename)
                    # Set the table values to _csv using our filename.
                    _csv[filename] = out
                    idx += 1

            if "{}Model".format(pc) in data_table:
                for item in data_table["{}Model".format(pc)]:
                    if "calibratedAges" in item:
                        idx = 1
                        # CA has an extra level of nesting
                        for name_ca, dat in item["calibratedAges"].items():
                            filename = "{}.distributionTable{}.csv".format(crumbs_tmp, idx)
                            dat = _set_filename(dat, filename)
                            out = _search_table_for_vals(dat, filename)
                            _csv[filename] = out
                            idx += 1

                    elif "distributionTable" in item:
                        idx = 1
                        # CA has an extra level of nesting
                        for name_ca, dat in item["distributionTable"].items():
                            filename = "{}.distributionTable{}.csv".format(crumbs_tmp, idx)
                            dat = _set_filename(dat, filename)
                            out = _search_table_for_vals(dat, filename)
                            _csv[filename] = out
                            idx += 1

                    if "{}ModelTable".format(pc) in item:
                        filename = "{}.{}.csv".format(crumbs_tmp, "{}ModelTable".format(pc))
                        item["{}ModelTable".format(pc)] = _set_filename(item["{}ModelTable".format(pc)], filename)
                        out = _search_table_for_vals(item["{}ModelTable".format(pc)], filename)
                        _csv[filename] = out

                    elif "summaryTable".format() in item:
                        filename = "{}.{}.csv".format(crumbs_tmp, "summaryTable".format(pc))
                        item["summaryTable"] = _set_filename(item["summaryTable"], filename)
                        out = _search_table_for_vals(item["summaryTable"], filename)
                        _csv[filename] = out

                    if "ensembleTable" in item:
                        filename = "{}.{}.csv".format(crumbs_tmp, "ensembleTable")
                        item["ensembleTable"] = _set_filename(item["ensembleTable"], filename)
                        out = _search_table_for_vals(item["ensembleTable"], filename)
                        _csv[filename] = out
            s_idx += 1

    except AttributeError:
        logger_csvs.info("get_csv_section: {}, AttributeError: expected type dict, given type {}".format(pc, type(_meta)))

    logger_csvs.info("exit get_csv_section: {}".format(pc))
    return _meta, _csv


def write_csv_to_file(d):
    """
    Writes columns of data to a target CSV file.
    :param dict d: A dictionary containing one list for every data column. Keys: int, Values: list
    :return None:
    """
    logger_csvs.info("enter write_csv_to_file")
    for filename, data in d.items():
        l_columns = []
        for k, v in data.items():
            l_columns.append(v)
        rows = zip(*l_columns)
        with open(filename, 'w+') as f:
            w = csv.writer(f)
            for row in rows:
                w.writerow(row)
    logger_csvs.info("exit write_csv_to_file")
    return


# HELPERS


def _search_table_for_vals(d, filename):
    """
    Search a data tables for column values. Return a dict of column values
    :param dict d: Table data
    :return dict: Column values. ref by var name
    """
    cols = {}
    # if something goes wrong, we want a filename that we can track this data back to
    # however, if there's no "filename" entry, then we'll leave that data missing
    if "columns" in d:
        try:
            for name_col, data_col in d["columns"].items():
                vals = _search_col_for_vals(data_col, filename)
                if vals:
                    cols[name_col] = vals
        except AttributeError:
            print("Error: Table 'columns' entries must be a dictionary type")
            logger_csvs.debug("search_table_for_vals: AttributeError: expected type dict, given type {}".format(type(d)))

    return cols


def _search_col_for_vals(data_col, filename):
    """
    Get the values key from a data column
    :param dict data_col: Metadata column w/ values
    :param str filename: Filename of where this column came from
    :return list:
    """
    val = []
    try:
        val = data_col["values"]
    except KeyError:
        # tell user which csv file and variable is causing issues.
        print("Error: {}, '{}' is missing a 'values' entry".format(filename, data_col["variableName"]))
        logger_csvs.info("_search_col_for_vals: KeyError: Filename: {},  '{}' is missing a 'values' "
                         "entry".format(filename, data_col["variableName"]))

    return val


def _set_filename(table, filename):
    """
    Overwrite filename in table with our standardized filename
    :param dict table: Metadata
    :param str filename: Crumbs filename
    :return dict: Metadata
    """
    try:
        table["filename"] = filename
    except KeyError:
        logger_csvs.info("_set_filename: KeyError, Unable to set filename into table")
    return table


def _get_filename(table, crumbs):
    """
    Get the filename from a data table. If it doesn't exist, create a new one based on table hierarchy in metadata file.
    format: <dataSetName>.<dataTableType><idx>.<dataTableName>.csv
    example: ODP1098B.Chron1.ChronMeasurementTable.csv
    :param dict table: Table data
    :return str: Filename
    """
    try:
        filename = table["filename"]
    except KeyError:
        logger_csvs.info("_get_filename: KeyError: missing filename key for {}".format(crumbs))
        print("Error: Missing filename for: {} , cannot load this file".format(crumbs))
        filename = ""
    return filename


def _get_dataset_name(d):
    """
    Get data set name from metadata
    :param dict d: Metadata
    :return str: Data set name
    """
    try:
        s = d["dataSetName"]
    except KeyError:
        logger_csvs.warn("get_dataset_name: KeyError: missing dataSetName")
        s = "lipds"
    return s


def _merge_ensemble(ensemble, col_nums, col_vals):
    """
    The second column is not typical.
    "number" is a list of column numbers and "values" is an array of column values.
    Before we can write this to csv, it has to match the format the writer expects.
    :param dict ensemble: First column data
    :param list col_nums: Second column numbers. list of ints
    :param list col_vals: Second column values. list of lists
    :return dict:
    """
    try:
        # Loop for each column available
        for num in col_nums:
            # first column number in col_nums is usually "2", so backtrack once since ensemble already has one entry
            # col_vals is 0-indexed, so backtrack 2 entries
            ensemble[num-1] = col_vals[num - 2]

    except IndexError:
        logger_csvs.debug("merge_ensemble: IndexError: index out of range")

    return ensemble

