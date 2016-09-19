import urllib.request
import urllib.parse
import urllib.error

from .loggers import *

logger_google = create_logger("google")

# GLOBALS
APPLICATION_NAME = 'lipds'
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'


def get_google_csv(file_id, filename):
    """
    Get a specific spreadsheet file from Google Drive using its FILE_ID.
    Write the spreadsheet on the local system as a CSV.
    TSNames ID: 1C135kP-SRRGO331v9d8fqJfa3ydmkG2QQ5tiXEHj5us
    :param str file_id: Google File ID of target file
    :param str filename: (Optional) Override filename from google your specified filename
    :return str: CSV Filename
    """
    # Download link format
    link_csv = 'https://docs.google.com/spreadsheet/ccc?key=' + file_id + '&output=csv&pref=2'

    try:
        urllib.request.urlretrieve(link_csv, filename)
    except Exception as e:
        logger_google.debug("get_google_csv: Error retrieving: {}, {}".format(filename, e))
        print("Error retrieving {}".format(filename))

    return filename

