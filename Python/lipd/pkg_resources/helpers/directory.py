import os
import tempfile
import shutil
import ntpath
import time
import tkinter
from tkinter import filedialog

from .loggers import create_logger


logger_directory = create_logger('directory')


def filename_from_path(path):
    """
    Extract the file name from a given file path.
    :param str path: File path
    :return str: File name with extension
    """
    head, tail = ntpath.split(path)
    return head, tail or ntpath.basename(head)


def create_tmp_dir():
    """
    Creates tmp directory in OS temp space.
    :return str: Path to tmp directory
    """
    t = tempfile.mkdtemp()
    logger_directory.info("temp directory: {}".format(t))
    return t


def list_files(x):
    """
    Lists file(s) in given path of the X type.
    :param str x: File extension that we are interested in.
    :return list of str: File name(s) to be worked on
    """
    logger_directory.info("enter list_files")
    file_list = []
    for file in os.listdir():
        if file.endswith(x) and not file.startswith(("$", "~", ".")):
            file_list.append(file)
    logger_directory.info("exit list_files")
    return file_list


def dir_cleanup(dir_bag, dir_data):
    """
    Moves JSON and csv files to bag root, then deletes all the metadata bag files. We'll be creating a new bag with
    the data files, so we don't need the other text files and such.
    :param str dir_bag: Path to root of Bag
    :param str dir_data: Path to Bag /data subdirectory
    :return None:
    """
    logger_directory.info("enter dir_cleanup")
    # dir : dir_data -> dir_bag
    os.chdir(dir_bag)

    # Delete files in dir_bag
    for file in os.listdir(dir_bag):
        if file.endswith('.txt'):
            os.remove(os.path.join(dir_bag, file))
    logger_directory.info("deleted files in dir_bag")
    # Move dir_data files up to dir_bag
    for file in os.listdir(dir_data):
        shutil.move(os.path.join(dir_data, file), dir_bag)
    logger_directory.info("moved dir_data contents to dir_bag")
    # Delete empty dir_data folder
    shutil.rmtree(dir_data)
    logger_directory.info("exit dir_cleanup")
    return


def check_file_age(filename, days):
    """
    Check if the target file has an older creation date than X amount of time.
    i.e. One day: 60*60*24
    :param str filename: Target filename
    :param int days: Limit in number of days
    :return bool: True - older than X time, False - not older than X time
    """
    logger_directory.info("enter check_file_age")
    # Multiply days given by time for one day.
    t = days * 60 * 60 * 24
    now = time.time()
    specified_time = now - t
    try:
        if os.path.getctime(filename) < specified_time:
            # File found and out of date
            logger_directory.info("{} not up-to-date".format(filename))
            logger_directory.info("exiting check_file_age()")
            return True
        # File found, and not out of date
        logger_directory.info("{} and up-to-date".format(filename))
        logger_directory.info("exiting check_file_age()")
        return False
    except FileNotFoundError:
        # File not found. Need to download it.
        logger_directory.info("{} not found in {}".format(filename, os.getcwd()))
        logger_directory.info("exiting check_file_age()")
        return True


def browse_dialog_dir():
    """
    Open up a GUI browse dialog window and let to user pick a target directory.
    :return str: Target directory path
    """
    logger_directory.info("enter browse_dialog")
    root = tkinter.Tk()
    root.withdraw()
    root.update()
    path = tkinter.filedialog.askdirectory(parent=root, initialdir=os.path.expanduser('~'), title='Please select a directory')
    logger_directory.info("chosen path: {}".format(path))
    root.destroy()
    logger_directory.info("exit browse_dialog")
    return path


def get_src_or_dst(mode):
    """
    User sets the path to a LiPD source location
    :return str: Path
    """
    logger_directory.info("enter set_src_or_dst")
    _path = ''
    invalid = True
    count = 0

    if mode == "save":
        prompt = "Where would you like to save your file(s)?\n1. Current\n2. Browse\n3. Downloads\n4. LiPD Workspace\n"
    elif mode == "load":
        prompt = "Where are your file(s) stored?\n1. Current\n2. Browse\n3. Downloads\n4. LiPD Workspace\n"
    else:
        # did you forget to enter a mode? silly
        invalid = False
    while invalid:
        print(prompt)
        option = input("Option: ")
        if option == '1':
            # Current directory
            logger_directory.info("1: current")
            _path = os.getcwd()
        elif option == '2':
            # Open up the GUI browse dialog
            logger_directory.info("2: browse")
            _path = browse_dialog_dir()
            # Set the path to the local files in CLI and lipd_lib
        elif option == '3':
            # Set the path to the system downloads folder.
            logger_directory.info("3: downloads")
            _path = os.path.expanduser('~/Downloads')
        elif option == '4':
            # Set path to the Notebook folder
            logger_directory.info("4: lipd workspace ")
            _path = os.path.expanduser('~/LiPD_Workspace')
        else:
            # Something went wrong. Prompt again. Give a couple tries before defaulting to downloads folder
            if count == 2:
                logger_directory.warn("too many attempts")
                print("Too many failed attempts. Defaulting to Downloads Folder.")
                _path = os.path.expanduser('~/Downloads')
            else:
                count += 1
                logger_directory.warn("failed attempts: {}".format(count))
                print("Invalid option. Try again.")
        if _path:
            invalid = False
    logger_directory.info("exit set_src_or_dst")
    return _path


def browse_dialog_file():
    """
    Open up a GUI browse dialog window and let to user pick a target directory.
    :return str: Target directory path
    :return:
    """
    root = tkinter.Tk()
    root.withdraw()
    root.update()
    path = tkinter.filedialog.askopenfilename(parent=root, initialdir=os.path.expanduser('~'), title='Please select a file')
    root.destroy()
    return path


def rm_files_in_dir(path):
    """
    Removes all files within a directory, but does not delete the directory
    :param str path: Target directory
    :return none:
    """
    for f in os.listdir(path):
        try:
            os.remove(f)
        except PermissionError:
            os.chmod(f, 0o777)
            try:
                os.remove(f)
            except Exception:
                pass
    return

