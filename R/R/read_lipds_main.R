###############################################
## Read Lipds - wrapper
## Combines all the file reading functions
## into one process
###############################################

#' Main LiPD reading function. Combines all processes into one.
#' @export
#' @keywords internal
#' @param path Target path (optional)
#' @return D LiPD Library
readLipd <- function(path=NULL){
  # setModules()
  options(warn = -1)
  D = list()

  # Ask user where files are stored, or sort the given path parameter
  path.and.file <- getSrcOrDst(path)

  # Do initial set up
  working.dir <- path.and.file[["dir"]]
  assign("working.dir", working.dir, envir = .GlobalEnv)
  setwd(working.dir)
  tmp <- createTmpDir()

  # Get names of lipd files present
  lpds_ext <- getListLpdExt(path.and.file)
  
  if (isNullOb(lpds_ext)){
    print("No LiPD file(s) found in the given path")
  } else {
    if (!is.null(path.and.file$file)){
      # Read one file. Reads data directly into variable
      # tryCatch({
      D <- singleRead(lpds_ext[[1]], working.dir, tmp)
      # }, error=function(cond){
      #   print(paste0("read_lipds_main: readLipd: Failed to import with singleRead(), ", cond))
      # })
    } else {
      # Read multiple files. Reads files into a list by filename.
      D <- multiRead(lpds_ext, working.dir, tmp)
    }
  }
  return(D)
}
  

#' Loop over multiple LiPD files. Read one at a time. 
#' @export
#' @keywords internal
#' @param lpds_ext List of LiPD filenames to read (w/ .lpd extension)
#' @param working.dir Directory that contains the target files
#' @param tmp Temporary directory to unpack LiPD data
#' @return D LiPD Library
multiRead <- function(lpds_ext, working.dir, tmp){
  # library to store all lpd data, indexed by lpd dataset name (no extension)
  D <- list()
  tryCatch({
    # loop and import for each file given
    for(i in 1:length(lpds_ext)){
      lpd_noext <- stripExtension(lpds_ext[[i]])
      # place data into the output list by lpd dataset name
      D[[lpd_noext]] <- singleRead(lpds_ext[[i]], working.dir, tmp)
    }
  }, error=function(cond){
    print(paste0("error read_lipds_main: multiRead: ", cond))
  })
  return(D)
}


#' Read one LiPD file. All steps
#' @export
#' @keywords internal
#' @param lpds_ext List of LiPD filenames to read (w/ .lpd extension)
#' @param working.dir Directory that contains the target files
#' @param tmp Temporary directory to unpack LiPD data
#' @return d LiPD File
singleRead <- function(lpd, working.dir, tmp){
  d <- list()
  tryCatch({
    
    lpd_noext <- stripExtension(lpd)
    
    # Unzip the lipd files to the temp workspace
    unzipper(lpd, tmp)

    # Start importing data from the unpacked temp workspace
    d <- readLipdFile(lpd_noext, tmp)

    # Convert metadata structure to newest LiPD version
    d <- convertVersion(d)

    # Now you have all the data Readed in memory, place data from csv into columns
    d <- addCsvToMetadataRead(d)

    # Change columns and tables to index-by-name
    d <- indexByNameRead(d)

    # We no longer need the csv and metadata separate parts. Link straight to the data.
    d <- removeLayers(d)

  }, error = function(cond){
    print(paste0("error read_lipds_main: singleRead: ", cond))
  })

  # Move back to the inital directory (Prior to temp folder)
  setwd(working.dir)

  return(d)
}
