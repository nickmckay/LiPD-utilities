from .doi_resolver import DOIResolver
from .bag import *
from .directory import *
from .zips import *
from .jsons import *
from .loggers import create_logger
from .misc import is_one_dataset

logger_doi_main = create_logger("doi_main")


def doi_main(D, force):
    """
    Main function that controls the script. Take in directory containing the .lpd file(s). Loop for each file.

    :param dict D: Metadata, single or multiple datasets
    :param bool force: Force DOIs to update even if they have previously been processed. Default is False.
    :return dict D: Metadata, single or multiple datasets
    """
    logger_doi_main.info("enter doi_main")

    results = previously_run_doi(D)
    display_results(results)
    # force = prompt_force()

    if is_one_dataset(D):
        name = D["dataSetName"]
        D = DOIResolver(dsn=name, D=D, results=results[name], force=force).main()

    else:
        for name, L in D.items():
            D[name] = DOIResolver(dsn=name, D=L, results=results[name], force=force).main()

    logger_doi_main.info("exit doi_main")
    print("Process Complete")
    return D


def previously_run_doi(D):
    """
    Check if the DOIs for each dataset were previosuly run through the API.
    If author, journal, and year data is present, then we assume that DOI was previously run.

    True: Yes, DOI was previously run through the API
    False: No, the DOI has not yet been processed.

    :param dict D: Metadata, single or multiple datasets
    :return dict results: True / False for each DOI
    """

    look_for = ["author", "journal", "year"]
    # Results for each DOI sorted by dataSetName
    results = {}

    try:
        # Run function if this is a single dataset
        if is_one_dataset(D):
            # Does pub exist?
            if "pub" in D:
                # Create an empty entry in the results dictionary for this dataset
                results[D["dataSetName"]] = {}
                # Loop for each pub
                for pub in D["pub"]:
                    # Temporary array that tracks if each key is present and has data.
                    _tmp = []
                    # Loop for each key
                    for key in look_for:
                        # Key is in pub
                        if key in pub:
                            # Key has data
                            if pub[key]:
                                _tmp.append(True)
                            # Key does not have data
                            else:
                                _tmp.append(False)
                        # Key is not in pub
                        else:
                            _tmp.append(False)
                    # If all the keys are present and contain data, then we say True, this DOI was previosuly run
                    if all(_tmp):
                        results[D["dataSetName"]][pub["doi"]] = True
                    else:
                        results[D["dataSetName"]][pub["doi"]] = False

        else:
            # Loop for each dataset given
            for name, L in D.items():
                # Recursive call to this same function, with one dataset
                results_nested = previously_run_doi(L)
                # Bubble up the results and add it to our current overall results.
                if results_nested:
                    for k,v in results_nested.items():
                        results[k] = v

    except Exception as e:
        # No DOI key in publication
        pass

    return results


def display_results(results):
    """

    :param dict results: Results of which DOIs have been previously processed, sorted by dataSetName
    :return:
    """
    processed = 0
    total = 0

    for name, dat in results.items():
        for doi, bool in dat.items():
            total += 1
            if bool:
                processed += 1

    print("{} of {} DOIs have previously been processed.". format(processed, total))
    return


def prompt_force():
    """
    Ask the user if they want to force update files that were previously resolved

    :return bool: True, force update, False, don't force update.
    """
    logger_doi_main.info("enter prompt_force")

    count = 0
    print("Do you want to force updates for previously processed DOIs? (y/n)")
    while True:
        force = input("> ")
        try:
            if count == 2:
                return True
            elif force.lower() in ('y', 'yes'):
                return True
            elif force.lower() in ('n', 'no'):
                return False
            else:
                print("Invalid response")
        except AttributeError as e:
            print("Invalid response")
            logger_doi_main.warn("invalid response: {}, {}".format(force, e))
        count += 1
    logger_doi_main.info("force update: {}".format(force))
    logger_doi_main.info("exit prompt_force")
    return True
