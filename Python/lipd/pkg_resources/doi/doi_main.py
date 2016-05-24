from .doi_resolver import DOIResolver
from ..helpers.bag import *
from ..helpers.directory import *
from ..helpers.zips import *
from ..helpers.jsons import *
from ..helpers.loggers import create_logger

logger_doi_main = create_logger("doi_main")


def doi():
    """
    Main function that controls the script. Take in directory containing the .lpd file(s). Loop for each file.
    :return None:
    """
    logger_doi_main.info("enter doi_main")
    # Find all .lpd files in current directory
    # dir: ? -> dir_root
    dir_root = os.getcwd()
    f_list = list_files('.lpd')
    print("Found {0} {1} file(s)".format(str(len(f_list)), 'LiPD'))
    force = prompt_force()
    for name_ext in f_list:
        # .lpd name w/o extension
        name = os.path.splitext(name_ext)[0]

        # Unzip file and get tmp directory path
        dir_tmp = create_tmp_dir()
        unzip(name_ext, dir_tmp)

        # Force DOI update?
        if not force:
            # Unbag and check resolved flag. Don't run if flag exists.
            if resolved_flag(open_bag(os.path.join(dir_tmp, name))):
                print('skipping: {}'.format(name_ext))
                logger_doi_main.info("skipping: {}".format(name_ext))
                shutil.rmtree(dir_tmp)

        # Process file if flag does not exist or force.
        else:
            print('processing: {}'.format(name_ext))
            logger_doi_main.info("processing: {}".format(name_ext))
            # dir: dir_root -> dir_tmp
            process_lpd(name, dir_tmp)
            # dir: dir_tmp -> dir_root
            os.chdir(dir_root)
            # Zip the directory containing the updated files. Created in dir_root directory
            re_zip(dir_tmp, name, name_ext)
            os.rename(name_ext + '.zip', name_ext)
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
    write_json_to_file(os.path.join(dir_data, name + '.jsonld'), jld_data)

    # Open changelog. timestamp it. Prompt user for short description of changes. Close and save
    update_changelog()

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
    force = False
    count = 0
    print("Do you want to force updates for previously resolved files? (y/n)")
    while True:
        f = input("> ")
        try:
            if count == 2:
                force = False
                break
            elif f.lower() in ('y', 'yes'):
                force = True
                break
            elif f.lower() in ('n', 'no'):
                force = False
                break
            else:
                print("invalid response")
        except AttributeError as e:
            print("invalid response")
            logger_doi_main.warn("invalid response: {}, {}".format(f, e))
        count += 1
    logger_doi_main.info("force update: {}".format(force))
    logger_doi_main.info("exit prompt_force")
    return force

if __name__ == '__main__':
    doi()
