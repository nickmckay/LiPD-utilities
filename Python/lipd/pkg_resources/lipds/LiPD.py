from ..helpers.zips import unzipper, zipper
from ..helpers.directory import rm_files_in_dir, rm_file_if_exists, get_filenames_in_lipd, get_filenames_generated
from ..helpers.bag import create_bag
from ..helpers.csvs import get_csv_from_metadata, write_csv_to_file, merge_csv_metadata
from ..helpers.jsons import read_json_from_file, write_json_to_file, split_csv_json, idx_num_to_name, idx_name_to_num,\
    rm_values_fields, rm_empty_doi, rm_empty_fields
from ..helpers.lipd_lint import lipd_lint
from ..helpers.loggers import create_logger
from ..helpers.dataframes import lipd_to_df
from ..helpers.misc import put_tsids
from ..helpers.validator_api import get_validator_format

from collections import OrderedDict
import json
import os
import copy
import shutil


logger_lipd = create_logger('LiPD')


class LiPD(object):
    """
    LiPD objects are meant to represent all the data needed to analyze a LiPD file. The object will open a LiPD file,
    allow you to analyze and query data within, modify, save, and close.
    """

    def __init__(self, dir_root, dir_tmp, name_ext):
        self.name_ext = name_ext  # Filename with .lpd extension
        self.name = os.path.splitext(name_ext)[0]  # Filename without .lpd extension
        self.dir_root = dir_root  # Directory where this file originated from
        self.dir_tmp = dir_tmp  # Directory containing unzipped files for this LiPD. Temporary workspace.
        self.dir_tmp_bag = os.path.join(dir_tmp, self.name)  # Bagit directory in temporary folder
        self.dir_tmp_bag_data = os.path.join(self.dir_tmp_bag, 'data')  # Data folder (json, csv) in Bagit directory.
        self.dir_save = dir_root # Optional: alternate location to save lipds files. Default to dir_root
        self.data_csv = OrderedDict()  # CSV data in format: { 'table1': { column_number: [value1, value2, value3... ]}}
        self.data_json = {}  # Metadata without CSV values
        self.data_json_raw = {}  # The untouched raw json from the jsonld file. Use for validate() function
        self.data_master = {}  # Metadata with CSV values
        self.data_filenames = []  # filenames of all the files in the LiPD archive
        self.data_validator_results = {}  # Results from lipd.net/api/validator that we store.
        self.dfs = {}  # Pandas data frame objects
        logger_lipd.info("object created: {}".format(self.name))

    # READ

    def read(self):
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
            # j = lipd_lint(j)

            # Read in metadata, and switch to idx-by-name
            j = idx_num_to_name(j)

            # Clean metadata of empty fields and data before loading. Set metadata to self
            self.data_master = rm_empty_fields(rm_empty_doi(j))

            # Copy metadata to self before adding csv
            self.data_json = copy.deepcopy(self.data_master)

            # Read CSV files into memory, and merge as "values" fields into data_master
            os.chdir(self.dir_tmp_bag_data)
            self.data_master = merge_csv_metadata(self.data_master)

            # Set CSV data to self, and receive updated data_master as well
            self.data_master, self.data_csv = get_csv_from_metadata(self.name, self.data_master)

            # A few things have changed in data_master metadata, so remove CSV data and update data_json
            self.data_json = rm_values_fields(copy.deepcopy(self.data_master))

            # Switch JSON back to old structure
            self.data_json_raw = copy.deepcopy(self.data_json)
            self.data_json_raw = idx_name_to_num(self.data_json_raw)

            # Create pandas data frames from metadata and csv
            self.dfs = lipd_to_df(self.data_master, self.data_csv)

            # Get list of all filenames found in LiPD archive.
            self.data_filenames = get_filenames_in_lipd(self.dir_tmp_bag, self.name)
            self.data_filenames = get_filenames_generated(self.data_csv, self.name, self.data_filenames)


        except FileNotFoundError:
            print("Error: LiPD file not found. Please make sure the filename includes the .lpd extension")
        except Exception as e:
            print("Error: unable to read LiPD: {}".format(e))

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

    # GET

    def get_validator_results(self):
        """
        Get stored validator results
        :return dict d: Stored results
        """
        return self.data_validator_results

    def get_whole_object(self):
        """
        Get object as a dictionary with all self attributes.
        :return dict:
        """
        return

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

    def get_name_ext(self):
        """
        Retrieve the LiPD filename (with extension)
        :return: (str) Filename
        """
        return self.name_ext

    def get_validator_formatted(self):
        """
        Format our LiPD data into the Validator format
        :return list: LiPD metadata ready for the validator API
        """
        # Get our LiPD data into the Validator format.
        _formatted = get_validator_format(self.data_json_raw, self.data_csv, self.data_filenames)
        return _formatted

    # PUT

    def put_validator_results(self, d):
        """
        Put validate results in object
        :param dict d: Validator results
        :return none:
        """
        self.data_validator_results = d
        return

    def put_metadata(self, d):
        """
        Replace self.data_json with the data provided
        :return none:
        """
        self.data_json = d
        return

    def put_master(self, d):
        """
        Replace self.data_master with the data provided
        :return none:
        """
        self.data_master = d
        return

    # WRITE

    def write(self, dir_dst):
        """
        Saves current state of LiPD object data. Outputs to a LiPD file.
        :param str dir_dst: Target directory destination
        :return:
        """
        # Remove everything in the tmp directory. We'll be writing all new files.
        os.chdir(self.dir_tmp_bag)
        try:
            shutil.rmtree(self.dir_tmp_bag_data)
            rm_files_in_dir(self.dir_tmp_bag)
        except Exception as e:
            logger_lipd.warn("lipd: write: tmp dir files already removed, don't exist: {}".format(e))

        # Collect all the csv data from the data_master
        self.data_json, self.data_csv = get_csv_from_metadata(self.name, self.data_master)

        # Write csv data to file(s)
        write_csv_to_file(self.data_csv)

        # Remove CSV data from self.data_master and update self.data_json
        self.data_json = rm_values_fields(copy.deepcopy(self.data_master))

        # Add TSids to columns wherever necessary! Generate them and get back the new JSON.
        self.data_json = put_tsids(self.data_json)

        # Switch JSON back to old structure
        self.data_json = idx_name_to_num(self.data_json)

        # Overwrite JSON dictionary to file
        write_json_to_file(self.name, self.data_json)

        # Call bagit
        create_bag(self.dir_tmp_bag)

        # Delete a LiPD file if it already exists in our destination location
        rm_file_if_exists(dir_dst, self.name_ext)

        # Zip directory and overwrite LiPD file
        # zipper(name_ext=self.name_ext, root_dir=self.dir_tmp, name=self.name, dir_dst)
        zipper(path_name_ext=os.path.join(dir_dst, self.name_ext), root_dir=self.dir_tmp, name=self.name)

        # Delete the LiPD directory from inside dir_tmp
        # shutil.rmtree(self.dir_tmp_bag)

        return

    def remove(self):
        """
        Remove the tmp folder for this object. Do not save data.
        :return: None
        """
        shutil.rmtree(self.dir_tmp)
        return

    # HELPERS

    def load_tso(self, d):
        """
        Overwrite LiPD self.data_master with metadata from TSO.
        :param dict d: Metadata from TSO
        """
        self.data_master = d
        # Split the JSON metadata from the CSV values. Update values to self.
        self.data_json, self.data_csv = get_csv_from_metadata(self.name, self.data_master)
        return






