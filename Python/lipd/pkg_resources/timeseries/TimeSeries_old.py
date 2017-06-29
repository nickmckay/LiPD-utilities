from ..helpers.jsons import *
from ..helpers.loggers import create_logger

logger_ts = create_logger('TimeSeries')


class TimeSeries(object):
    def __init__(self):
        self.master = {}  # Master data. JSON metadata
        self.ts_name = ''  # TimeSeries Object name. <Dataset_table_column> format.
        self.lpd_name = ''  # LiPD filename. Original from LiPD object.
        logger_ts.info("TimeSeries: object created")

    # LOADING

    def load(self, d):
        """
        Load TimeSeries metadata into object
        :param dict d: TS Metadata
        """
        self.master = d
        return

    def set_ts_name(self, ts_name):
        """
        Set the filename to match LiPD filename counterpart
        :param str ts_name: TimeSeries name. Dataset + table + column
        """
        self.ts_name = ts_name
        return

    def set_lpd_name(self, lpd_name):
        """
        Set the data set name for this TSO
        :param str lpd_name: Name_ext from the LiPD object. Needed if converting back to LiPD.
        """
        self.lpd_name = lpd_name
        return

    # ANALYSIS

    def get_master(self):
        """
        Retrieves the metadata from self.master
        :return dict: Metadata
        """
        return self.master

    def get_lpd_name(self):
        """
        Get LiPD filename for this dataset.
        """
        return self.lpd_name

    def display_data(self):
        """
        Displays the metadata contents of self.master
        """
        print(json.dumps(self.master, indent=2))
        return

    # CLOSING

    # HELPERS
