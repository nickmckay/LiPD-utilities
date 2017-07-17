###############################################
## Versions
## Updates the incoming LiPD to the most recent
## LiPD standards
###############################################


#' Add createdBy key to metdata
#' @export
#' @keywords internal
#' @param list d: Metadata
#' @return list d: Metadata
add_created_by <- function(d){
  if(!("createdBy" %in% names(d))){
    d[["createdBy"]] <- "unknown"
  }
  return(d)
}

#' Check what version of LiPD this file is using. If none is found, assume it's using version 1.0
#' @export
#' @keywords internal
#' @param list d: Metadata
#' @return numeric version: Version number
get_lipd_version <- function(d){
  version <- NULL
  keys <- c("lipdVersion", "liPDVersion", "LiPDVersion")
  for (i in 1:length(keys)){
    key <- keys[[i]]
    if (key %in% names(d)){
      version <- d[[key]]
      d[[key]] <- NULL
      print(paste0("Version key: ", key, " Version number: ", version))
    }
  }
  version <- as.numeric(version)
  if (isNullOb(version) || is.na(version)){
    # Since R does not yet do all the version 1.3 changes, we have to assume 1.2 for now.
    version <- 1.0
  }
  else if (!(version %in% c(1, 1.0, 1.1, 1.2, 1.3))){
    print(sprintf("LiPD version is invalid: %s", version))
  }
  return(version)
}


#' Use the current version number to determine where to start updating from. Use "chain versioning" to make it
#' modular. If a file is a few versions behind, convert to EACH version until reaching current. If a file is one
#' version behind, it will only convert once to the newest.
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Metadata
update_lipd_version <- function(d){
  # Get the lipd version number.
  version <- get_lipd_version(d)
  
  # Update from (N/A or 1.0) to 1.1
  if (version == 1.0 || version == "1.0"){
    print("Updating to version 1.1")
    d = update_lipd_v1_1(d)
    version <- 1.1
  }
    
    # Update from 1.1 to 1.2
    if (version == 1.1 || version == "1.1"){
      print("Updating to version 1.2")
      d = update_lipd_v1_2(d)
      version = 1.2
    }
    
    # Update from 1.2 to 1.3
    if(version == 1.2 || version == "1.2"){
      print("Updating to version 1.3")
      d = update_lipd_v1_3(d)
      version = 1.3
    }
    return(d)
}


#' Update LiPD v1.0 to v1.1
#' - chronData entry is a list that allows multiple tables
#' - paleoData entry is a list that allows multiple tables
#' - chronData now allows measurement, model, summary, ensemble, calibratedAges tables
#' - Added 'lipdVersion' key
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Metadata
update_lipd_v1_1 <- function(d){
  # Cannot v1.0 files, and I'm pretty sure there are less than 5 files in existence. 
  return(d)
}

#' Update LiPD v1.1 to v1.2
#' - Added NOAA compatible keys : maxYear, minYear, originalDataURL, WDCPaleoURL, etc
#' - 'calibratedAges' key is now 'distribution' (handled in update_lipd_v1_3_keys instead)
#' - paleoData structure mirrors chronData. Allows measurement, model, summary, ensemble,
#'   distribution tables
#' @export
#' @keywords internal
#' @param list d: Metadata
#' @return list d: Metadata
update_lipd_v1_2 <- function(d){
  if("paleoData" %in% names(d)){
    d <- update_lipd_v1_2_section()
  }
  if("chronData" %in% names(d)){
    d <- update_lipd_v1_2_section(d, pc)
  }
}

#' Update LiPD v1.1 to v1.2 - one section
#' @export
#' @keywords internal
#' @param list d: Metadata
#' @param char pc: paleoData or chronData
#' @return list d: Metadata
update_lipd_v1_2_section <- function(d, pc){
  if(!isNullOb(d[[pc]])){
    # Create the structure that we want. 
    tmp <- list()
    tmp[["measurementTable"]] <- list()
    # Append the existing tables as mesurement tables in the new structure
    for(i in 1:length(d[[pc]])){
      tmp[["measurementTable"]][[i]] <- d[[pc]][[i]]
    }
    # Overwrite the old structure with the new structure
    d[[pc]] <- list()
    d[[pc]][[1]] <- tmp
  }
  return(d)
}

#' Update LiPD v1.2 to v1.3
#' - Added 'createdBy' key
#' - Top-level folder inside LiPD archives are named "bag". (No longer <datasetname>)
#' - .jsonld file is now generically named 'metadata.jsonld' (No longer <datasetname>.lpd )
#' - All "paleo" and "chron" prefixes are removed from "paleoMeasurementTable", "paleoModel", etc.
#' - Merge isotopeInterpretation and climateInterpretation into "interpretation" block
#' - ensemble table entry is a list that allows multiple tables
#' - summary table entry is a list that allows multiple tables
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Metadata
update_lipd_v1_3 <- function(d){
  # TODO  need to write the merge_interpretation function
  d <- update_lipd_v1_3_keys(d)
  d <- update_lipd_v1_3_structure(d)
  d <- add_created_by(d)
  return(d)
}

#' Update v1.2 keys to v1.3 keys: recursive
#' @export
#' @keywords internal
#' @param list d: Metadata
#' @return list d: Metadata
update_lipd_v1_3_keys <- function(d){
  v12keys <- c("paleoMeasurementTable", "chronMeasurementTable", "paleoModel", "chronModel", "paleoDataMD5", "chronDataMD5", "paleoEnsembleMD5",  
               "chronEnsembleMD5", "paleoEnsembleTableMD5", "chronEnsembleTableMD5", "paleoMeasurementTableMD5", "chronMeasurementTableMD5", "name",
               "calibratedAges")
  v13keys <- c("measurementTable", "measurementTable", "model", "model", "dataMD5", "dataMD5", "tableMD5", "tableMD5", "tableMD5", "tableMD5",
               "tableMD5", "tableMD5", "tableName", "distributionTable")
  v13keymap <- setNames(as.list(v13keys), v12keys)
  v12keys_rm <- c("chronTableName", "paleoTableName", "paleoDataTableName", "chronDataTableName",
                  "chronMeasurementTableName", "paleoMeasurementTableName")
  
  # Keys that are in this list
  keys <- names(d)
  
  # For any lists that are indexed by name 
  if(!isNullOb(keys) && !is.na(keys)){
    for(i in 1:length(keys)){
      old_key <- keys[[i]]
      # Dive down first
      if(typeof(d[[old_key]]) == "list"){
        d[[old_key]] <- update_lipd_v1_3_keys(d[[old_key]])
      } 
      # When you bubble back up, then check if this key should be switched
      if(old_key %in% v12keys){
        # Set the old
        new_key <- v13keymap[[old_key]]
        d[[new_key]] <- d[[old_key]]
        # Remove the old key
        d[[old_key]] <- NULL
      } else if(old_key %in% v12keys_rm){
        d[[old_key]] <- NULL
      }
    }
  } else {
    # For any lists that are indexed by number
    if(typeof(d)=="list"){
      for(i in 1:length(d)){
        tryCatch({
          d[[i]] <- update_lipd_v1_3_keys(d[[i]])
        }, error=function(cond){
          print(paste0("Error: update_lipd_v1_3_keys: ", cond))
        })
      }
    }
  }
  return(d)
}

#' Update the structure for summary and ensemble tables
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Metadata
update_lipd_v1_3_structure <- function(d){
  
  # Tables that need changing
  change <- c("ensembleTable", "summaryTable")
  
  # Keys in this data
  keys <- names(d)
  
  # For any lists that are indexed by name 
  if(!isNullOb(keys) && !is.na(keys)){
    for(i in 1:length(keys)){
      curr_key <- keys[[i]]
      # Dive down first
      if(typeof(d[[curr_key]]) == "list"){
        d[[curr_key]] <- update_lipd_v1_3_structure(d[[curr_key]])
      } 
      # When you bubble back up, then check if this key should be switched
      if(curr_key %in% change){
        # Found a table. Do the 'ol switcheroo
        tmp <- d[[curr_key]]
        d[[curr_key]] <- list()
        d[[curr_key]][[1]] <- tmp
      }
    }
  } else {
    # For any lists that are indexed by number
    if(typeof(d)=="list"){
      for(i in 1:length(d)){
        tryCatch({
          d[[i]] <- update_lipd_v1_3_structure(d[[i]])
        }, error=function(cond){
          print(paste0("Error: update_lipd_v1_3_structure: ", cond))
        })
      }
    }
  }
  return(d)
}


# DEPRECATED CODE

#' #' Convert LiPD version structure whenever necessary
#' #' @export
#' #' @keywords internal
#' #' @param d Metadata
#' #' @return d Metadata
#' convertVersion <- function(d){
#'   # Check which version this LiPD file is
#'   d <- check_version(d)
#'   # check and convert any data frames into lists
#'   d <- convert_dataframes_list(d)
#'   return(d)
#' }
#' 
#' #' Check / convert and fixed data frames into scalable lists
#' #' @export
#' #' @keywords internal
#' #' @param d LiPD metadata
#' #' @return d Modified LiPD metadata
#' convert_dataframes_list <- function(d){
#'   # convert single entries to lists. matching structure to 1.2
#'   d <- convert_single_multiple(d, "paleoData")
#'   d <- convert_single_multiple(d, "chronData")
#' 
#'   return(d)
#' }
#' 
#' #' Convert from a single fixed table, to a multiple scalable table
#' #' (LiPD Verison 1.1 to 1.2 change)
#' #' @export
#' #' @keywords internal
#' #' @param d LiPD metadata
#' #' @return d Modified LiPD metadata
#' convert_single_multiple <- function(d, pc){
#' 
#'   # data frame?
#'   dat <- hasData(d, pc)
#' 
#'   # proceed of section exists
#'   if (!is.null(dat)){
#' 
#'     if (is.data.frame(dat)){
#'       d[[pc]] <- list()
#'       d[[pc]][[1]] <- as.list(dat)
#'     }
#'     # multiples?
#'     dat <- hasData(d[[pc]], 1)
#'     # convert to multiples
#'     if (is.null(dat)){
#'       d[[pc]] <- list()
#'       d[[pc]][[1]] <- dat
#'     } # END PALEODATA
#' 
#'     # loop
#'     for (i in 1:length(d[[pc]])){
#' 
#'       # PALEODATA[[i]]
#'       # data frame?
#'       dat <- hasData(d[[pc]], i)
#'       if (is.data.frame(!is.null(dat))){
#'           d[[pc]][[i]] <- as.list(dat)
#'       }
#'       # MEAS + MODEL
#'       # table exists ?
#'       # d$paleoData[[i]]$paleoMeasurementTable
#'       dat.meas <- hasData(d[[pc]][[i]], "measurementTable")
#' 
#'       # table exists ?
#'       # d$paleoData[[i]]$paleoModel
#'       dat.model <- hasData(d[[pc]][[i]], "model")
#' 
#'       # tables do not exist.
#'       # make a meas table
#'       if (is.null(dat.meas) & is.null(dat.model)){
#'         tmp <- d[[pc]][[i]]
#'         d[[pc]][[i]] <- list()
#'         d[[pc]][[i]][["measurementTable"]] <- list()
#'         d[[pc]][[i]][["measurementTable"]][[1]] <- tmp
#'       }  # end meas and model
#' 
#'       # DIRECT
#'       # multiples ?
#'       # d$paleoData[[i]]$paleoMeasurementTable$columns
#'       dat <- hasData(d[[pc]][[i]][["measurementTable"]], "columns")
#'       # convert to multiples
#'       # d$paleoData[[i]]$paleoMeasurementTable
#'       if (!is.null(dat)){
#'         tmp <- d[[pc]][[i]][["measurementTable"]]
#'         d[[pc]][[i]][["measurementTable"]] <- list()
#'         d[[pc]][[i]][["measurementTable"]][[1]] <- tmp
#'       } # end direct data
#' 
#'       # MEASUREMENT
#'       # paleoData[[i]]paleoMeasurementTable
#'       # data frame ?
#'       dat <- hasData(d[[pc]][[i]], "measurementTable")
#'       if (is.data.frame(!is.null(dat))){
#'         d[[pc]][[i]][["measurementTable"]] <- as.list(dat)
#'       }
#'       # multiples ?
#'       if (!is.null(dat)){
#'         dat <- hasData(d[[pc]][[1]][["measurementTable"]], 1)
#'         # convert to multiples
#'         # d$paleoData[[i]]$paleoMeasurementTable[[j]]
#'         if (is.null(dat)){
#'           tmp <- d[[pc]][[1]][["measurementTable"]]
#'           d[[pc]][[1]][["measurementTable"]] <- list()
#'           d[[pc]][[1]][["measurementTable"]][[1]] <- tmp
#'         } # END MEASUREMENT
#' 
#'         # loop
#'         for (j in 1:length(d[[pc]][[i]][["measurementTable"]])){
#' 
#'           # MEASUREMENT[[j]]
#'           # paleoData[[i]]paleoMeasurementTable[[j]]
#'           # data frame?
#'           dat <- hasData(d[[pc]][[i]][["measurementTable"]], j)
#'           if (is.data.frame(!is.null(dat))){
#'             d[[pc]][[i]][["measurementTable"]][[j]] <- as.list(dat)
#'           } # END MEASUREMENT[[j]]
#' 
#'         } # end meas loop
#'       } # end meas exists
#' 
#'       # continue if Model table present
#'       if (length(d[[pc]][[i]][["model"]]) > 0){
#'         # MODEL
#'         # paleoData[[i]]paleoModel
#'         # data frame ?
#'         dat <- hasData( d[[pc]][[i]], "model")
#'         if (is.data.frame(!is.null(dat))){
#'           d[[pc]][[i]][["model"]] <- as.list(dat)
#'         }
#'         # multiples ?
#'         # convert to multiples
#'         if (!is.null(dat)){
#'           dat <- hasData(d[[pc]][[1]][["model"]], 1)
#'           if (is.null(dat)){
#'             tmp <- d[[pc]][[1]][["model"]]
#'             d[[pc]][[1]][["model"]] <- list()
#'             d[[pc]][[1]][["model"]][[1]] <- tmp
#'           } # END MODEL
#' 
#'           # loop
#'           for (j in 1:length(d[[pc]][[i]][["model"]])){
#' 
#'             # MODEL[[j]]
#'             # paleoModel[[j]]
#'             # data frame ?
#'             dat <- hasData(d[[pc]][[i]][["model"]], j)
#'             if (is.data.frame(!is.null(dat))){
#'               d[[pc]][[i]][["model"]][[j]] <- as.list(dat)
#'             }
#' 
#'             # SUMMARY
#'             # paleoModel[[j]]$summaryTable
#'             # data frame ?
#'             dat <- hasData(d[[pc]][[i]][["model"]][[j]], "summaryTable")
#'             if (is.data.frame(!is.null(dat))){
#'               d[[pc]][[i]][["model"]][[j]][["summaryTable"]] <- as.list(dat)
#'             }
#' 
#'             # ENSEMBLE
#'             # paleoModel[[j]]$ensembleTable
#'             # data frame ?
#'             dat <- hasData(d[[pc]][[i]][["model"]][[j]], "ensembleTable")
#'             if (is.data.frame(!is.null(dat))){
#'               d[[pc]][[i]][["model"]][[j]][["ensembleTable"]] <- as.list(dat)
#'             }
#' 
#'             # DISTRIBUTION
#'             # paleoModel[[j]]$distributionTable
#'             dat <- hasData(d[[pc]][[i]][["model"]][[j]], "distributionTable")
#'             if (is.data.frame(!is.null(dat))){
#'               d[[pc]][[i]][["model"]][[j]][["distributionTable"]] <- as.list(dat)
#'             } # end dist
#' 
#'             # multiples ?
#'             # convert to multiples
#'             if (!is.null(dat)){
#'               dat <- hasData(d[[pc]][[1]][["model"]][[j]][["distributionTable"]], 1)
#'               if (is.null(dat) & !is.null(dat)){
#'                 tmp <- d[[pc]][[i]][["model"]][[j]][["distributionTable"]]
#'                 d[[pc]][[i]][["model"]][[j]][["distributionTable"]] <- list()
#'                 d[[pc]][[i]][["model"]][[j]][["distributionTable"]][[1]] <- tmp
#'               } # end dist 1
#' 
#'               # loop
#'               for (k in 1:length(d[[pc]][[i]][["model"]][[j]][["distributionTable"]])){
#' 
#'                 # DISTRIBUTION[[k]]
#'                 dat <- hasData(d[[pc]][[i]][["model"]][[j]][["distributionTable"]], k)
#'                 if (is.data.frame(!is.null(dat))){
#'                   d[[pc]][[i]][["model"]][[j]][["distributionTable"]][[k]] <- as.list(dat)
#'                 } # END DISTRIBUTION[[k]]
#' 
#'               } # end dist loop
#' 
#'             } # end dist exists
#' 
#'           } # end models
#' 
#'         } # end model exists
#' 
#'       } # end if
#' 
#'     } # end section
#' 
#'   } # end if section
#' 
#'   # change the LiPDVersion value to 1.2
#'   d[["lipdVersion"]] <- 1.2
#'   return(d)
#' }

