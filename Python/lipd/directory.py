import os
import tempfile
import shutil
import ntpath
import time
import sys

import subprocess
from .loggers import create_logger


logger_directory = create_logger('directory')
_site_pkgs = ""

def _ask_how_many():
    """
    Ask user if they want to load in one file or do a batch process of a whole directory. Default to batch "m" mode.
    :return str: Path or none
    """
    batch = True
    invalid = True
    _option = ""

    try:
        while invalid:
            print("\nChoose a loading option:\n1. Select specific file(s)\n2. Load entire folder")
            _option = input("Option: ")
            # these are the only 2 valid options. if this is true, then stop prompting
            if _option in ["1", "2"]:
                invalid = False
        # indicate whether to leave batch on or turn off
        if _option == "1":
            batch = False
    except Exception:
        logger_directory.info("_askHowMany: Couldn't get a valid input from the user.")

    return batch


def _go_to_package():
    global _site_pkgs
    try:
        if not _site_pkgs:
            # Store new site pkg path
            _site_pkgs = os.path.dirname(os.path.abspath(__file__))
            os.chdir(_site_pkgs)
        else:
            # Use existing site pkg path
            os.chdir(_site_pkgs)
    except Exception as e:
        print("There was an error finding the scripts to run the GUI: " + str(e))


def browse_dialog_dir():
    """
    Open up a GUI browse dialog window and let to user pick a target directory.
    :return str: Target directory path
    """
    _go_to_package()
    logger_directory.info("enter browse_dialog")
    _path_bytes = subprocess.check_output(['python', 'gui_dir_browse.py'], shell=False)
    _path = _fix_path_bytes(_path_bytes, file=False)
    if len(_path) >= 1:
        _path = _path[0]
    else:
        _path = ""
    logger_directory.info("chosen path: {}".format(_path))
    logger_directory.info("exit browse_dialog")
    return _path


def _fix_path_bytes(_path_bytes, file=True):
    _path = str(_path_bytes.decode("utf-8"))
    _path = _path.replace("(", "").replace(")", "").replace("'", "").replace('"', "")
    _path = _path.split(",")
    for idx,i in enumerate(_path):
        _path[idx] = i.replace("\n", "").strip()
    if file:
        _new_path = [i for i in _path if i.endswith(".lpd")]
    else:
        _new_path = [i for i in _path if os.path.isdir(i)]
    return _new_path


def browse_dialog_file():
    """
    Open up a GUI browse dialog window and let to user select one or more files
    :return str _path: Target directory path
    :return list _files: List of selected files

    """
    logger_directory.info("enter browse_dialog")

    # We make files a list, because the user can multi-select files.
    _files = []
    _path = ""
    try:
        _go_to_package()
        _path_bytes = subprocess.check_output(['python', 'gui_file_browse.py'])
        _path = _fix_path_bytes(_path_bytes)
        _files = [i for i in _path]
        _path = os.path.dirname(_path[0])
        logger_directory.info("chosen path: {}, chosen file: {}".format(_path, _files))

    except IndexError:
        logger_directory.warn("directory: browse_dialog_file: IndexError: no file chosen")
    except Exception as e:
        logger_directory.error("directory: browse_dialog_file: UnknownError: {}".format(e))

    logger_directory.info("exit browse_dialog_file")

    return _path, _files


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


def create_tmp_dir():
    """
    Creates tmp directory in OS temp space.
    :return str: Path to tmp directory
    """
    t = tempfile.mkdtemp()
    logger_directory.info("temp directory: {}".format(t))
    return t


def collect_metadata_files(cwd, new_files, existing_files):
    """
    Collect all files from a given path. Separate by file type, and return one list for each type
    If 'files' contains specific
    :param str cwd: Directory w/ target files
    :param list new_files: Specific new files to load
    :param dict existing_files: Files currently loaded, separated by type
    :return list: All files separated by type
    """
    obj = {}
    try:
        os.chdir(cwd)

        # Special case: User uses gui to mult-select 2+ files. You'll be given a list of file paths.
        if new_files:
            for full_path in new_files:
                # Create the file metadata for one file, and append it to the existing files.
                obj = collect_metadata_file(full_path)

        # directory: get all files in the directory and sort by type
        else:
            for file_type in [".lpd", ".xls", ".txt"]:
                # get all files in cwd of this file extension
                files_found = list_files(file_type)
                # if looking for excel files, also look for the alternate extension.
                if file_type == ".xls":
                    files_found += list_files(".xlsx")
                # for each file found, build it's metadata and append it to files_by_type
                for file in files_found:
                    fn = os.path.splitext(file)[0]
                    existing_files[file_type].append({"full_path": os.path.join(cwd, file), "filename_ext": file, "filename_no_ext": fn, "dir": cwd})
    except Exception:
        logger_directory.info("directory: collect_files: there's a problem")

    return obj


def collect_metadata_file(full_path):
    """
    Create the file metadata and add it to the appropriate section by file-type
    :param str full_path:
    :param dict existing_files:
    :return dict existing files:
    """
    fne = os.path.basename(full_path)
    fn = os.path.splitext(fne)[0]
    obj = {"full_path": full_path, "filename_ext": fne, "filename_no_ext": fn, "dir": os.path.dirname(full_path)}
    return obj


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


def filename_from_path(path):
    """
    Extract the file name from a given file path.
    :param str path: File path
    :return str: File name with extension
    """
    head, tail = ntpath.split(path)
    return head, tail or ntpath.basename(head)


def find_files():
    """
    Search for the directory containing jsonld and csv files. chdir and then quit.
    :return none:
    """
    _dir = os.getcwd()
    _files = os.listdir()
    # Look for a jsonld file
    for _file in _files:
        if _file.endswith(".jsonld"):
            return os.getcwd()
    # No jsonld file found, try to chdir into "bag" (LiPD v1.3)
    if "bag" in _files:
        os.chdir("bag")
        _dir = find_files()
    # No "bag" dir. Try chdir into whatever dataset name dir we find (< LiPD v1.2)
    else:
        for _file in _files:
            if os.path.isdir(_file):
                os.chdir(_file)
                _dir = find_files()
    return _dir

def get_downloads_folder():
    if os.name == 'nt':
        import ctypes
        from ctypes import windll, wintypes
        from uuid import UUID

        # ctypes GUID copied from MSDN sample code
        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", wintypes.BYTE * 8)
            ]

            def __init__(self, uuidstr):
                uuid = UUID(uuidstr)
                ctypes.Structure.__init__(self)
                self.Data1, self.Data2, self.Data3, \
                self.Data4[0], self.Data4[1], rest = uuid.fields
                for i in range(2, 8):
                    self.Data4[i] = rest >> (8 - i - 1) * 8 & 0xff

        SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
        SHGetKnownFolderPath.argtypes = [
            ctypes.POINTER(GUID), wintypes.DWORD,
            wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
        ]

        def _get_known_folder_path(uuidstr):
            pathptr = ctypes.c_wchar_p()
            guid = GUID(uuidstr)
            if SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)):
                raise ctypes.WinError()
            return pathptr.value

        FOLDERID_Download = '{374DE290-123F-4565-9164-39C4925E467B}'

        return _get_known_folder_path(FOLDERID_Download)
    else:
        home = os.path.expanduser("~")
        return os.path.join(home, "Downloads")

def get_filenames_generated(d, name="", csvs=""):
    """
    Get the filenames that the LiPD utilities has generated (per naming standard), as opposed to the filenames that
    originated in the LiPD file (that possibly don't follow the naming standard)
    :param dict d: Data
    :param str name: LiPD dataset name to prefix
    :param list csvs: Filenames list to merge with
    :return list: Filenames
    """
    filenames = []
    try:
        filenames = d.keys()
        if name:
            filenames = [os.path.join(name, "data", filename) for filename in filenames]
        if csvs:
            lst = [i for i in csvs if not i.endswith("csv")]
            filenames = lst + filenames
    except Exception as e:
        logger_directory.debug("get_filenames_generated: Exception: {}".format(e))
    return filenames


def get_filenames_in_lipd(path, name=""):
    """
    List all the files contained in the LiPD archive. Bagit, JSON, and CSV
    :param str path: Directory to be listed
    :param str name: LiPD dataset name, if you want to prefix it to show file hierarchy
    :return list: Filenames found
    """
    _filenames = []
    try:
        # in the top level, list all files and skip the "data" directory
        _top = [os.path.join(name, f) for f in os.listdir(path) if f != "data"]
        # in the data directory, list all files
        _dir_data = [os.path.join(name, "data", f) for f in os.listdir(os.path.join(path, "data"))]
        # combine the two lists
        _filenames = _top + _dir_data
    except Exception:
        pass
    return _filenames


def get_src_or_dst(mode, path_type):
    """
    User sets the path to a LiPD source location
    :param str mode: "read" or "write" mode
    :param str path_type: "directory" or "file"
    :return str path: dir path to files
    :return list files: files chosen
    """
    logger_directory.info("enter set_src_or_dst")
    _path = ""
    _files = ""
    invalid = True
    count = 0

    # Did you forget to enter a mode?
    if not mode:
        invalid = False

    # Special case for gui reading a single or multi-select file(s).
    elif mode == "read" and path_type == "file":
        _path, _files = browse_dialog_file()
        # Return early to skip prompts, since they're not needed
        return _path, _files

    # All other cases, prompt user to choose directory
    else:
        prompt = get_src_or_dst_prompt(mode)

    # Loop max of 3 times, then default to Downloads folder if too many failed attempts
    while invalid and prompt:
        # Prompt user to choose target path
        _path, count = get_src_or_dst_path(prompt, count)
        if _path:
            invalid = False

    logger_directory.info("exit set_src_or_dst")
    return _path, _files


def get_src_or_dst_prompt(mode):
    """
    String together the proper prompt based on the mode
    :param str mode: "read" or "write"
    :return str prompt: The prompt needed
    """
    _words = {"read": "from", "write": "to"}
    # print(os.getcwd())
    prompt = "Where would you like to {} your file(s) {}?\n" \
             "1. Desktop ({})\n" \
             "2. Downloads ({})\n" \
             "3. Current ({})\n" \
             "4. Browse".format(mode, _words[mode],
                                  os.path.expanduser('~/Desktop'),
                                    os.path.expanduser('~/Downloads'),
                                    os.getcwd())
    return prompt


def get_src_or_dst_path(prompt, count):
    """
    Let the user choose a path, and store the value.
    :return str _path: Target directory
    :return str count: Counter for attempted prompts
    """
    _path = ""
    print(prompt)
    option = input("Option: ")
    print("\n")
    if option == '1':
        # Set the path to the system desktop folder.
        logger_directory.info("1: desktop")
        _path = os.path.expanduser('~/Desktop')
    elif option == '2':
        # Set the path to the system downloads folder.
        logger_directory.info("2: downloads")
        _path = os.path.expanduser('~/Downloads')
    elif option == '3':
        # Current directory
        logger_directory.info("3: current")
        _path = os.getcwd()
    elif option == '4':
        # Open up the GUI browse dialog
        logger_directory.info("4: browse ")
        _path = browse_dialog_dir()

    else:
        # Something went wrong. Prompt again. Give a couple tries before defaulting to downloads folder
        if count == 2:
            logger_directory.warn("too many attempts")
            print("Too many failed attempts. Defaulting to current working directory.")
            _path = os.getcwd()
        else:
            count += 1
            logger_directory.warn("failed attempts: {}".format(count))
            print("Invalid option. Try again.")

    return _path, count


def list_files(x, path=""):
    """
    Lists file(s) in given path of the X type.
    :param str x: File extension that we are interested in.
    :param str path: Path, if user would like to check a specific directory outside of the CWD
    :return list of str: File name(s) to be worked on
    """
    logger_directory.info("enter list_files")
    file_list = []
    if path:
        # list files from target directory
        files = os.listdir(path)
        for file in files:
            if file.endswith(x) and not file.startswith(("$", "~", ".")):
                # join the path and basename to create full path
                file_list.append(os.path.join(path, file))
    else:
        # list files from current working directory
        files = os.listdir()
        for file in files:
            if file.endswith(x) and not file.startswith(("$", "~", ".")):
                # append basename. not full path
                file_list.append(file)
    logger_directory.info("exit list_files")
    return file_list


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


def rm_file_if_exists(path, filename):
    """
    Remove a file if it exists. Useful for when we want to write a file, but it already exists in that locaiton.
    :param str filename: Filename
    :param str path: Directory
    :return none:
    """
    _full_path = os.path.join(path, filename)
    if os.path.exists(_full_path):
        os.remove(_full_path)
    return
