#' Collapse time series into LiPD dataset form
#' @export
#' @param ts Time series
#' @return D LiPD data, sorted by dataset name
collapseTs <- function(ts){
  D <- list()
  # Do some collapse stuff
  for(i in 1:length(ts)){
    pc <- paste0(ts[[i]][["mode"]], "Data")
    # First occurance of this dataset. Add the raw data to the dataset library.
    if(!ts[[i]][["dataSetName"]] %in% names(D)){
      dsn <- ts[[i]][["dataSetName"]]
      print(paste0("processing: ", dsn))
      # Create a new entry for this dataset
      D[[dsn]] <- ts[[i]][["raw"]]
    }
    # Use the time series entry to overwrite the (old) raw data for this column
    D[[dsn]] <- collapse_pc(D[[dsn]], ts[[i]], pc)    
  }
  
  # Is there only one dataset after all this? Set it directly in D. 
  if(length(D)==1){
    D<-D[[1]]
  }
  return(D)
}

#' Collapse time series section; paleo or chron 
#' @export
#' @param list d: Metadata
#' @param list entry: Time series entry
#' @param char pc: paleoData or chronData
#' @return list d: Metadata
collapse_pc <- function(d, entry, pc){
  # Get the crumbs to the target table
  m <- get_crumbs(entry)
  # Get the existing target table
  table <- get_table(d, m, pc)
  # Overwrite the existing table root items and existing (one) specific column
  new_column <- list()
  exclude_keys <- c("mode", "measurementTableNumber", "paleoNumber")
  root_keys <- c('filename', 'googleWorkSheetKey', 'tableName', "missingValue", "tableMD5", "dataMD5", "googWorkSheetKey")
  ts_keys <- names(entry)
  for(i in 1:length(ts_keys)){
    ts_key <- stringr::str_match_all(ts_keys[[i]], "(\\w+)[_](\\w+)")
    if(!isNullOb(ts_key[[1]])){
      # Root keys
      if(ts_key[[1]][[3]] %in% root_keys){
        print(paste0("ROOT: ", ts_keys[[i]]))
      }
      # Table / column keys
      else if(grepl(pc, ts_keys[[i]])){
        print(paste0("TABLE: ", ts_keys[[i]]))
      }
      # Interpretations, special case
      else if (grepl("interpretation", ts_keys[[i]])){
        print(paste0("INTERPRETATION: ", ts_keys[[i]]))
      }
    }
  }
  # Put the new modified table back into the metadata
  d <- put_table(d, m, pc, table)
  return(d)
}

collapse_column <- function(){
  
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
