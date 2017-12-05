from .zips import unzipper, zipper
from .directory import rm_file_if_exists, create_tmp_dir, find_files
from .bag import create_bag
from .csvs import get_csv_from_metadata, write_csv_to_file, merge_csv_metadata, read_csvs
from .jsons import write_json_to_file, idx_num_to_name, idx_name_to_num, rm_empty_fields, read_jsonld
from .loggers import create_logger
from .misc import put_tsids, check_dsn, get_dsn, rm_empty_doi, rm_values_fields, print_filename
from .versions import update_lipd_version

import copy
import os
import shutil


logger_lipd = create_logger('LiPD')


# READ


def lipd_read(path):
    """
    Loads a LiPD file from local path. Unzip, read, and process data
    Steps: create tmp, unzip lipd, read files into memory, manipulate data, move to original dir, delete tmp.

    :param str path: Source path
    :return none:
    """
    _j = {}
    dir_original = os.getcwd()

    # Import metadata into object
    try:
        print("reading: {}".format(print_filename(path)))
        # bigger than 2mb file? This could take a while
        if os.stat(path).st_size > 1000000:
            _size = os.stat(path).st_size
            print("{} :That's a big file! This may take a while to load...".format("{} MB".format(round(_size/1000000,2))))
        dir_tmp = create_tmp_dir()
        unzipper(path, dir_tmp)
        os.chdir(dir_tmp)
        _dir_data = find_files()
        os.chdir(_dir_data)
        _j = read_jsonld()
        _j = rm_empty_fields(_j)
        _j = check_dsn(path, _j)
        _j = update_lipd_version(_j)
        _j = idx_num_to_name(_j)
        _j = rm_empty_doi(_j)
        _j = rm_empty_fields(_j)
        _j = put_tsids(_j)
        _csvs = read_csvs()
        _j = merge_csv_metadata(_j, _csvs)
        # Why ? Because we need to align the csv filenames with the table filenames. We don't need the csv output here.
        _j, _csv = get_csv_from_metadata(_j["dataSetName"], _j)
        os.chdir(dir_original)
        shutil.rmtree(dir_tmp)
    except FileNotFoundError:
        print("Error: lipd_read: LiPD file not found. Please make sure the filename includes the .lpd extension")
    except Exception as e:
        logger_lipd.error("lipd_read: {}".format(e))
        print("Error: lipd_read: unable to read LiPD: {}".format(e))
    os.chdir(dir_original)
    logger_lipd.info("lipd_read: record loaded: {}".format(path))
    return _j


# WRITE


def lipd_write(_json, path):
    """
    Saves current state of LiPD object data. Outputs to a LiPD file.
    Steps: create tmp, create bag dir, get dsn, splice csv from json, write csv, clean json, write json, create bagit,
        zip up bag folder, place lipd in target dst, move to original dir, delete tmp

    :param dict _json: Metadata
    :param str path: Destination path
    :return none:
    """
    # Json is pass by reference. Make a copy so we don't mess up the original data.
    _json_tmp = copy.deepcopy(_json)
    dir_original = os.getcwd()
    try:
        dir_tmp = create_tmp_dir()
        dir_bag = os.path.join(dir_tmp, "bag")
        os.mkdir(dir_bag)
        os.chdir(dir_bag)
        _dsn = get_dsn(_json_tmp)
        _dsn_lpd = _dsn + ".lpd"
        _json_tmp, _csv = get_csv_from_metadata(_dsn, _json_tmp)
        write_csv_to_file(_csv)
        _json_tmp = rm_values_fields(_json_tmp)
        _json_tmp = put_tsids(_json_tmp)
        _json_tmp = idx_name_to_num(_json_tmp)
        write_json_to_file(_json_tmp)
        create_bag(dir_bag)
        rm_file_if_exists(path, _dsn_lpd)
        zipper(root_dir=dir_tmp, name="bag", path_name_ext=os.path.join(path, _dsn_lpd))
        os.chdir(dir_original)
        shutil.rmtree(dir_tmp)
    except Exception as e:
        logger_lipd.error("lipd_write: {}".format(e))
        print("Error: lipd_write: {}".format(e))
    return






