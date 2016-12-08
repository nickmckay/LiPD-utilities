import os
import shutil

from ..helpers.misc import update_lipd_version
from ..helpers.directory import create_tmp_dir
from ..helpers.jsons import read_json_from_file
from ..helpers.zips import zipper, unzipper
from .lpd_noaa import LPD_NOAA
# from .noaa_lpd import NOAA_LPD
from ..helpers.loggers import create_logger

logger_noaa = create_logger("noaa")


def noaa_main(files):
    """
    Convert between NOAA and LiPD file formats.
    :return:
    """
    logger_noaa.info("enter noaa")
    # Run lpd_noaa or noaa_lpd ?
    print("Which conversion?\n1. LPD to NOAA\n2. NOAA to LPD\n")
    mode = input("Option: ")
    logger_noaa.info("chose option: {}".format(mode))
    ft = ""
    ft_print = ""

    # .lpd to noaa
    if mode == '1':
        ft = ".lpd"
        ft_print = 'LiPD'
    # Find all needed files in current directory
    elif mode == '2':
        ft = ".txt"
        ft_print = 'NOAA'
    # only continue if the user selected a mode correctly
    if ft and ft_print:
        logger_noaa.info("Found {} {} file(s)".format(str(len(files[ft])), ft_print))
        print("Found {0} {1} file(s)".format(str(len(files[ft])), ft_print))
        # Process each available file of the specified .lpd or .txt type
        for file in files[ft]:
            # try to filter out example files and stuff without real data
            if "template" not in file["filename_ext"] and "example" not in file["filename_ext"]:
                os.chdir(file["dir"])
                print('processing: {}'.format(file["filename_ext"]))
                logger_noaa.info("processing: {}".format(file["filename_ext"]))

                # Unzip file and get tmp directory path
                dir_tmp = create_tmp_dir()

                # Process file
                if mode == '1':
                    unzipper(file["filename_ext"], dir_tmp)
                    _process_lpd(file, dir_tmp)
                elif mode == '2':
                    _process_noaa(file, dir_tmp)

                # Delete tmp folder and all contents
                os.chdir(file["dir"])
                try:
                    shutil.rmtree(dir_tmp)
                except FileNotFoundError:
                    # directory is already gone. keep going.
                    pass

    else:
        print("Error: a mode was not selected")
        logger_noaa.info("noaa_main: a mode was not selected")
    print("Process Complete")
    logger_noaa.info("exit noaa")
    return


def _process_noaa(file, dir_tmp):
    """
    Convert NOAA format to LiPD format
    :param dict file: File metadata
    :param str dir_tmp: Path to tmp directory
    :return None:
    """
    logger_noaa.info("enter process_noaa")
    # NOAA_LPD(dir_root, dir_tmp, name).main()
    os.chdir(file["dir"])
    zipper(dir_tmp, file["filename_no_ext"], file["filename_ext"])
    logger_noaa.info("exit process_noaa")
    return


def _process_lpd(file, dir_tmp):
    """
    Convert a LiPD format to NOAA format
    :param dict file: File metadata
    :param str dir_tmp: Path to tmp directory
    :return None:
    """
    logger_noaa.info("enter process_lpd")
    dir_bag = os.path.join(dir_tmp, file["filename_no_ext"])
    dir_data = os.path.join(dir_bag, 'data')

    # Navigate down to jld file
    # Directory Change: dir_root -> dir_data
    try:
        os.chdir(dir_data)
        # Open file and execute conversion script
        d = read_json_from_file(os.path.join(dir_data, file["filename_no_ext"] + '.jsonld'))
        # Do we need to update json to most recent LiPD Version? Check before passing to converter
        d = update_lipd_version(d)
        # create object and start conversion process
        LPD_NOAA(file["dir"], file["filename_no_ext"], d).main()
    except FileNotFoundError:
        logger_noaa.debug("process_lpd: FileNotFound: tmp directory not found")
        print("Error: Unable to process {}".format(file["filename_no_ext"]))
    logger_noaa.info("exit process_lpd")
    return

