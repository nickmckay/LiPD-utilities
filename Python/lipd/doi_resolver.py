import urllib.error
from collections import OrderedDict
import json

import requests

from .blanks import EMPTY
from .misc import rm_empty_fields, clean_doi
from .loggers import create_logger

logger_doi_resolver = create_logger("doi_resolver")


class DOIResolver(object):
    """
    Use DOI id(s) to pull updated publication info from doi.org and overwrite file data.

    Input:  Original publication dictionary
    Output: Updated publication dictionary (success), original publication dictionary (fail)
    """

    def __init__(self, dsn, D, results, force):
        """

        :param dict: Full dict loaded from jsonld file
        """
        # Metadata
        self.D = D
        # Dataset name
        self.dsn = dsn
        # Results of which DOIs were previously processed. (One dataset)
        self.results = results
        # Force update DOIs that were previously processed, Boolean
        self.force = force

    def main(self):
        """
        Main function that gets file(s), creates outputs, and runs all operations.
        :return dict: Updated or original data for jsonld file
        """
        logger_doi_resolver.info("enter doi_resolver")
        if "pub" in self.D:
            for idx, pub in enumerate(self.D['pub']):
                # Retrieve DOI id key-value from the D
                try:
                    doi_string = pub["identifier"][0]["id"]
                except KeyError:
                    doi_string = ""

                # If a DOI is found..
                if doi_string:
                    logger_doi_resolver.info("doi entry exists: {}".format(doi_string))
                    # May be one DOI id, multiple, or none. Use regex to parse DOI(s) as a list.
                    doi_list = clean_doi(doi_string)
                    # Empty list, no DOIs found
                    if not doi_list:
                        print("Failed : {} [{}]: {}".format(self.dsn, idx, "DOI entry doesn't contain a DOI id"))
                        self.illegal_doi(doi_string)
                    # DOI(s) found
                    else:
                        # Loop for each DOI
                        for doi_id in doi_list:
                            # Send an API request for the current DOI
                            if doi_id not in self.results or self.force:
                                self.get_data(doi_id, idx)
                            else:
                                print(
                                    "Skip   : {} [{}]: {} {}".format(self.dsn, idx, doi_id, "DOI previously processed"))

                # No DOI entry in this publication
                else:
                    print("DOI Failed : {} [{}]: {}".format(self.dsn, idx, "No DOI key in publication"))
                    # Note that this data is manually entered since there is no DOI as a source.
                    logger_doi_resolver.warn("doi not found: publication index: {}".format(self.dsn, idx))
                    self.D['pub'][idx]['pubDataUrl'] = 'Manually Entered'
        logger_doi_resolver.info("exit doi_resolver")
        # Remove all empty fields from the metadata before returning.
        return rm_empty_fields(self.D)

    @staticmethod
    def compile_date(date_parts):
        """
        Compiles date only using the year
        :param list date_parts: List of date parts retrieved from doi.org
        :return str: Date string or NaN
        """
        if date_parts[0][0]:
            return date_parts[0][0]
        return 'NaN'

    @staticmethod
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

    # def remove_empties(self, pub):
    #     for x in list(self.D['pub'][pub].keys()):
    #         if x == 'identifier':
    #             try:
    #                 if self.D['pub'][pub][x][0]['id'] in EMPTY:
    #                     del self.D['pub'][pub][x]
    #             except KeyError:
    #                 pass
    #         elif x == "doi":
    #             try:
    #                 if self.D['pub'][pub][x] in EMPTY:
    #                     del self.D['pub'][pub][x]
    #             except KeyError:
    #                 pass
    #         elif self.D['pub'][pub][x] in EMPTY:
    #             del self.D['pub'][pub][x]
    #     return

    def noaa_citation(self, doi_string):
        """
        Special instructions for moving noaa data to the correct fields
        :param doi_string: (str) NOAA url
        :return: None
        """
        # Append location 1
        if 'link' in self.D['pub'][0]:
            self.D['pub'][0]['link'].append({"url": doi_string})
        else:
            self.D['pub'][0]['link'] = [{"url": doi_string}]

        # Append location 2
        self.D['dataURL'] = doi_string

        return

    def illegal_doi(self, doi_string):
        """
        DOI string did not match the regex. Determine what the data is.
        :param doi_string: (str) Malformed DOI string
        :return: None
        """
        logger_doi_resolver.info("enter illegal_doi")
        # Ignores empty or irrelevant strings (blank, spaces, na, nan, ', others)
        if len(doi_string) > 5:

            # NOAA string
            if 'noaa' in doi_string.lower():
                self.noaa_citation(doi_string)

            # Paragraph citation / Manual citation
            elif doi_string.count(' ') > 3:
                self.D['pub'][0]['citation'] = doi_string

            # Strange Links or Other, send to quarantine
            else:
                logger_doi_resolver.warn("illegal_doi: bad doi string: {}".format(doi_string))
        logger_doi_resolver.info("exit illegal_doi")
        return

    def compile_fetch(self, raw, doi_id):
        """
        Loop over Raw and add selected items to Fetch with proper formatting
        :param dict raw: JSON data from doi.org
        :param str doi_id:
        :return dict:
        """
        fetch_dict = OrderedDict()
        order = {'author': 'author', 'type': 'type', 'identifier': '', 'title': 'title', 'journal': 'container-title',
                 'year': '', 'volume': 'volume', 'publisher': 'publisher', 'page': 'page', 'issue': 'issue'}

        for k, v in order.items():
            try:
                if k == 'identifier':
                    fetch_dict[k] = [{"type": "doi", "id": doi_id, "url": "http://dx.doi.org/" + doi_id}]
                elif k == 'author':
                    fetch_dict[k] = self.compile_authors(raw[v])
                elif k == 'year':
                    fetch_dict[k] = self.compile_date(raw['issued']['date-parts'])
                else:
                    fetch_dict[k] = raw[v]
            except KeyError as e:
                # If we try to add a key that doesn't exist in the raw dict, then just keep going.
                logger_doi_resolver.warn("compile_fetch: KeyError: key not in raw: {}, {}".format(v, e))
        return fetch_dict

    def get_data(self, doi_id, idx):
        """
        Resolve DOI and compile all attributes into one dictionary
        :param str doi_id:
        :param int idx: Publication index
        :return dict: Updated publication dictionary
        """

        tmp_dict = self.D['pub'][0].copy()
        try:
            # Send request to grab metadata at URL
            url = "http://dx.doi.org/" + doi_id
            headers = {"accept": "application/rdf+xml;q=0.5, application/citeproc+json;q=1.0"}
            r = requests.get(url, headers=headers)

            # Ignore other status codes. Run when status is 200 (good response)
            if r.status_code == 200:
                logger_doi_resolver.info("doi.org STATUS: 200")
                # Load data from http response
                raw = json.loads(r.text)

                # Create a new pub dictionary with metadata received
                fetch_dict = self.compile_fetch(raw, doi_id)

                # Compare the two pubs. Overwrite old data with new data where applicable
                tmp_dict = self.compare_replace(tmp_dict, fetch_dict)
                tmp_dict['pubDataUrl'] = 'doi.org'
                self.D['pub'][idx] = tmp_dict
                print("Success: {} [{}]: {}".format(self.dsn, idx, doi_id))

            # DOI Error. Data not retrieved. Log and return original pub
            else:
                logger_doi_resolver.warn("doi.org STATUS: {}, {}".format(r.status_code, doi_id))
                print("Failed : {} [{}]: {} HTTP {} Error".format(self.dsn, idx, doi_id, str(r.status_code)))

        except urllib.error.URLError as e:
            print("Failed : {} [{}]: {} URL Error".format(self.dsn, idx, doi_id))
            logger_doi_resolver.warn("get_data: URLError: malformed doi: {}, {}".format(doi_id, e))
        except ValueError as e:
            print("Failed : {} [{}]: {} Cannot resolve DOIs from this publisher".format(self.dsn, idx, doi_id))
            logger_doi_resolver.warn(
                "get_data: ValueError: cannot resolve dois from this publisher: {}, {}".format(doi_id, e))
        return

    def find_doi(self, curr_dict):
        """
        Recursively search the file for the DOI id. More taxing, but more flexible when dictionary structuring isn't absolute
        :param dict curr_dict: Current dictionary being searched
        :return dict bool: Recursive - Current dictionary, False flag that DOI was not found
        :return str bool: Final - DOI id, True flag that DOI was found
        """
        try:
            if 'id' in curr_dict:
                return curr_dict['id'], True
            elif isinstance(curr_dict, list):
                for i in curr_dict:
                    return self.find_doi(i)
            elif isinstance(curr_dict, dict):
                for k, v in curr_dict.items():
                    if k == 'identifier' or k == "doi":
                        return self.find_doi(v)
                return curr_dict, False
            else:
                return curr_dict, False
        # If the ID key doesn't exist, then return the original dict with a flag
        except TypeError:
            return curr_dict, False
