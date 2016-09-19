from ..helpers.loggers import *
from ..helpers.misc import unwrap_arrays, match_arr_lengths

logger_ensembles = create_logger("ensembles")


def create_ensemble(ensemble):
    """
    Add ensemble data to a LiPD object
    :param list ensemble: Ensemble data nested lists
    :return dict: Structured Ensemble data
    """
    logger_ensembles.info("enter add_ensemble")
    ens = {}
    # "Flatten" the nested lists. Bring all nested lists up to top-level. Output looks like [ [1,2], [1,2], ... ]
    ll = unwrap_arrays(ensemble)
    # Check that list lengths are all equal
    valid = match_arr_lengths(ll)
    if valid:
        # Template for ensemble structure
        ens = {"columns": {
                "depth":{"number": 1, "variableName": "depth", "units":"cm", "values": []},
                "age":{"number": [], "variableName": "age","units": "BP", "values": []}}}
        # Start creating the ensemble dictionary.
        for idx, l in enumerate(ll):
            if idx > 0:
                ens["columns"]["age"]["values"].append(l)
                ens["columns"]["age"]["number"].append(idx+1)
            else:
                ens["columns"]["depth"]["values"] = l
    else:
        # Lists are unequal. Print error and return nothing.
        print("Error: Numpy Array lengths do not match. Cannot create ensemble entry")
    logger_ensembles.info("exit add_ensemble")
    return ens


def insert_ensemble(d, ens):
    """
    Insert the ensemble table dictionary into the LiPD metadata
    :param dict d: LiPD metadata
    :param dict ens: Ensemble data to insert
    :return dict:
    """
    # Check for chronData section
    if "chronData" in d:
        # Have to loop, even though we'll quit after inserting on one table
        for k, v in d["chronData"].items():
            # Check for a chronModel
            if "chronModel" in v:
                # Check for a chronModel[0].
                try:
                    x = d["chronData"][k]["chronModel"][0]
                # No chronModel[0]. Build it.
                except IndexError:
                    d["chronData"][k]["chronModel"][0] = {}
                d["chronData"][k]["chronModel"][0]["ensembleTable"] = ens
            # No chronModel. Build it.
            else:
                v["chronModel"] = []
                v["chronModel"][0] = {}
                v["chronModel"][0]["ensembleTable"] = ens

    else:
        # There is no chronData section. Build from scratch.
        d["chronData"] = {}
        d["chronData"]["chron"] = {}
        d["chronData"]["chron"]["chronModel"] = []
        d["chronData"]["chron"]["chronModel"][0] = {"ensembleTable": ens}

    return d