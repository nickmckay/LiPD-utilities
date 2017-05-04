import os

import bagit
from .loggers import create_logger


logger_bagit = create_logger('bag')


def create_bag(dir_bag):
    """
    Create a Bag out of given files.
    :param str dir_bag: Directory that contains csv, jsonld, and changelog files.
    :return obj: Bag
    """
    logger_bagit.info("enter create_bag")
    # if not dir_bag:
    #     dir_bag = os.getcwd()
    try:
        bag = bagit.make_bag(dir_bag, {'Name': 'LiPD Project', 'Reference': 'www.lipds.net', 'DOI-Resolved': 'True'})
        logger_bagit.info("created bag")
        return bag
    except FileNotFoundError as e:
        print("Error: directory not found to create bagit")
        logger_bagit.debug("create_bag: FileNotFoundError: failed to create bagit, {}".format(e))
    except Exception as e:
        print("Error: failed to create bagit bag")
        logger_bagit.debug("create_bag: Exception: failed to create bag, {}".format(e))
    return None


def open_bag(dir_bag):
    """
    Open Bag at the given path
    :param str dir_bag: Path to Bag
    :return obj: Bag
    """
    logger_bagit.info("enter open_bag")
    try:
        bag = bagit.Bag(dir_bag)
        logger_bagit.info("opened bag")
        return bag
    except Exception as e:
        print("Error: failed to open bagit bag")
        logger_bagit.debug("failed to open bag, {}".format(e))
    return None


def validate_md5(bag):
    """
    Check if Bag is valid
    :param obj bag: Bag
    :return None:
    """
    logger_bagit.info("validate_md5")
    if bag.is_valid():
        print("Valid md5")
        # for path, fixity in bag.entries.items():
        #     print("path:{}\nmd5:{}\n".format(path, fixity["md5"]))
    else:
        print("Invalid md5")
        logger_bagit.debug("invalid bag")
    return


def resolved_flag(bag):
    """
    Check DOI flag in bag.info to see if doi_resolver has been previously run
    :param obj bag: Bag
    :return bool: Flag
    """
    if 'DOI-Resolved' in bag.info:
        logger_bagit.info("bagit resolved_flag: true")
        return True
    logger_bagit.info("bagit resolved_flag: false")
    return False


def finish_bag(dir_bag):
    """
    Closing steps for creating a bag
    :param obj dir_bag:
    :return None:
    """
    logger_bagit.info("enter finish_bag")
    # Create a bag for the 3 files
    new_bag = create_bag(dir_bag)
    open_bag(dir_bag)
    new_bag.save(manifests=True)
    logger_bagit.info("exit finish_bag")
    return
