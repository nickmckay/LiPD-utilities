import os
import tempfile
import shutil
import ntpath

__author__ = 'Chris Heiser'


def file_from_path(path):
    """
    Extract the file name from a given file path.
    :param path: (str) File path
    :return: (str) File name with extension
    """
    head, tail = ntpath.split(path)
    return head, tail or ntpath.basename(head)


def create_tmp_dir():
    """
    Creates tmp directory in OS temp space.
    :return: (str) Path to tmp directory
    """
    path_tmp = tempfile.mkdtemp()
    # os.makedirs(os.path.join(path, 'tmp'), exist_ok=True)
    return path_tmp


def list_files(x):
    """
    Lists file(s) in given path of the X type.
    :param x: (str) File extension that we are interested in.
    :return: (list of str) File name(s) to be worked on
    """
    file_list = []
    for file in os.listdir():
        if file.endswith(x):
            file_list.append(file)
    return file_list


def dir_cleanup(dir_bag, dir_data):
    """
    Moves JSON and csv files to bag root, then deletes all the metadata bag files. We'll be creating a new bag with
    the data files, so we don't need the other text files and such.
    :param dir_bag: (str) Path to root of Bag
    :param dir_data: (str) Path to Bag /data subdirectory
    :return: None
    """
    # dir : dir_data -> dir_bag
    os.chdir(dir_bag)

    # Delete files in dir_bag
    for file in os.listdir(dir_bag):
        if file.endswith('.txt'):
            os.remove(os.path.join(dir_bag, file))

    # Move dir_data files up to dir_bag
    for file in os.listdir(dir_data):
        shutil.move(os.path.join(dir_data, file), dir_bag)

    # Delete empty dir_data folder
    shutil.rmtree(dir_data)

    return
