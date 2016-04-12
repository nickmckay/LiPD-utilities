from .TimeSeries import TimeSeries


class TimeSeries_Library(object):
    def __init__(self):
        self.master = {}  # Master data. (Key: Name of TimeSeries Object. Value: TimeSeries Object)

    # LOADING

    def loadTso(self, name, d):
        """
        Load in a single TimeSeries Objects.
        :param name: (str) TSO name
        :param d: (dict) TSO metadata
        """
        t = TimeSeries()
        t.load(d)
        self.master[name] = t
        return

    def loadTsos(self, name_ext, d):
        """
        Load in multiple TimeSeries Objects.
        :param name_ext: (str) Need lpd filename in case we have to convert TSOs back to LiPDs.
        :param d: (dict) All TSOs resulting from one LiPD file. K: TS names, V: TS metadata
        """
        # Create a TSO for each, and load into the TS_Library master
        for k, v in d.items():
            t = TimeSeries()
            t.load(v)
            t.set_ts_name(k)
            t.set_lpd_name(name_ext)
            self.master[k] = t
        return

    # ANALYSIS

    def showTso(self, name):
        """
        Show contents of one TSO object.
        :param name:
        :return:
        """
        try:
            self.master[name].display_data()
        except KeyError:
            print("TimeSeries not found")
        return

    def showTsos(self):
        """
        Display all TimeSeries names in the TimeSeries_Library
        :return:
        """
        for name, tso in sorted(self.master.items()):
            print(name)
        return

    def saveTso(self, tso):
        """
        Write data for one specified TSO to file.
        :param tso: (obj)
        :return:
        """
        pass

    def saveTsos(self):
        """
        Write data from all TSOs to file.
        :return:
        """
        pass

    # CLOSING

    # HELPERS

    def get_master(self):
        """
        Get master list of TSO names and TSOs
        :return: (dict) Master dictionary
        """
        return self.master

