import csv

from ..helpers.directory import check_file_age
from ..helpers.google import get_google_csv


def lipd_lint(d):
    """
    Main lint function. Correct any invalid terms.
    :param d: (dict) Unmodified metadata
    :return: (dict) Modified metadata
    """
    # Retrieve valid terms
    full, quick, sections = _fetch_lipdnames()
    # Validate the metadata
    metadata = _verify_sections(full, quick, d, sections)

    return metadata


def _fetch_lipdnames():
    """
    Call down a current version of terms spreadsheet from google. Convert to a structure better
    for comparisons.
    :return: (full_list) Complete terms dictionary. Keys: Valid term, Values: Synonyms
    :return: (quick_list) List of valid terms
    """
    section = ''
    sections = ['@context']
    full_list = {}
    quick_list = []

    # Check if it's been longer than one day since updating the csv file.
    # If so, go fetch the file from google in case it's been updated since.
    # Or if file isn't found at all, download it also.
    if check_file_age('lipdnames.csv', 1):
        # Fetch sheet from google
        print("Fetching update for lipdnames.csv")
        _id = '1ccPOueT5ZAm5Vmd3ys2hyVvtr9fz-lhfPvZfwweIB3k'
        get_google_csv(_id, 'lipdnames.csv')

    try:
        # Start sorting the tsnames into an organized structure
        with open('lipdnames.csv', 'r') as f:
            r = csv.reader(f, delimiter=',')
            for idx, line in enumerate(r):
                if idx != 0:
                    permutations = []
                    # Do not record empty lines. Create list of non-empty entries.
                    line = [x for x in line if x]

                    # Record lines with content
                    if line:
                        # Get section header
                        if 'SECTION' in line[0]:
                            section = line[0].split(':')[1]
                            sections.append(section)
                        else:
                            # Create and add name permutations
                            if section != 'root':
                                for name in line:
                                    permutations.append(section + "_" + name)
                                    permutations.append(section + name)

                            # Add items to the lists
                            if section not in full_list:
                                full_list[section] = []
                            quick_list.append(line[0])
                            full_list[section].append(line + permutations)


    except FileNotFoundError:
        print("CSV FileNotFound: lipdnames")

    return full_list, quick_list, sections


def _verify_sections(full, quick, d, sections):
    """
    Verify terms by section (in case of overlapping terms)
    :param full: (dict) Complete dictionary of terms
    :param quick: (list) Complete list of valid terms only
    :param d: (dict) Unmodified metadata
    :param sections: (list) Names of sections
    :return: (dict) Modified metadata
    """
    metadata = {}
    for k, v in d.items():
        # Item is in root
        if isinstance(v, str) and k != '@context' and k not in quick:
            # Invalid key. Get valid
            metadata[k] = _iter_root(full, 'root', k)

        # Item is a section
        elif isinstance(v, list) or isinstance(v, dict) and k in sections:
            # Invalid key. Get valid
            metadata[k] = _iter_section(full, quick, k, v)
        else:
            # Rogue key. Just keep it as-is
            metadata[k] = v
    return metadata


def _iter_root(full, section, key):
    """
    Single pass. Find valid key for root item.
    :param full: (dict) Full list of valid keys and synonyms
    :param section: (str) Name of current section
    :param key: (str) Invalid key
    :return: (str) Key, as-is or modified
    """
    try:
        for line in full[section]:
            if key in line:
                # Found a match. Replace with valid
                return line[0]
            else:
                # No match found. Return original key
                return key
    except KeyError:
        return key


def _iter_section(full, quick, section, d1):
    """
    Multi-pass. Find valid keys for all items in one section.
    :param full: (dict) Full list of valid keys and synonyms
    :param section: (str) Name of current section
    :param d1: (any) Unmodified data
    :return: (any) Modified data
    """
    tmp = {}
    switch = {}

    if isinstance(d1, str):
        # Base case: Return as-is.
        return d1

    elif isinstance(d1, list):
        # Intermediate case: Call for each item in list
        for idx, item in enumerate(d1):
            d1[idx] = _iter_section(full, quick, section, item)

    elif isinstance(d1, dict):

        # Can't mod dict in-place. Track which keys need to be switched.
        for name in list(d1.keys()):
            if name not in quick:
                # Not valid term. Start looking for valid.
                for line in full[section]:
                    # Check each line to see where its match is.
                    if name in line:
                        # Found a match. Keep the valid term.
                        switch[name] = line[0]
            if name not in switch:
                # Not in switch means valid term wasn't found, or is already valid. Keep as-is
                switch[name] = name

        for k, v in d1.items():
            # Intermediate case: Call again. Set returned data in tmp under new valid term.
            tmp[switch[k]] = _iter_section(full, quick, section, v)
        d1 = tmp
    return d1
