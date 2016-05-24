
"""
GLOBAL LIST OF ALTERNATES AND SYNONYMS
"""

# FILTER
comparisons = {
    "==": "=",
    "is": "=",
    "greater than": ">",
    "equals": "=",
    "equal": "=",
    "less than": "<"
}

# EXCEL
EXCEL_GEO = [
    "latMax",
    "latMin",
    "lonMax",
    "lonMin",
    "elevation"
]


# Missing value name appears as many variations. Try to account for all of them
ALTS_MV = [
    'missing value',
    'missing values',
    'missingvalue',
    'missingvalues',
    'missing_values',
    'missing variables',
    'missing_variables',
    'missingvariables'
]

# NOAA
# Lists for what keys go in specific dictionary blocks
NOAA_SITE_INFO = {
    'lat': [
        'northernmostlatitude',
        'northernmost latitude',
        'northernmost_latitude',
        'southernmostlatitude',
        'southernmost latitude',
        'southernmost_latitude'],
    'lon': [
        'easternmostlongitude',
        'easternmost longitude',
        'easternmost_longitude',
        'westernmostlongitude',
        'westernmost longitude',
        'westernmost_longitude'],
    'properties': [
        'location',
        'country',
        'elevation',
        'site_name',
        'region'
    ],
}

NOAA_VAR_COLS = [
    "variableName",
    "description",
    "measurementMaterial",
    "uncertainty",
    "units",
    "seasonality",
    "archive",
    "detail",
    "measurementMethod",
    "dataType",
    "interpDirection"
]

FUNDING_LIST = [
    'funding_agency_name',
    'grant'
]

# 13 is a list of keys to ignore when using create_blanks
NOAA_SECTIONS = {
    1: ['onlineResource', 'studyName', 'archive', 'parameterKeywords', 'originalSourceUrl'],
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
    13: []
}

# The order of the items in the list is the order that we want to write them to the file.
# 11 is the order for writing each column in the variables section
NOAA_ORDERING = {
    1: ['studyName',
        'onlineResource',
        'originalSourceUrl',
        'archive',
        'parameterKeywords'],
    2: ['date'],
    3: ['studyName'],
    4: ['investigators'],
    5: ['description'],
    6: ['authors',
        'publishedDateOrYear',
        'publishedTitle',
        'journalName',
        'volume',
        'edition',
        'issue',
        'pages',
        'doi',
        'onlineResource',
        'fullCitation',
        'abstract',
        'identifier'],
    7: ['agency', 'grant'],
    8: ['siteName',
        'location',
        'country',
        'northernmostLatitude',
        'southernmostLatitude',
        'easternmostLongitude',
        'westernmostLongitude',
        'elevation'],
    9: ['collectionName',
        'earliestYear',
        'mostRecentYear',
        'timeUnit',
        'coreLength',
        'notes'],
    10: ['speciesName', 'commonName'],
    11: ['variableName',
         'description',
         'measurementMaterial',
         'uncertainty',
         'units',
         'seasonality',
         'archive',
         'detail',
         'method',
         'dataType']
}

NOAA_ROOT_KEYS = [
    "pu"
]

UNITS = {
    "meters": "m",
    "meter": "m",
    "centimeters": "cm",
    "centimeter": "cm",
    "feet": "ft",
    "foot": "ft",
    "millimeter": "mm",
    "millimeters": "mm"
}

NOAA_IGNORE_KEYS = [
    "originalSourceUrl",
    "original_source_url",
    "commonName",
    "common_name",
    "parameterKeywords",
    "parameter_keywords",
    "speciesName",
    "species_name",
    "timeUnit",
    "time_unit",
    "collectionName",
    "collection_name",
    "earliestYear",
    "earliest_year",
    "mostRecentYear",
    "most_recent_year",
    "coreLength",
    "core_length",
    "note"
]

NOAA_DOI_KEYS = [
    "DOI",
    "DOI_url",
    "DOI_id"
]

ALTS_JSONLD = {
    "metadata": "metadata",
    "chronology": "chronology",
    "data (qc)": "dataQC",
    "data(qc)": "dataQC",
    "data (original)": "dataOriginal",
    "data(original)": "dataOriginal",
    "data": "data",
    "proxyList": "proxy",
    "proxy": "proxy",
    "about": "about",
    "study title": "studyName",
    "investigators": "investigators",
    "authors": "author",
    "publication title": "title",
    "journal": "journal",
    "year": "year",
    "volume": "volume",
    "issue": "issue",
    "pages": "pages",
    "dataUrl": "dataUrl",
    "link": "link",
    "report number": "reportNumber",
    "doi": "id",
    "abstract": "abstract",
    "alternate citation": "alternateCitation",
    "site name": "siteName",
    "northernmost latitude": "latMax",
    "southernmost latitude": "latMin",
    "easternmost longitude": "lonMax",
    "westernmost longitude": "lonMin",
    "elevation": "elevation",
    "short_name": "variableName",
    "what": "description",
    "material": "measurementMaterial",
    "error": "error",
    "units": "units",
    "seasonality": "seasonality",
    "archive": "archive",
    "detail": "detail",
    "method": "method",
    "data_type": "dataType",
    "basis of climate relation": "basis",
    "climate_interpretation_code": "climateInterpretation",
    "climate_intepretation_code": "climateInterpretation",
    "notes": "notes",
    "comments": "notes"
}
