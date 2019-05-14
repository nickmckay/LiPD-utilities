from .doi_resolver import DOIResolver
from .bag import *
from .directory import *
from .zips import *
from .jsons import *
from .loggers import create_logger
from .misc import is_one_dataset

logger_doi_main = create_logger("doi_main")


def doi_main(D):
    """
    Main function that controls the script. Take in directory containing the .lpd file(s). Loop for each file.
    :return None:
    """
    logger_doi_main.info("enter doi_main")

    if is_one_dataset(D):
        D = DOIResolver(D["dataSetName"], D).main()

    else:
        for name, L in D.items():
            D[name] = DOIResolver(name, L).main()

    logger_doi_main.info("exit doi_main")
    print("Process Complete")
    return D


# def process_lpd(name, dir_tmp):
#     """
#     Opens up json file, invokes doi_resolver, closes file, updates changelog, cleans directory, and makes new bag.
#     :param str name: Name of current .lpd file
#     :param str dir_tmp: Path to tmp directory
#     :return none:
#     """
#     logger_doi_main.info("enter process_lpd")
#     dir_root = os.getcwd()
#     dir_bag = os.path.join(dir_tmp, name)
#     dir_data = os.path.join(dir_bag, 'data')
#
#     # Navigate down to jLD file
#     # dir : dir_root -> dir_data
#     os.chdir(dir_data)
#
#     # Open jld file and read in the contents. Execute DOI Resolver.
#     jld_data = read_json_from_file(os.path.join(dir_data, name + '.jsonld'))
#
#     # Overwrite data with new data
#     jld_data = DOIResolver(dir_root, name, jld_data).main()
#     # Open the jld file and overwrite the contents with the new data.
#     write_json_to_file(jld_data)
#
#     # Open changelog. timestamp it. Prompt user for short description of changes. Close and save
#     # update_changelog()
#
#     # Delete old bag files, and move files to bag root for re-bagging
#     # dir : dir_data -> dir_bag
#     dir_cleanup(dir_bag, dir_data)
#     finish_bag(dir_bag)
#
#     logger_doi_main.info("exit process_lpd")
#     return


# def prompt_force():
#     """
#     Ask the user if they want to force update files that were previously resolved
#
#     :return bool: response
#     """
#     logger_doi_main.info("enter prompt_force")
#     count = 0
#     print("Do you want to force updates for previously resolved files? (y/n)")
#     while True:
#         force = input("> ")
#         try:
#             if count == 2:
#                 return True
#             elif force.lower() in ('y', 'yes'):
#                 return True
#             elif force.lower() in ('n', 'no'):
#                 return False
#             else:
#                 print("invalid response")
#         except AttributeError as e:
#             print("invalid response")
#             logger_doi_main.warn("invalid response: {}, {}".format(force, e))
#         count += 1
#     logger_doi_main.info("force update: {}".format(force))
#     logger_doi_main.info("exit prompt_force")
#     return True
#
#
# if __name__ == '__main__':
#     doi_main()
#
