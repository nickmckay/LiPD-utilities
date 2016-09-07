
"""
GLOBAL LIST OF ALTERNATES AND SYNONYMS
"""

SHEETS = {
    "paleo": ["p", "paleo"],
    "chron": ["c", "chron"],
    "measurement": ["m", "meas", "measurement"],
    "ensemble": ["e", "ens", "ensemble"],
    "distribution": ["d", "dist", "distribution"],
    "summary": ["s", "sum", "summary"]
}

# TABLES
DATA_FRAMES = [
    "chron",
    "paleo",
    "ensemble",
    "calibratedage",
    "distribution",
    "model",
    "table",
    "measurement"
]

# Allowable int and float fields
NUMERIC_INTS = [
    "maxYear",
    "minYear",
    "pubYear",
    "number",
    "year",
    "age14c",
    "sd14c"
]

NUMERIC_FLOATS = [
    "LiPDVersion",
    "coordinates",
    "depth"
]

# FILTER
COMPARISONS = {
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
    "elevation",
    "siteName"
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
    11: ['chronData'],
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
    6: ['author',
        'publishedDateOrYear',
        'publishedTitle',
        'journalName',
        'volume',
        'edition',
        'issue',
        'pages',
        "reportNumber",
        'doi',
        'onlineResource',
        'fullCitation',
        'abstract'
        ],
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
    11: ["variableName",
         "variableType",
         "measurementMaterial",
         "uncertainty",
         "units",
         "seasonality",
         "archive",
         "detail",
         "measurementMethod",
         "dataType"
         ]
}

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

# These keys do not have a corresponding match in the LiPD schema. Do not include them.
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

# Excel metadata keys. Left side: Excel keys, Right Side: LiPD keys
EXCEL_KEYS = {
    "archive type": "archiveType",
    "dataset name": "dataSetName",
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
    "variablename": "variableName",
    "description": "description",
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

EXCEL_TEMPLATE = [
    "data",
    "chronology table containing measured depths and ages",
    "chronology table as paragraph (insert table into cell b3) not preferred",
    "chronology table (use as many rows and columns are needed below this line)",
    "note: additional chronology tables should be put below the first one with no blank lines.",
    "variables",
    "use one row to define each variable, beginning with depth then age; add additional worksheets for additional tables",
    "note: data_type is 'n' for numeric and 'c' for character data",
    "paste data table below starting in column a",
    "the value or character string used as a placeholder for missing values",
    "<missing value>",
    "<notes that describe the table as a whole>"
]

EXCEL_HEADER = [
    "variablename",
    "short_name",
    "what",
    "material",
    "error",
    "units",
    "seasonality",
    "archive",
    "detail",
    "method",
    "data_type",
    "uncertainty_level",
    "calibration_curve",
    "climate_interpretation_code",
    "standard",
    "basis_of_climate_relation"
]