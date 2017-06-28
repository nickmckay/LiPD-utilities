from ..helpers.zips import unzipper, zipper
from ..helpers.directory import rm_file_if_exists, create_tmp_dir, find_files
from ..helpers.bag import create_bag
from ..helpers.csvs import get_csv_from_metadata, write_csv_to_file, merge_csv_metadata
from ..helpers.jsons import write_json_to_file, idx_num_to_name, idx_name_to_num, rm_empty_fields, read_jsonld
from ..helpers.loggers import create_logger
from ..helpers.misc import put_tsids, check_dsn, rm_empty_doi, rm_values_fields

from collections import OrderedDict
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
        dir_tmp = create_tmp_dir()
        unzipper(path, dir_tmp)
        os.chdir(dir_tmp)
        _dir_data = find_files()
        os.chdir(_dir_data)
        _j = read_jsonld()
        _j = rm_empty_fields(_j)
        _j = check_dsn(path, _j)
        _j = idx_num_to_name(_j)
        _j = rm_empty_doi(_j)
        _j = rm_empty_fields(_j)
        _j = put_tsids(_j)
        _j = merge_csv_metadata(_j)
        os.chdir(dir_original)
        shutil.rmtree(dir_tmp)
    except FileNotFoundError:
        print("Error: LiPD file not found. Please make sure the filename includes the .lpd extension")
    except Exception as e:
        print("Error: unable to read LiPD: {}".format(e))
    os.chdir(dir_original)
    logger_lipd.info("object loaded: {}".format(path))
    return _j


# WRITE


def lipd_write(dat, path):
    """
    Saves current state of LiPD object data. Outputs to a LiPD file.
    Steps: create tmp, create bag dir, get dsn, splice csv from json, write csv, clean json, write json, create bagit,
        zip up bag folder, place lipd in target dst, move to original dir, delete tmp
    :param dict dat: LiPD data
    :param str path: Destination path
    :return none:
    """
    dir_original = os.getcwd()
    try:
        dir_tmp = create_tmp_dir()
        dir_bag = os.path.join(dir_tmp, "bag")
        os.mkdir(dir_bag)
        os.chdir(dir_bag)
        _dsn = check_dsn(path, dat)
        _dsn_lpd = _dsn + ".lpd"
        _json, _csv = get_csv_from_metadata(_dsn, dat)
        write_csv_to_file(_csv)
        _json = rm_values_fields(_json)
        _json = put_tsids(_json)
        _json = idx_name_to_num(_json)
        write_json_to_file(_dsn, _json)
        create_bag(dir_bag)
        rm_file_if_exists(path, _dsn_lpd)
        zipper(root_dir=dir_tmp, name="bag", path_name_ext=os.path.join(path, _dsn_lpd))
        os.chdir(dir_original)
        shutil.rmtree(dir_tmp)
    except Exception as e:
        logger_lipd.error("lipd_write: {}".format(e))
    return






