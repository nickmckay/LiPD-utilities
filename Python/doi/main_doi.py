from Python.modules.bag import *
from Python.modules.directory import *
from Python.modules.zips import *
from Python.doi.doi_resolver import *

__author__ = 'Chris Heiser'

"""
Basic Process:
Take .lpd file(s) that have been bagged with Bagit, and compressed (zip). Uncompress and unbag,
read in the DOI from the jsonld file, invoke DOI resolver script, retrieve doi.org info with given DOI,
update jsonld file, Bag the files, and compress the Bag. Output a txt log file with names and errors of
problematic files.

"""

# GLOBALS
DIRECTORY_PATH = 'SET_DIRECTORY_PATH_HERE'


def doi(directory):
    """
    Main function that controls the script. Take in directory containing the .lpd file(s). Loop for each file.
    :return: None
    """
    # Enter user-chosen directory path
    dir_root = DIRECTORY_PATH

    # Find all .lpd files in current directory
    # dir: ? -> dir_root
    os.chdir(dir_root)
    f_list = list_files('.lpd')

    for name_ext in f_list:
        print('processing: {}'.format(name_ext))

        # .lpd name w/o extension
        name = os.path.splitext(name_ext)[0]

        # Unzip file and get tmp directory path
        dir_tmp = create_tmp_dir()
        unzip(name_ext, dir_tmp)

        # Unbag and check resolved flag. Don't run if flag exists
        if resolved_flag(open_bag(os.path.join(dir_tmp, name))):
            print("DOI previously resolved. Next file...")
            shutil.rmtree(dir_tmp)

        # Process file if flag does not exist
        else:
            # dir: dir_root -> dir_tmp
            process_lpd(name, dir_tmp)
            # dir: dir_tmp -> dir_root
            os.chdir(dir_root)
            # Zip the directory containing the updated files. Created in dir_root directory
            re_zip(dir_tmp, name, name_ext)
            os.rename(name_ext + '.zip', name_ext)
            # Cleanup and remove tmp directory
            shutil.rmtree(dir_tmp)
    print("Remember: Quarantine.txt contains a list of errors that may have happened during processing.")
    return


def process_lpd(name, dir_tmp):
    """
    Opens up a jsonld file, invokes doi_resolver, closes file, updates changelog, cleans directory, and makes new bag.
    :param name: (str) Name of current .lpd file
    :param dir_tmp: (str) Path to tmp directory
    :return: none
    """

    dir_root = os.getcwd()
    dir_bag = os.path.join(dir_tmp, name)
    dir_data = os.path.join(dir_bag, 'data')

    # Navigate down to jLD file
    # dir : dir_root -> dir_data
    os.chdir(dir_data)

    # Open jld file and read in the contents
    with open(os.path.join(dir_data, name + '.jsonld'), 'r') as jld_file:
        jld_data = json.load(jld_file)

    # Create DOIResolver object and run
    jld_data = DOIResolver(dir_root, name, jld_data).main()

    # Open the jld file again, and overwrite the contents with the new data.
    with open(os.path.join(dir_data, name + '.jsonld'), 'w+') as jld_file:
        json.dump(jld_data, jld_file, indent=2, sort_keys=True)

    # except ValueError:
    #     txt_log(dir_root, 'quarantine.txt', name, "Invalid Unicode characters. Unable to load file.")

    # jld_file.close()

    # Open changelog. timestamp it. Prompt user for short description of changes. Close and save
    update_changelog()

    # Delete old bag files, and move files to bag root for re-bagging
    # dir : dir_data -> dir_bag
    dir_cleanup(dir_bag, dir_data)

    # Create a bag for the 3 files
    new_bag = create_bag(dir_bag)
    open_bag(dir_bag)
    new_bag.save(manifests=True)

    return


if __name__ == '__main__':
    doi()
