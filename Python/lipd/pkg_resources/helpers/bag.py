import bagit


def create_bag(dir_bag):
    """
    Create a Bag out of given files.
    :param dir_bag: (str) Directory that contains csv, jsonld, and changelog files.
    :return: (obj) Bag
    """
    bag = bagit.make_bag(dir_bag, {'Name': 'LiPD Project', 'Reference': 'www.lipd.net', 'DOI-Resolved': 'True'})
    return bag


def open_bag(dir_bag):
    """
    Open Bag at the given path
    :param dir_bag: (str) Path to Bag
    :return: (obj) Bag
    """
    bag = bagit.Bag(dir_bag)
    return bag


def validate_md5(bag):
    """
    Check if Bag is valid
    :param bag: (obj) Bag
    :return: None
    """
    if bag.is_valid():
        print("Valid md5")
        # for path, fixity in bag.entries.items():
        #     print("path:{}\nmd5:{}\n".format(path, fixity["md5"]))
    else:
        print("Invalid md5")
    return


def resolved_flag(bag):
    """
    Check DOI flag in bag.info to see if doi_resolver has been previously run
    :param bag: (obj) Bag
    :return: (bool) Flag
    """
    if 'DOI-Resolved' in bag.info:
        return True
    return False

