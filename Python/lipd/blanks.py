
"""
List of empty and ignored keys
"""

# GENERAL
EMPTY = ['', ' ', None, 'na', 'n/a', '?', "'", "''"]

# NOAA
NOAA_EMPTY = ['\n', '', '#\n', '# \n', ' ']
NOAA_KEYS = ['earliest_year', 'most_recent_year', 'note']
NOAA_VAR_LINES = [
    'have no #',
    'variables',
    'lines begin with #',
    'double marker',
    'line variables format',
    'line format',
    'c or n for character or numeric',
    'preceded by'
]
NOAA_DATA_LINES = [
    'have no #',
    'tab-delimited text',
    'age ensembles archived'
]
