import csv

from ..helpers.loggers import *

logger_csvs = create_logger("csvs")


# IMPORT


def import_csv_to_metadata(d):
    """
    Using the given metadata dictionary, retrieve CSV data from CSV files, and insert the CSV
    values into their respective metadata columns. Checks for both paleoData and chronData tables.
    :param dict d: Metadata
    :return dict: Modified metadata dictionary
    """
    logger_csvs.info("enter import_csv_to_metadata")

    # Add CSV to paleoData
    if "paleoData" in d:
        d["paleoData"] = _import_csv_section(d["paleoData"], "paleo")

    # Add CSV to chronData
    if "chronData" in d:
        d["chronData"] = _import_csv_section(d["chronData"], "chron")

    logger_csvs.info("exit import_csv_to_metadata")
    return d


def _import_csv_section(section_data, pc):
    """
    Add csv data to all paleo data tables
    :param dict section_data: Metadata
    :return dict: Modified metadata
    """
    logger_csvs.info("enter import_csv: {}".format(pc))

    # Loop through each table_data in paleoData
    for table_name, table_data in section_data.items():

        if "{}MeasurementTable".format(pc) in table_data:
            # Send whole table_data through. Adds csv data to columns
            for table_name2, table_data2 in table_data["{}MeasurementTable".format(pc)].items():
                table_data["{}MeasurementTable".format(pc)][table_name2] = _add_csv_to_columns(table_data2)

        if "{}Model".format(pc) in table_data:
            table_data["{}Model".format(pc)] = _import_model_csv(table_data["{}Model".format(pc)], pc)

    logger_csvs.info("exit import_csv: {}".format(pc))
    return section_data


def _import_model_csv(models, pc):
    """
    Add csv data to each column in chron model
    :param list models: Metadata
    :param str pc: Paleo or chron
    :return dict: Modified metadata
    """
    logger_csvs.info("enter import_model_csv: {}".format(pc))

    for model in models:

        if "{}ModelTable".format(pc) in model:
            model["{}ModelTable".format(pc)] = _add_csv_to_columns(model["{}ModelTable".format(pc)])
        if "ensembleTable" in model:
            model["ensembleTable"] = _add_csv_to_columns(model["ensembleTable"])

        # Check for calibratedAges (old format) and distributionTable (current format)
        if "calibratedAges" in model:
            model["distributionTable"] = {}
            # Calibrated age tables are nested. Go down an extra layer.
            for k, v in model["calibratedAges"].items():
                model["distributionTable"][k] = _add_csv_to_columns(v)
        elif "distributionTable" in model:
            for k, v in model["distributionTable"].items():
                model["distributionTable"][k] = _add_csv_to_columns(v)

    logger_csvs.info("exit import_model_csv: {}".format(pc))
    return models


# EXPORT


def export_csv_to_metadata(d):
    """
    Initial call. Start the process of finding column values in metadata and writing it to csv files
    :param dict d:
    :return:
    """
    logger_csvs.info("enter export_csv_to_metadata")
    csv_only = {}
    crumbs = _get_data_set_name(d)

    # read from paleo data
    if "paleoData" in d:
        tmp = _export_csv_section(d["paleoData"], crumbs, "paleo")
        csv_only.update(tmp)

    # read from chron data
    if "chronData" in d:
        tmp = _export_csv_section(d["chronData"], crumbs, "chron")
        csv_only.update(tmp)

    # Write out all the tables that we collected
    for filename, data in csv_only.items():
        write_csv_to_file(filename, data)

    logger_csvs.info("exit export_csv_to_metadata")
    return csv_only


def _export_csv_section(section_data, crumbs, pc):
    """
    Export data from chron data
    :param dict section_data: Metadata
    :param str crumbs: Table name bread crumbs
    :param str pc: Paleo or chron
    :return:
    """
    logger_csvs.info("enter export_csv_section: {}".format(pc))
    chron_csv = {}
    idx = 1

    try:
        for table_name, table_data in section_data.items():
            # Process Model
            if "{}Model".format(pc) in table_data:

                # String together crumbs for this level
                crumbs_tmp = "{}{}{}".format(crumbs, pc, str(idx))

                # Replace the chronModel in-place
                tmp = _export_model_csv(table_data["{}Model".format(pc)], crumbs_tmp, pc)
                chron_csv.update(tmp)

            # Process chronMeasurementTable
            if "{}MeasurementTable".format(pc) in table_data:

                # String together crumbs for this level
                crumbs_tmp = "{}{}{}{}MeasurementTable".format(crumbs, pc, str(idx), pc)

                # Replace the chronMeasurementTable in-place
                tmp = _rip_csv_to_columns(table_data["{}MeasurementTable".format(pc)], crumbs_tmp)
                chron_csv.update(tmp)

            idx += 1

    except AttributeError:
        logger_csvs.debug("export_csv_section: {}, AttributeError: expected dict type, given {}".format(pc, type(section_data)))

    logger_csvs.info("exit export_csv_section: {}".format(pc))
    return chron_csv


def _export_model_csv(models, crumbs, pc):
    """
    Export data from chron model
    :param dict models: Metadata
    :param str crumbs: Table name bread crumbs
    :param str pc: Paleo or chron
    :return dict:
    """
    logger_csvs.info("enter export_model_csv: {}".format(pc))
    model_csv = {}
    idx = 1

    for model in models:
        tmp = {}

        # String together crumbs for this level
        crumbs_tmp = "{}model{}".format(crumbs, str(idx))

        # This could be more efficient by doing model_csv.update(_rip_csv_to_columns(model["chronModelTable"]))
        if "{}ModelTable" in model:
            crumbs_model = "{}{}summaryTable.csv".format(crumbs_tmp, pc)
            tmp = _rip_csv_to_columns(model["{}ModelTable".format(pc)], crumbs_model)
        elif "summaryTable" in model:
            crumbs_model = "{}{}summaryTable.csv".format(crumbs_tmp, pc)
            tmp = _rip_csv_to_columns(model["{}summaryTable".format(pc)], crumbs_model)
        if "ensembleTable" in model:
            crumbs_ensemble = "{}ensembleTable.csv"
            tmp = _rip_csv_to_columns(model["ensembleTable"], crumbs_ensemble)
        if "calibratedAges" in model:
            # Calibrated age tables are nested. Go down an extra layer.
            c_idx = 1
            for k, v in model["calibratedAges"].items():
                crumbs_ca = "{}distributionTable{}.csv".format(crumbs_tmp, str(c_idx))
                tmp2 = _rip_csv_to_columns(v, crumbs_ca)
                tmp.update(tmp2)
                c_idx += 1
        elif "distributionTable" in model:
            # Calibrated age tables are nested. Go down an extra layer.
            c_idx = 1
            for k, v in model["distributionTable"].items():
                crumbs_ca = "{}distributionTable{}.csv".format(crumbs_tmp, str(c_idx))
                tmp2 = _rip_csv_to_columns(v, crumbs_ca)
                tmp.update(tmp2)
                c_idx += 1

        # Update the model_csv with the new csv data that trickled up.
        model_csv.update(tmp)
        idx += 1

    logger_csvs.info("exit export_model_csv: {}".format(pc))
    return model_csv


def _rip_csv_to_columns(table, crumbs):
    """
    Rip the csv data from a given table
    :param dict table: Table data
    :return dict: key: table filename val: column data
    """
    col_data = {}
    complete = {}
    ens = False

    # Get the filename or table name
    filename = _get_filename(table, crumbs)

    try:
        # Loop over "columns" key and track all data
        for var, col in table["columns"].items():

            # Get the column number, and decrement for 0-index.
            # This is the position that the col will be written to in csv.
            try:
                # Catch the ensemble table exception. "number" is a list instead of an int
                if isinstance(col["number"], list):
                    ens_num = col["number"]
                    ens_val = col["values"]
                    ens = True
                else:
                    num = col["number"] - 1
                    arr = col["values"]

                    # Set data to the running col data
                    col_data[num] = arr

            except KeyError:
                logger_csvs.warning("rip_csv_to_columns: KeyError: missing number or values keys")
        if ens:
            col_data = _merge_ensemble(col_data, ens_num, ens_val)

    except AttributeError:
        logger_csvs.debug("rip_csv_to_columns: AttributeError: expected dict, given {}".format(type(table)))

    complete[filename] = col_data

    return complete


def write_csv_to_file(filename, d):
    """
    Writes columns of data to a target CSV file.
    :param str filename: Target CSV file
    :param dict d: A dictionary containing one list for every data column. Keys: int, Values: list
    :return None:
    """
    logger_csvs.info("enter write_csv_to_file")
    l_columns = []
    for k, v in d.items():
        l_columns.append(v)
    rows = zip(*l_columns)
    with open(filename, 'w+') as f:
        w = csv.writer(f)
        for row in rows:
            w.writerow(row)
    logger_csvs.info("exit write_csv_to_file")
    return


# SKIM CSV AFTER IMPORT


def get_organized_csv(metadata):
    """
    Get only csv data from metadata
    :param dict metadata: Metdata
    :return dict:
    """
    logger_csvs.info("enter get_organized_csv")

    d = {}
    crumbs = _get_data_set_name(metadata)

    if "paleoData" in metadata:
        crumbs_tmp = "{}paleo".format(crumbs)
        pd_out = _get_csv_section(metadata["paleoData"], crumbs_tmp, "paleo")
        d.update(pd_out)

    if "chronData" in metadata:
        crumbs_tmp = "{}chron".format(crumbs)
        cd_out = _get_csv_section(metadata["chronData"], crumbs_tmp, "chron")
        d.update(cd_out)

    logger_csvs.info("exit get_organized_csv")
    return d


def _get_csv_section(section_data, crumbs, pc):
    """
    Get table name, variable name, and column values from paleo metadata
    :param dict section_data: Metadata
    :param str crumbs: Table name crumbs
    :param str pc: Paleo or chron
    :return dict: Metadata
    """
    logger_csvs.info("enter get_csv_section: {}".format(pc))
    d = {}
    try:
        # Process the tables in chronData
        for name_table, data_table in section_data.items():
            crumbs_tmp = "{}{}".format(crumbs, str(name_table))

            # Process each entry sub-table below if they exist
            if "{}MeasurementTable".format(pc) in data_table:
                idx = 1
                for name_pmt, data_pmt in data_table["{}MeasurementTable".format(pc)].items():
                    crumbs_tmp_cmt = "{}{}{}csv".format(crumbs_tmp, "{}MeasurementTable".format(pc), idx)
                    filename = _get_filename(data_pmt, crumbs_tmp_cmt)
                    out = _search_table_for_vals(data_pmt)
                    d[filename] = out
                    idx += 1

            if "{}Model".format(pc) in data_table:
                for item in data_table["{}Model".format(pc)]:
                    if "calibratedAges" in item:
                        # CA has an extra level of nesting
                        for name_ca, data_ca in item["calibratedAges"].items():
                            crumbs_tmp_ca = "{}{}.csv".format(crumbs, name_ca)
                            filename = _get_filename(data_ca, crumbs_tmp_ca)
                            out = _search_table_for_vals(data_ca)
                            d[filename] = out
                    elif "distributionTable" in item:
                        # CA has an extra level of nesting
                        for name_ca, data_ca in item["distributionTable"].items():
                            crumbs_tmp_ca = "{}{}.csv".format(crumbs, name_ca)
                            filename = _get_filename(data_ca, crumbs_tmp_ca)
                            out = _search_table_for_vals(data_ca)
                            d[filename] = out

                    if "{}ModelTable".format(pc) in item:
                        crumbs_tmp_cmt2 = "{}{}.csv".format(crumbs, "{}ModelTable".format(pc))
                        filename = _get_filename(item["{}ModelTable".format(pc)], crumbs_tmp_cmt2)
                        out = _search_table_for_vals(item["{}ModelTable".format(pc)])
                        d[filename] = out

                    elif "summaryTable".format() in item:
                        crumbs_tmp_cmt2 = "{}{}.csv".format(crumbs, "summaryTable".format(pc))
                        filename = _get_filename(item["summaryTable"], crumbs_tmp_cmt2)
                        out = _search_table_for_vals(item["summaryTable"])
                        d[filename] = out

                    if "ensembleTable" in item:
                        crumbs_tmp_et = "{}{}.csv".format(crumbs, "ensembleTable")
                        filename = _get_filename(item["ensembleTable"], crumbs_tmp_et)
                        out = _search_table_for_vals(item["ensembleTable"])
                        d[filename] = out

    except AttributeError:
        logger_csvs.info("get_csv_section: {}, AttributeError: expected type dict, given type {}".format(pc, type(section_data)))

    logger_csvs.info("exit get_section_csv: {}".format(pc))
    return d


# HELPERS


def _search_table_for_vals(d):
    """
    Search a data tables for column values. Return a dict of column values
    :param dict d: Table data
    :return dict: Column values. ref by var name
    """
    cols = {}
    if "columns" in d:
        try:
            for name_col, data_col in d["columns"].items():
                vals = _get_key_values(data_col)
                if vals:
                    cols[name_col] = vals
        except AttributeError:
            logger_csvs.debug("search_table_for_vals: AttributeError: expected type dict, given type {}".format(type(d)))

    return cols


def _get_key_values(data_col):
    """
    Get the values key from a data column
    :param dict data_col:
    :return list:
    """
    val = []
    try:
        val = data_col["values"]
    except KeyError:
        logger_csvs.info("get_values_key: KeyError: missing values key")

    return val


def _get_table_csv_filename(table):
    """
    Get the value from the filename field if the table has one
    :param dict table: Table metadata
    :return str: Filename
    """
    file = ""
    try:
        file = table["filename"]
    except KeyError:
        logger_csvs.info("get_table_csv_filename: KeyError: missing csv filename")
    return file


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
        logger_csvs.info("get_filename: KeyError: missing filename key")
        filename = crumbs
    return filename


def _get_data_set_name(d):
    """
    Get data set name from metadata
    :param dict d: Metadata
    :return str: Data set name
    """
    try:
        s = d["dataSetName"]
    except KeyError:
        logger_csvs.warn("get_data_set_name: KeyError: missing dataSetName")
        s = "lipd"
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


def _cast_value(d, idx, x):
    """
    Attempt to cast string to float. If error, keep as a string.
    :param str x: String data
    :return any:
    """
    try:
        d[idx].append(float(x))
    except ValueError as e:
        d[idx].append(x)
        logger_csvs.warn("ValueError: col: {}, {}".format(x, e))
    except KeyError as e:
        logger_csvs.warn("KeyError: col: {}, {}".format(x, e))

    return d


def _add_csv_to_columns(table):
    """
    Add csv data to each column in a list of columns
    :param dict table: Table metadata
    :return dict: Table metadata with csv "values" entry
    """
    # Get the filename or this table
    filename = _get_table_csv_filename(table)

    # If there's no filename, bypass whole process
    if filename:
        # Call read_csv_to_columns for this filename. csv_data is list of lists.
        csv_data = _read_csv_to_columns(filename)

        # Start putting CSV data into corresponding column "values" key
        try:
            for col_name, col in table['columns'].items():
                # The "number" entry in the ensemble table is a list of columns, instead of an int.
                # In this case, just store all the csv data as a batch.
                if isinstance(col["number"], list):
                    col["values"] = csv_data
                # For all other cases, "number" is a single int, and "values" should hold one column list.
                else:
                    col['values'] = csv_data[col["number"] - 1]
        except IndexError:
            logger_csvs.warning("add_csv_to_json: IndexError: index out of range of csv_data list")
        except KeyError:
            logger_csvs.debug("add_csv_to_json: KeyError: missing columns key")

    return table


def _read_csv_to_columns(filename):
    """
    Opens the target CSV file and creates a dictionary with one list for each CSV column.
    :param str filename:
    :return list of lists: column values
    """
    logger_csvs.info("enter read_csv_to_columns")
    d = {}
    l = []
    try:
        with open(filename, 'r') as f:
            r = csv.reader(f, delimiter=',')

            # Create a dict with X lists corresponding to X columns
            for idx, col in enumerate(next(r)):
                d[idx] = []
                d = _cast_value(d, idx, col)

            # Start iter through CSV data
            for row in r:
                for idx, col in enumerate(row):
                    # Append the cell to the correct column list
                    d = _cast_value(d, idx, col)

        # Make a list of lists out of the dictionary instead
        for idx, col in d.items():
            l.append(col)

    except FileNotFoundError as e:
        print('CSV FileNotFound: ' + filename)
        logger_csvs.warn("read_csv_to_columns: FileNotFound: {}, {}".format(filename, e))
    logger_csvs.info("exit read_csv_to_columns")
    return l

