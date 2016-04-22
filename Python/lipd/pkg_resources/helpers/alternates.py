
"""
GLOBAL LIST OF ALTERNATES AND SYNONYMS
"""

# FILTER
comparisons = {"==": "=", "is": "=", "greater than": ">", "equals": "=", "equal": "=", "less than": "<"}


# Missing value name appears as many variations. Try to account for all of them
ALTS_MV = ['missing value', 'missing values', 'missingvalue', 'missingvalues', 'missing_values',
                    'missing variables', 'missing_variables', 'missingvariables']

# NOAA
# Lists for what keys go in specific dictionary blocks
NOAA_SITE_INFO = {'lat': ['northernmostlatitude', 'northernmost latitude', 'northernmost_latitude',
                     'southernmostlatitude', 'southernmost latitude', 'southernmost_latitude'],
             'lon': ['easternmostlongitude', 'easternmost longitude', 'easternmost_longitude',
                     'westernmostlongitude', 'westernmost longitude', 'westernmost_longitude'],
             'properties': ['location', 'country', 'elevation', 'site_name', 'region'],
                  }
FUNDING_LIST = ['funding_agency_name', 'grant']

# 13 is a list of keys to ignore when using create_blanks
NOAA_SECTIONS = {1: ['onlineResource', 'studyName', 'archive', 'parameterKeywords', 'originalSourceUrl'],
                 2: ['date'],
                 3: ['studyName'],
                 4: ['investigators'],
                 5: ['description'],
                 6: ['pub'],
                 7: ['funding', 'agency', 'grant'],
                 8: ['geo'],
                 9: ['collectionName', 'earliestYear', 'mostRecentYear', 'timeUnit', 'coreLength', 'notes'],
                 10: ['speciesName', 'commonName', 'treeSpeciesCode'],
                 11: ['chronology'],
                 12: ['paleoData'],
                 13: ['funding', 'type', 'bbox', 'geo']}

# The order of the items in the list is the order that we want to write them to the file.
# 11 is the order for writing each column in the variables section
NOAA_ORDERING = {1: ['studyName', 'onlineResource', 'originalSourceUrl', 'archive', 'parameterKeywords'],
                 2: ['date'],
                 3: ['studyName'],
                 4: ['investigators'],
                 5: ['description'],
                 6: ['authors', 'publishedDateOrYear', 'publishedTitle', 'journalName', 'volume', 'edition', 'issue',
                'pages', 'doi', 'onlineResource', 'fullCitation', 'abstract', 'identifier'],
                 7: ['agency', 'grant'],
                 8: ['siteName', 'location', 'country', 'northernmostLatitude', 'southernmostLatitude',
                'easternmostLongitude', 'westernmostLongitude', 'elevation'],
                 9: ['collectionName', 'earliestYear', 'mostRecentYear', 'timeUnit', 'coreLength', 'notes'],
                 10: ['speciesName', 'commonName'],
                 11: ['parameter', 'description', 'material', 'error', 'units', 'seasonality', 'archive', 'detail',
                 'method', 'dataType']}