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

    def setDir(self, dir_root):
        self.dir_root = dir_root
        os.chdir(self.dir_root)
        print("Directory: " + str(dir_root))

    def loadLiPDdir(self):
        # Confirm that a CWD is set first.
        if self.dir_root == '':
            print("Current Working Directory has not been set.")
            return
        os.chdir(self.dir_root)
        # Get a list of all lpd files
        file_list = list_files('lpd')
        # Loop: Append each file to Library
        for name_ext in file_list:
            self.appendLiPD(name_ext)
        return

    def loadLiPD(self, name_ext):
        """
        Load a single LiPD file into the LiPD Library.
        :param name_ext: (str) File name
        :return: None
        """
        self.appendLiPD(name_ext)
        return

    def saveLiPD(self, name_ext):
        pass

    def saveAll(self):
        pass

    def close(self):
        pass

    def displayLiPD(self, name_ext):
        self.master[name_ext].displayData()

    def displayAll(self):
        for k, v in self.master.items():
            print(k)

    def appendLiPD(self, name_ext):
        os.chdir(self.dir_root)
        # create a lpd object
        lipd_obj = LiPD(self.dir_root, self.dir_tmp, name_ext)
        # load in the data from the lipd file (unpack, and create a temp workspace)
        lipd_obj.load()
        # add the lpd object to the master dictionary
        self.master[name_ext] = lipd_obj
