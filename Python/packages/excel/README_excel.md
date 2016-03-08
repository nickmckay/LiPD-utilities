# ![LiPD Logo](https://www.dropbox.com/s/tnt1d10vwx4zlla/lipd_rm_trans.png?raw=1) LiPD

Excel to LiPD Converter
------

Use XLRD python package to parse Excel spreadsheet data and convert it to the LiPD structure.

Overview
------

###### Input
```
Excel spreadsheet (.xlsx)
```

###### Output
```
LiPD file (.lpd) and Comma Separated Value file (.csv)
* One CSV is created for each data sheet in the Excel spreadsheet
```

###### Choosing a target directory

The target directory must be set in the "main_excel.py" file before running the program. This target directory must contain the Excel spreadsheet files (.xlsx) that you wish to convert.

Example:
```
Directory Path
/User/Documents/Antarctica/excel_files
```
Locate "main()" function in the "main_excel.py" file, and replace dir_root with your directory path.

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
    dir_root = '/User/Documents/Antarctica/excel_files'
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
