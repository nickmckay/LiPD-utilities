# LiPD Utilities - R

[![DOI](https://zenodo.org/badge/23949/chrismheiser/lipdR.svg)](https://zenodo.org/badge/latestdoi/23949/chrismheiser/lipdR)
[![R](https://img.shields.io/badge/R-3.3.1-blue.svg)]()
[![R Studio](https://img.shields.io/badge/RStudio-1.0.136-blue.svg)]()
[![license](https://img.shields.io/badge/license-GPL-brightgreen.svg)]()


Welcome to LiPD Utilities in R . This guide will provide everything you need to get up and running with the LiPD Utilities in R,  and show you how to use the core functions in the LiPD package. 


-----

## Requirements


R, the language, is availalble from CRAN. R Studio is an IDE that will work using R and make your workflow much easier. Software version numbers are listed at the top of this README file.  If you do not have any datasets in LiPD format yet, feel free to experiment with the one below. 

**R**

https://cran.r-project.org

 **R Studio**

 https://www.rstudio.com

**LiPD file**

[ODP1098B13.lpd](https://github.com/nickmckay/LiPD-utilities/raw/master/Examples/ODP1098B13.lpd)

-------------


## Installation

Create a new project in R Studio and start with a fresh workspace:

![Workspace](https://www.dropbox.com/s/wg2w9ag7hwi7knd/1_fresh.png?raw=1)

Install _devtools_ in the console window:
 
    install.packages("devtools")

Load the _devtools_ package:

    library(devtools)

Use _devtools_ to install the LiPD Utilities package from github:

    install_github("nickmckay/LiPD-Utilities", subdir = "R")

Load the _lipdR_ package:

    library(lipdR)

And that's it! You have successfully installed the LiPD utilities and are ready to start working. Your console should now look similar to this:

![Installed](https://www.dropbox.com/s/dl45u3r4yheeqxh/1_installed.png?raw=1)


## Core functions

> **Notation:**
>
>  This guide uses notation that may be new to you. In case you are unfamiliar with these terms, the list below provides an explanation for each. Please feel free to name your own variables as you move through the guide.
> 
> **D**
>
> Represents multiple datasets read into a single variable. Each dataset is organized by its dataset name.   `D[["ODP1098B13"]][["paleoData"]]`
>
>
> **L**
>
> Represents a single dataset. The dataset does not need to be organized by name.  `L[["paleoData"]]` 
> 
>
> **ts**
>
> A time series. The `ts` notation is used both in variable names and time series related functions, like `extractTs` 

-----

### **readLipd(path = "")**

**Purpose:** 
Reads LiPD files from a source path into the environment. Read in a single file, or a directory of multiple files.

**Parameters:**
> **path** (optional)
> 
> The path to the locally stored file or directory that you would like to read into the workspace
>
>Example: Provide a path to a file
>
> `L = readLipd("/Users/bobsmith/Downloads/filename.lpd")`
>
>Example: Provide a path to a directory
>
> `D = readLipd("/Users/bobsmith/Desktop")`
> 
> Example: Browse for file or directory
>
> ` D = readLipd()`

**Returns:**
> 
> **D**
> 
> Multiple datasets `D` or one dataset `L`
> 

**Example 1: Browse for file** 

Call `readLipd` as shown below:

![readlipd_browse_file_prompt](https://www.dropbox.com/s/suv2u7egvsh24hn/1_readlipd_prompt.png?raw=1)

Leave the path empty in this example.  A prompt will ask you to choose to read a `single file` or a `directory`.  Choose `s` and read a single file:

![readlipd_browse_file_dialog](https://www.dropbox.com/s/xcx36hjmjp3wot4/readlipd_1_browse_file.png?raw=1)

A browse dialog opens and asks you to choose the LiPD file that you want. Here, I have selected the file and clicked "Open":


![readlipd_browse_file_done](https://www.dropbox.com/s/5kpj0iz8cwn9wql/readlipd_1_done.png?raw=1)

The console shows the name of the current file being read. When the file is finished reading, the `>` indicator appears again and the process is finished. (shown on the left)

The LiPD file loads into the environment under variable `L` .  The environment `L` variable allows you to preview some of the LiPD data with the dropdown arrow (shown on the right).

![readlipd_browse_file_L](https://www.dropbox.com/s/tvnodp9ewiiatze/readlipd_1_L.png?raw=1)

A quick look at `L` shows that the data is at the root of the variable, as expected.


----------


**Example 2: Browse for directory** 

> **NOTE:**
>
> Reading a directory is most commonly used for reading multiple files. I have added LiPD files to my source folder and will load them into variable `D`.
> 

Call `readLipd` as shown below:

![readlipd_browse_dir_prompt](https://www.dropbox.com/s/suv2u7egvsh24hn/1_readlipd_prompt.png?raw=1)

Leave the path empty in this example.  A prompt will ask you to choose to read a `single file` or a `directory`.  Choose `d` and read a directory:

![readlipd_browse_dir_dialog](https://www.dropbox.com/s/bxndk6abu7a70rh/readlipd_2_browse_dir.png?raw=1)

> **NOTE:**
> 
> Due to a bug in R, we are not able to use the module for choosing a directory with the GUI. It causes R Studio to crash and that's not an experience we want to give you. The instructions below are a workaround that will provide the same result.  

A browse dialog opens. Please choose **any** LiPD file **within** the directory that you want. For example, I want to load all the LiPD files in the `quickstart` directory,  so I will choose the `ODP1098B13.lpd`. Choosing either of the other two LiPD files has the same outcome. 

![readlipd_browse_dir_done](https://www.dropbox.com/s/pxnkwnjzn3d594t/readlipd_2_done.png?raw=1)

The console shows that 3 files have been read, and processing is finished. 

The LiPD files load into the environment under variable `D`.  The `D` variable shows that it is a `list of 3`,  which matches the number of LiPD files in the source directory. Success!

![readlipd_browse_dir_D](https://www.dropbox.com/s/clgcdza7k3mpnw8/readlipd_2_D.png?raw=1)

A quick look at `D` shows that the datasets are sorted by dataset names, as expected. If you look one more level down, we can see the data.

![readlipd_browse_dir_D2](https://www.dropbox.com/s/gvoyijx44j6zisc/readlipd_2_D_2.png?raw=1)

> **REMEMBER**
> 
> Since `D` contains multiple datasets, we organize the data by `dataSetName`. Since `L` only holds one dataset, we do not use this `dataSetName` layer, and instead link directly to the data. 


**Example 3: Provide a path**

If you have the path to a specific file or directory that you would like to read, you can read in data in less steps. I'll use a path to a file on my desktop.

![readlipd_path_file](https://www.dropbox.com/s/tq20wfubnr4n3zy/readlipd_3_path_file.png?raw=1)

> **NOTE:**
> 
> Relative paths do not work in R. If the file you want to read is located in your 'current working directory' (use `getwd()`) then you can load it directly using the filename.
> 
> `readLipd("ODP1098B13.lpd")`
> 
> If a file is _not_ in your current working directory, then you must give an explicit path to the file.
> 
> `readLipd("/Users/bobsmith/Desktop/ODP1098B13.lpd")`
> _or_
> `readLipd("~/Desktop/ODP1098B13.lpd")`

----------


### **writeLipd(D,  path = "")**

**Purpose:** 
Writes LiPD data from the environment as a LiPD file. 

**Parameters:**
> **D**
> 
>  Multiple datasets `D` or one dataset `L`
>  ----
> **path** (optional)
> 
> The directory path that you would like to write the LiPD file(s) to. 
> 
>  Provide a destination directory path: 
>  
> `writeLipd(D, "/Users/bobsmith/Desktop")`
> 
> Or, omit the path to browse for a destination:
>
> `writeLipd(D)`

**Returns:**
> 
> This function does not return data
> 

Call `writeLipd` as shown below.  Pass your LiPD data. In this case, I pass `L` to the function, which represents one LiPD dataset. 
![writelipd_file_call](https://www.dropbox.com/s/8sr6dkwlx8swkdb/writelipd_1_call.png?raw=1)

![writelipd_file_choose](https://www.dropbox.com/s/6z0j99px5l9r4ta/writelipd_1_choose.png?raw=1)

A dialog opens and asks you to choose a directory.  Choose a file **within** the directory that you to write to. (Reference Example 2 for `readLipd` for further explanation)

![writelipd_file_done](https://www.dropbox.com/s/agh4cfnqcnmqmvh/writelipd_1_done.png?raw=1)

The console window will show each data file as it is compressed into the LiPD file being written. The list should contain four `.txt`,  _at least_ one `.csv` file, and one `.jsonld` file. 

---

### **extractTs(D)**

**Purpose:** 
Creates a time series from LiPD datasets.
[What is a time series?](#helptimeseries)

**Parameters:**
> 
> **D**
> 
>  Multiple datasets `D` or one dataset `L`
> 

**Returns:**
> 
> **ts**
> 
> A time series
> 

Call `extractTs` as shown below:

![extractts_call](https://www.dropbox.com/s/e2aebrn33u2v570/extractTs_start.png?raw=1)

The time series is created and placed in the `ts` variable. Click the arrow next to the `ts` variable in the environment to see the what the contents look like.  

![extractts_done](https://www.dropbox.com/s/27s93kgnnwnuj65/extractTs_finish.png?raw=1)


---

### **collapseTs(ts)**

**Purpose:** 
Collapse a time series back into LiPD datasets. This function is lossless and will return the data back to its original form. If you made and changes or edits to the time series,  they will persist. (This is the opposite function of `extractTs`)
[What is a time series?](#helptimeseries)


**Parameters:**
> **ts**
> 
>  A time series
> 

**Returns:**
> 
> **D**
> 
> Multiple datasets `D` or one dataset `L`
> 

Call `collapseTs` as shown below:

![collapsets_start](https://www.dropbox.com/s/jbxaoakv1bksblv/collapseTs_start.png?raw=1)

The goal of `collapseTs` is to recreate the same data (without losing anything) that you had _before_ calling `extractTs`. This is most useful if you have edited the time series in some way. 

![collapsets_done](https://www.dropbox.com/s/dj8ppdv8cbrcwt2/collapseTs_done.png?raw=1)

In this example, `L` represents your original dataset, `ts` represents the time series, and `L2` represents the new dataset.  Note how the number of elements, and the size of `L` and `L2` are equal.

![collapsets_expand](https://www.dropbox.com/s/dlhjnre66vkan47/collapseTs_expand.png?raw=1)

Expanding `L2` in the environment shows that the data has returned to the LiPD dataset hierarchy as before.

--- 

### **queryTs(ts, expression)**

**Purpose:** 
Find all the entries in a time series that match your specified criteria. For example, if you only want data located at a certain latitude, or if you only want data of a certain archive type.

[How are queryTs and filterTs different?](#helpqueryfilter)

**Parameters:**
> **ts**
> 
>  A time series
> 
> **expression**
> 
>  The criteria that you choose to find data. Only data that matches this expression will be returned.
> 

**Returns:**
> 
> **matches**
> 
> The  index numbers for all entries that match the expression. 
> 


For this example, I've read and created a time series using multiple datasets to emphasize the point of querying. All the steps are shown below:

![filterts_prestart](https://www.dropbox.com/s/chg23m4lc7qb7n4/filterTs_prestart.png?raw=1)

I'll use the expression `paleoData_variableName == d18O` to get the index numbers of  all time series entries that represent d18O measurements.

Call `queryTs` as shown below: 

![queryts_call](https://www.dropbox.com/s/ng62tmjmxxocsvl/queryTs_call.png?raw=1)

A list of index numbers is returned as `matches` and shows you all the entry numbers that match the `paleoData_variableName == d18O` expression. The `ts` time series variable has 9 entries, and 2 of those entries are `d18O` entries. Index number 1 and index number 3. 

![queryts_done](https://www.dropbox.com/s/sud31wot97si34p/queryTs_done.png?raw=1)


---

### **filterTs(ts, expression)**

**Purpose:** 
Create a new, smaller,  time series that only contains entries that match your specified criteria. For example, if you only want data located at a certain latitude, or if you only want data of a certain archive type.

[How are queryTs and filterTs different?](#helpqueryfilter)

**Parameters:**
> **ts**
> 
>  A time series
> 
> **expression**
> 
>  The criteria that you choose to find data. Only data that matches this expression will be returned.
> 

**Returns:**
> 
> **ts**
> 
> A time series
> 

For this example, I've read and created a time series using multiple datasets to emphasize the point of filtering. All the steps are shown below:

![filterts_prestart](https://www.dropbox.com/s/chg23m4lc7qb7n4/filterTs_prestart.png?raw=1)

> **NOTE:**
> There are many different criteria to search by, and it's quite lengthy to list them all. However, if you look at 
> the time series variable in your environment (`ts`), you'll be able to see the searchable terms. The image 
> below also shows a small sample of the `ts` variable that I'm using now. 

I'll use the expression `paleoData_variableName == d18O` to get all time series entries that represent d18O measurements.

Call `filterTs` as shown below: 

![filterts_call](https://www.dropbox.com/s/cjtx22whffi6yk8/filterTs_call.png?raw=1)

A new, filtered time series is created as `new_ts` and the original time series remains as `ts`. 

![filterts_done](https://www.dropbox.com/s/r08c58km4s816id/filterTs_done.png?raw=1)


----

## Help


### <a name="helptimeseries"></a>**What is a time series?**

A time series is a flattened set of data that makes data more approachable and is used to perform data analysis. The LiPD dataset hierarchy is great for organization and giving context to data, but can be more difficult to sift through to find relevant information since it can often go 10+ levels deep. 

**1-to-1 ratio**
1 time series entry = 1 measurement table column

Each entry within a time series is made from one column of data in a **measurement** table. It's important to note that this only pertains to measurement table data. All model data (ensemble, distribution, summary) are not included when creating a time series. 

**Example 1: One dataset**

 - ODP1098B13
	- 1 measurement table
		- 5 columns
			- depth,  depth1,  SST,  TEX86,  age

`extractTs` creates a time series (`ts`) of **5** entries

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
			
`extractTs` creates a time series (`ts`) of **9** entries


-----

### <a name="helpqueryfilter"></a>**How are queryTs and filterTs different?**

It's easy to confuse these two functions as they are almost identical in purpose. Here's what you need to know: 

`queryTs`: 

This function returns the **index numbers** of entries that match your expression.

`filterTs`:

This function returns the **actual data** of entries that match your expression. 