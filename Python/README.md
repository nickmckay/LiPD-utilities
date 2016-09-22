LiPD
========

Input/output and manipulation utilities for LiPD files in Matlab, R and Python.


What is it?
----

LiPD is short for Linked PaleoData. LiPD is the data standard for paleoclimatology and the exchange of data amongst paleoclimate experts. This package will help you convert your existing database of paleoclimate observations into LiPD files. Moreover, it contains tools to analyze and manipulate LiPD data.


Installation
------------

LiPD is a package containing multiple modules. Install globally on your system with:

```
pip install LiPD
```

Python v3.4+ is required


Usage
----------------

Using your preferred Python IDE or a Python console, you can import the LiPD package using:
```
import lipd
```
This import will trigger a prompt asking you to choose a source directory containing files.

Now you can call any function in the LiPD package.
```
lipd.loadLipds()
```
```
lipd.excel()
```
```
lipd.doi()
```

Starter files
------------

[Download ZIP file](https://dl.dropboxusercontent.com/s/azp3m2hggh0l0jr/lipd_starter_files.zip?dl=1)

The starter files will give you working examples to try out LiPD, as well as blank templates to insert your own data.

__Included:__
* NOAA blank template and example file
* Excel blank template and example file
* LiPD example file

Features
----

- Convert Excel files to LiPD files
- Convert NOAA files to LiPD files
- Convert LiPD files to NOAA files
- Load LiPD files for data analysis
- Extract TimeSeries

Jupyter Notebooks
----------------

A Jupyter Notebook is an instructional tool to show examples of python code and code output. We have created a set of Notebooks as guides to getting familiar with LiPD and its functions. These Notebooks can be found in the github repository as '.ipynb' files.

_Jupyter is not required to use the LiPD package._

Requirements
----
For a list of modules that are installed with this package, please refer to the file called REQUIREMENTS.


Further information
----------
Github:
https://github.com/nickmckay/LiPD-utilities

Linked Earth Wiki:
wiki.linked.earth

Jupyter:
www.jupyter.org


Contact
-------

If you are having issues, please let me know.
Contact me at heiser@nau.edu.


License
-------

The project is licensed under the GNU Public License. Please refer to the file called LICENSE.
