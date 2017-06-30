#' Main function. Loop through all LiPD records, saving, and then cleaning up
#' @export
#' @param D LiPD Library
#' @return none
writeLipds <- function(D){
  ans <- readline(prompt="Write files to the current working directory? (y/n): ")
  if (ans=="n"){
    change.dir <- browseDialog(NULL)
    setwd(change.dir[["dir"]])
  }
  # starting directory. this is where files will be written to
  initial.dir <- getwd()

  # Parse one or many records?
  if ("paleoData" %in% names(D)){
      singleWrite(D)
    } else {
      multiWrite(D)
    }
  # return back to the initial directory
  setwd(initial.dir)
}

#' Parse one data record
#' @export
#' @keywords internal
#' @param d LiPD data
#' @param name Data set name
#' @return none
singleWrite <- function(d, name=NA){
  # Write one lipd
  if (is.na(name)){
    name <- getDatasetName(d)
  }
  writeLipdFile(d, name)

  # # Write lipd data
  # tryCatch({
  #   print(sprintf("saving: %s", name))
  #   Write.lipd.file(d, name)
  # }, error = function(cond){
  #   print(sprintf("error saving: %s", name))
  # })
}

#' Parse library of data records
#' @export
#' @keywords internal
#' @param D LiPD data
#' @return none
multiWrite <- function(D){
  # loop by record names
  lpds <- names(D)

  for (i in 1:length(lpds)){
    tryCatch({
        # reference to single lipd record
        d <- D[[lpds[[i]]]]
        print(sprintf("saving: %s", lpds[[i]]))
        singleWrite(d, lpds[[i]])
    }, error=function(cond){
      print(paste0("error saving: ", lpds[[i]], ": ", cond))
    })

  }
}

#' Get data set name from metadata
#' @export
#' @keywords internal
#' @param d LiPD data
#' @return name Data set name
getDatasetName <- function(d){
  # Attempt to find data set name entry
  name <- tryCatch({
    name <- d$dataSetName
  }, error=function(cond){
    return(NA)
  })
  # No dataSetName entry in record. Have user enter a name
  if (is.na(name)){
    name <- promptStringWrite("No data set name found. Enter the name: ")
  }
  return(name)
}

#' Prompt the user for some string entry
#' @export
#' @keywords internal
#' @param statement Statement that gets printed to the user
#' @return ans User input entry
promptStringWrite <- function(statement){
  invalid = TRUE
  # Loop until valid input
  while (invalid){
    ans <- readline(prompt=statement)
    ans <- as.character(ans)
    if (ans != ""){
      # Valid input. Stop looping
      invalid = FALSE
    }
  }
  return(ans)
}
