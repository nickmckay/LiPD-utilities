#' #!/usr/bin/env python3
#' # -*- coding: utf-8 -*-
#' 
#' #' Created on Fri Mar 30 09:25:09 2018
#' #' 
#' #' @author: deborahkhider
#' #' @author: chrisheiser
#' #' 
#' #' Script to batch download LiPD files from the wiki after query
#' #' Written in Python by Deborah, adapted to R by Chris
#' 
#' 
#' # 1. Query the wiki (note this is taken directly from the Jupyter Notebook on
#' # GitHub) The query can be changed but doesn't matter in the grand scheme.
#' import json
#' import requests
#' import sys                    
#' 
#' #%% 1.1 Query terms
#' 
#' # By archive
#' archiveType = ["marine sediment","Marine Sediment"]
#' 
#' # By variable
#' proxyObsType = ["Mg/Ca", "Mg Ca"]
#' infVarType = ["Sea Surface Temperature"]
#' 
#' # By sensor
#' sensorGenus=["Globigerinoides"]
#' sensorSpecies=["ruber"]
#' 
#' # By interpretation
#' interpName =["temperature", "Temperature"]
#' interpDetail =["sea surface"]
#' 
#' # By Age
#' ageUnits = ["yr BP"]
#' ageBound = [3000,6000] #Must enter minimum and maximum age search
#' ageBoundType = ["entirely"] # Other values include "any", "entire"
#' recordLength = [1500]
#' 
#' # By resolution
#' #Make sure the resolution makes sense with the age units
#' # Will look for records with a max resolution of number entered
#' resolution = [100]
#' 
#' #By location
#' #Enter latitude boundaries below.
#' #If searching for entire latitude band, leave blank.
#' #Otherwise, enter both lower and upper bonds!!!!
#' #Enter south latitude as negative numbers
#' lat = [-30, 30]
#' 
#' #Enter Longitude boundaries below
#' # If searching for entire longitude band, leave blank
#' # Otherhwise, enter both lower and upper bonds!!!!
#' # Enter west longitude as negative numbers
#' lon = [100,160]
#' 
#' # Enter altitude boundaries below
#' # If not searching for specific altitude, leave blank
#' # Otherwise, enter both lower and upper bonds!!!!
#' # Enter depth in the ocean as negative numbers
#' # All altitudes on the wiki are in m!
#' alt = [-10000,0]