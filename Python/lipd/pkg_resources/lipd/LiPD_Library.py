import string

from .LiPD import LiPD
from ..helpers.directory import *
from ..helpers.google import *
from ..helpers.PDSlib import *
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

    def setDir(self, dir_root):
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

    def loadLipd(self, name):
        """
        Load a single LiPD object into the LiPD Library.
        :param str name: Filename
        :return None: None
        """
        self.__append_lipd(name)
        print("Loaded 1 LiPD file")
        return

    def loadLipds(self):
        """
        Load a directory (multiple) LiPD objects into the LiPD Library
        :return:
        """
        # Confirm that a CWD is set first.
        if not self.dir_root:
            print("Current Working Directory has not been set.")
            return
        os.chdir(self.dir_root)
        # Get a list of all lpd files
        file_list = list_files('.lpd')
        # Loop: Append each file to Library
        print("Found: {} LiPD file(s)".format(len(file_list)))
        for name_ext in file_list:
            try:
                print("processing: {}".format(name_ext))
                self.__append_lipd(name_ext)
            except Exception as e:
                print("Error: {}".format(name_ext))
                logger_lipd_lib.warn("loadLipds: failed to load {}, {}".format(name_ext, e))

        return

    # ANALYSIS

    def showCsv(self, name):
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

    def getCsv(self, name):
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

    def showMetadata(self, name):
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

    def getMetadata(self, name):
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

    def showLipdMaster(self, name):
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

    def showLipds(self):
        """
        Display all LiPD files in the LiPD Library
        :return None:
        """
        print("Found: {} file(s)".format(len(self.master)))
        for k, v in sorted(self.master.items()):
            print(k)
        return

    def showMap(self, filename):
        """
        Intermediate function. Determines which type of map to create based on input.
        :param str filename: (str) Map the specified LiPD files. (none) Map all files in LiPD_Library.
        :return None: Google map image with location markers
        """
        try:
            # No input given. Map all LiPDs
            if not filename:
                self.map_all()
            # One or more records given. Map them.
            else:
                self.map_some(filename)
        except KeyError:
            print("LiPD file(s) not found")
        return

    def map_some(self, files):
        """
        Map one or more specified LiPDs.
        :param str files: Comma separated filenames
        :return None:
        """
        logger_lipd_lib.info("enter map_some")
        f = files.split(',')
        logger_lipd_lib.info("Mapping {} LiPDs".format(len(f)))
        chars = list(string.ascii_uppercase + string.digits)
        markers = []
        # Call a single point
        if len(f) is 1:
            c = self.master[f[0]].data_json['geo']['geometry']['coordinates']
            c_str = str(c[0]) + ',' + str(c[1])
            markers.append("markers=size:large|color:red|label:1|" + c_str)
            get_static_google_map(f[0], center=c_str, zoom=7, markers=markers)

        # Call a list of markers
        else:
            # Pull coordinates from master list for each given filename
            for idx, filename in enumerate(f):
                try:
                    c = self.master[filename].data_json['geo']['geometry']['coordinates']
                    markers.append('markers=size:large|color:red|label:' + chars[idx] + '|' + str(c[0]) + ',' + str(c[1]))
                    print('Key: ' + chars[idx] + '  Record: ' + str(filename))
                except KeyError:
                    print('Coordinates Error: ' + str(filename))
            # Map the list of markers
            get_static_google_map('multi-marker', markers=markers)
        logger_lipd_lib.info("exit map_some")
        return

    def map_all(self):
        """
        Map all LiPDs in the library.
        """
        logger_lipd_lib.info("enter map_all")
        logger_lipd_lib.info("map_all: mapping {} lipds".format(len(self.master)))
        chars = list(string.ascii_uppercase + string.digits)
        markers = []
        n = 0

        # Pull coordinates from master list for each given filename
        for k, v in self.master.items():
            try:
                c = v.data_json['geo']['geometry']['coordinates']
                markers.append('markers=size:large|color:red|label:' + chars[n] + '|' + str(c[0]) + ',' + str(c[1]))
                print('Key: ' + chars[n] + '  Record: ' + str(k))
                n += 1
            except KeyError as e:
                print("Coordinates Error: " + str(k))
                logger_lipd_lib.warn("map_all: coordinates error: {}, {}".format(str(k), e))
        # Map the list of markers
        get_static_google_map('multi-marker', markers=markers)
        logger_lipd_lib.info("exit map_all")
        return

    def LiPD_to_df(self, filename):
        """
        Create a pandas data frame from a LiPD file
        :param str filename:
        :return obj: Pandas data frames - 3
        """
        df_meta, df_data, df_chron = LiPD_to_df(self.master[filename].get_master())
        return df_meta, df_data, df_chron

    # CLOSING

    def saveLipd(self, name):
        """
        Overwrite LiPD files in OS with LiPD data in the current workspace.
        """
        try:
            self.master[name].save()
        except KeyError:
            print("LiPD file not found")
        return

    def saveLipds(self):
        """
        Overwrite target LiPD file in OS with LiPD data in the current workspace.
        """
        for k, v in self.master.items():
            self.master[k].save()
        return

    def removeLipd(self, name):
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

    def removeLipds(self):
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
        # load in the data from the lipd file (unpack, and create a temp workspace)
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
