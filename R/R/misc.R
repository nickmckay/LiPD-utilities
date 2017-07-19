#' Create the range for ensemble table "number" field
#' @export
#' @keywords internal
#' @param start Number to start at
#' @param len Amount of times to loop
#' @return l A vectory of column ints
createRange <- function(start, len){
  l <- c()
  for (i in 1:len){
    l[[i]] <- start
    start <- start + 1
  }
  return(l)
}

#' Get dataSetName from metadata. If one is not found, use filename as fallback.
#' @export
#' @keywords internal
#' @param list d: Metadata
#' @param char name: Filename fallback
#' @return char dsn: Dataset name
get_datasetname <- function(d, name){
  dsn <- name
  # Attempt to find data set name entry
  if ("dataSetName" %in% names(d)){
    dsn <- d[["dataSetName"]]
  }
  return(dsn)
}

#' Check if metadata path exists. Combine path and i to check for existence
#' @export
#' @keywords internal
#' @param path Path in metadata
#' @param i Next path level.
#' @return dat Data found or null
hasData <- function(path, i){
  dat <- tryCatch({
    dat <- path[[i]]
  }, error=function(cond){
    return(NULL)
  })
  if (isNullOb(dat)){
    dat <- NULL
  }
  return(dat)
}

#' Checks if an object is null/empty
#' @export
#' @keywords internal
#' @param x Data object to check
#' @return boolean
isNullOb <- function(x) is.null(x) | all(sapply(x, is.null))

#' Checks if a path is a directory or not a directory
#' @export
#' @keywords internal
#' @param s Target path
#' @return boolean
isDirectory <- function(s){
  # Get the basename (last item in file path), and check it for a file extension
  # If there is not a file extension (like below), then we can assume that it's a directory
  if (tools::file_ext(basename(s)) == ""){
    return(TRUE)
  }
  # No file extension. Assume it's a file and not a directory
  return(FALSE)
} 

#' Make geo semi-flat. Remove unnecessary levels between us and data.
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Modified metadata
indexGeo <- function(d){
  # create a tmp list
  tmp <- list()
  geo <- d$metadata$geo

  if (!is.null(geo)){
    # properties
    if (!isNullOb(geo$properties)){
      gnames <- names(geo$properties)
      for (i in 1:length(gnames)){
        tmp[[gnames[[i]]]] <- geo$properties[[i]]
      }
    } # end properties

    # geometry
    if (!isNullOb(geo$geometry)){
      gnames <- names(geo$geometry)
      for (i in 1:length(gnames)){
        if (gnames[[i]] == "coordinates"){
          tmp$longitude <- geo$geometry$coordinates[[1]]
          tmp$latitude <- geo$geometry$coordinates[[2]]
          if (length(geo$geometry$coordinates) == 3){
            tmp$elevation <- geo$geometry$coordinates[[3]]
          }
        }
        else if (gnames[[i]] == "type"){
          tmp$geometryType <- geo$geometry[[i]]
        }
        else{
          tmp[[gnames[[i]]]] <- geo$geometry[[i]]
        }
      }
    } # end geometry

    # root geo
    gnames <- names(geo)
    for (i in 1:length(gnames))
      if (gnames[[i]] != "geometry" & gnames[[i]] != "properties"){
        tmp[[gnames[[i]]]] <- geo[[gnames[[i]]]]
      }

    # set the new data in d
    d$metadata$geo <- tmp
  }
  return(d)
}

#' Remove all NA, NULL, and empty objects from the data structure
#' @export
#' @keywords internal
#' @param x Data structure
#' @return x Modified data structure
rm_empty_fields <- function( x ){
  # don't process matrices. it'll turn them to lists and that ruins ensemble data.
  if (!is.matrix(x)){
    # Remove all the nulls
    x <- x[ !isNullOb( x )]
    x <- x[ !sapply( x, is.null ) ]
    # Recursion
    if( is.list(x) ){
      # Recursive dive
      x <- lapply(x, rm_empty_fields)
    }
    x <- x[ unlist(sapply(x, length) != 0)]
  }
  return(x)
}

#' Return to preset "home" working directory
#' @export
#' @keywords internal
#' @return none
returnToRoot <- function(){
  if(!exists("working.dir",where = .GlobalEnv)){
    print("Working directory not set. Choose any file -inside- your target directory")
    out <- guiForPath(NULL)
    working.dir <- out[["dir"]]
    assign("working.dir", working.dir, envir = .GlobalEnv)
  }
  setwd(working.dir)
}

#' An old bug caused some geo coordinates to be reversed. This will switch them back to normal.
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Modified metadata
swapGeoCoordinates <- function(d){
  tryCatch({
    tmp <- d$geo$longitude
    d$geo$longitude <- d$geo$latitude
    d$geo$latitude <- tmp
  },error=function(cond){
    print("unable to swap coordinates")
  })
  return(d)
}

#' Convert geo from semi-flat structure back to original GeoJSON structure.
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Modified metadata
unindexGeo <- function(d){
  
  tmp <- list()
  tmp$geometry <- list()
  tmp$geometry$coordinates <- list()
  tmp$properties <- list()
  geo <- d$geo
  
  if (!is.null(geo)){
    gnames <- names(geo)
    for (i in 1:length(gnames)){
      
      # type goes in root
      if (gnames[[i]] == "type"){
        tmp$type <- geo$type
      }
      # geometry
      else if (gnames[[i]] %in% c("latitude", "longitude", "elevation", "geometryType")){
        if (gnames[[i]] == "latitude"){ tmp$geometry$coordinates[[1]] <- geo$longitude }
        else if (gnames[[i]] == "longitude"){ tmp$geometry$coordinates[[2]] <- geo$latitude }
        else if (gnames[[i]] == "elevation"){ tmp$geometry$coordinates[[3]] <- geo$elevation }
        else if (gnames[[i]] == "geometryType"){ tmp$geometry$type <- geo$geometryType}
      }
      
      # properties
      else{
        tmp[[gnames[[i]]]] <- geo[[gnames[[i]]]]
      }
    } # end loop
    d$geo <- tmp
  } # end if
  
  return(d)
}

#' Check if output datasetname has invalid characters. Replace if necessary
#' R will not zip directories with certain characters.
#' @export
#' @keywords internal
#' @param char dsn: Dataset name
#' @return char dsn: Dataset name
replace_invalid_chars <- function(dsn){
  dsn <- gsub("[.]", "-", dsn)
  return(dsn)
}
