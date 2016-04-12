from .doi_resolver import DOIResolver
from ..helpers.bag import *
from ..helpers.directory import *
from ..helpers.zips import unzip, re_zip
from ..helpers.jsons import json, write_json_to_file
from ..helpers.loggers import txt_log, update_changelog


def doi():
    """
    Main function that controls the script. Take in directory containing the .lpd file(s). Loop for each file.
    :param dir_root: (str) Directory location of target files
    :return: None
    """

    # Find all .lpd files in current directory
    # dir: ? -> dir_root
    dir_root = os.getcwd()
    f_list = list_files('.lpd')
    print("Found {0} {1} file(s)".format(str(len(f_list)), 'LiPD'))

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
    print("NOTE: Quarantine.txt contains a list of errors that may have occurred during processing.")
    print("Process Complete")

    return


def process_lpd(name, dir_tmp):
    """
    Opens up json file, invokes doi_resolver, closes file, updates changelog, cleans directory, and makes new bag.
    :param name: (str) Name of current .lpd file
    :param dir_tmp: (str) Path to tmp directory
    :return: none
    """

    dir_root = os.getcwd()
    dir_bag = os.path.join(dir_tmp, name)
    dir_data = os.path.join(dir_bag, 'data')
    jld_data = {}
    valid = True

    # Navigate down to jLD file
    # dir : dir_root -> dir_data
    os.chdir(dir_data)

    # Open jld file and read in the contents. Execute DOI Resolver.
    with open(os.path.join(dir_data, name + '.jsonld'), 'r') as f:
        try:
            jld_data = json.load(f)
        except ValueError:
            valid = False
            txt_log(dir_root,  name,'quarantine.txt', "Invalid characters. Unable to load file.")

    if valid:
        # Overwrite data with new data
        jld_data = DOIResolver(dir_root, name, jld_data).main()
        # Open the jld file and overwrite the contents with the new data.
        write_json_to_file(os.path.join(dir_data, name + '.jsonld'), jld_data)

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


