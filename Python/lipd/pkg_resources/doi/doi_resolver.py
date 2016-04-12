import re
import urllib.error
from collections import OrderedDict

import requests

from ..helpers.loggers import *
from ..helpers.jsons import *


class DOIResolver(object):
    """
    Use DOI id(s) to pull updated publication info from doi.org and overwrite file data.

    Input:  Original publication dictionary
    Output: Updated publication dictionary (success), original publication dictionary (fail)
    """

    def __init__(self, dir_root, name, root_dict):
        """
        :param dir_root: (str) Path to dir containing all .lpd files
        :param name: (str) Name of current .lpd file
        :param root_dict: (dict) Full dict loaded from jsonld file
        """
        self.dir_root = dir_root
        self.name = name
        self.root_dict = root_dict

    def main(self):
        """
        Main function that gets file(s), creates outputs, and runs all operations.
        :return: (dict) Updated or original data for jsonld file
        """

        for idx, pub in enumerate(self.root_dict['pub']):
            # Retrieve DOI id key-value from the root_dict
            doi_string, doi_found = self.find_doi(pub)

            if doi_found:
                # Empty list for no match, or list of 1+ matching DOI id strings
                doi_list = self.clean(doi_string)
                if not doi_list:
                    self.illegal_doi(doi_string)
                else:
                    for doi_id in doi_list:
                        self.get_data(doi_id, idx)
            else:
                # Quarantine the flagged file and log it
                txt_log(self.dir_root, self.name, "quarantine.txt", "Publication #" + str(idx) + ": DOI not provided")
                self.root_dict['pub'][idx]['pubDataUrl'] = 'Manually Entered'
            # self.remove_empties(idx)
        return remove_empty_fields(self.root_dict)

    @staticmethod
    def clean(doi_string):
        """
        Use regex to extract all DOI ids from string (i.e. 10.1029/2005pa001215)
        :param doi_string: (str) Raw DOI string value from input file. Often not properly formatted.
        :return: (list) DOI ids. May contain 0, 1, or multiple ids.
        """
        regex = re.compile(r'\b(10[.][0-9]{3,}(?:[.][0-9]+)*/(?:(?!["&\'<>,])\S)+)\b')
        try:
            # Returns a list of matching strings
            m = re.findall(regex, doi_string)
        except TypeError:
            # If doi_string is None type, return empty list
            m = []
        return m

    @staticmethod
    def compile_date(date_parts):
        """
        Compiles date only using the year
        :param date_parts: List of date parts retrieved from doi.org
        :return: Date string or NaN
        """
        if date_parts[0][0]:
            return date_parts[0][0]
        return 'NaN'

    @staticmethod
    def compile_authors(authors):
        """
        Compiles authors "Last, First" into a single list
        :param authors: (list) Raw author data retrieved from doi.org
        :return: (list) Author objects
        """
        author_list = []
        for person in authors:
            author_list.append({'name': person['family'] + ", " + person['given']})
        return author_list

    @staticmethod
    def compare_replace(pub_dict, fetch_dict):
        """
        Take in our Original Pub, and Fetched Pub. For each Fetched entry that has data, overwrite the Original entry
        :param pub_dict: (dict) Original pub dictionary
        :param fetch_dict: (dict) Fetched pub dictionary from doi.org
        :return: (dict) Updated pub dictionary, with fetched data taking precedence
        """
        blank = [" ", "", None]
        for k, v in fetch_dict.items():
            try:
                if fetch_dict[k] != blank:
                    pub_dict[k] = fetch_dict[k]
            except KeyError:
                pass
        return pub_dict

    def remove_empties(self, pub):
        for x in list(self.root_dict['pub'][pub].keys()):
            if x == 'identifier':
                if self.root_dict['pub'][pub][x][0]['id'] in EMPTY:
                    del self.root_dict['pub'][pub][x]
            elif self.root_dict['pub'][pub][x] in EMPTY:
                del self.root_dict['pub'][pub][x]
        return

    def noaa_citation(self, doi_string):
        """
        Special instructions for moving noaa data to the correct fields
        :param doi_string: (str) NOAA url
        :return: None
        """
        # Append location 1
        if 'link' in self.root_dict['pub'][0]:
            self.root_dict['pub'][0]['link'].append({"url": doi_string})
        else:
            self.root_dict['pub'][0]['link'] = [{"url": doi_string}]

        # Append location 2
        self.root_dict['dataURL'] = doi_string

        return

    def illegal_doi(self, doi_string):
        """
        DOI string did not match the regex. Determine what the data is.
        :param doi_string: (str) Malformed DOI string
        :return: None
        """

        # Ignores empty or irrelevant strings (blank, spaces, na, nan, ', others)
        if len(doi_string) > 5:

            # NOAA string
            if 'noaa' in doi_string.lower():
                self.noaa_citation(doi_string)

            # Paragraph citation / Manual citation
            elif doi_string.count(' ') > 3:
                self.root_dict['pub'][0]['citation'] = doi_string

            # Strange Links or Other, send to quarantine
            else:
                txt_log(self.dir_root, self.name, "quarantine.txt", "Malformed DOI: " + doi_string)

        return

    def compile_fetch(self, raw, doi_id):
        """
        Loop over Raw and add selected items to Fetch with proper formatting
        :param raw: (dict) JSON data from doi.org
        :param doi_id: (str)
        :return:
        """
        fetch_dict = OrderedDict()
        order = {'author': 'author', 'type': 'type', 'identifier': '', 'title': 'title', 'journal': 'container-title',
                'pubYear': '', 'volume': 'volume', 'publisher': 'publisher', 'page':'page', 'issue': 'issue'}

        for k, v in order.items():
            try:
                if k == 'identifier':
                    fetch_dict[k] = [{"type": "doi", "id": doi_id, "url": "http://dx.doi.org/" + doi_id}]
                elif k == 'author':
                    fetch_dict[k] = self.compile_authors(raw[v])
                elif k == 'pubYear':
                    fetch_dict[k] = self.compile_date(raw['issued']['date-parts'])
                else:
                    fetch_dict[k] = raw[v]
            except KeyError as e:
                # If we try to add a key that doesn't exist in the raw dict, then just keep going.
                pass

        return fetch_dict

    def get_data(self, doi_id, idx):
        """
        Resolve DOI and compile all attributes into one dictionary
        :param doi_id: (str)
        :param idx: (int) Publication index
        :return: (dict) Updated publication dictionary
        """

        tmp_dict = self.root_dict['pub'][0].copy()
        try:
            # Send request to grab metadata at URL
            url = "http://dx.doi.org/" + doi_id
            headers = {"accept": "application/rdf+xml;q=0.5, application/citeproc+json;q=1.0"}
            r = requests.get(url, headers=headers)

            # DOI 404. Data not retrieved. Log and return original pub
            if r.status_code == 400:
                txt_log(self.dir_root, self.name, "quarantine.txt", "DOI.org 404 response: " + doi_id)

            # Ignore other status codes. Run when status is 200 (good response)
            elif r.status_code == 200:

                # Load data from http response
                raw = json.loads(r.text)

                # Create a new pub dictionary with metadata received
                fetch_dict = self.compile_fetch(raw, doi_id)

                # Compare the two pubs. Overwrite old data with new data where applicable
                tmp_dict = self.compare_replace(tmp_dict, fetch_dict)
                tmp_dict['pubDataUrl'] = 'doi.org'
                self.root_dict['pub'][idx] = tmp_dict

        except urllib.error.URLError:
            txt_log(self.dir_root, self.name, "quarantine.txt", "Malformed DOI: " + doi_id)
        except ValueError:
            txt_log(self.dir_root, self.name, "quarantine.txt", "Cannot resolve DOIs from this publisher: " + doi_id)

        return

    def find_doi(self, curr_dict):
        """
        Recursively search the file for the DOI id. More taxing, but more flexible when dictionary structuring isn't absolute
        :param curr_dict: (dict) Current dictionary being searched
        :recursive return: (dict) Current dictionary, (bool) False flag that DOI was not found
        :final return: (str) DOI id, (bool) True flag that DOI was found
        """
        try:
            if 'id' in curr_dict:
                return curr_dict['id'], True
            elif isinstance(curr_dict, list):
                for i in curr_dict:
                    return self.find_doi(i)
            elif isinstance(curr_dict, dict):
                for k, v in curr_dict.items():
                    if k == 'identifier':
                        return self.find_doi(v)
                return curr_dict, False
            else:
                return curr_dict, False
        # If the ID key doesn't exist, then return the original dict with a flag
        except TypeError:
            return curr_dict, False
