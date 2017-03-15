import numpy as np

from ..helpers.loggers import create_logger

logger_inferred_data = create_logger("inferred_data")


def _get_age(columns):
    """
    Sift through table column data and find the "age" or "year" column. Return its "values" data.
    :param dict columns: Column data
    :return list age: Age values
    """
    age = []
    try:
        # Check for age first (exact match)
        if "age" in columns:
            # Save the values
            age = columns["age"]["values"]
        # Check for year second (exact match)
        elif "year" in columns:
            # Save the values
            age = columns["year"]["values"]
        # No year or age found, start searching more intently.
        else:
            # Loop through column variableNames
            for k, v in columns.items():
                # Check for age in the variableName (loose match)
                if "age" in k:
                    # Save the values
                    age = v["values"]
                # Check for year in variableName (loose match)
                elif "year" in k:
                    # Save the values
                    age = v["values"]
    # If we expected a dictionary, and didn't get one
    except AttributeError as e:
        logger_inferred_data.warn("get_age: AttributeError: {}".format(e))
    # If we were looking for values, and didn't get one
    except KeyError as e:
        logger_inferred_data.warn("get_age: KeyError: {}".format(e))
    # Fail-safe for other problems
    except Exception as e:
        logger_inferred_data.warn("get_age: Exception: {}".format(e))

    return age


def _get_resolution(age, values):
    """
    Calculates the resolution (res)
    Thanks Deborah!
    """
    res = []
    try:
        # Get the nan index from the values and remove from age
        age2 = age[np.where(~np.isnan(values))[0]]
        res = np.diff(age2)
    except IndexError as e:
        print("get_resolution: IndexError: {}".format(e))
    except Exception as e:
        logger_inferred_data.warn("get_resolution: Exception: {}".format(e))
    return res


def _get_inferred_data_column(column, age):
    """
    Column level: Start creating the new fields and calculating the new data.
    :param dict column: Column data
    :param list age: Age values
    :return dict column: Column data - modified
    """
    try:
        # Make sure that age and values are numpy arrays
        age = np.asarray(age)
        # Get the values for this column
        values = column["values"]
        # If we have values, keep going
        if values:
            # Turn the values into a numpy array
            values = np.asarray(values)
            # Use the values to create new entries and data
            column["hasMinValue"] = np.min(values).tolist()
            column["hasMaxValue"] = np.max(values).tolist()
            column["hasMedianValue"] = np.median(values).tolist()
            column["hasMeanValue"] = np.mean(values).tolist()
            # Get the resolution for this age and column values data
            res = _get_resolution(age, values)
            # If we have successful resolution data, keep going
            if len(res) != 0:
                # Use the resolution values to create new entries and data
                column["hasResolution"] = {
                    "hasMinValue": np.min(res).tolist(),
                    "hasMaxValue": np.max(res).tolist(),
                    "hasMeanValue": np.mean(res).tolist(),
                    "hasMedianValue": np.median(res).tolist(),
                    "values": res.tolist()
                }
    except KeyError as e:
        logger_inferred_data.debug("get_inferred_data_column: KeyError: {}".format(e))
    except Exception as e:
        logger_inferred_data.debug("get_inferred_data_column: Exception: {}".format(e))

    return column


def get_inferred_data_table(table):
    """
    Table level: Dive down, calculate data, then return the new table with the inferred data.
    :param dict table: Table data
    :return dict table: Table with new data
    """

    # Get the age values data first, since it's needed to calculate the other column data.
    age = _get_age(table["columns"])

    # If age values were not found, then don't continue. There's no point!
    if age:
        try:
            # Loop for all the columns in the table
            for var, col in table["columns"].items():
                # Special cases
                # We do not calculate data for each of the keys below, and we cannot calculate any "string" data
                if var not in ["depth", "age", "year"] and not all(isinstance(i, str) for i in col["values"]):
                    # Send this particular column down to be calculated. Set the returned data in-place in the table.
                    table["columns"][var] = _get_inferred_data_column(col, age)
                # If we want to know which columns aren't being calculated...they end up here.
                # else:
                #     logger_inferred_data.info("get_inferred_data_table: "
                #                               "Not calculating inferred data for variableName: {}".format(var))
        except AttributeError as e:
            logger_inferred_data.warn("get_inferred_data_table: AttributeError: {}".format(e))
        except Exception as e:
            logger_inferred_data.warn("get_inferred_data_table: Exception: {}".format(e))
    else:
        try:
            logger_inferred_data.info("Unable to calculate inferred data for: {}".format(table["filename"]))
        except KeyError:
            logger_inferred_data.warn("get_inferred_data_table: Unable to calculate inferred data for: unknown table")

    return table
