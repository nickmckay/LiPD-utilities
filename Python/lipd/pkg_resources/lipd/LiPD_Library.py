import string

from .LiPD import LiPD
from ..helpers.directory import *
from ..helpers.google import *
from ..helpers.PDSlib import *


class LiPD_Library(object):
    """
    The LiPD Library is meant to encompass a collection of LiPD file objects that are being analyzed in the current
    workspace. The library holds one LiPD object for each LiPD file that is loaded.
    """

    def __init__(self):
        self.dir_root = ''
        self.dir_tmp = create_tmp_dir()
        self.master = {}

    # LOADING

    def setDir(self, dir_root):
        """
        Changes the current working directory.
        :param dir_root:
        :return:
        """
        try:
            self.dir_root = dir_root
            os.chdir(self.dir_root)
            # print("Directory: " + str(dir_root) + '\n')
        except FileNotFoundError:
            pass
            # print("Not a valid directory")
        return

    def loadLipd(self, name):
        """
        Load a single LiPD object into the LiPD Library.
        :param name: (str) Filename
        :return: None
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
            except:
                print("ERROR: {}".format(name_ext))

        return

    # ANALYSIS

    def showCsv(self, name):
        """
        Show CSV data from one LiPD object
        :param name: (str) Filename
        :return:
        """
        try:
            self.master[name].display_csv()
        except KeyError:
            print("LiPD not found")
        return

    def getCsv(self, name):
        """

        :param name:
        :return:
        """
        d = {}
        try:
            d = self.master[name].get_csv()
        except KeyError:
            pass

        return d

    def showMetadata(self, name):
        """
        Display data from target LiPD file.
        :param name: (str) Filename
        :return:
        """
        try:
            self.master[name].display_json()
        except KeyError:
            pass
        return

    def getMetadata(self, name):
        """

        :param name:
        :return:
        """
        d = {}
        try:
            d = self.master[name].get_metadata()
        except KeyError:
            pass

        return d

    def showLipdMaster(self, name):
        """
        Display data from target LiPD file.
        :param name: (str) Filename
        :return:
        """
        try:
            self.master[name].display_master()
        except KeyError:
            print("LiPD not found")
        return

    def showLipds(self):
        """
        Display all LiPD files in the LiPD Library
        :return:
        """
        print("Found: {} file(s)".format(len(self.master)))
        for k, v in sorted(self.master.items()):
            print(k)
        return

    def showMap(self, filename):
        """
        Intermediate function. Determines which type of map to create based on input.
        :param filename: (str) Map the specified LiPD files. (none) Map all files in LiPD_Library.
        :return: (img) Google map with location markers
        """
        try:
            # No input given. Map all LiPDs
            if not filename:
                self.map_all()
            # One or more records given. Map them.
            else:
                self.map_some(filename)
        except KeyError:
            print("ERROR: Unable to find record(s)")
        return

    def map_some(self, files):
        """
        Map one or more specified LiPDs.
        :param files: (str) Comma separated filenames
        :return: None
        """
        f = files.split(',')
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
        return

    def map_all(self):
        """
        Map all LiPDs in the library.
        """
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
            except KeyError:
                print("Coordinates Error: " + str(k))
        # Map the list of markers
        get_static_google_map('multi-marker', markers=markers)
        return

    def LiPD_to_df(self, filename):
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
            print("LiPD not found")
        return

    def saveLipds(self):
        """
        Overwrite target LiPD file in OS with LiPD data in the current workspace.
        """
        for k, v in self.master.items():
            self.master[k].save()

    def removeLipd(self, name):
        """
        Removes target LiPD file from the workspace. Delete tmp folder, then delete object.
        :param name: (str) Filename
        """
        try:
            self.master[name].remove()
            del self.master[name]
        except KeyError:
            print("LiPD not found")
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
        :param name_ext: (str) Filename with extension
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
        :return:
        """
        return self.master

    def load_tsos(self, d):
        """
        Overwrite converted TS metadata back into its matching LiPD object.
        :param d: (dict) Metadata from TSO
        """

        for name_ext, metadata in d.items():
            # Important that the dataSetNames match for TSO and LiPD object. Make sure
            try:
                self.master[name_ext].load_tso(metadata)
            except KeyError:
                print("LiPD_Library: Error loading " + str(name_ext) + " from TSO")

        return
