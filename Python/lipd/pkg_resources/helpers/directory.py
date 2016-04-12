import os
import tempfile
import shutil
import ntpath
import time
import tkinter
from tkinter import filedialog


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
    return tempfile.mkdtemp()


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


def check_file_age(filename, days):
    """
    Check if the target file has an older creation date than X amount of time.
    i.e. One day: 60*60*24
    :param filename: (str) Target filename
    :param days: (int) Limit in number of days
    :return: (bool) True - older than X time, False - not older than X time
    """
    # Multiply days given by time for one day.
    t = days * 60 * 60 * 24
    now = time.time()
    specified_time = now - t
    try:
        if os.path.getctime(filename) < specified_time:
            # File found and out of date
            return True
        # File found, and not out of date
        return False
    except FileNotFoundError:
        # File not found. Need to download it.
        return True


def browse_dialog():
    """
    Open up a GUI browse dialog window and let to user pick a target directory.
    :return str: Target directory path
    """

    root = tkinter.Tk()
    root.withdraw()
    root.update()
    path = tkinter.filedialog.askdirectory(parent=root, initialdir=os.path.expanduser('~'), title='Please select a directory')
    root.destroy()

    return path


def set_source():
    """
    User sets the path to LiPD source. Local or online.
    :return: (str) Path
    """
    path = None
    invalid = True
    count = 0
    print("Where are your files stored? Choose an option by number:\n1. Online URL\n2. Local Computer\n3. "
      "Downloads "
      "Folder\n")
    while invalid:
        option = input("Option: ")
        if option == '1':
            # Retrieve data from the online URL
            path = input("Enter the URL: ")
        elif option == '2':
            # Open up the GUI browse dialog
            path = browse_dialog()
            # Set the path to the local files in CLI and lipd_lib
        elif option == '3':
            # Set the path to the system downloads folder.
            path = os.path.expanduser('~/Downloads')
        else:
            # Something went wrong. Prompt again. Give a couple tries before defaulting to downloads folder
            if count == 2:
                print("Defaulting to Downloads Folder.")
                path = os.path.expanduser('~/Downloads')
            else:
                count += 1
                print("Invalid option. Try again.")
        if path:
            invalid = False
    print(path)
    return path
