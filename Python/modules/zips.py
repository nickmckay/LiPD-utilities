import zipfile
import shutil
from Python.modules.directory import create_tmp_dir

__author__ = 'Chris Heiser'


def re_zip(dir_tmp, name, name_ext):
    """
    Zips up directory back to the original location
    :param dir_tmp: (str) Path to tmp directory
    :param name: (str) Name of current .lpd file
    :param name_ext: (str) Name of current .lpd file with extension
    :return: None
    """
    shutil.make_archive(name_ext, format='zip', root_dir=dir_tmp, base_dir=name)
    return


def unzip(name_ext):
    """
    Unzip .lpd file contents to tmp directory. Save path to the tmp directory.
    :param name_ext: (str) Name of lpd file with extension
    :return: (str) Path to tmp directory
    """
    # Creates tmp directory somewhere deep in OS
    dir_tmp = create_tmp_dir()

    # Unzip contents to the tmp directory
    try:
        with zipfile.ZipFile(name_ext) as f:
            f.extractall(dir_tmp)
    except FileNotFoundError:
        shutil.rmtree(dir_tmp)
        return None
    return dir_tmp
