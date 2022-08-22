<h1 align="left">
  <br>
  <a href="http://www.lipd.net"><img src="https://www.dropbox.com/s/kgeyec2b8cft5mo/lipd4.png?raw=1" alt="LiPD" width="225"></a>
</h1>

<p align="left">
  <a href="http://doi.org/10.5281/zenodo.60813"><img src="https://zenodo.org/badge/24036/nickmckay/LiPD-utilities.svg"></a>
  <a href="https://img.shields.io/badge/python-3.4-blue.svg"><img src="https://img.shields.io/badge/python-3.4-blue.svg"></a>
    <a href="https://img.shields.io/badge/matlab-R2017a-red.svg"><img src="https://img.shields.io/badge/matlab-R2017a-red.svg"></a>
      <a href="https://img.shields.io/badge/R-3.3.1-yellow.svg"><img src="https://img.shields.io/badge/R-3.3.1-yellow.svg"></a>
      <a href="https://img.shields.io/badge/license-GPL-brightgreen.svg"><img src="https://img.shields.io/badge/license-GPL-brightgreen.svg"></a>
</p>

# Update

The R package hosted here is now deprecated, but do not fear! **A significantly updated version is available at [http:/github.com/nickmckay/lipdR](http:/github.com/nickmckay/lipdR) and the [documentation is available here](https://nickmckay.github.io/lipdR/)**.

The python package is also in the process of being replaced with a more modern architecture.

## Lipd utitilities

Input/output and manipulation utilities for LiPD files in Matlab, R and Python.

-----

### What is it?

LiPD is short for Linked PaleoData. LiPD files are the data standard for storing and exchanging data amongst paleoclimate scientists. The package will help you convert your existing paleoclimate observations into LiPD files that can be shared and analyzed.

Organizing and using your observation data can be time  consuming. Our goal is to let you focus on more important tasks  than data wrangling.


--------

## Core functions

The functions below are considered the core functions of the LiPD package. These functions are consistent in Matlab, Python, and R. The function names, parameters and returned data are the same.

### readLipd

Read LiPD files from your computer into your workspace

### writeLipd

Write LiPD data from your workspace onto your computer.


### extractTs

Extract a time series from one or more datasets in the workspace. Your hierarchical LiPD data structure is extracted into a flattened time series structure.

### collapseTs

Collapse a time series back into LiPD dataset form in the workspace. Your flattened time series structure is condensed back into a hierarchical LiPD data structure

### filterTs

Retrieve **time series objects** that match a specific criteria. This filters out the data that you don't want, and returns a **new time series** of data that you do want.

### queryTs

Retrieve the **index numbers** of time series objects that match a specific criteria. This filters out the data that you don't want, and returns a list of **index numbers** of the data that you do want. 

------

## Language-specific Documentation

The core functions are consistent across the 3 languages; However, each language has some nuances that you may be unfamiliar with. For example, in Python you may use `lipd.readLipd()`, whereas in R you use `lipd::readLipd()` or `readLipd()`. 

Additionally, while the core functions remain the same, we chose to take advantage of the strengths of each language. The Python utilities have additional functions for converting and validating data. The R and Matlab utilities are better suited for data analyzation.
The language-specific documentation linked below will go into detail about all the functions included in each language.

* [Python Docs](http://nickmckay.github.io/LiPD-utilities/python/index.html)

* [R Docs](http://nickmckay.github.io/LiPD-utilities/r/index.html)

* [Matlab Docs](http://nickmckay.github.io/LiPD-utilities/matlab/index.html)

------

## FAQ


### What is a time series?

The LiPD dataset hierarchy is great for organization and giving context to data, but can be more difficult to sift through to find relevant information since it can often go 10+ levels deep. 

A time series is a flattened set of data that makes data more approachable and is used to perform data analysis. A time series is a collection of _time series objects_.

**1-to-1 ratio**
1 time series object = 1 measurement table column

Each _object_ within a time series is made from one column of data in a **measurement** table. It's important to note that this only pertains to measurement table data. All model data (ensemble, distribution, summary) are not included when creating a time series. 

**Example 1: One dataset**

 - ODP1098B13
	- 1 measurement table
		- 5 columns
			- depth,  depth1,  SST,  TEX86,  age

`extractTs` creates a time series (`ts`) of **5** objects

**Example 2: Multiple datasets**

 - `ODP1098B13`
	- 1 measurement table
		- 5 columns
			- depth,  depth1,  SST,  TEX86,  age
			
 - `Ant-CoastalDML.Thamban.2006`
	- 1 measurement table
		- 2 columns
			- d18O, year

 - `CO00COKY`
	- 1 measurement table
		- 2 columns
			- d18O, year
			
`extractTs` creates a time series (`ts`) of **9** objects


------


## How to Cite this code

  <a href="http://doi.org/10.5281/zenodo.60813"><img src="https://zenodo.org/badge/24036/nickmckay/LiPD-utilities.svg"></a>

Use this link to visit the Zenodo website. It provides citation information in many popular formats.

------

## Further information

[Github - GeoChronR](https://github.com/nickmckay/GeoChronR)

[Linked Earth Wiki](http://wiki.linked.earth/Main_Page)

[LiPD.net](http://www.lipd.net)

------

## Contact

If you are having issues, please let me know at [heiser@nau.edu](mailto:heiser@nau.edu).


------


## License

The project is licensed under the [GNU Public License](https://github.com/nickmckay/LiPD-utilities/blob/master/Python/LICENSE).

![footer NSF](assets/logo_nsf.png)
