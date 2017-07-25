from .doi_resolver import DOIResolver
from .bag import *
from .directory import *
from .zips import *
from .jsons import *
from .loggers import create_logger

logger_doi_main = create_logger("doi_main")


def doi_main(files):
    """
    Main function that controls the script. Take in directory containing the .lpd file(s). Loop for each file.
    :return None:
    """
    logger_doi_main.info("enter doi_main")

    print("Found {0} {1} file(s)".format(str(len(files[".lpd"])), 'LiPD'))
    force = prompt_force()
    for file in files[".lpd"]:

        # Unzip file and get tmp directory path
        dir_tmp = create_tmp_dir()
        unzipper(file["filename_ext"], dir_tmp)

        # Force DOI update?
        if force:
            # Update file. Forcing updates for all files.
            print('processing: {}'.format(file["filename_ext"]))
            logger_doi_main.info("processing: {}".format(file["filename_ext"]))
            # dir: dir_root -> dir_tmp
            process_lpd(file["filename_no_ext"], dir_tmp)
            # dir: dir_tmp -> dir_root
            os.chdir(file["dir"])
            # Zip the directory containing the updated files. Created in dir_root directory
            zipper(path_name_ext=file["filename_ext"], root_dir=dir_tmp, name=file["filename_no_ext"])
            # Cleanup and remove tmp directory
            shutil.rmtree(dir_tmp)

        if not force:
            # Don't Update File. Flag found and we're not forcing updates.
            if resolved_flag(open_bag(os.path.join(dir_tmp, file["filename_no_ext"]))):
                print('skipping: {}'.format(file["filename_ext"]))
                logger_doi_main.info("skipping: {}".format(file["filename_ext"]))
                shutil.rmtree(dir_tmp)

            # Update File. No flag found and hasn't been processed before.
            else:
                print('processing: {}'.format(file["filename_ext"]))
                logger_doi_main.info("processing: {}".format(file["filename_ext"]))
                # dir: dir_root -> dir_tmp
                process_lpd(file["filename_no_ext"], dir_tmp)
                # dir: dir_tmp -> dir_root
                os.chdir(file["dir"])
                # Zip the directory containing the updated files. Created in dir_root directory
                zipper(path_name_ext=file["filename_ext"], root_dir=dir_tmp, name=file["filename_no_ext"])
                # Cleanup and remove tmp directory
                shutil.rmtree(dir_tmp)
    logger_doi_main.info("exit doi_main")
    print("Process Complete")
    return


def process_lpd(name, dir_tmp):
    """
    Opens up json file, invokes doi_resolver, closes file, updates changelog, cleans directory, and makes new bag.
    :param str name: Name of current .lpd file
    :param str dir_tmp: Path to tmp directory
    :return none:
    """
    logger_doi_main.info("enter process_lpd")
    dir_root = os.getcwd()
    dir_bag = os.path.join(dir_tmp, name)
    dir_data = os.path.join(dir_bag, 'data')

    # Navigate down to jLD file
    # dir : dir_root -> dir_data
    os.chdir(dir_data)

    # Open jld file and read in the contents. Execute DOI Resolver.
    jld_data = read_json_from_file(os.path.join(dir_data, name + '.jsonld'))

    # Overwrite data with new data
    jld_data = DOIResolver(dir_root, name, jld_data).main()
    # Open the jld file and overwrite the contents with the new data.
    write_json_to_file(jld_data)

    # Open changelog. timestamp it. Prompt user for short description of changes. Close and save
    # update_changelog()

    # Delete old bag files, and move files to bag root for re-bagging
    # dir : dir_data -> dir_bag
    dir_cleanup(dir_bag, dir_data)
    finish_bag(dir_bag)

    logger_doi_main.info("exit process_lpd")
    return


def prompt_force():
    """
    Ask the user if they want to force update files that were previously resolved
    :return bool: response
    """
    logger_doi_main.info("enter prompt_force")
    count = 0
    print("Do you want to force updates for previously resolved files? (y/n)")
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
                print("invalid response")
        except AttributeError as e:
            print("invalid response")
            logger_doi_main.warn("invalid response: {}, {}".format(force, e))
        count += 1
    logger_doi_main.info("force update: {}".format(force))
    logger_doi_main.info("exit prompt_force")
    return True

if __name__ == '__main__':
    doi_main()
