# LiPD Utilities - R

[![DOI](https://zenodo.org/badge/23949/chrismheiser/lipdR.svg)](https://zenodo.org/badge/latestdoi/23949/chrismheiser/lipdR)
[![Github All Releases](https://img.shields.io/github/downloads/chrismheiser/lipdR/total.svg?maxAge=2592000)](https://github.com/chrismheiser/lipdR)
[![R](https://img.shields.io/badge/R-3.3.1-blue.svg)]()
[![R Studio](https://img.shields.io/badge/RStudio-0.99.903-yellow.svg)]()
[![license](https://img.shields.io/badge/license-GPL-brightgreen.svg)]()


Requirements
-------------

R, the language, is availalble from CRAN. R Studio is an IDE that will work using R and make your workflow much easier. We have developed the utilities using R version 3.3.1 and R Studio version 1.0.136. If you do not have any datasets in LiPD format yet, feel free to experiment with the one below. 

**R**

https://cran.r-project.org

 **R Studio**

 https://www.rstudio.com

**LiPD file**

[ODP1098B13.lpd](https://github.com/nickmckay/LiPD-utilities/raw/master/Examples/ODP1098B13.lpd)

Installing the packages
-------------
Create a new project in R Studio and start with a fresh workspace:

![Workspace](https://www.dropbox.com/s/1yt894ph4cosou3/1_fresh.png?raw=1)

Install 'devtools' in the console window:

    install.packages("devtools")

Load the 'devtools' package:

    library(devtools)

Use 'devtools' to install the LiPD Utilities package from github:

    install_github("nickmckay/LiPD-Utilities", subdir = "R")

Load the 'lipdR' package:

    library(lipdR)

And that's it! You have successfully installed the LiPD utilities and are ready to start working. Your console should now look similar to this:

![Installed](https://www.dropbox.com/s/dl45u3r4yheeqxh/1_installed.png?raw=1)


Core Functions
===============



**readLipd(path = "")**

---------

**Purpose:** 
Reads LiPD files from a source path into the environment. Read in a single file, or a directory of multiple files.

**Parameters:**
> **path** (optional)
> example: `L = readLipd("/Users/bobalice/Downloads/filename.lpd")`
> example: `D = readLipd("/Users/bobalice/Desktop")`
> example: ` D = readLipd()`
> 
> The path to the locally stored file or directory that you would like to read into the workspace
>



**Example 1: Read a single file without using a path** 

Leave the path empty in this example.  A prompt will ask you to choose to read a `single file` or a `directory`.  Choose `s` and read a single file:

![readlipd_single_prompt](https://www.dropbox.com/s/suv2u7egvsh24hn/1_readlipd_prompt.png?raw=1)

A browse dialog opens and asks you to choose the LiPD file that you want:

![readlipd_single_browse](https://www.dropbox.com/s/6lqrx075onpnzqp/2_readlipd_browse.png?raw=1)



The LiPD file will load into the workspace under variable `L` .  The environment variable allows you to preview some of the information in the LiPD data with the dropdown arrow.


![](https://www.dropbox.com/s/0h58wbl1ovk8rw8/3_readlipd_done.png?raw=1)


----------


**Example 2: Read a directory without using a path** 


----------