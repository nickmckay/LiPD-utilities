###############################################
## Read Lipds - wrapper
## Combines all the file loading functions
## into one process
###############################################

#' Main LiPD reading function. Combines all processes into one.
#' @export
#' @keywords internal
#' @return D LiPD Library
loadLipds <- function(){
  # setModules()
  options(warn = -1)

  # Ask user where files are stored
  path.and.file <- getSrcOrDst()

  # Do initial set up
  working.dir <- path.and.file[["dir"]]
  assign("working.dir", working.dir, envir = .GlobalEnv)
  setwd(working.dir)
  tmp <- createTmpDir()

  # Get names of lipd files present
  lpds_ext <- getListLpdExt(path.and.file)

  if (!is.null(path.and.file$file)){
    # load one file. loads data directly into variable
    # tryCatch({
      D <- singleLoad(lpds_ext[[1]], working.dir, tmp)
    # }, error=function(cond){
    #   print(paste0("load_lipds_main: loadLipds: Failed to import with singleLoad(), ", cond))
    # })
  } else {
    # load multiple files. loads files into a list by filename.
    D <- multiLoad(lpds_ext, working.dir, tmp)
  }
  return(D)
}
  

#' Loop over multiple LiPD files. Load one at a time. 
#' @export
#' @keywords internal
#' @return D LiPD Library
multiLoad <- function(lpds_ext, working.dir, tmp){
  # library to store all lpd data, indexed by lpd dataset name (no extension)
  D <- list()
  tryCatch({
    # loop and import for each file given
    for(i in 1:length(lpds_ext)){
      lpd_noext <- stripExtension(lpds_ext[[i]])
      # place data into the output list by lpd dataset name
      D[[lpd_noext]] <- singleLoad(lpds_ext[[i]], working.dir, tmp)
    }
  }, error=function(cond){
    print(paste0("error load_lipds_main: multiLoad: ", cond))
  })
  return(D)
}


#' Load one LiPD file. All steps
#' @export
#' @keywords internal
#' @return d LiPD File
singleLoad <- function(lpd, working.dir, tmp){
  d <- list()
  tryCatch({
    
    lpd_noext <- stripExtension(lpd)
    
    # Unzip the lipd files to the temp workspace
    unzipper(lpd, tmp)

    # Start importing data from the unpacked temp workspace
    d <- loadLipdFile(lpd_noext, tmp)

    # Convert metadata structure to newest LiPD version
    d <- convertVersion(d)

    # Now you have all the data loaded in memory, place data from csv into columns
    d <- addCsvToMetadataLoad(d)

    # Change columns and tables to index-by-name
    d <- indexByNameLoad(d)

    # We no longer need the csv and metadata separate parts. Link straight to the data.
    d <- removeLayers(d)

  }, error = function(cond){
    print(paste0("error load_lipds_main: singleLoad: ", cond))
  })

  # Move back to the inital directory (Prior to temp folder)
  setwd(working.dir)

  return(d)
}
