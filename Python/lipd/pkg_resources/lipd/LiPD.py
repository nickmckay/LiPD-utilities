from ..helpers.zips import *
from ..helpers.directory import *
from ..helpers.bag import *
from ..helpers.csvs import *
from ..helpers.jsons import *
from ..helpers.lipd_lint import *
from ..helpers.loggers import create_logger


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
        self.data_csv = {}  # CSV data in format: { 'table1': { column_number: [value1, value2, value3... ]}}
        self.data_json = {}  # Metadata without CSV values
        self.data_master = {}  # Metadata with CSV values
        logger_lipd.info("object created: {}".format(self.name))

    # LOADING

    def load(self):
        # Start in dir_root

        # Unzip LiPD into tmp folder
        unzip(self.name_ext, self.dir_tmp)

        # Import metadata into object
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
        self.data_master = import_csv_to_metadata(self.data_master)

        os.chdir(self.dir_root)
        logger_lipd.info("object loaded: {}".format(self.name))
        return

    # ANALYSIS

    def display_csv(self):
        """
        Display only CSV data
        :return: None
        """
        print(json.dumps(self.data_csv, indent=2))

    def display_json(self):
        """
        Display JSON data.
        :return: None
        """
        print(json.dumps(self.data_json, indent=2))

    def display_master(self):
        """
        Display CSV and JSON data
        :return: None
        """
        print(json.dumps(self.data_master, indent=2))

    def get_master(self):
        """
        Retrieve the contents of self.data_master
        :return: (dict) Metadata + CSV data
        """
        return self.data_master

    def get_metadata(self):
        """

        :return:
        """
        return self.data_master

    def get_csv(self):
        """

        :return:
        """
        return self.data_csv

    # CLOSING

    def save(self):

        # Move to data files
        os.chdir(self.dir_tmp_bag_data)

        # Collect all the csv data from the metadata
        # Write each table to its own csv file
        self.data_csv = export_csv_to_metadata(self.data_master)

        # Remove CSV data from self.data_master and update self.data_json
        self.data_json = remove_values_fields(self.data_master)

        # Switch JSON back to old structure
        self.data_json = idx_name_to_num(self.data_json)

        # Overwrite JSON dictionary to file
        write_json_to_file(self.name_ext, self.data_json)

        # Cleanup directory and prep for bagit
        dir_cleanup(self.dir_tmp_bag, self.dir_tmp_bag_data)

        # Call bagit
        create_bag(self.dir_tmp_bag)

        # Zip directory and overwrite LiPD file
        re_zip(self.dir_tmp, self.name, self.name_ext)

        # Move back to root
        os.chdir(self.dir_root)

        return

    def remove(self):
        """
        Remove the tmp folder for this object. Do not save data.
        :return: None
        """
        shutil.rmtree(self.dir_tmp)
        return

    # HELPERS

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






