# LiPD Utilities - R

[![DOI](https://zenodo.org/badge/23949/chrismheiser/lipdR.svg)](https://zenodo.org/badge/latestdoi/23949/chrismheiser/lipdR)
[![R](https://img.shields.io/badge/R-3.3.1-blue.svg)]()
[![R Studio](https://img.shields.io/badge/RStudio-0.99.903-yellow.svg)]()
[![license](https://img.shields.io/badge/license-GPL-brightgreen.svg)]()


Welcome to LiPD Utilities in R . This guide will provide everything you need to get up and running with the LiPD Utilities in R,  and show you how to use the core functions in the LiPD package. 

## Table of contents

-----


[TOC]



## Requirements

-----

R, the language, is availalble from CRAN. R Studio is an IDE that will work using R and make your workflow much easier. We have developed the utilities using R version 3.3.1 and R Studio version 1.0.136. If you do not have any datasets in LiPD format yet, feel free to experiment with the one below. 

**R**

https://cran.r-project.org

 **R Studio**

 https://www.rstudio.com

**LiPD file**

[ODP1098B13.lpd](https://github.com/nickmckay/LiPD-utilities/raw/master/Examples/ODP1098B13.lpd)

## Installation

-------------
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
>
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



**Example 1: Browse for file** 

Start by calling `readLipd` as shown below.

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

Start by calling `readLipd` as shown below

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

----------


### **writeLipd(D,  path = "")**

---

### **extractTs(D)**

---

### **collapseTs(ts)**

---

### **queryTs(ts, expression)**

---

### **filterTs(ts, expression)**
