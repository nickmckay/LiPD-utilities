import bagit
from .log_init import create_logger

logger_bagit = create_logger(__name__)


def create_bag(dir_bag):
    """
    Create a Bag out of given files.
    :param dir_bag: (str) Directory that contains csv, jsonld, and changelog files.
    :return: (obj) Bag
    """
    logger_bagit.info("enter create_bag()")
    try:
        bag = bagit.make_bag(dir_bag, {'Name': 'LiPD Project', 'Reference': 'www.lipd.net', 'DOI-Resolved': 'True'})
        logger_bagit.info("Created bagit bag")
        return bag
    except Exception as e:
        logger_bagit.debug("Failed to create bag, {}".format(e))
    return None


def open_bag(dir_bag):
    """
    Open Bag at the given path
    :param dir_bag: (str) Path to Bag
    :return: (obj) Bag
    """
    logger_bagit.info("enter open_bag()")
    try:
        bag = bagit.Bag(dir_bag)
        logger_bagit.info("Opened bag")
        return bag
    except Exception as e:
        logger_bagit.debug("Failed to open bag, {}".format(e))
    return None


def validate_md5(bag):
    """
    Check if Bag is valid
    :param bag: (obj) Bag
    :return: None
    """
    logger_bagit.info("enter validate_md5()")
    if bag.is_valid():
        print("Valid md5")
        # for path, fixity in bag.entries.items():
        #     print("path:{}\nmd5:{}\n".format(path, fixity["md5"]))
    else:
        print("Invalid md5")
        logger_bagit.debug("Invalid bag")
    return


def resolved_flag(bag):
    """
    Check DOI flag in bag.info to see if doi_resolver has been previously run
    :param bag: (obj) Bag
    :return: (bool) Flag
    """
    logger_bagit.info("enter resolved_flag()")
    if 'DOI-Resolved' in bag.info:
        return True
    return False


def finish_bag(dir_bag):
    """
    Closing steps for creating a bag
    :param dir_bag:
    :return:
    """
    logger_bagit.info("enter finish_bag()")
    # Create a bag for the 3 files
    new_bag = create_bag(dir_bag)
    open_bag(dir_bag)
    new_bag.save(manifests=True)
    logger_bagit.info("exit finish_bag()")
    return
