###############################################
## Read LiPD - Helpers
## Misc functions that aid the reading of LiPD files
###############################################

#' Convert column type: data frame to list
#' Function may be unused right now
#' @export
#' @keywords internal
#' @param table Data table
#' @return table Converted data table
colsToList <- function(table){
  meta.list <- list()

  # columns are at index 1
  cols <- table[[1]][["columns"]][[1]]

  # loop over dim
  for (i in 1:dim(cols)){
    #make it a list
    meta.list[[i]]=as.list(cols[i,])
  }
  # insert new columns
  table[[1]][["columns"]] <- meta.list

  return(meta.list)
}

#' Convert table type: data frame to list
#' @export
#' @keywords internal
#' @param table Data table
#' @return table Converted data table
tableToList <- function(table){

  # convert table index
  if (is.dataframe(table[[1]])){
    table <- as.list(table[[1]])
  }
  # convert table
  if (is.dataframe(table)){
    table <- as.list(table)
  }
  return(table)
}



