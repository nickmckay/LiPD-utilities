###############################################
## Read LiPD - Helpers
## Misc functions that aid the reading of LiPD files
###############################################

#' Get list of all LiPD files in current directory
#' @export
#' @keywords internal
#' @param path.and.file Target directory and 1+ files
#' @return f List of LiPD files w. ext
list_files <- function(path){
  file <- path.and.file[["file"]]
  # Multiple file grab. No single filename given.
  if (is.null(file)){
    f <- list.files(path=path.and.file[["dir"]], pattern='\\.lpd$')
  }
  # Single file given. Create list of one filename.
  else {
    f <- list()
    f[[1]] <- file
  }
  return(f)
}




#' Remove the file extension from string name
#' @export
#' @keywords internal
#' @param filename One LiPD filename
#' @return x LiPD filename w/o extension
stripExtension <- function(filename){
  filename <- Kmisc::strip_extension(filename)
  return(filename)
}

#' Get list of csv files in current directory and below
#' @export
#' @keywords internal
#' @return f List of csv files
listFiles <- function(x){
  # create the file type filter string
  ft <- paste0("\\.", x, "$")
  # get the list of filenames from the current directory and below
  f <- list.files(path=getwd(), pattern=ft, recursive=TRUE)
  return(f)
}

#' Remove CSV and metadata layer from LiPD file. Also, remove empties
#' @export
#' @keywords internal
#' @param d LiPD file
#' @return d Modified LiPD file
removeLayers <- function(d){
  d <- removeEmptyRec(d[["metadata"]])
  return(d)
}

#' Ask if user wants to read one file or a directory with multiple files.
#' @export
#' @keywords internal
#' @return ans Answer to prompt (s/m)
askHowMany <- function(){
  ans <- readline(prompt="Are you reading one file or multiple? (s/m): ")
  # Test if input matches what we expect. Keep prompting until valid input.
  if(!grepl("\\<s\\>",ans) & !grepl("\\<m\\>", ans))
  { return(askHowMany()) }
  # Return a valid answer
  return(as.character(ans))
}


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



