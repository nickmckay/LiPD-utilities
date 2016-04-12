from Parser.doi.main_doi import *
from Parser.excel.main_excel import *
from Parser.noaa.main_noaa import *


def main():
    """
    Simple command prompt. Use to run any of the subprograms.
    No need to mess with all the subprogram files. Set the directory and choose which program to run.
    """

    directory = '/Users/chrisheiser1/Desktop/lipds'

    print("Welcome to LiPD. Type help or ? to list commands.\n" \
            "Choose an action by number:\n"\
          "1. doi\n"\
          "2. excel\n"\
          "3. noaa\n")

    c = input()
    print(c)

    if c == '1' or c == 'doi':
        doi(directory)
    elif c == '2' or c == 'excel':
        excel(directory)
    elif c == '3' or c == 'noaa':
        noaa(directory)
    else:
        print("Invalid command")

    return

if __name__ == '__main__':
    main()
