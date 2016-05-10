import csv
import copy

from ..helpers.directory import check_file_age
from ..helpers.google import get_google_csv
from ..helpers.loggers import *

logger_lipd_lint = create_logger("lipd_lint")


def lipd_lint(d):
    """
    Main lint function. Correct any invalid terms.
    :param dict d: Unmodified metadata
    :return dict: Modified metadata
    """
    logger_lipd_lint.info("enter lipd_lint")
    # Retrieve valid terms
    full, sections = _fetch_lipdnames()
    # Validate the metadata
    metadata = _verify_sections(full, d, sections)
    logger_lipd_lint.info("exit lipd_lint")
    return metadata


def _fetch_lipdnames():
    """
    Call down a current version of terms spreadsheet from google. Convert to a structure better
    for comparisons.
    :return dict: Complete terms dictionary. Keys: Valid term, Values: Synonyms
    """
    section = ''
    sections = ['@context']
    full = {}

    # Check if it's been longer than one day since updating the csv file.
    # If so, go fetch the file from google in case it's been updated since.
    # Or if file isn't found at all, download it also.
    if check_file_age('lipdnames.csv', 1):
        # Fetch sheet from google
        logger_lipd_lint.info("fetching update for lipdnames.csv")
        _id = '1tlTQiVRdVOj-ccygIQALq0OFKwI84fnVXKI-8Ir_1Ms'
        get_google_csv(_id, 'lipdnames.csv')

    try:
        # Start sorting the lint into an organized structure
        logger_lipd_lint.info("organize lipdnames.csv")
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
                            if section not in ('root', 'chronology'):
                                for name in line:
                                    permutations.append(section + "_" + name)
                                    permutations.append(section + name)

                            # Add items to the lists
                            if section not in full:
                                full[section] = []
                            full[section].append(line + permutations)

    except FileNotFoundError as e:
        print("CSV FileNotFound: lipdnames.csv")
        logger_lipd_lint.debug("fetch_lipdnames: FileNotFound: lipdnames.csv, {}".format(e))
    logger_lipd_lint.info("exit fetch_lipdnames")
    return full, sections


def _verify_sections(full, d, sections):
    """
    Verify terms by section (in case of overlapping terms)
    :param dict full: Complete dictionary of terms
    :param dict d: Unmodified metadata
    :param list sections: Names of sections
    :return dict: Modified metadata
    """
    logger_lipd_lint.info("enter verify_sections")
    metadata = {}
    quick = _create_quick(full)

    for k, v in d.items():
        # Item is in root
        if isinstance(v, str) and k != '@context' and k not in quick['root']:
            # Invalid key. Get valid
            metadata[k] = _iter_root(full, 'root', k)
        elif k in ('chronData', 'chronTable'):
            metadata[k] = v
        # Item is a section
        elif isinstance(v, list) or isinstance(v, dict) and k in sections:
            # Invalid key. Get valid
            metadata[k] = _iter_section(full, quick, k, v)
        else:
            # Rogue key. Just keep it as-is
            metadata[k] = v
    logger_lipd_lint.info("exit verify_sections")
    return metadata


def _iter_root(full, section, key):
    """
    Single pass. Find valid key for root item.
    :param dict full: Full list of valid keys and synonyms
    :param str section: Name of current section
    :param str key: Invalid key
    :return str: Key, as-is or modified
    """
    try:
        for line in full[section]:
            if key in line:
                # Found a match. Replace with valid
                return line[0]
            else:
                # No match found. Return original key
                return key
    except KeyError as e:
        logger_lipd_lint.warn("iter_root: KeyError: key: {}, {}".format(key, e))
        return key


def _iter_section(full, quick, section, d1):
    """
    Multi-pass. Find valid keys for all items in one section.
    :param dict full: Full list of valid keys and synonyms
    :param str section: Name of current section
    :param any d1: Unmodified data
    :return any: Modified data
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
            if name not in quick[section]:
                # Invalid term. Start looking for valid.
                for line in full[section]:
                    # Check each line to see where its match is.
                    if name in line:
                        # Found a match. Keep the valid term.
                        switch[name] = line[0]
                        break
            if name not in switch:
                # Valid term not found, or was already valid. Keep as-is
                switch[name] = name

        for k, v in d1.items():
            if k in ('calibration', 'climateInterpretation'):
                # Nested case paleoData: Switch from paleoData to different section
                tmp[switch[k]] = _iter_section(full, quick, k, v)
            else:
                # Intermediate case: Call again. Set returned data in tmp under new valid term.
                tmp[switch[k]] = _iter_section(full, quick, section, v)
        d1 = tmp
    return d1


def _create_quick(d):
    """
    Create a dict of lists of valid names for each section
    :param dict d: Full term dictionary
    :return dict: All valid terms separated by section
    """
    logger_lipd_lint.info("enter create_quick")
    quick = {}
    try:
        for section_name, all_lists in d.items():
            section_quick = []
            for one_list in all_lists:
                try:
                    section_quick.append(one_list[0])
                except IndexError as e:
                    logger_lipd_lint.debug("create_quick: IndexError at Idx 0: {}, {}".format(one_list, e))
            quick[section_name] = copy.deepcopy(section_quick)
    except AttributeError as e:
        logger_lipd_lint.debug("create_quick: AttributeError: Failed to create quick list, {}".format(e))
    logger_lipd_lint.info("exit create_quick")
    return quick

