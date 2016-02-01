from lpd import *
from directory import *

class LiPD_Library(object):
    """
    The LiPD Library is meant to encompass a collection of LiPD file objects that are being analyzed in the current
    workspace. The library holds one LiPD object for each LiPD file that is loaded.
    """

    def __init__(self):
        self.dir_root = ''
        self.dir_tmp = create_tmp_dir()
        self.master = {}

    # GETTING STARTED

    def setDir(self, dir_root):
        """
        Changes the current working directory.
        :param dir_root:
        :return:
        """
        self.dir_root = dir_root
        os.chdir(self.dir_root)
        print("Directory: " + str(dir_root))
        return

    def loadLipds(self):
        """
        Load a directory (multiple) LiPD objects into the LiPD Library
        :return:
        """
        # Confirm that a CWD is set first.
        if self.dir_root == '':
            print("Current Working Directory has not been set.")
            return
        os.chdir(self.dir_root)
        # Get a list of all lpd files
        file_list = list_files('lpd')
        # Loop: Append each file to Library
        for name_ext in file_list:
            self.appendLipd(name_ext)
        return

    def loadLipd(self, name):
        """
        Load a single LiPD object into the LiPD Library.
        :param name: (str) Filename
        :return: None
        """
        self.appendLipd(name + '.lpd')
        return

    # ANALYSIS

    def showCsv(self, name):
        """
        Show CSV data from one LiPD object
        :param name: (str) Filename
        :return:
        """
        try:
            self.master[name + '.lpd'].display_csv()
        except KeyError:
            print("Invalid Filename")
        return

    def showLipd(self, name):
        """
        Display data from target LiPD file.
        :param name: (str) Filename
        :return:
        """
        try:
            self.master[name + '.lpd'].display_data()
        except KeyError:
            print("Invalid Filename")
        return

    def showFiles(self):
        """
        Display all LiPD files in the LiPD Library
        :return:
        """
        for k, v in self.master.items():
            print(k)
        return

    # CLOSING

    def saveLipd(self, name):
        """
        Overwrite LiPD files in OS with LiPD data in the current workspace.
        :return: None
        """
        self.master[name + '.lpd'].save()
        return

    def saveLipds(self):
        """
        Overwrite target LiPD file in OS with LiPD data in the current workspace.
        :return: None
        """
        for k, v in self.master.items():
            self.master[k].save()

    def removeLipd(self, name):
        """
        Removes target LiPD file from the workspace. Delete tmp folder, then delete object.
        :param name: (str) Filename
        :return:
        """
        self.master[name + '.lpd'].remove()
        try:
            del self.master[name + '.lpd']
        except KeyError:
            print("Problem removing LiPD object.")
        return

    def removeLipds(self):
        """
        Clear the workspace. Empty the master dictionary.
        :return:
        """
        self.master = {}
        return

    # HELPERS

    def appendLipd(self, name_ext):
        """
        Creates and adds a new LiPD object to the LiPD Library for the given LiPD file...
        :param name_ext: (str) Filename with extension
        :return:
        """
        os.chdir(self.dir_root)
        # create a lpd object
        lipd_obj = LiPD(self.dir_root, self.dir_tmp, name_ext)
        # load in the data from the lipd file (unpack, and create a temp workspace)
        lipd_obj.load()
        # add the lpd object to the master dictionary
        self.master[name_ext] = lipd_obj
        return
