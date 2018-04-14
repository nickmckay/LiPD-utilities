#' Create the range for ensemble table "number" field
#' @export
#' @keywords internal
#' @param start Number to start at
#' @param len Amount of times to loop
#' @return l A vectory of column ints
create_range <- function(start, len){
  l <- c()
  for (i in 1:len){
    l[[i]] <- start
    start <- start + 1
  }
  return(l)
}

#' Download a LiPD file from a URL
#' @export
#' @keywords internal
#' @param path URL path to LiPD file
#' @return path Local path to downloaded file
download_from_url <- function(path){
  # Test if the string is a URL or not
  if(is.url(path)){
    # Prompt user to enter a DSN or some type of filename
    dsn <-readline("Please enter the dataset name for this file (Name.Location.Year) : ")
    # String together a local download path
    local_path <- paste0("~/Downloads/", dsn, ".lpd")
    # Initiate download
    download.file(path, local_path, method = "auto")
    # Set the local path as our output path
    path <- local_path
  }
  return(path)
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

#' Check if given string is a URL or not
#' @export
#' @keywords internal
#' @param x Path or URL string
#' @return bool
is.url <-function(x) {
    return(grepl("www.|http:|https:", x))
  }

#' Checks if an object is null/empty
#' @export
#' @keywords internal
#' @param x Data object to check
#' @return boolean
isNullOb <- function(x) is.null(x) | all(sapply(x, is.null))


#' Make geo semi-flat. Remove unnecessary levels between us and data.
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Modified metadata
index_geo <- function(d){
  # create a tmp list
  tmp <- list()
  geo <- d$geo

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
    d$geo <- tmp
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
unindex_geo <- function(d){
  
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


#' Detect the OS being used
#' @export
#' @keywords internal
#' @return char: OS name
get_os <- function() {
  if (.Platform$OS.type == "windows") { 
    return("win")
  } else if (Sys.info()["sysname"] == "Darwin") {
    return("osx") 
  } else if (.Platform$OS.type == "unix") { 
    return("unix")
  } else {
    return("unknown")
  }
}

#' Warn people about writing ageEnsembles that have been mapped into paleoData. This is a common procedure in GeoChronR,
#' and thus will come up, however it can greatly increase the size of the LiPD file, and is easily and quickly replicated 
#' upon loading with geoChronR::mapAgeEnsembleToPaleoData()
#' @export
#' @keywords internal
#' @param d Metadata
#' @return Metadata
warn_ensembles_in_paleo <- function(L, ignore.warnings){
  ans <- NULL
  # Only bother to check for ensembles if ignore.warnings is FALSE
  if(!ignore.warnings){
    # We're good to go, look for stuff. 
    if(is.null(L$paleoData)){
      stop("There's no paleoData in this file")
    }
    else {
      for(i in 1:length(L$paleoData)){
        if ("model" %in% names(L$paleoData[[i]])){
          for(j in 1:length(L$paleoData[[i]]$model)){
            if ("ensembleTable" %in% names(L$paleoData[[i]]$model[[j]])){
             ans = readline(prompt="We detected ageEnsemble data in paleoData. This data can greatly increase the size of the file and can easily be recreated. Would you like to remove it before writing the LiPD file? (y/n)")
             break
            }
          }
        }
      }
      if(ans == "y"){
        for(i in 1:length(L$paleoData)){
          if ("model" %in% names(L$paleoData[[i]])){
            for(j in 1:length(L$paleoData[[i]]$model)){
              if ("ensembleTable" %in% names(L$paleoData[[i]]$model[[j]])){
                L$paleoData[[i]]$model[[j]]$ensembleTable <- NULL
              }
            }
          }
        }
      }
    }
  }
  return(L)
  
}


