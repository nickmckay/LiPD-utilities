from .alternates import VER_1_3
from .loggers import create_logger
from .misc import is_one_dataset

logger_versions = create_logger("versions")


def fix_pubYear(D):
    """
    Move the DOI from the BibJson location, to our desired pub top-level location under "doi"

    Remove 'pubYear' keys and reassign to 'year' if necessary.

    :param   dict D: Metadata
    :return  dict D: Metadata, with data modified where applicable
    """
    if is_one_dataset:
        if "pub" in D:
            # Loop for each publication entry
            for pub in D["pub"]:
                if "pubYear" in pub:
                    if "year" not in pub:
                        pub["year"] = pub["pubYear"]
                    del pub["pubYear"]

    else:
        # Loop for each dataset if D is multiple datasets
        for idx, L in enumerate(D):
            D[idx] = fix_pub(L)

    return D


def fix_doi(L):
    """
    'pubYear' keys need to be switched to 'year' where applicable

    DOIs are commonly stored in the BibJson format under "identifier". We want to move these to the root
    of the publication under "doi". Make the reassignments necessary and also remove duplicate and unwanted
    Doi/DOI keys.

    :param  dict L:  Metadata
    :return dict L:  Metdata
    """
    # Keys that we don't want. Reassign data to 'doi' key
    _dois = ["DOI", "Doi"]
    # Loop for each publication entry
    try:
        if "pub" in L:
            for pub in L["pub"]:
                try:
                    # Is there an identifier in this publication?
                    if "identifier" in pub:
                        # Attempt to grab the doi from the id location. If it doesn't work, we'll catch the error.
                        _identifier = pub["identifier"][0]["id"]
                        # Got identifier. Is there a valid string here?
                        if _identifier:
                            # Reassign the doi to the publication root 'doi' key
                            pub["doi"] = _identifier
                            # Delete the identifier key and data
                            del pub["identifier"]
                except Exception:
                    # Catch the KeyError, and continue on normally.
                    pass

                # Check for each doi key that we don't want
                for _key in _dois:
                    # Is it in the publication entry?
                    if _key in pub:
                        #  Is there valid string data?
                        if pub[_key]:
                            # Reassign the doi to the 'doi' key
                            pub["doi"] = pub[_key]
                        # Delete the bad doi key
                        del pub[_key]
        else:
            L["pub"] = []
    except Exception as e:
        logger_versions.info("fix_doi: Publication error: {}".format(e))
    return L


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

    L = fix_doi(L)
    L = fix_pubYear(L)
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


