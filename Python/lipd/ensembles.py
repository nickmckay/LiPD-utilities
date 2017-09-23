import re

from .loggers import *
from .misc import unwrap_arrays, match_arr_lengths
from .regexes import re_model_name
from collections import OrderedDict


logger_ensembles = create_logger("ensembles")


# def create_ensemble(ensemble):
#     """
#     Add ensemble data to a LiPD object
#     :param list ensemble: Ensemble data nested lists
#     :return dict: Structured Ensemble data
#     """
#     logger_ensembles.info("enter add_ensemble")
#     ens = {}
#     # "Flatten" the nested lists. Bring all nested lists up to top-level. Output looks like [ [1,2], [1,2], ... ]
#     ll = unwrap_arrays(ensemble)
#     # Check that list lengths are all equal
#     valid = match_arr_lengths(ll)
#     if valid:
#         # Template for ensemble structure
#         ens = {"columns": {
#                 "depth":{"number": 1, "variableName": "depth", "units":"cm", "values": []},
#                 "age":{"number": [], "variableName": "age","units": "BP", "values": []}}}
#         # Start creating the ensemble dictionary.
#         for idx, l in enumerate(ll):
#             if idx > 0:
#                 ens["columns"]["age"]["values"].append(l)
#                 ens["columns"]["age"]["number"].append(idx+1)
#             else:
#                 ens["columns"]["depth"]["values"] = l
#     else:
#         # Lists are unequal. Print error and return nothing.
#         print("Error: Numpy Array lengths do not match. Cannot create ensemble entry")
#     logger_ensembles.info("exit add_ensemble")
#     return ens


def addModel(D, models):
    """
    Insert model data into a LiPD dataset

    Model names should be in the format:
    chron0model0
    chron0model1
    chron1model0
    etc

    :param dict D: Metadata
    :param dict models: Model data to add
    :return dict D: Metadata
    """
    try:
        # Loop for each model that needs to  be added
        for _model_name, _model_data in models.items():
            # split the table name into a path that we can use
            _m = re.match(re_model_name, _model_name)
            if _m:
                D = _put_model(D, _model_name, _model_data, _m)
            else:
                print("The table name found in the given model data isn't valid for automatic placement")
                _placement_name = _prompt_placement(D)
                _m = re.match(re_model_name, _placement_name)
                if _m:
                    D = _put_model(D, _placement_name, _model_data, _m)
                else:
                    print("Oops. This shouldn't happen")
                    return

    except Exception as e:
        print("addModel: Model data NOT added, {}".format(e))

    return D



def _get_available_placements(D):
    """
    Get a list of possible places that we can put the new model data into.
    If no model exists yet, we'll use something like chron0model0. If other models exist,
    we'll go for the n+1 entry.
    ex: chron0model0 already exists, so we'll look to chron0model1 next.

    :param dit D: Metadata
    :return list _options: Possible placements
    """
    _options = []

    try:
        for _pc in ["paleoData", "chronData"]:
            if _pc in D:
                for section_name, section_data in D[_pc].items():
                    if "model" in section_data:
                        _idx = 0
                        while True:
                            _tmp_name = "{}model{}".format(section_name, _idx)
                            if _tmp_name not in section_data["model"]:
                                _options.append(_tmp_name)
                                break
                            _idx += 1
                    else:
                        _options.append("{}model0".format(section_name))
    except Exception as e:
        print("addModel: Unable to compile a list of placement options, {}".format(e))

    return _options

def _prompt_placement(D):
    """
    Since automatic placement didn't work, find somewhere to place the model data manually with the help of the user.

    :param dict D: Metadata
    :return str _model_name: Chosen placement
    """
    _model_name = ""
    # There wasn't a table name match, so we need prompts to fix it
    _placement_options = _get_available_placements(D)
    print("Please choose where you'd like to place this model:")
    for _idx, _opt in enumerate(_placement_options):
        print("({}) {}".format(_idx, _opt))
    _choice = input("> ")
    try:
        if int(_choice) <= len(_placement_options) and _choice:
            # Get the option the user chose
            _model_name = _placement_options[int(_choice)]
        else:
            # They user chose an option out of the placement list range
            print("Invalid choice input")
            return
    except Exception as e:
        # Choice was not a number or empty
        print("Invalid choice")

    return _model_name

def _put_model(D, name, dat, m):
    """


    :param D:
    :param name:
    :param dat:
    :param m:
    :return:
    """
    try:
        print("Placing model: {}".format(name))
        _pc = m.group(1) + "Data"
        _section = m.group(1) + m.group(2)
        if _pc not in D:
            # Section missing entirely? Can't continue
            print("{} not found in the provided dataset. Please try again".format(_pc))
            return
        else:
            if _section not in D[_pc]:
                # Creates section: Example: D[chronData][chron0]
                D[_pc][_section] = OrderedDict()
            if "model" not in D[_pc][_section]:
                # Creates model top level: Example: D[chronData][chron0]["model"]
                D[_pc][_section]["model"] = OrderedDict()
            if name not in D[_pc][_section]["model"]:
                D[_pc][_section]["model"][name] = dat
            else:
                # Model already exists, should we overwrite it?
                _prompt_overwrite = input(
                    "This model already exists in the dataset. Do you want to overwrite it? (y/n)")
                # Yes, overwrite with the model data provided
                if _prompt_overwrite == "y":
                    D[_pc][_section]["model"][name] = dat
                # No, do not overwrite.
                elif _prompt_overwrite == "n":
                    _name2 = _prompt_placement(D)
                    _m = re.match(re_model_name, _name2)
                    if _m:
                        D = _put_model(D, _name2, dat, _m)
                else:
                    print("Invalid choice")
    except Exception as e:
        print("addModel: Unable to put the model data into the dataset, {}".format(e))

    return D