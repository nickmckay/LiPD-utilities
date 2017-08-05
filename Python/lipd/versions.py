from .alternates import VER_1_3
from .loggers import create_logger

logger_versions = create_logger("versions")


def get_lipd_version(L):
    """
    Check what version of LiPD this file is using. If none is found, assume it's using version 1.0
    :param dict L: Metadata
    :return float:
    """
    version = 1.0
    _keys = ["LipdVersion", "LiPDVersion", "lipdVersion", "liPDVersion"]
    for _key in _keys:
        if _key in L:
            version = L[_key]
            # Cast the version number to a float
            try:
                version = float(version)
            except AttributeError:
                # If the casting failed, then something is wrong with the key so assume version is 1.0
                version = 1.0
            L.pop(_key)
    return L, version


def _merge_interpretations(d):
    """

    :param d:
    :return:
    """
    _tmp = []
    try:
        # Now loop and aggregate the interpretation data into one list
        for k, v in d.items():
            if k in ["climateInterpretation", "isotopeInterpretation", "interpretation"]:
                # now add in the new data
                if isinstance(v, list):
                    for i in v:
                        _tmp.append(i)
                elif isinstance(v, dict):
                    _tmp.append(d[k])
        # Set the aggregate data into the interpretation key
        d["interpretation"] = _tmp

    except Exception as e:
        print("Error: merge_interpretations: {}".format(e))

    # Now remove the old interpretation keys
    for key in ["climateInterpretation", "isotopeInterpretation"]:
        try:
            d[key] = ""
        except Exception:
            pass

    return d


def update_lipd_version(L):
    """
    Metadata is indexed by number at this step.

    Use the current version number to determine where to start updating from. Use "chain versioning" to make it
    modular. If a file is a few versions behind, convert to EACH version until reaching current. If a file is one
    version behind, it will only convert once to the newest.
    :param dict L: Metadata
    :return dict d: Metadata
    """
    # Get the lipd version number.
    L, version = get_lipd_version(L)

    # Update from (N/A or 1.0) to 1.1
    if version in [1.0, "1.0"]:
        L = update_lipd_v1_1(L)
        version = 1.1

    # Update from 1.1 to 1.2
    if version in [1.1, "1.1"]:
        L = update_lipd_v1_2(L)
        version = 1.2
    if version in [1.2, "1.2"]:
        L = update_lipd_v1_3(L)
        version = 1.3

    L["lipdVersion"] = 1.3
    return L


def update_lipd_v1_1(d):
    """
    Update LiPD v1.0 to v1.1
    - chronData entry is a list that allows multiple tables
    - paleoData entry is a list that allows multiple tables
    - chronData now allows measurement, model, summary, modelTable, ensemble, calibratedAges tables
    - Added 'lipdVersion' key

    :param dict d: Metadata v1.0
    :return dict d: Metadata v1.1
    """
    logger_versions.info("enter update_lipd_v1_1")
    tmp_all = []

    try:
        # ChronData is the only structure update
        if "chronData" in d:
            # As of v1.1, ChronData should have an extra level of abstraction.
            # No longer shares the same structure of paleoData

            # If no measurement table, then make a measurement table list with the table as the entry
            for table in d["chronData"]:
                if "chronMeasurementTable" not in table:
                    tmp_all.append({"chronMeasurementTable": [table]})

                # If the table exists, but it is a dictionary, then turn it into a list with one entry
                elif "chronMeasurementTable" in table:
                    if isinstance(table["chronMeasurementTable"], dict):
                        tmp_all.append({"chronMeasurementTable": [table["chronMeasurementTable"]]})
            if tmp_all:
                d["chronData"] = tmp_all

        # Log that this is now a v1.1 structured file
        d["lipdVersion"] = 1.1
    except Exception as e:
        logger_versions.error("update_lipd_v1_1: Exception: {}".format(e))
    logger_versions.info("exit update_lipd_v1_1")
    return d


def update_lipd_v1_2(d):
    """
    Update LiPD v1.1 to v1.2
    - Added NOAA compatible keys : maxYear, minYear, originalDataURL, WDCPaleoURL, etc
    - 'calibratedAges' key is now 'distribution'
    - paleoData structure mirrors chronData. Allows measurement, model, summary, modelTable, ensemble,
        distribution tables
    :param dict d: Metadata v1.1
    :return dict d: Metadata v1.2
    """
    logger_versions.info("enter update_lipd_v1_2")
    tmp_all = []

    try:
        # PaleoData is the only structure update
        if "paleoData" in d:
            # As of 1.2, PaleoData should match the structure of v1.1 chronData.
            # There is an extra level of abstraction and room for models, ensembles, calibrations, etc.
            for table in d["paleoData"]:
                if "paleoMeasurementTable" not in table:
                    tmp_all.append({"paleoMeasurementTable": [table]})

                # If the table exists, but it is a dictionary, then turn it into a list with one entry
                elif "paleoMeasurementTable" in table:
                    if isinstance(table["paleoMeasurementTable"], dict):
                        tmp_all.append({"paleoMeasurementTable": [table["paleoMeasurementTable"]]})
            if tmp_all:
                d["paleoData"] = tmp_all
        # Log that this is now a v1.1 structured file
        d["lipdVersion"] = 1.2
    except Exception as e:
        logger_versions.error("update_lipd_v1_2: Exception: {}".format(e))

    logger_versions.info("exit update_lipd_v1_2")
    return d


def update_lipd_v1_3(d):
    """
    Update LiPD v1.2 to v1.3
    - Added 'createdBy' key
    - Top-level folder inside LiPD archives are named "bag". (No longer <datasetname>)
    - .jsonld file is now generically named 'metadata.jsonld' (No longer <datasetname>.lpd )
    - All "paleo" and "chron" prefixes are removed from "paleoMeasurementTable", "paleoModel", etc.
    - Merge isotopeInterpretation and climateInterpretation into "interpretation" block
    - ensemble table entry is a list that allows multiple tables
    - summary table entry is a list that allows multiple tables
    :param dict d: Metadata v1.2
    :return dict d: Metadata v1.3
    """
    # sub routine (recursive): changes all the key names and merges interpretation
    d = update_lipd_v1_3_names(d)
    # sub routine: changes ensemble and summary table structure
    d = update_lipd_v1_3_structure(d)
    d["lipdVersion"] = 1.3
    if "LiPDVersion" in d:
        del d["LiPDVersion"]
    return d


def update_lipd_v1_3_names(d):
    """
    Update the key names and merge interpretation data
    :param dict d: Metadata
    :return dict d: Metadata
    """
    try:
        if isinstance(d, dict):
            for k, v in d.items():
                # dive down for dictionaries
                d[k] = update_lipd_v1_3_names(v)

                # see if the key is in the remove list
                if k in VER_1_3["swap"]:
                    # replace the key in the dictionary
                    _key_swap = VER_1_3["swap"][k]
                    d[_key_swap] = d.pop(k)
                elif k in VER_1_3["tables"]:
                    d[k] = ""
            for _key in ["climateInterpretation", "isotopeInterpretation"]:
                if _key in d:
                    d = _merge_interpretations(d)

        elif isinstance(d, list):
            # dive down for lists
            for idx, i in enumerate(d):
                d[idx] = update_lipd_v1_3_names(i)
    except Exception as e:
        print("Error: Unable to update file to LiPD v1.3: {}".format(e))
        logger_versions.error("update_lipd_v1_3_names: Exception: {}".format(e))
    return d


def update_lipd_v1_3_structure(d):
    """
    Update the structure for summary and ensemble tables
    :param dict d: Metadata
    :return dict d: Metadata
    """
    for key in ["paleoData", "chronData"]:
        if key in d:
            for entry1 in d[key]:
                if "model" in entry1:
                    for entry2 in entry1["model"]:
                        for key_table in ["summaryTable", "ensembleTable"]:
                            if key_table in entry2:
                                if isinstance(entry2[key_table], dict):
                                    try:
                                        _tmp = entry2[key_table]
                                        entry2[key_table] = []
                                        entry2[key_table].append(_tmp)
                                    except Exception as e:
                                        logger_versions.error("update_lipd_v1_3_structure: Exception: {}".format(e))
    return d


