import zipfile
import shutil
import os

from .loggers import create_logger

logger_zips = create_logger("zips")

# zipper(self.dir_tmp, self.name, self.name_ext)


def zipper(root_dir="", name="", path_name_ext=""):
    """
    Zips up directory back to the original location
    :param str root_dir: Root directory of the archive
    :param str name: <datasetname>.lpd
    :param str path_name_ext: /path/to/filename.lpd
    """
    logger_zips.info("re_zip: name: {}, dir_tmp: {}".format(path_name_ext, root_dir))
    # creates a zip archive in current directory. "somefile.lpd.zip"
    shutil.make_archive(path_name_ext, format='zip', root_dir=root_dir, base_dir=name)
    # drop the .zip extension. only keep .lpd
    os.rename("{}.zip".format(path_name_ext), path_name_ext)
    return


def unzipper(name_ext, dir_tmp):
    """
    Unzip .lpd file contents to tmp directory.
    :param str name_ext: Name of lpd file with extension
    :param str dir_tmp: Tmp folder to extract contents to
    :return None:
    """
    logger_zips.info("enter unzip")
    # Unzip contents to the tmp directory
    try:
        with zipfile.ZipFile(name_ext) as f:
            f.extractall(dir_tmp)
    except FileNotFoundError as e:
        logger_zips.debug("unzip: FileNotFound: {}, {}".format(name_ext, e))
        shutil.rmtree(dir_tmp)
    logger_zips.info("exit unzip")
    return


