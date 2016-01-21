# ![LiPD Logo](https://www.dropbox.com/s/tnt1d10vwx4zlla/lipd_rm_trans.png?raw=1) LiPD

LiPD DOI Resolver
------

Use Digital Object Identifier (DOI) names to fetch the most current online data for your records and update your local copies.

Overview
------

###### Input
```
LiPD file (.lpd)
```

###### Output
```
LiPD file (.lpd)
```

###### Choosing a target directory

The target directory must be set in the "main_doi.py" file before running the program. This target directory must contain the LiPD files (.lpd) that you wish to update.

Example:
```
Directory Path
/User/Documents/Antarctica/lpd_files
```
Locate "main()" function in the "main_doi.py" file, and replace dir_root with your directory path.

Before:
```python
def main():

    # Enter user-chosen directory path
    dir_root = 'ENTER_DIRECTORY_PATH_HERE'

```
After:
```python
def main():

    # Enter user-chosen directory path
    dir_root = '/User/Documents/Antarctica/lpd_files'

```

Changelog
------
Version 1.0 / 12.08.2015 / Chris

Installation
------
Refer to master README_lipd.md for installation information.

Contributors
------
The LiPD team. More information on the LiPD project can be found on the [LiPD website](www.lipd.net).
