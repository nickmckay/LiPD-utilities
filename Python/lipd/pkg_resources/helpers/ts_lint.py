import csv

from ..helpers.regexes import *
from ..helpers.directory import check_file_age
from ..helpers.google import get_google_csv

# VALIDATING AND UPDATING TSNAMES


def update_tsnames(metadata):
    """
    Updates the TS names for a given metadata dictionary
    :param metadata: (dict) Metadata dictionary
    :return: (dict) Updated metadata dictionary
    """
    full, quick = _fetch_tsnames()
    metadata = _verify_tsnames(full, quick, metadata)
    return metadata


def _fetch_tsnames():
    """
    Call down a current version of the TSNames spreadsheet from google. Convert to a structure better
    for comparisons.
    :return: (full_list) Complete TSName dictionary. Keys: Valid TSName, Values: Synonyms
    :return: (quick_list) List of valid TSnames
    """
    full_list = {"root": [], "pub": [], "climateInterpretation": [], "calibration": [], "geo": [], "paleoData": []}
    quick_list = []

    # Check if it's been longer than one day since updating the TSNames.csv file.
    # If so, go fetch the file from google in case it's been updated since.
    # Or if file isn't found at all, download it also.
    if check_file_age('tsnames.csv', 1):
        # Fetch TSNames sheet from google
        print("Fetching update for tsnames.csv")
        ts_id = '1C135kP-SRRGO331v9d8fqJfa3ydmkG2QQ5tiXEHj5us'
        get_google_csv(ts_id, 'tsnames.csv')
    try:
        # Start sorting the tsnames into an organized structure
        with open('tsnames.csv', 'r') as f:
            r = csv.reader(f, delimiter=',')
            for idx, line in enumerate(r):
                if idx != 0:
                    # Do not record empty lines. Create list of non-empty entries.
                    line = [x for x in line if x]
                    # If line has content (i.e. not an empty line), then record it
                    if line:
                        # We don't need all the duplicates of pub and fund.
                        if "pub" in line[0] or "funding" in line[0]:
                            if re_pub_fetch.match(line[0]):
                                quick_list.append(line[0])
                                full_list['pub'].append(line)
                        elif re_misc_fetch.match(line[0]):
                            # Other Categories. Not special
                            quick_list.append(line[0])
                            cat, key = line[0].split('_')
                            full_list[cat].append(line)
                        else:
                            # Any of the root items
                            quick_list.append(line[0])
                            full_list["root"].append(line)
    except FileNotFoundError:
        print("CSV FileNotFound: TSNames")

    return full_list, quick_list


def _verify_tsnames(full_list, quick_list, d):
    """
    Verify TSNames are current and valid. Compare to TSNames spreadsheet in Google Drive. Update where necessary.
    """
    # Temp to store incorrect keys
    bad_keys = []
    limbo = {}

    # Build onto the "limbo" dictionary so we have a list of keys to replace.
    for k, v in d.items():
        # @context, pub, fund should be ignored
        if k not in quick_list and not re_pub_valid.match(k) and not re_fund_valid.match(k) and k != '@context':
            # Invalid key. Store in temp for processing.
            if k not in limbo:
                bad_keys.append(k)
    # Start to find replacements for empty entries in "limbo"
    for invalid in bad_keys:
        # Set incorrect name as key, and valid name as value.
        limbo[invalid] = _get_valid_tsname(full_list, invalid)

    # Use limbo to start replacing entries in d
    for invalid, valid in limbo.items():
        try:
            # Add new item, and remove old item in one step
            d[valid] = d.pop(invalid)
        except KeyError:
            continue

    return d


def _get_valid_tsname(full_list, invalid):
    """
    Turn a bad tsname into a valid one.
    * Note: Index[0] for each TSName is the most current, valid entry. Index[1:] are synonyms
    :param invalid: (str) Invalid tsname
    :return: (str) valid tsname
    """
    valid = ''
    invalid = invalid.lower()
    try:
        # PUB ENTRIES
        if re_pub_invalid.match(invalid):

            # Case 1: pub1_year (number and hyphen)
            if re_pub_nh.match(invalid):
                s_invalid = invalid.split('_', 1)
                # Check which list the key word is in
                for line in full_list['pub']:
                    for key in line:
                        if s_invalid[1] in key.lower():
                            # Get the keyword from the valid entry.
                            v = line[0].split("_")
                            # Join our category with the valid keyword
                            valid = ''.join([s_invalid[0], '_', v[1]])

            # Case 2: pub_year (hyphen)
            elif re_pub_h.match(invalid):
                s_invalid = invalid.split('_', 1)
                # The missing pub number is the main problem, but the keyword may or may not be correct. Check.
                for line in full_list['pub']:
                    for key in line:
                        if s_invalid[1] in key.lower():
                            # We're going to use the valid entry as-is, because that's what we need for this case.
                            valid = line[0]

            # Case 3: pub1year (number)
            elif re_pub_n.match(invalid):
                s_invalid = re_pub_n.match(invalid)
                for line in full_list['pub']:
                    for key in line:
                        if s_invalid.group(2) in key.lower():
                            v = line[0].split('_', 1)
                            valid = ''.join(['pub', s_invalid.group(0), v[1]])

            # Case 4: pubYear (camelcase)
            elif re_pub_cc.match(invalid):
                valid = _iter_ts(full_list, 'pub', invalid)

        # FUNDING
        elif re_fund_invalid.match(invalid):
            if "grant" in invalid:
                valid = 'funding1_grant'
            elif "agency" in invalid:
                valid = "funding1_agency"

        # GEO
        elif re_geo_invalid.match(invalid):
            valid = _iter_ts(full_list, 'geo', invalid)

        # PALEODATA
        elif re_paleo_invalid.match(invalid):
            g1 = re_paleo_invalid.match(invalid).group(1)
            valid = _iter_ts(full_list, 'paleoData', g1)

        # CALIBRATION
        elif re_calib_invalid.match(invalid):
            g1 = re_calib_invalid.match(invalid).group(1)
            valid = _iter_ts(full_list, 'calibration', g1)

        # CLIMATE INTERPRETATION
        elif re_clim_invalid.match(invalid):
            g1 = re_clim_invalid.match(invalid).group(1)
            if 'climate' in g1:
                g1 = re.sub('climate', '', g1)
            valid = _iter_ts(full_list, 'climateInterpretation', g1)

        else:
            # ROOT
            valid = _iter_ts(full_list, 'root', invalid)

        # LAST CHANCE:
        # Specific case that isn't a typical format, or no match. Go through all possible entries.
        if not valid:
            valid = _iter_ts(full_list, None, invalid)

    except IndexError:
        print("ERROR TSName: Getting TS Name")

    if not valid:
        print("ERROR TSName: No match: " + invalid)
        return invalid

    return valid


def _iter_ts(full_list, category, invalid):
    """
    Match an invalid entry to one of the TSName synonyms.
    :param category: (str) Name of category being searched
    :param invalid: (str) Invalid tsname string
    :return: (str) Valid tsname
    """
    valid = ''

    # If a leading hyphen is in the string, get rid of it.
    if '_' == invalid[0]:
        invalid = invalid[1:]

    # If one specific category is passed through
    if category:
        for line in full_list[category]:
            for key in line:
                if invalid in key.lower():
                    valid = line[0]
                    break
    # If the entire TSNames dict is passed through (i.e. final effort, all categories have failed so far)
    else:
        for k, v in full_list.items():
            for line in v:
                for key in line:
                    if invalid in key.lower():
                        valid = line[0]
                        break

    return valid
