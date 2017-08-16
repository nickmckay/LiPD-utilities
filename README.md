![](https://www.dropbox.com/s/kgeyec2b8cft5mo/lipd4.png?raw=1)


Input/output and manipulation utilities for LiPD files in Matlab, R and Python.

-----

### What is it?

LiPD is short for Linked PaleoData. LiPD files are the data standard for storing and exchanging data amongst paleoclimate scientists. The package will help you convert your existing paleoclimate observations into LiPD files that can be shared and analyzed.

Organizing and using your observation data can be time  consuming. Our goal is to let you focus on more important tasks  than data wrangling.


--------

## Core functions

The functions below are considered the core functions of the LiPD package. These functions are consistent in Matlab, Python, and R. The function names, parameters and returned data is the same.

### LiPD I/O functions
Getting LiPD data in and out of the stored files is the most important part! These are the two functions that allow that to happen. 

#### readLipd

Read LiPD files from your computer into your workspace

#### writeLipd

Write LiPD data from your workspace onto your computer.

### Time series functions

[What is a time series?](something)
The FAQ explains what a time series is. Once you have a basic understanding of a time series, the functions below will be much more relevant!

#### extractTs

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

## Example Files

* [Examples](https://github.com/nickmckay/LiPD-utilities/tree/master/Examples)

The examples folder contains blank templates and example files. Use the blank templates to insert your own data for conversion, or test out the package using some of the example files.

------

## Further information

[Github - GeoChronR](https://github.com/nickmckay/GeoChronR)

[Linked Earth Wiki](http://wiki.linked.earth/Main_Page)

------

## Contact

If you are having issues, please let me know at [heiser@nau.edu](mailto:heiser@nau.edu).


------


## License

The project is licensed under the [GNU Public License](https://github.com/nickmckay/LiPD-utilities/blob/master/Python/LICENSE).
