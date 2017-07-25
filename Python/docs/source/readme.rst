LiPD
====

Input/output and manipulation utilities for LiPD files in Matlab, R and
Python.

What is it?
-----------

LiPD is short for Linked PaleoData. LiPD is the data standard for
paleoclimatology and the exchange of data amongst paleoclimate experts.
This package will help you convert your existing database of
paleoclimate observations into LiPD files. Moreover, it contains tools
to analyze and manipulate LiPD data.

Installation
------------

LiPD is a package containing multiple modules. Install globally on your
system with:

::

    pip install LiPD

Python v3.4+ is required

Usage
-----

Using your preferred Python IDE or a Python console, you can import the
LiPD package using:

::

    import lipd

Now you can call any function in the LiPD package.

::

    lipd.readLipds()

::

    lipd.excel()

::

    lipd.doi()

Getting started
---------------

Examples and guides are located on the github at:

https://github.com/nickmckay/LiPD-utilities/tree/master/Examples

Features
--------

-  Convert Excel –> LiPD
-  Convert NOAA <–> LiPD
-  Read LiPD file for data analysis
-  Write LiPD file
-  Extract/collapse/filter/query on a time series

Requirements
------------

For a list of modules that are installed with this package, please refer
to the file called REQUIREMENTS.

Further information
-------------------

Github: https://github.com/nickmckay/LiPD-utilities

Linked Earth Wiki: wiki.linked.earth

Contact
-------

If you are having issues, please let me know. Contact me at
heiser@nau.edu.

License
-------

The project is licensed under the GNU Public License. Please refer to
the file called LICENSE.