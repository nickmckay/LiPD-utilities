#' Collapse time series into LiPD dataset form
#' @export
#' @author Chris Heiser
#' @param ts Time series : list
#' @usage collapseTs(ts)
#' @return D: LiPD data, sorted by dataset name : list
#' @examples 
#' D <- readLipds()
#' ts <- extractTs(D)
#' D <- collapseTs(ts)
#' 
collapseTs <- function(ts){
  D <- list()
  tryCatch({
    # Do some collapse stuff
    for(i in 1:length(ts)){
      pc <- paste0(ts[[i]][["mode"]], "Data")
      # First occurance of this dataset. Add the raw data to the dataset library.
      if(!ts[[i]][["dataSetName"]] %in% names(D)){
        dsn <- ts[[i]][["dataSetName"]]
        print(paste0("collapsing: ", dsn))
        # Recover paleoData and chronData from raw data
        D[[dsn]] <- put_base_data(ts[[i]])
        # Remove the old summary and measurement tables, as we'll be writing these fresh. Other tables as-is.
        D[[dsn]] <- rm_existing_tables(D[[dsn]], pc)
        # Collapse root data keys (pub, funding, archiveType, etc)
        D[[dsn]] <- collapse_root(D[[dsn]], ts[[i]], pc)
      }
      # Use the time series entry to overwrite the (old) raw data for this column
      D[[dsn]] <- collapse_table(D[[dsn]], ts[[i]], pc)    
    }
    # Is there only one dataset after all this? Set it directly in D. 
    if(length(D)==1){
      D<-D[[1]]
    }
  }, error=function(cond){
    print(paste0("Error: collapseTs: ", cond))
  })
  return(D)
}

is_include_key <- function(key, exclude, pc){
  for(i in 1:length(exclude)){
    if(key == exclude[[i]] || grepl(pc, key) || grepl(exclude[[i]], key)){
      return(FALSE)
    }
  }
  return(TRUE)
} 

collapse_root <- function(d, entry, pc){
  exclude <- c("mode", "measurementTableNumber", "paleoNumber", "summaryTableNumber", 
               "raw", "depth", "depthUnits", "age", "ageUnits", "interpretation", "calibration", "hasResolution")
  ts_keys <- names(entry)
  pub <- list()
  funding <- list()
  geo <- list(geometry=list(coordinates=list(NA, NA, NA), type="Point"), properties=list())
  for(i in 1:length(ts_keys)){
    key <- ts_keys[[i]]
    # Is this a key that should be added
    include <- is_include_key(key, exclude, pc)
    # Filter all the keys we don't want
    if(include){
      if(grepl("geo", key)){
        m <- stringr::str_match_all(key, "(\\w+)[_](\\w+)")
        g_key = m[[1]][[3]]
        if(g_key == "longitude" || g_key == "meanLon"){
          geo[["geometry"]][["coordinates"]][[1]] <- entry[[key]]
        } else if (g_key == "latitude" || g_key == "meanLat"){
          geo[["geometry"]][["coordinates"]][[2]] <- entry[[key]]
        } else if (g_key == "elevation" || g_key == "meanElev"){
          geo[["geometry"]][["coordinates"]][[3]] <- entry[[key]]
        } else if (g_key == "type"){
          geo[["type"]] <- entry[[key]]
        } else {
          geo[["properties"]][[g_key]] <- entry[[key]]
        }
      } else if(grepl("pub", key)){
        pub <- collapse_block(entry, pub, key)
      } else if(grepl("funding", key)){
        funding <- collapse_block(entry, funding, key)
      } else{
        # Root key that is not a special case; move it right on over
        d[[key]] <- entry[[key]]
      }
    }
  }
  # Only add these lists if they're not empty 
  if(!isNullOb(pub)){ d[["pub"]] <- pub }
  if(!isNullOb(funding)){ d[["funding"]] <- funding }
  if(!isNullOb(geo)){ d[["geo"]] <- geo }
  d[["@context"]] <- "context.jsonld"
  return(d)
}

collapse_author <- function(d, entry){
  return(d)
}

#' Collapse time series section; paleo or chron 
#' @export
#' @param list d: Metadata
#' @param list entry: Time series entry
#' @param char pc: paleoData or chronData
#' @return list d: Metadata
collapse_table <- function(d, entry, pc){
  # Get the crumbs to the target table
  m <- get_crumbs(entry)
  # Get the existing target table
  table <- get_table(d, m, pc)
  table <- collapse_table_root(table, entry, pc)
  table <- collapse_column(table, entry, pc)
  # Put the new modified table back into the metadata
  d <- put_table(d, m, pc, table)
  return(d)
}

#' Collapse time series table root. All keys listed below are known table root keys. 
#' @export
#' @param list table: Metadata
#' @param list entry: Time series entry
#' @param char pc: paleoData or chronData
#' @return list table: Metadata
collapse_table_root <- function(table, entry, pc){
  root_keys <- c('filename', 'googleWorkSheetKey', 'tableName', "missingValue", "tableMD5", "dataMD5", "googWorkSheetKey")
  for(i in 1:length(root_keys)){
    key <- paste0(pc, "_", root_keys[[i]])
    if(key %in% names(entry)){
      table[[root_keys[[i]]]] <- entry[[key]]
    }
  }
  return(table)
}

#' Collapse time series column. Compile column entries and place new column in table. 
#' @export
#' @param list table: Metadata
#' @param list entry: Time series entry
#' @param char pc: paleoData or chronData
#' @return list table: Metadata
collapse_column <- function(table, entry, pc){
  new_column <- list()
  interp <- list()
  calib <- list()
  res <- list()
  include <- c("paleoData", "chronData", "interpretation", "calibration", "hasResolution") 
  exclude <- c('filename', 'googleWorkSheetKey', 'tableName', "missingValue", "tableMD5", "dataMD5", "googWorkSheetKey")
  ts_keys <- names(entry)
  tryCatch({
    for(i in 1:length(ts_keys)){
      if (grepl("interpretation", ts_keys[[i]])){
        interp <- collapse_block(entry, interp, ts_keys[[i]])
      } else if (grepl("calibration", ts_keys[[i]])){
        calib <- collapse_block(entry, calib, ts_keys[[i]])
      } else if (grepl("hasResolution", ts_keys[[i]])){
        calib <- collapse_block(entry, res, ts_keys[[i]])
      } else {
        # ts_key / 1,1 "paleoData" / 1,2 "_" / 1,3 "someKey"
        ts_key <- stringr::str_match_all(ts_keys[[i]], "(\\w+)[_](\\w+)")
        if(!isNullOb(ts_key[[1]])){
          # Not a root table key, and pc matches the given mode
          if(!ts_key[[1]][[3]] %in% exclude && ts_key[[1]][[2]] == pc){
            # set ts entry value to new entry in column
            new_column[[ts_key[[1]][[3]]]] <- entry[[ts_keys[[i]]]]
          }
        }
      }
    }
    # Add the special sub-lists if data was found
    if(!isNullOb(interp)){
      new_column[["interpretation"]] <- interp
    }
    if(!isNullOb(calib)){
      new_column[["calibration"]] <- calib
    }
    if(!isNullOb(calib)){
      new_column[["hasResolution"]] <- res
    }
    vn <- new_column[["variableName"]]
    # Set the new column into the table using the variableName
    table[[vn]] <- new_column
  }, error=function(cond){
    print(paste0("Error: collapse_column: ", cond))
  })
  return(table)
}

#' Use regex to split the tableName into a crumbs path
#' @export
#' @param list ts: Time series
#' @return list matches: Separated names and indices
get_crumbs <- function(ts){
  matches <- c()
  tryCatch({
    mode <- ts[["mode"]]
    key <- paste0(mode, "Data_tableName")
    m <- stringr::str_match_all(ts[[key]], "(\\w+)(\\d+)(\\w+)(\\d+)")
    if(isNullOb(m[[1]])){
      m <- stringr::str_match_all(ts[[key]], "(\\w+)(\\d+)(\\w+)(\\d+)(\\w+)(\\d+)")
      matches <- c(m[[1]][[2]], m[[1]][[3]], m[[1]][[4]], m[[1]][[5]], m[[1]][[6]], m[[1]][[7]])
    } else {
      matches <- c(m[[1]][[2]], m[[1]][[3]], m[[1]][[4]], m[[1]][[5]])
    }
  }, error=function(cond){
    stop(paste0("Error: ", cond))
  })
  return(matches)
}

#' Collapse all blocks listed: funding, publication calibration, interpretation
#' These follow the regex format of "<key1><idx>_<key2>"
#' @export
#' @param list entry: Time series entry
#' @param list l: Metadata (to append to)
#' @param char key: Key from time series entry
#' @return list l: Metadata
collapse_block <- function(entry, l, key){
  match <- stringr::str_match_all(key, "(\\w+)(\\d+)[_](\\w+)")
  if(!isNullOb(match[[1]])){
    tryCatch({
      l[[as.numeric(match[[1]][[3]])]] <- entry[[key]]
    }, error=function(cond){
      l[[as.numeric(match[[1]][[3]])]] <- list()
      l[[as.numeric(match[[1]][[3]])]] <- entry[[key]]
    })
  }
  return(l)
}

#' Get the target table
#' @export
#' @param list d: Metadata
#' @param list m: Regex match
#' @param char pc: paleoData or chronData
#' @return list table: Metadata
get_table <- function(d, m, pc){
  # Measurement table
  if(m[[3]] == "measurement"){
    table <- d[[pc]][[as.numeric(m[[2]])]][[paste0(m[[3]], "Table")]][[as.numeric(m[[4]])]]
  }
  # Model - summary table
  else {
    table <- d[[pc]][[as.numeric(m[[2]])]][[m[[3]]]][[as.numeric(m[[4]])]][[paste0(m[[5]], "Table")]]
  }
  return(table)
}

#' Put the target table
#' @export
#' @param list d: Metadata
#' @param list m: Regex match
#' @param char pc: paleoData or chronData
#' @param list table: Metadata (to be placed)
#' @return list d: Metadata
put_table <- function(d, m, pc, table){
  # Measurement table
  if(m[[3]] == "measurement"){
    d[[pc]][[as.numeric(m[[2]])]][[paste0(m[[3]], "Table")]][[as.numeric(m[[4]])]] <- table
  }
  # Model - summary table
  else {
    d[[pc]][[as.numeric(m[[2]])]][[m[[3]]]][[as.numeric(m[[4]])]][[paste0(m[[5]], "Table")]][[as.numeric(m[[6]])]] <- table
  }
  return(d)
}

#' Remove any measurement or summary tables in the metadata for the given mode
#' @export
#' @param list d: Metadata
#' @param char pc: paleoData or chronData
#' @return list d: Metadata
rm_existing_tables <- function(d, pc){
  if(pc %in% names(d)){
    for(i in 1:length(d)){
      if("measurementTable" %in% names(d[[i]])){
        for(j in 1:length(d[[i]][["measurementTable"]])){
          d[[i]][["measurementTable"]][[j]] <- list()
        }
      }
      if("model" %in% names(d[[i]])){
        for(j in 1:length(d[[i]][["model"]])){
          if("summaryTable" %in% d[[i]][["model"]][[j]]){
            for(k in 1:length(d[[i]][["model"]][[j]][["summaryTable"]])){
              d[[i]][["model"]][[j]][["summaryTable"]][[k]] < list()
            }
          }
        }
      }
    }
  }
  return(d)
}

#' Put in paleoData and chronData as the base for this dataset using the pre-extractTs data.  
#' @export
#' @param list d: Metadata
#' @param char pc: paleoData or chronData
#' @return list d: Metadata
put_base_data <- function(entry){
  d <- list()
  if("paleoData" %in% names(entry[["raw"]])){
    d[["paleoData"]] <- entry[["raw"]][["paleoData"]]
  }
  if("chronData" %in% names(entry[["raw"]])){
    d[["chronData"]] <- entry[["raw"]][["chronData"]]
  }
  return(d)
}