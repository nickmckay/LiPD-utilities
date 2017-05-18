
"""
GLOBAL LIST OF ALTERNATES AND SYNONYMS
"""

# LiPD Excel Template expects these types of data sheets
EXCEL_SHEET_TYPES = {
    "paleo": ["p", "paleo"],
    "chron": ["c", "chron"],
    "measurement": ["m", "meas", "measurement"],
    "ensemble": ["e", "ens", "ensemble"],
    "distribution": ["d", "dist", "distribution"],
    "summary": ["s", "sum", "summary"]
}

# LiPD Utilities currently supports the 4 file types listed below
FILE_TYPE_MAP = {
    ".xlsx": {"load_fn": "readExcel()", "file_type": "Excel"},
    ".xls": {"load_fn": "readExcel()", "file_type": "Excel"},
    ".txt": {"load_fn": "readNoaa()", "file_type": "NOAA"},
    ".lpd": {"load_fn": "readLipd()", "file_type": "LiPD"}
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


# FILTER
# Used to parse user expressions
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

# # NOAA: This does not include principal investigator or country.
# NOAA_FUNDING_LIST = [
#     'funding_agency_name',
#     'grant',
# ]

# Use this list to sort the top level keys in the LiPD file.
# Ex: if the LiPD has geo data, take the whole geo dictionary and put it into section 8.
# reorganize(), create_blanks()
NOAA_KEYS_BY_SECTION = {
    "Top": ["Study_Name", 'Online_Resource', "Online_Resource_Description", 'Original_Source_URL', 'Archive',
            "Dataset_DOI", "Parameter_Keywords"],
    "Contribution_Date": ['Date'],
    "File_Last_Modified_Date": ["Modified_Date"],
    "Title": ['Study_Name'],
    "Investigators": ['Investigators'],
    "Description_Notes_and_Keywords": ['Description'],
    "Publication": ['Authors', 'Published_Date_or_Year', 'Published_Title', 'Journal_Name', 'Volume', 'Edition',
                    'Issue', 'Pages', "Report", 'DOI', 'Online_Resource', 'Full_Citation', 'Abstract'],
    "Funding_Agency": ["Funding_Agency_Name", "Grant"],
    "Site_Information": ["Site_Name", "Location", "Country", "Northernmost_Latitude", "Southernmost_Latitude",
                          "Easternmost_Longitude",  "Westernmost_Longitude", "Elevation"],
    "Data_Collection": ['Collection_Name', 'Earliest_Year', 'Most_Recent_Year', 'Time_Unit', 'Core_Length', 'Notes'],
    "Species": ['Species_Name', 'Species_Code', "Common_Name"],
    "Chronology_Information": ['Chronology'],
    "Variables": ["shortname", "what", "material", "error", "units", "seasonality", "archive", "detail", "method",
                  "dataType", "additional"],
    "Data": ["Missing_Value"],
    # OTHERS. These are not sections, but they are important for parsing
    "Pub_Data_Citation": [""],
    # These are keys that do not currently have NOAA - LPD mappings
    "Ignore":
        ["Date", "Parameter_Keywords", "Dataset_Name", "Tree_Species_Code", "Species_Name", "Common_Name",
               "Core_Length", "Time_Unit", "Most_Recent_Year", "Earliest_Year", "Collection_Name",
               "Online_Resource_Description"]
}


# LPD to NOAA keys mapped according to NOAA sections.
LIPD_NOAA_MAP_BY_SECTION = {
    "Top": {
        "studyName": "Study_Name",
        'onlineResource': 'Online_Resource',
        "onlineResourceDescription": "Online_Resource_Description",
        "url": "Original_Source_URL",
        "dataUrl": "Original_Source_URL",
        "originalDataURL": "Original_Source_URL",
        'originalSourceURL': 'Original_Source_URL',
        "archiveType": "Archive",
        "datasetDOI": "Dataset_DOI",
        "parameterKeywords": "Parameter_Keywords"
    },
    "Contribution_Date": {
        "date": "Date",
    },
    "File_Last_Modified_Date": {
        "modifiedDate": "Modified_Date",
    },
    "Title": {
        'studyName': 'Study_Name',
    },
    "Investigators": {
        "investigators": "Investigators",
    },
    "Description_Notes_and_Keywords": {
        'notes': 'Description',

    },
    "Publication": {
        "url": "Online_Resource",
        "dataUrl": "Online_Resource",
        'pages': 'Pages',
        "pub": "Publication",
        'pubYear': 'Published_Date_or_Year',
        "year": "Published_Date_or_Year",
        'report': 'Report_Number',
        'title': 'Published_Title',
        'volume': 'Volume',
        'abstract': 'Abstract',
        "authors": "Authors",
        "author": "Authors",
        'identifier': 'DOI',
        'investigators': 'Investigators',
        'issue': 'Issue',
        "journal": "Journal_Name",
        "edition": "Edition",
        'citation': 'Full_Citation',
        'onlineResource': 'Online_Resource',
        "type": "Type",
    },
    "Funding_Agency": {
        'grant': 'Grant',
        "funding": "Funding_Agency",
        "agency": "Funding_Agency",
    },
    "Site_Information": {
        'country': 'Country',
        'siteName': 'Site_Name',
        "nLat": "Northernmost_Latitude",
        "sLat": "Southernmost_Latitude",
        "eLon": "Easternmost_Longitude",
        "wLon": "Westernmost_Longitude",
        "elevation": "Elevation",

    },
    "Data_Collection": {
        "collectionName": "Collection_Name",
        "minYear": "Earliest_Year",
        "maxYear": "Most_Recent_Year",
        "timeUnit": "Time_Unit",
        "coreLength": "Core_Length",
        "notes": "Notes"
    },
    "Species": {
        "sensorSpecies": "Species_Name",
        "sensorGenus": "Species_Code",
        "commonName": "Common_Name",
    },
    "Chronology_Information": {
        "chronology": "Chronology"
    },
    "Variables": {
        'description': 'what',
        'detail': 'detail',
        'dataType': 'dataType',
        'error': 'error',
        'units': 'units',
        'variableName': 'shortname',
        'measurementMaterial': 'material',
        'measurementMethod': 'method',
        'seasonality': 'seasonality',
        "notes": "notes",
        "additional": "additional"
    },
    "Data": {
        "missingValue": "Missing_Value"
    },
    # These are keys that do not currently have NOAA - LPD mappings
    "Ignore": {
        "date": "Date",
        "parameterKeywords": "Parameter_Keywords",
        "datasetName": "Dataset_Name",
        "speciesName": "Species_Name",
        "commonName": "Common_Name",
        "coreLength": "Core_Length",
        "collectionName": "Collection_Name",
        "onlineResourceDescription": "Online_Resource_Description"
    }
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

# LiPD terms on left, NOAA terms on right
# Used to map LiPD to NOAA ontology (and vice versa)
LIPD_NOAA_MAP_FLAT = {
    # column 9-part-variables
    'description': 'what',
    'detail': 'detail',
    'dataType': 'dataType',
    'uncertainty': 'uncertainty',
    "error": "error",
    'units': 'units',
    'variableName': 'shortname',
    'measurementMaterial': 'material',
    'measurementMethod': 'method',
    'seasonality': 'seasonality',
    "notes": "notes",

    # all other sections
    "minYear": "Earliest_Year",
    "maxYear": "Most_Recent_Year",
    "timeUnit": "Time_Unit",
    'datasetDOI': "Dataset_DOI",
    'LiPDVersion': 'LiPD_Version',
    'abstract': 'Abstract',
    'agency': 'Funding_Agency_Name',
    'archiveType': 'Archive',
    'authors': 'Authors',
    'citation': 'Full_Citation',
    'country': 'Country',
    "funding": "Funding_Agency",
    "geo": "Site_Information",
    'grant': 'Grant',
    'identifier': 'DOI',
    'investigator': 'Investigators',
    'investigators': 'Investigators',
    'issue': 'Issue',
    'journal': 'Journal_Name',
    'location': 'Location',
    'missingValue': 'Missing_Values',
    'notes': 'Description',
    'onlineResource': 'Online_Resource',
    "url": "Original_Source_URL",
    "originalDataURL": "Original_Source_URL",
    'originalSourceURL': 'Original_Source_URL',
    'pages': 'Pages',
    "pub": "Publication",
    'pubYear': 'Published_Date_or_Year',
    "year": "Published_Date_or_Year",
    'report': 'Report_Number',
    'siteName': 'Site_Name',
    'studyName': 'Study_Name',
    'title': 'Published_Title',
    'volume': 'Volume',

    ########################
    # MULTIPOINT
    # Since coordinates are not explicit individual fields in LiPD, we'll have to manually transfer these.
    # coordinates[0]: "Northernmost_Latitude",
    # coordinates[0]: "Southernmost_Latitude",
    # coordinates[1]: "Easternmost_Longitude",
    # coordinates[1]: "Westernmost_Longitude",
    # coordinates[2]: "Elevation", (OPTIONAL)
    ########################
    # SINGLE POINT
    # coordinates[0]: "Northernmost_Latitude",
    # coordinates[0]: "Southernmost_Latitude",
    # coordinates[1]: "Easternmost_Longitude",
    # coordinates[1]: "Westernmost_Longitude",
    # coordinates[2]: "Elevation", (OPTIONAL)
    ########################
    # "doi": pub[i]["identifier"][0]["id"]
}

# Excel on left, LiPD on right
# excel_main()
EXCEL_LIPD_MAP_FLAT = {
    "agency": "agency",
    "archive type": "archiveType",
    "archiveType": "archiveType",
    "authors": "author",
    "about": "about",
    "abstract": "abstract",
    "alternate citation": "citation",
    "archive": "archiveType",
    "basis of climate relation": "basis",
    "comments": "notes",
    "climate_interpretation_code": "climateInterpretation",
    "climate_intepretation_code": "climateInterpretation",
    "chronology": "chronology",
    "country": "country",
    "dataUrl": "dataUrl",
    "doi": "id",
    "description": "description",
    "dataset name": "dataSetName",
    "data (qc)": "dataQC",
    "data(qc)": "dataQC",
    "data (original)": "dataOriginal",
    "data(original)": "dataOriginal",
    "data": "data",
    "detail": "detail",
    "data_type": "dataType",
    "elevation": "elevation",
    "error": "error",
    "easternmost longitude": "lonMax",
    "grant": "grant",
    "investigators": "investigators",
    "issue": "issue",
    "journal": "journal",
    "link": "link",
    "metadata": "metadata",
    "method": "method",
    "material": "measurementMaterial",
    "notes": "notes",
    "northernmost latitude": "latMax",
    "pages": "pages",
    "proxyList": "proxy",
    "proxy": "proxy",
    "principal_investigator": "principalInvestigator",
    "publication title": "title",
    "report number": "reportNumber",
    "seasonality": "seasonality",
    "study title": "studyName",
    "short_name": "variableName",
    "site name": "siteName",
    "southernmost latitude": "latMin",
    "variablename": "variableName",
    "volume": "volume",
    "what": "description",
    "westernmost longitude": "lonMin",
    "year": "year",
    "units": "units",
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

# HEADER ROW for parsing excel worksheets
# excel_main()
EXCEL_HEADER = [
    "variablename",
    "variableType",
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
    "basis_of_climate_relation",
    "OnProxyObservationProperty",
    "OnInferredVariableProperty",
    "takenatdepth",
    "InferredFrom",
    "notes",
    "sensorGenus",
    "sensorSpecies",
    "archiveGenus",
    "archiveSpecies"


]

