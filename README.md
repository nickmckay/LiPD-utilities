[![DOI](https://zenodo.org/badge/24036/nickmckay/LiPD-utilities.svg)](https://zenodo.org/badge/latestdoi/24036/nickmckay/LiPD-utilities)
[![PyPI](https://img.shields.io/pypi/dm/LiPD.svg?maxAge=2592000)](https://pypi.python.org/pypi/LiPD)
[![PyPI](https://img.shields.io/pypi/v/LiPD.svg?maxAge=2592000)]()
[![PyPI](https://img.shields.io/badge/python-3.4-yellow.svg)]()
[![license](https://img.shields.io/github/license/nickmckay/LiPD-utilities.svg?maxAge=2592000)]()

# LiPD Utilities

Input/output and manipulation utilities for LiPD files in
            Matlab, R and Python.

<!-- WHAT IS IT -->

### What is it?

LiPD is short for Linked PaleoData. LiPD files are the data standard for storing and exchanging data amongst paleoclimate scientists. The package will help you convert your existing paleoclimate observations into LiPD files that can be shared and analyzed.

Organizing and using your observation data can be time  consuming. Our goal is to let you focus on more important tasks  than data wrangling.

<!-- INSTALLATION -->

### Installation

**Python:**

Python v3.4+ is required

`pip install LiPD`


**R:**

Using the devtools package:

`devtools::install_github("nickmckay/LiPD-Utilities", subdir = "R")`


**Matlab:**

Use the "Clone or download" button on the [Github repository](https://github.com/nickmckay/LiPD-utilities) page to get a copy of the LiPD Utilities code on your computer. Note where the code is saved, and add the the path in you Matlab search path.

<!-- USAGE -->

## Usage

The functions below are considered the core functions of the LiPD package. These functions are consistent across the 3 languages. The function names, parameters and returned data is the same.

 `readLipd(path="")`

`writeLipd(data, path="")`

`extractTs(data, chron=False)`

`collapseTs(timeseries)`

`filterTs(timeseries, expression)`

`queryTs(timeseries, expression)`


<!-- SPECIFIC DOC LINKS -->

## Language-specific Documentation

The core functions are consistent across the 3 languages; However, each language has some nuances that you may be unfamiliar with. For example, in Python you may use `lipd.readLipd()`, whereas in R you use `lipd::readLipd()` or `readLipd()`. 

Additionally, while the core functions remain the same, we chose to take advantage of the strengths of each language. The Python utilities have additional functions for converting and validating data. The R and Matlab utilities are better suited for data analyzation.
The language-specific documentation linked below will go into detail about all the functions included in each language.

* [Python Docs](docs_py/index.html)

* R Docs (website coming soon, also available using the '??<function>' command in RStudio)

* Matlab Docs (coming soon)

<!-- FEATURES -->

## Features

*   Read & write LiPD files
*   Extract & collapse a time series for data analysis
*   Filter & query a time series for subset data
*   Convert Excel files to LiPD files (Python only)
*   Convert NOAA files to/from LiPD files (Python only)
*   Update LiPD publication data through DOI.org (Python only)
*   Validate LiPD files through lipd.net API (Python only)

<!-- EXAMPLES -->

## Example Files

* [Examples](https://github.com/nickmckay/LiPD-utilities/tree/master/Examples)

The examples folder contains blank templates and example files. Use the blank templates to insert your own data for conversion, or test out the package using some of the example files.

You'll also find a set of [Jupyter](http://jupyter.org) notebooks in the examples folder. Notebooks are used to show examples of python code and code output. Use these notebooks as a guide to getting familiar with LiPD Utilities and its functions.

<!-- REQUIREMENTS -->

## Requirements

**Python**

[Python 3.4+](https://www.python.org)

Python IDE (Spyder or PyCharm are highly recommended)

[pip](https://pip.pypa.io/en/stable/installing/)


**R**

[R language](https://cran.r-project.org)

[R Studio](https://www.rstudio.com)


**Matlab**

[Matlab](https://www.mathworks.com)

<!-- FURTHER INFORMATION -->

## Further information

[Github - LiPD-utilities](https://github.com/nickmckay/LiPD-utilities)

[Github - GeoChronR](https://github.com/nickmckay/GeoChronR)

[Linked Earth Wiki](http://wiki.linked.earth/Main_Page)

[Jupyter Documentation](www.jupyter.org)

## Contact

If you are having issues, please let me know at [heiser@nau.edu](mailto:heiser@nau.edu).

<!-- LICENSE -->

## License

The project is licensed under the [            GNU Public License](https://github.com/nickmckay/LiPD-utilities/blob/master/Python/LICENSE).

