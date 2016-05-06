import datetime
import logging
import sys
import os


def update_changelog():
    """
    Create or update the changelog txt file. Prompt for update description.
    :return: none
    """
    # description = input("Please enter a short description for this update:\n ")
    description = 'Placeholder for description here.'

    # open changelog file for appending. if doesn't exist, creates file.
    with open('changelog.txt', 'a+') as f:
        # write update line
        f.write(str(datetime.datetime.now().strftime("%d %B %Y %I:%M%p")) + '\nDescription: ' + description)
    return


def txt_log(dir_root, filename, quarantine_txt, info):
    """
    Debug Log. Log names and error of problematic files to a txt file
    :param dir_root: (str) Directory containing .lpd file(s)
    :param quarantine_txt: (str) Name of the txt file to be written to
    :param filename: (str) Name of the current .lpd file
    :param info: (str) Error description
    :return: None
    """
    org_dir = os.getcwd()
    os.chdir(dir_root)
    with open(quarantine_txt, 'a+') as f:
        try:
            # Write update line
            f.write("File: " + filename + "\n" + "Error: " + info + "\n\n")
        except KeyError:
            print("Debug Log Error")
    os.chdir(org_dir)
    return


def txt_log_end(dir_root, quarantine_txt):
    """
    At the end of a batch, add a divider line and timestamp
    Quarantine.txt file is a continually growing file.
    :param dir_root: (str) Directory containing .lpd file(s)
    :param quarantine_txt: (str) Name of the txt file to be written to
    :return: None
    """
    org_dir = os.getcwd()
    os.chdir(dir_root)
    with open(quarantine_txt, 'a+') as f:
        try:
            # Write update line
            f.write('Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
            f.write("\n------------------------------------\n")
        except KeyError:
            print("Debug Log Error")
    os.chdir(org_dir)
    return
