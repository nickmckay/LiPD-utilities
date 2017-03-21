import os
import shutil

from ..helpers.directory import create_tmp_dir
from ..helpers.zips import zipper
from .lpd_noaa import LPD_NOAA
# from .noaa_lpd import NOAA_LPD
from ..helpers.loggers import create_logger


logger_noaa = create_logger("noaa")


def noaa_prompt():
    """
    Convert between NOAA and LiPD file formats.
    :return:
    """
    logger_noaa.info("enter noaa")
    # Run lpd_noaa or noaa_lpd ?
    print("Which conversion?\n1. LPD to NOAA\n2. NOAA to LPD (under construction!)\n")
    mode = input("Option: ")
    logger_noaa.info("chose option: {}".format(mode))

    return mode


def noaa_to_lpd(files):
    """
    Convert NOAA format to LiPD format
    :param dict file: File metadata
    :param str dir_tmp: Path to tmp directory
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

            # NOAA_LPD(dir_root, dir_tmp, name).main()
            os.chdir(file["dir"])

            zipper(path_name_ext=file["filename_ext"], root_dir=dir_tmp, name=file["filename_no_ext"])

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
        d = obj.get_metadata()
        # Create the conversion object, and start the conversion process
        _convert_obj = LPD_NOAA(obj.dir_root, obj.name, d, obj.data_csv)
        _convert_obj.main()
        # add the URL to the json dict and master dict in the object.
        d["WDCPaleoUrl"] = _convert_obj.get_wdc_paleo_url()
        m = obj.get_master()
        m["WDCPaleoUrl"] = _convert_obj.get_wdc_paleo_url()
        obj.put_master(m)
        obj.put_metadata(d)

    except FileNotFoundError:
        logger_noaa.debug("process_lpd: FileNotFound: tmp directory not found")
        print("Error: Unable to process {}".format(obj.name))
    logger_noaa.info("exit process_lpd")
    return obj
