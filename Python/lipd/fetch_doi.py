import urllib.error
from collections import OrderedDict
import json
import re
import requests
import csv
import os
import demjson

def update_dois(csv_source, write_file=True):
    """
    Get DOI publication info for a batch of DOIs. This is LiPD-independent and only requires a CSV file with all DOIs
    listed in a single column. The output is LiPD-formatted publication data for each entry.

    :param str csv_source: Local path to CSV file
    :param bool write_file: Write output data to JSON file (True), OR pretty print output to console (False)
    :return none:
    """

    _dois_arr = []
    _dois_raw = []

    # open the CSV file
    with open(csv_source, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            # sort the DOIs as an array of DOI strings
            _dois_arr.append(row[0])

    # run the DOI resolver once for each DOI string.
    for _doi in _dois_arr:
        _dois_raw.append(_update_doi(_doi))

    if write_file:
        # Write the file
        new_filename = os.path.splitext(csv_source)[0]
        write_json_to_file(_dois_raw, new_filename)

    else:
        print(json.dumps(_dois_raw, indent=2))

    return


def write_json_to_file(json_data, filename="metadata"):
    """
    Write all JSON in python dictionary to a new json file.
    :param any json_data: JSON data
    :param str filename: Target filename (defaults to 'metadata.jsonld')
    :return None:
    """
    # Use demjson to maintain unicode characters in output
    json_bin = demjson.encode(json_data, encoding='utf-8', compactly=False)
    # Write json to file
    try:
        open("{}.json".format(filename), "wb").write(json_bin)
    except FileNotFoundError as e:
        print("Error: Writing json to file: {}".format(filename))
    return


def _update_doi(doi_string):
    """
    """
    res = []
    doi_list = clean_doi(doi_string)
    if not doi_list:
        print("That doesn't look like a DOI: {}".format(doi_string))
    else:
        for doi_id in doi_list:
            res.append(get_data(doi_id))

    return res


def compile_date(date_parts):
    """
    Compiles date only using the year
    :param list date_parts: List of date parts retrieved from doi.org
    :return str: Date string or NaN
    """
    if date_parts[0][0]:
        return date_parts[0][0]
    return 'NaN'

def compile_authors(authors):
    """
    Compiles authors "Last, First" into a single list
    :param list authors: Raw author data retrieved from doi.org
    :return list: Author objects
    """
    author_list = []
    for person in authors:
        author_list.append({'name': person['family'] + ", " + person['given']})
    return author_list


def compile_fetch(raw, doi_id):
    """
    Loop over Raw and add selected items to Fetch with proper formatting
    :param dict raw: JSON data from doi.org
    :param str doi_id:
    :return dict:
    """
    fetch_dict = OrderedDict()
    order = {'author': 'author', 'type': 'type', 'identifier': '', 'title': 'title', 'journal': 'container-title',
            'pubYear': '', 'volume': 'volume', 'publisher': 'publisher', 'page':'page', 'issue': 'issue'}

    for k, v in order.items():
        try:
            if k == 'identifier':
                fetch_dict[k] = [{"type": "doi", "id": doi_id, "url": "http://dx.doi.org/" + doi_id}]
            elif k == 'author':
                fetch_dict[k] = compile_authors(raw[v])
            elif k == 'pubYear':
                fetch_dict[k] = compile_date(raw['issued']['date-parts'])
            else:
                fetch_dict[k] = raw[v]
        except KeyError as e:
            # If we try to add a key that doesn't exist in the raw dict, then just keep going.
            pass
    return fetch_dict

def get_data(doi_id):
    """
    Resolve DOI and compile all attributes into one dictionary
    :param str doi_id:
    :param int idx: Publication index
    :return dict: Updated publication dictionary
    """

    fetch_dict = {}

    try:
        # Send request to grab metadata at URL
        print("Requesting : {}".format(doi_id))
        url = "http://dx.doi.org/" + doi_id
        headers = {"accept": "application/rdf+xml;q=0.5, application/citeproc+json;q=1.0"}
        r = requests.get(url, headers=headers)


        # DOI 404. Data not retrieved. Log and return original pub
        if r.status_code == 400 or r.status_code == 404:
            print("HTTP 404: DOI not found, {}".format(doi_id))

        # Ignore other status codes. Run when status is 200 (good response)
        elif r.status_code == 200:
            # Load data from http response
            raw = json.loads(r.text)
            # Create a new pub dictionary with metadata received
            fetch_dict = compile_fetch(raw, doi_id)
            fetch_dict['pubDataUrl'] = 'doi.org'

    except urllib.error.URLError as e:
        fetch_dict["ERROR"] = e
        fetch_dict["doi"] = doi_id
        print("get_data: URLError: malformed doi: {}, {}".format(doi_id, e))
    except Exception as e:
        fetch_dict["ERROR"] = e
        fetch_dict["doi"] = doi_id
        print("get_data: ValueError: cannot resolve dois from this publisher: {}, {}".format(doi_id, e))
    return fetch_dict


def clean_doi(doi_string):
    """
    Use regex to extract all DOI ids from string (i.e. 10.1029/2005pa001215)

    :param str doi_string: Raw DOI string value from input file. Often not properly formatted.
    :return list: DOI ids. May contain 0, 1, or multiple ids.
    """
    regex = re.compile(r'\b(10[.][0-9]{3,}(?:[.][0-9]+)*/(?:(?!["&\'<>,])\S)+)\b')
    try:
        # Returns a list of matching strings
        m = re.findall(regex, doi_string)
    except TypeError as e:
        # If doi_string is None type, return empty list
        print("TypeError cleaning DOI: {}, {}".format(doi_string, e))
        m = []
    return m