import urllib.request
import os

def get_download_path():
    """
    Determine the OS and the associated download folder.
    :return str Download path:
    """
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')


def download_from_url(src_url, dst_dir):
    """
    Use the given URL and destination to download and save a file
    :param str src_url: Direct URL to lipd file download
    :param str dst_path: Local path to download file to, including filename and ext. ex. /path/to/filename.lpd
    :return none:
    """
    dst_path = ""
    if "MD982181" not in src_url:
        dsn = input("Please enter the dataset name for this file (Name.Location.Year) : ")
        dst_path = os.path.join(dst_dir, dsn + ".lpd")
        try:
            print("downloading file from url...")
            urllib.request.urlretrieve(src_url, dst_path)
        except Exception as e:
            print("Error: unable to download from url: {}".format(e))
    else:
        print("Error: That file cannot be download due to server restrictions")
    return dst_path