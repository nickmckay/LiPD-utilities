###############################################
## Versions
## Updates the incoming LiPD to the most recent
## LiPD standards
###############################################

#' Check what version of LiPD this file is using. If none is found, assume it's using version 1.0
#' @export
#' @keywords internal
#' @param d LiPD Metadata
#' @return version LiPD version number
get_lipd_version <- function(d){
  version <- NULL
  keys <- c("lipdVersion", "liPDVersion", "LiPDVersion")
  for (i in 1:length(keys)){
    key <- keys[[i]]
    if (key %in% names(d[["metadata"]])){
      version <- d[["metadata"]][[key]]
      d[["metadata"]][[key]] <- NULL
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
    d = update_lipd_v1_1(d)
    version <- 1.1
  }
    
    # Update from 1.1 to 1.2
    if (version == 1.1 || version == "1.1"){
      d = update_lipd_v1_2(d)
      version = 1.2
    }
    
    # Update from 1.2 to 1.3
    if(version == 1.2 || version == "1.2"){
      d = update_lipd_v1_3(d)
      version = 1.3
    }
    return(d)
}


#' Update LiPD v1.0 to v1.1
#' - chronData entry is a list that allows multiple tables
#' - paleoData entry is a list that allows multiple tables
#' - chronData now allows measurement, model, summary, modelTable, ensemble, calibratedAges tables
#' - Added 'lipdVersion' key
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Metadata
update_lipd_v1_1 <- function(d){
  
}

#' Update LiPD v1.1 to v1.2
#' - Added NOAA compatible keys : maxYear, minYear, originalDataURL, WDCPaleoURL, etc
#' - 'calibratedAges' key is now 'distribution'
#' - paleoData structure mirrors chronData. Allows measurement, model, summary, modelTable, ensemble,
#'   distribution tables
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Metadata
update_lipd_v1_2 <- function(d){
  
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
  
}

#' Update the key names and merge interpretation data
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Metadata
update_lipd_v1_3_keys <- function(d){
  v12keys <- c("paleoMeasurementTable", "chronMeasurementTable", "paleoModel", "chronModel", "paleoDataMD5", "chronDataMD5", "paleoEnsembleMD5",  
                 "chronEnsembleMD5", "paleoEnsembleTableMD5", "chronEnsembleTableMD5", "paleoMeasurementTableMD5", "chronMeasurementTableMD5", "name")
  v13keys <- c("measurementTable", "measurementTable", "model", "model", "dataMD5", "dataMD5", "tableMD5", "tableMD5", "tableMD5", "tableMD5",
                 "tableMD5", "tableMD5", "tableName")
  v13keymap <- setNames(as.list(v13keys), v12keys)
  
}

#' Update the structure for summary and ensemble tables
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Metadata
update_lipd_v1_3_structure <- function(d){
  
}



#' Convert LiPD version structure whenever necessary
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Metadata
convertVersion <- function(d){
  # Check which version this LiPD file is
  d <- checkVersion(d)
  # check and convert any data frames into lists
  d <- convertDfsLst(d)
  return(d)
}

#' Check / convert and fixed data frames into scalable lists
#' @export
#' @keywords internal
#' @param d LiPD metadata
#' @return d Modified LiPD metadata
convertDfsLst <- function(d){

  paleos <- c("paleoData", "paleoMeasurementTable", "paleoModel")
  chrons <- c("chronData", "chronMeasurementTable", "chronModel")

  # convert single entries to lists. matching structure to 1.2
  d <- convertSM(d, paleos)
  d <- convertSM(d, chrons)

  return(d)
}

#' Convert from a single fixed table, to a multiple scalable table
#' (LiPD Verison 1.1 to 1.2 change)
#' @export
#' @keywords internal
#' @param d LiPD metadata
#' @return d Modified LiPD metadata
convertSM <- function(d, keys){

  key1 <- keys[[1]]
  key2 <- keys[[2]]
  key3 <- keys[[3]]

  # PALEODATA
  # data frame?
  dat <- hasData(d[["metadata"]], key1)

  # proceed of section exists
  if (!is.null(dat)){

    if (is.data.frame(dat)){
      d[["metadata"]][[key1]] <- list()
      d[["metadata"]][[key1]][[1]] <- as.list(dat)
    }
    # multiples?
    dat <- hasData(d[["metadata"]][[key1]], 1)
    # convert to multiples
    if (is.null(dat)){
      d[["metadata"]][[key1]] <- list()
      d[["metadata"]][[key1]][[1]] <- dat
    } # END PALEODATA

    # loop
    for (i in 1:length(d[["metadata"]][[key1]])){

      # PALEODATA[[i]]
      # data frame?
      dat <- hasData(d[["metadata"]][[key1]], i)
      if (is.data.frame(!is.null(dat))){
          d[["metadata"]][[key1]][[i]] <- as.list(dat)
      }
      # MEAS + MODEL
      # table exists ?
      # d$paleoData[[i]]$paleoMeasurementTable
      dat.meas <- hasData(d[["metadata"]][[key1]][[i]], key2)

      # table exists ?
      # d$paleoData[[i]]$paleoModel
      dat.model <- hasData(d[["metadata"]][[key1]][[i]], key3)

      # tables do not exist.
      # make a meas table
      if (is.null(dat.meas) & is.null(dat.model)){
        tmp <- d[["metadata"]][[key1]][[i]]
        d[["metadata"]][[key1]][[i]] <- list()
        d[["metadata"]][[key1]][[i]][[key2]] <- list()
        d[["metadata"]][[key1]][[i]][[key2]][[1]] <- tmp
      }  # end meas and model

      # DIRECT
      # multiples ?
      # d$paleoData[[i]]$paleoMeasurementTable$columns
      dat <- hasData(d[["metadata"]][[key1]][[i]][[key2]], "columns")
      # convert to multiples
      # d$paleoData[[i]]$paleoMeasurementTable
      if (!is.null(dat)){
        tmp <- d[["metadata"]][[key1]][[i]][[key2]]
        d[["metadata"]][[key1]][[i]][[key2]] <- list()
        d[["metadata"]][[key1]][[i]][[key2]][[1]] <- tmp
      } # end direct data

      # MEASUREMENT
      # paleoData[[i]]paleoMeasurementTable
      # data frame ?
      dat <- hasData(d[["metadata"]][[key1]][[i]], key2)
      if (is.data.frame(!is.null(dat))){
        d[["metadata"]][[key1]][[i]][[key2]] <- as.list(dat)
      }
      # multiples ?
      if (!is.null(dat)){
        dat <- hasData(d[["metadata"]][[key1]][[1]][[key2]], 1)
        # convert to multiples
        # d$paleoData[[i]]$paleoMeasurementTable[[j]]
        if (is.null(dat)){
          tmp <- d[["metadata"]][[key1]][[1]][[key2]]
          d[["metadata"]][[key1]][[1]][[key2]] <- list()
          d[["metadata"]][[key1]][[1]][[key2]][[1]] <- tmp
        } # END MEASUREMENT

        # loop
        for (j in 1:length(d[["metadata"]][[key1]][[i]][[key2]])){

          # MEASUREMENT[[j]]
          # paleoData[[i]]paleoMeasurementTable[[j]]
          # data frame?
          dat <- hasData(d[["metadata"]][[key1]][[i]][[key2]], j)
          if (is.data.frame(!is.null(dat))){
            d[["metadata"]][[key1]][[i]][[key2]][[j]] <- as.list(dat)
          } # END MEASUREMENT[[j]]

        } # end meas loop
      } # end meas exists

      # continue if Model table present
      if (length(d[["metadata"]][[key1]][[i]][[key3]]) > 0){
        # MODEL
        # paleoData[[i]]paleoModel
        # data frame ?
        dat <- hasData( d[["metadata"]][[key1]][[i]], key3)
        if (is.data.frame(!is.null(dat))){
          d[["metadata"]][[key1]][[i]][[key3]] <- as.list(dat)
        }
        # multiples ?
        # convert to multiples
        if (!is.null(dat)){
          dat <- hasData(d[["metadata"]][[key1]][[1]][[key3]], 1)
          if (is.null(dat)){
            tmp <- d[["metadata"]][[key1]][[1]][[key3]]
            d[["metadata"]][[key1]][[1]][[key3]] <- list()
            d[["metadata"]][[key1]][[1]][[key3]][[1]] <- tmp
          } # END MODEL

          # loop
          for (j in 1:length(d[["metadata"]][[key1]][[i]][[key3]])){

            # MODEL[[j]]
            # paleoModel[[j]]
            # data frame ?
            dat <- hasData(d[["metadata"]][[key1]][[i]][[key3]], j)
            if (is.data.frame(!is.null(dat))){
              d[["metadata"]][[key1]][[i]][[key3]][[j]] <- as.list(dat)
            }

            # SUMMARY
            # paleoModel[[j]]$summaryTable
            # data frame ?
            dat <- hasData(d[["metadata"]][[key1]][[i]][[key3]][[j]], "summaryTable")
            if (is.data.frame(!is.null(dat))){
              d[["metadata"]][[key1]][[i]][[key3]][[j]][["summaryTable"]] <- as.list(dat)
            }

            # ENSEMBLE
            # paleoModel[[j]]$ensembleTable
            # data frame ?
            dat <- hasData(d[["metadata"]][[key1]][[i]][[key3]][[j]], "ensembleTable")
            if (is.data.frame(!is.null(dat))){
              d[["metadata"]][[key1]][[i]][[key3]][[j]][["ensembleTable"]] <- as.list(dat)
            }

            # DISTRIBUTION
            # paleoModel[[j]]$distributionTable
            dat <- hasData(d[["metadata"]][[key1]][[i]][[key3]][[j]], "distributionTable")
            if (is.data.frame(!is.null(dat))){
              d[["metadata"]][[key1]][[i]][[key3]][[j]][["distributionTable"]] <- as.list(dat)
            } # end dist

            # multiples ?
            # convert to multiples
            if (!is.null(dat)){
              dat <- hasData(d[["metadata"]][[key1]][[1]][[key3]][[j]][["distributionTable"]], 1)
              if (is.null(dat) & !is.null(dat)){
                tmp <- d[["metadata"]][[key1]][[i]][[key3]][[j]][["distributionTable"]]
                d[["metadata"]][[key1]][[i]][[key3]][[j]][["distributionTable"]] <- list()
                d[["metadata"]][[key1]][[i]][[key3]][[j]][["distributionTable"]][[1]] <- tmp
              } # end dist 1

              # loop
              for (k in 1:length(d[["metadata"]][[key1]][[i]][[key3]][[j]][["distributionTable"]])){

                # DISTRIBUTION[[k]]
                dat <- hasData(d[["metadata"]][[key1]][[i]][[key3]][[j]][["distributionTable"]], k)
                if (is.data.frame(!is.null(dat))){
                  d[["metadata"]][[key1]][[i]][[key3]][[j]][["distributionTable"]][[k]] <- as.list(dat)
                } # END DISTRIBUTION[[k]]

              } # end dist loop

            } # end dist exists

          } # end models

        } # end model exists

      } # end if

    } # end section

  } # end if section

  # change the LiPDVersion value to 1.2
  d[["metadata"]][["lipdVersion"]] <- 1.2
  return(d)
}

