import os

from ..helpers.directory import list_files, create_tmp_dir
from ..helpers.jsons import read_json_from_file
from ..helpers.zips import *
from .lpd_noaa import LPD_NOAA
from .noaa_lpd import NOAA_LPD


def noaa():
    """
    Convert between NOAA and LiPD file formats.
    :return:
    """
    dir_root = os.getcwd()
    # Run lpd_noaa or noaa_lpd ?
    print("Which conversion?\n1. LPD to NOAA\n2. NOAA to LPD\n")
    mode = input("Option: ")
    f_list = []
    ft = ''

    # .lpd to noaa
    if mode == '1':
        f_list = list_files('.lpd')
        ft = ' LiPD'
    # Find all needed files in current directory
    elif mode == '2':
        f_list = list_files('.txt')
        if 'noaa-blank.txt' in f_list:
            f_list.remove('noaa-blank.txt')
        if 'quarantine.txt' in f_list:
            f_list.remove('quarantine.txt')
        ft = ' NOAA'

    print("Found {0} {1} file(s)".format(str(len(f_list)), ft))
    # Process each available file
    for name_ext in f_list:
        print('processing: {}'.format(name_ext))

        # File name w/o extension
        name = os.path.splitext(name_ext)[0]

        # Unzip file and get tmp directory path
        dir_tmp = create_tmp_dir()

        # Process file
        if mode == '1':
            unzip(name_ext, dir_tmp)
            _process_lpd(name, dir_tmp, dir_root)

        elif mode == '2':
            _process_noaa(name, dir_tmp, dir_root)

        # Delete tmp folder and all contents
        os.chdir(dir_root)
        shutil.rmtree(dir_tmp)

    print("Process Complete")

    return


def _process_noaa(name, dir_tmp, dir_root):
    """
    Convert NOAA format to LiPD format
    :param name: (str) Name of file, no extension
    :param dir_tmp: (str) Path to tmp directory
    :return: none
    """
    NOAA_LPD(dir_root, dir_tmp, name).main()
    os.chdir(dir_root)
    re_zip(dir_tmp, name, name + ".lpd")
    os.rename(name + ".lpd" + '.zip', name + ".lpd")
    return


def _process_lpd(name, dir_tmp, dir_root):
    """
    Convert a LiPD format to NOAA format
    :param name: (str) Name of file, no extension
    :param dir_tmp: (str) Path to tmp directory
    :return: none
    """
    dir_bag = os.path.join(dir_tmp, name)
    dir_data = os.path.join(dir_bag, 'data')

    # Navigate down to jld file
    # Directory Change: dir_root -> dir_data
    os.chdir(dir_data)

    # Open file and execute conversion script
    d = read_json_from_file(os.path.join(dir_data, name + '.jsonld'))
    LPD_NOAA(dir_root, name, d).main()

    # except ValueError:
    #     txt_log(dir_root, 'quarantine.txt', name, "Invalid Unicode characters. Unable to load file.")

    return

