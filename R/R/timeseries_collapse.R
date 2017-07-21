#' Collapse time series into LiPD dataset form
#' @export
#' @param ts Time series
#' @return D LiPD data, sorted by dataset name
collapseTs <- function(ts){
  D <- list()
  # Do some collapse stuff
  for(i in 1:length(ts)){
    # First occurance of this dataset. Add the raw data to the dataset library.
    if(!ts[[i]][["dataSetName"]] %in% names(D)){
      dsn <- ts[[i]][["dataSetName"]]
      print(paste0("processing: ", dsn))
      # Create a new entry for this dataset
      D[[dsn]] <- ts[[i]][["raw"]]
    }
    # Use the time series entry to overwrite the (old) raw data for this column
    D[[dsn]] <- collapse_pc(D[[dsn]], ts[[i]])    
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
#' @param list ts: Time series entry
#' @return list d: Metadata
collapse_pc <- function(d, ts){
  # What mode is this?
  
  
  
}

collapse_table_root <- function(){
  
}

collapse_column <- function(){
  
}

collapse_pub <- function(){
  
}

collapse_geo <- function(){
  
}
