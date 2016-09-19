from ..helpers.zips import *
from ..helpers.directory import *
from ..helpers.bag import *
from ..helpers.csvs import *
from ..helpers.jsons import *
from ..helpers.lipd_lint import *
from ..helpers.loggers import create_logger
from ..helpers.dataframes import *


logger_lipd = create_logger('LiPD')


class LiPD(object):
    """
    LiPD objects are meant to represent all the data needed to analyze a LiPD file. The object will open a LiPD file,
    allow you to analyze and query data within, modify, save, and close.
    """

    def __init__(self, dir_root, dir_tmp, name_ext):
        self.name_ext = name_ext  # Filename with .lpd extension
        self.name = os.path.splitext(name_ext)[0]  # Filename without .lpd extension
        self.dir_root = dir_root  # Directory containing all original LiPD files.
        self.dir_tmp = dir_tmp  # Directory containing unzipped files for this LiPD. Temporary workspace.
        self.dir_tmp_bag = os.path.join(dir_tmp, self.name)  # Bagit directory in temporary folder
        self.dir_tmp_bag_data = os.path.join(self.dir_tmp_bag, 'data')  # Data folder (json, csv) in Bagit directory.
        self.dir_save = dir_root # Optional: alternate location to save lipds files. Default to dir_root
        self.data_csv = {}  # CSV data in format: { 'table1': { column_number: [value1, value2, value3... ]}}
        self.data_json = {}  # Metadata without CSV values
        self.data_master = {}  # Metadata with CSV values
        self.dfs = {}  # Pandas data frame objects
        logger_lipd.info("object created: {}".format(self.name))

    # LOADING

    def load(self):
        """
        Loads a LiPD file from local path. Unpacks, processes, and sets data to object self.
        :return:
        """
        # Start in dir_root

        # Unzip LiPD into tmp folder
        unzipper(self.name_ext, self.dir_tmp)

        # Import metadata into object
        try:
            os.chdir(self.dir_tmp_bag_data)

            # Read in metadata file
            j = read_json_from_file(self.name + '.jsonld')

            # Run the metadata through lint and correct any invalid keys
            os.chdir(self.dir_root)
            t = lipd_lint(j)

            # Read in metadata, and switch to idx-by-name
            j = idx_num_to_name(t)

            # Clean metadata of empty fields and data before loading. Set metadata to self
            self.data_master = remove_empty_fields(remove_empty_doi(j))

            # Copy metadata to self before adding csv
            self.data_json = copy.deepcopy(self.data_master)

            # Import csv into data_master
            os.chdir(self.dir_tmp_bag_data)
            self.data_master = merge_csv_metadata(self.data_master)

            # Set CSV data to self
            self.data_json, self.data_csv = get_csv_from_metadata(self.name, self.data_master)

            # Create pandas data frames from metadata and csv
            self.dfs = lipd_to_df(self.data_master, self.data_csv)

        except FileNotFoundError:
            print("LiPD file not found. Please make sure the filename includes the .lpd extension")

        os.chdir(self.dir_root)
        logger_lipd.info("object loaded: {}".format(self.name))
        return

    # ANALYSIS

    def display_csv(self):
        """
        Display csv data
        :return: None
        """
        print(json.dumps(self.data_csv, indent=2))

    def display_json(self):
        """
        Display metadata.
        :return none:
        """
        print(json.dumps(self.data_json, indent=2))

    def display_master(self):
        """
        Display metadata w/ csv
        :return none:
        """
        print(json.dumps(self.data_master, indent=2))

    def get_master(self):
        """
        Return data_master (metadata w/ csv)
        :return dict:
        """
        return self.data_master

    def get_metadata(self):
        """
        Return metadata
        :return dict:
        """
        return self.data_json

    def get_csv(self):
        """
        Return csv data
        :return dict:
        """
        return self.data_csv

    def get_dfs(self):
        """
        Return metadata, paleo, and chron data frames
        :return dict:
        """
        return self.dfs

    def get_dfs_chron(self):
        """
        Return chron data frames
        :return:
        """
        try:
            return self.dfs["chronData"]
        except KeyError:
            return {}

    def get_dfs_lipd(self):
        """
        Return metadata data frames
        :return:
        """
        try:
            return self.dfs["metadata"]
        except KeyError:
            return {}

    def get_dfs_paleo(self):
        """
        Return paleo data frames
        :return:
        """
        try:
            return self.dfs["paleoData"]
        except KeyError:
            return {}

    # CLOSING

    def save(self):
        """
        Saves current state of LiPD object data. Outputs to a LiPD file.
        :return:
        """
        # Remove everything in the tmp directory. We'll be writing all new files.
        os.chdir(self.dir_tmp_bag)
        shutil.rmtree(self.dir_tmp_bag_data)
        rm_files_in_dir(self.dir_tmp_bag)

        # Collect all the csv data from the data_master
        self.data_json, self.data_csv = get_csv_from_metadata(self.name, self.data_master)

        # Write csv data to file(s)
        write_csv_to_file(self.data_csv)

        # Remove CSV data from self.data_master and update self.data_json
        self.data_json = remove_values_fields(self.data_master)

        # Switch JSON back to old structure
        self.data_json = idx_name_to_num(self.data_json)

        # Overwrite JSON dictionary to file
        write_json_to_file(self.name, self.data_json)

        # Call bagit
        create_bag(self.dir_tmp_bag)

        # Change to dir_root, and delete the old lpd file if it's there.
        os.chdir(self.dir_root)
        if os.path.exists(self.name_ext):
            os.remove(self.name_ext)

        # Zip directory and overwrite LiPD file
        zipper(self.dir_tmp, self.name, self.name_ext)

        # Delete the LiPD directory from inside dir_tmp
        shutil.rmtree(self.dir_tmp_bag)

        return

    def remove(self):
        """
        Remove the tmp folder for this object. Do not save data.
        :return: None
        """
        shutil.rmtree(self.dir_tmp)
        return

    # HELPERS

    def set_metadata(self, dat):
        """
        Set the dictionary to the self metadata
        :param dict dat: Metadata
        :return none:
        """
        self.data_json = dat
        return

    def load_tso(self, metadata):
        """
        Overwrite LiPD self.data_master with metadata from TSO.
        :param metadata: (dict) Metadata from TSO
        """
        self.data_master = metadata
        # Split the JSON metadata from the CSV values. Update values to self.
        self.data_json, self.data_csv = split_csv_json(metadata)
        return

    def get_name_ext(self):
        """
        Retrieve the LiPD filename (with extension)
        :return: (str) Filename
        """
        return self.name_ext






