from .directory import get_downloads_folder

from urllib.request import urlopen
import requests
import os
import re
import cgi


def get_filename_from_cd(url):
    remotefile = urlopen(url)
    blah = remotefile.info()['Content-Disposition']
    value, params = cgi.parse_header(blah)
    filename = params["filename"]
    return filename


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


def download_from_url(src_url):
    """
    Use the given URL and destination to download and save a file
    :param str src_url: Direct URL to lipd file download
    :param str dst_path: Local path to download file to, including filename and ext. ex. /path/to/filename.lpd
    :return none:
    """
    if "MD982181" not in src_url:
        try:
            # Find the user's local downloads folder, os dependent
            #dir_downloads = get_downloads_folder()
            cwd = os.getcwd()
            # Get the filename from the URL Header Content Disposition
            filename = get_filename_from_cd(src_url)
            local_path = os.path.join(cwd, filename)
            # HTTP GET the url
            r = requests.get(src_url, allow_redirects=True)
            # Write file to downloads folder
            open(os.path.join(cwd, filename), 'wb').write(r.content)
        except Exception as e:
            print("Error: unable to download from url: {}".format(e))
    else:
        print("Error: That file cannot be download due to server restrictions")
    return local_path