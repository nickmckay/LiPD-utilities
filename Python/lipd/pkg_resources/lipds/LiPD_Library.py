from .LiPD import LiPD
from ..helpers.directory import *
from ..helpers.loggers import create_logger

logger_lipd_lib = create_logger('LiPD_Library')


class LiPD_Library(object):
    """
    The LiPD Library is meant to encompass a collection of LiPD file objects that are being analyzed in the current
    workspace. The library holds one LiPD object for each LiPD file that is loaded.
    """

    def __init__(self):
        self.dir_root = ''
        self.dir_tmp = create_tmp_dir()
        self.master = {}
        logger_lipd_lib.info("LiPD Library created")

    # LOADING

    def get_dir(self):
        """
        Get the dir_root value
        :return str: dir_root path
        """
        return self.dir_root

    def set_dir(self, dir_root):
        """
        Changes the current working directory.
        :param str dir_root:
        :return:
        """
        try:
            self.dir_root = dir_root
            os.chdir(self.dir_root)
        except FileNotFoundError as e:
            logger_lipd_lib.debug("setDir: FileNotFound: invalid directory: {}, {}".format(self.dir_root, e))
        return

    def load_lipd(self, name):
        """
        Load a single LiPD object into the LiPD Library.
        :param str name: Filename
        :return None: None
        """
        self.__append_lipd(name)
        print("Found: 1 LiPD file(s)")
        print("processing: {}".format(name))
        return

    def load_lipds(self, single_file):
        """
        Load a directory (multiple) LiPD objects into the LiPD Library
        :return:
        """
        # Confirm that a CWD is set first.
        if not self.dir_root:
            print("Error: Current Working Directory has not been set. Use lipd.setDir()")
            return
        os.chdir(self.dir_root)
        if single_file:
            file_list = [single_file]
        else:
            # Get a list of all lpd files
            file_list = list_files('.lpd')
        # Loop: Append each file to Library
        print("Found: {} LiPD file(s)".format(len(file_list)))
        for name_ext in file_list:
            try:
                print("processing: {}".format(name_ext))
                self.__append_lipd(name_ext)
            except Exception as e:
                print("Error: unable to load {}".format(name_ext))
                logger_lipd_lib.warn("loadLipds: failed to load {}, {}".format(name_ext, e))

        return

    # ANALYSIS

    def show_csv(self, name):
        """
        Show CSV data from one LiPD object
        :param str name: Filename
        :return None:
        """
        try:
            self.master[name].display_csv()
        except KeyError:
            print("LiPD not found")
        return

    def get_csv(self, name):
        """
        Get CSV data from LiPD file
        :param str name:
        :return dict:
        """
        d = {}
        try:
            d = self.master[name].get_csv()
        except KeyError:
            print("LiPD file not found")
        return d

    def show_metadata(self, name):
        """
        Display data from target LiPD file.
        :param str name: Filename
        :return None:
        """
        try:
            self.master[name].display_json()
        except KeyError:
            print("LiPD file not found")
        return

    def get_metadata(self, name):
        """
        Get metadata from LiPD file
        :param str name:
        :return dict:
        """
        d = {}
        try:
            d = self.master[name].get_metadata()
        except KeyError:
            print("LiPD file not found")
        return d

    def get_dfs(self, name):
        """
        Get data frames from LiPD object
        :return dict:
        """
        d = {}
        try:
            d = self.master[name].get_dfs()
        except KeyError:
            logger_lipd_lib.debug("getDfs: KeyError: missing lipds {}".format(name))
        return d

    def show_lipd_master(self, name):
        """
        Display data from target LiPD file.
        :param str name: Filename
        :return None:
        """
        try:
            self.master[name].display_master()
        except KeyError:
            print("LiPD not found")
        return

    def show_lipds(self):
        """
        Display all LiPD dataset names in the LiPD Library
        :return None:
        """
        print("Found: {} file(s)".format(len(self.master)))
        for k, v in sorted(self.master.items()):
            print(k)
        return

    # CLOSING

    def lib_to_dict(self):
        """
        Return compiled dictionary of master data from all LiPDs in library.
        :return:
        """
        d = {}
        # for each dataset in the lipds library
        for k,v in self.master.items():
            # key is dataset name, value is master data
            d[k] = v.get_master()
        return d

    def save_lipd(self, name):
        """
        Overwrite LiPD files in OS with LiPD data in the current workspace.
        """
        try:
            self.master[name].save()
            # Reload the newly saved LiPD file back into the library.
            self.load_lipd(name)
        except KeyError:
            print("LiPD file not found")
        return

    def save_lipds(self):
        """
        Overwrite target LiPD file in OS with LiPD data in the current workspace.
        """
        for k, v in self.master.items():
            self.master[k].save()
        # Reload the newly saved LiPD files back into the library.
        print("Re-loading workspace..")
        self.load_lipds()
        return

    def remove_lipd(self, name):
        """
        Removes target LiPD file from the workspace. Delete tmp folder, then delete object.
        :param str name: Filename
        """
        try:
            self.master[name].remove()
            del self.master[name]
        except KeyError:
            print("LiPD file not found")
        return

    def remove_lipds(self):
        """
        Clear the workspace. Empty the master dictionary.
        """
        self.master = {}
        return

    # HELPERS

    def __append_lipd(self, name_ext):
        """
        Creates and adds a new LiPD object to the LiPD Library for the given LiPD file...
        :param str name_ext: Filename with extension
        """
        os.chdir(self.dir_root)
        # create a lpd object
        lipd_obj = LiPD(self.dir_root, self.dir_tmp, name_ext)
        # load in the data from the lipds file (unpack, and create a temp workspace)
        lipd_obj.load()
        # add the lpd object to the master dictionary
        self.master[name_ext] = lipd_obj
        return

    def get_master(self):
        """
        Retrieve the LiPD_Library master list. All names and LiPD objects.
        :return dict:
        """
        return self.master

    def set_master(self, dat):
        """
        Set new data as the master dictionary
        :param dict dat:
        :return none:
        """
        self.master = dat
        return

    def load_tsos(self, d):
        """
        Overwrite converted TS metadata back into its matching LiPD object.
        :param dict d: Metadata from TSO
        """

        for name_ext, metadata in d.items():
            # Important that the dataSetNames match for TSO and LiPD object. Make sure
            try:
                self.master[name_ext].load_tso(metadata)
            except KeyError as e:
                print("Error loading " + str(name_ext) + " from TimeSeries object")
                logger_lipd_lib.warn("load_tsos: KeyError: failed to load {} from tso, {}".format(name_ext, e))

        return
