from zips import *
from directory import *
from bag import *
import json
import csv


class LiPD(object):
    """
    LiPD objects are meant to represent all the data needed to analyze a LiPD file. The object will open a LiPD file,
    allow you to analyze and query data within, modify, save, and close.
    """

    def __init__(self, dir_root, dir_tmp, name_ext):
        self.name_ext = name_ext
        self.name = os.path.splitext(name_ext)[0]
        self.dir_root = dir_root
        self.dir_tmp = dir_tmp
        self.dir_bag = os.path.join(dir_tmp, self.name)
        self.dir_data = os.path.join(self.dir_bag, 'data')
        self.data = {}

    def load(self):
        # unzip lpd file to tmp workspace (in it's own folder)
        unzip(self.name_ext, self.dir_tmp)
        try:
            # Open jld file and read in the contents. Execute DOI Resolver.
            with open(os.path.join(self.dir_data, self.name + '.jsonld'), 'r') as jld_file:
                # set all the json data
                self.data = json.load(jld_file)
        except FileNotFoundError:
            print("Lpd object: Load(). file not found")
        return

    def addCSV(self):
        # os.chdir(self.dir_data)
        # # loop through for each data table in the paleoData dictionary
        # for table in self.data['paleoData']:
        #     # create a values list for the coming csv data
        #     for col in table['columns']:
        #         col['values'] = []
        #     try:
        #         with open(table['filename'], 'r') as f:
        #             reader = csv.reader(f)
        #             for row in reader:
        #
        # os.chdir(self.dir_root)
        return

    def displayData(self):
        """
        Display all data for this file. Pretty print for readability.
        :return: None
        """
        print(json.dumps(self.data, indent=2))

    def save(self):
        # write new CSV data to new CSV files
        # remove CSV data from self.data dictionary
        # write self.data dictionary to .jsonld file (overwrite the old one)
        # run dir_cleanup (deletes old bag files and moves all data files to bag root)
        # bag the directory (dir_bag)
        # zip the directory (with the destination being the dir_root / overwrites old LPD file)
        pass

    def close(self):
        # close without saving
        # remove its folder from the tmp directory
        pass