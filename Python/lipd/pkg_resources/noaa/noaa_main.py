import os
import shutil

from ..helpers.directory import create_tmp_dir
from ..helpers.zips import zipper
from .lpd_noaa import LPD_NOAA
from .noaa_lpd import NOAA_LPD
from ..helpers.loggers import create_logger


logger_noaa = create_logger("noaa")


def noaa_prompt():
    """
    Convert between NOAA and LiPD file formats.
    :return:
    """
    logger_noaa.info("enter noaa")
    # Run lpd_noaa or noaa_lpd ?
    print("Which conversion?\n1. LPD to NOAA\n2. NOAA to LPD\n")
    mode = input("Option: ")
    logger_noaa.info("chose option: {}".format(mode))

    return mode


def noaa_to_lpd(files):
    """
    Convert NOAA format to LiPD format
    :param dict files: Files metadata
    :return None:
    """
    logger_noaa.info("enter process_noaa")
    # only continue if the user selected a mode correctly
    logger_noaa.info("Found {} NOAA txt file(s)".format(str(len(files[".txt"]))))
    print("Found {} NOAA txt file(s)".format(str(len(files[".txt"]))))
    # Process each available file of the specified .lpd or .txt type
    for file in files[".txt"]:
        # try to filter out example files and stuff without real data
        if "template" not in file["filename_ext"] and "example" not in file["filename_ext"]:
            os.chdir(file["dir"])
            print('processing: {}'.format(file["filename_ext"]))
            logger_noaa.info("processing: {}".format(file["filename_ext"]))

            # Unzip file and get tmp directory path
            dir_tmp = create_tmp_dir()
            try:
                NOAA_LPD(file["dir"], dir_tmp, file["filename_no_ext"]).main()
            except Exception as e:
                print("Error: Unable to convert file: {}, {}".format(file["filename_no_ext"], e))

            # Create the lipd archive in the original file's directory.
            zipper(path_name_ext=os.path.join(file["dir"], file["filename_no_ext"] + ".lpd"), root_dir=dir_tmp, name=file["filename_no_ext"])
            # Delete tmp folder and all contents
            os.chdir(file["dir"])
            try:
                shutil.rmtree(dir_tmp)
            except FileNotFoundError:
                # directory is already gone. keep going.
                pass

    logger_noaa.info("exit noaa_to_lpd")
    return


def lpd_to_noaa(obj):
    """
    Convert a LiPD format to NOAA format
    :param obj obj: LiPD object
    :return obj: LiPD object (modified)
    """
    logger_noaa.info("enter process_lpd")

    try:
        os.chdir(obj.dir_root)
        # Get the json data from the lipd object
        d = obj.get_master()
        # Create the conversion object, and start the conversion process
        _convert_obj = LPD_NOAA(obj.dir_root, obj.name, d)
        _convert_obj.main()
        # get our new, modified master JSON from the conversion object
        m = _convert_obj.get_master()
        # remove any root level urls that are deprecated
        m = __rm_wdc_url(m)
        obj.put_master(m)
        obj.put_metadata(d)

    except FileNotFoundError:
        logger_noaa.debug("process_lpd: FileNotFound: tmp directory not found")
        print("Error: Unable to process {}".format(obj.name))

    logger_noaa.info("exit process_lpd")
    return obj


def __rm_wdc_url(d):
    """
    Remove the WDCPaleoUrl key. It's no longer used but still exists in some files.
    :param dict d: Metadata
    :return dict d: Metadata
    """
    if "WDCPaleoUrl" in d:
        del d["WDCPaleoUrl"]
    if "WDSPaleoUrl" in d:
        del d["WDSPaleoUrl"]
    return d
