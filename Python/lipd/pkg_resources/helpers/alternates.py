
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

FUNDING_LIST = [
    'funding_agency_name',
    'grant'
]

# Use this list to sort the top level keys in the LiPD file.
# Ex: if the LiPD has geo data, take the whole geo dictionary and put it into section 8.
# reorganize(), create_blanks()
NOAA_ALL = {
    "Top": ['Study_Name', 'Online_Resource', "Online_Resource_Description", 'Original_Source_URL', 'Archive',
            "Dataset_DOI", "Parameter_Keywords"],
    "Contribution_Date": ['Date'],
    "File_Last_Modified_Date": ["Modified_Date"],
    "Title": ['Study_Name'],
    "Investigators": ['Investigators'],
    "Description_Notes_and_Keywords": ['Description'],
    "Publication": ['Author', 'Published_Date_or_Year', 'Published_Title', 'Journal_Name', 'Volume', 'Edition',
                    'Issue', 'Pages', "Report", 'DOI', 'Online_Resource', 'Full_Citation', 'Abstract'],
    "Funding_Agency": ["Funding_Agency_Name", "Grant"],
    "Site_Information": ["Site_Name", "Location", "Country", "Northernmost_Latitude", "Southernmost_Latitude",
                          "Easternmost_Longitude",  "Westernmost_Longitude", "Elevation"],
    "Data_Collection": ['Collection_Name', 'Earliest_Year', 'Most_Recent_Year', 'Time_Unit', 'Core_Length', 'Notes'],
    "Species": ['Species_Name', 'Species_Code', "Common_Name"],
    "Chronology_Information": ['Chronology'],
    "Variables": ["shortname", "what", "material", "error", "units", "seasonality", "archive", "detail", "method", "dataType"],
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
NOAA_ALL_DICT = {
    "Top": {
        "studyName": "",
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
        "earliestYear": "Earliest_Year",
        "mostRecentYear": "Most_Recent_Year",
        "timeUnit": "Time_Unit",
        "coreLength": "Core_Length",
        "notes": "Notes"
    },
    "Species": {
        "speciesName": "Species_Name",
        "speciesCode": "Species_Code",
        "commonName": "Common_Name",
    },
    "Chronology_Information": {
        "chronology": "Chronology"
    },
    "Variables": {
        'description': 'what',
        'detail': 'detail',
        'dataType': 'dataType',
        'uncertainty': 'error',
        'units': 'units',
        'variableName': 'shortname',
        'measurementMaterial': 'material',
        'measurementMethod': 'method',
        'seasonality': 'seasonality',
    },
    "Data": {
        "missingValue": "Missing_Value"
    },
    # These are keys that do not currently have NOAA - LPD mappings
    "Ignore": {
        "date": "Date",
        "parameterKeywords": "Parameter_Keywords",
        "datasetName": "Dataset_Name",
        "treeSpeciesCode": "Tree_Species_Code",
        "speciesName": "Species_Name",
        "commonName": "Common_Name",
        "coreLength": "Core_Length",
        "timeUnit": "Time_Unit",
        "mostRecentYear": "Most_Recent_Year",
        "earliestYear": "Earliest_Year",
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

# LiPD on left, NOAA on right
# Used to map LiPD to NOAA ontology (and vice versa)
NOAA_KEYS = {
    # column 9-part-variables
    'description': 'what',
    'detail': 'detail',
    'dataType': 'dataType',
    'uncertainty': 'error',
    'units': 'units',
    'variableName': 'shortname',
    'measurementMaterial': 'material',
    'measurementMethod': 'method',
    'seasonality': 'seasonality',

    # all other sections
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
    "alternate citation": "citation",
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

# HEADER ROW for parsing excel worksheets
# excel_main()
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

