###############################################
## Read/Write Lipds
###############################################

#' stripExtension
#'
#' @param filename file name or path
#'
#' @return dataset name without extension
#' @export
stripExtension <- function(filename){
  basef <- basename(filename)
  if(stringr::str_detect(basef,"[.]")){#there's a period, strip
  dsn <- stringr::str_sub(basef,1,max(stringr::str_locate_all(basef,pattern = "[.]")[[1]][,1])-1)
  }else{#if not then just return the base name
    dsn <- basef
  }
  return(dsn)
}

#' Read LiPD files into R workspace
#' @export
#' @author Chris Heiser
#' @import stringr
#' @keywords internal
#' @param path Source path (optional) : char
#' @usage readLipd(path)
#' @return D : LiPD dataset(s)
#' @examples
#' read in multiple datasets - no path argument
#' D <- readLipd()   # choose option 'd' for directory
#'
#' read in multiple datasets - with path argument
#' D <- readLipd("/Users/bobsmith/Desktop/lipd_files")
#' 
#' read in one dataset - no path argument
#' L <- readLipd()  # choose option "s" for single file
#' 
#' read in one dataset - with path argument
#' L <- readLipd("/Users/bobsmith/Desktop/lipd_files/dataset.lpd")
#' 
readLipd <- function(path=NULL){
  D = list()
  # Warnings are annoying, we don't want them
  options(warn = -1)
  # Ask user where files are stored, or sort the given path parameter
  path <- get_src_or_dst(path)
  
  # If this is a URL, download the file and return the local path where the file is saved. 
  path <- download_from_url(path)
  
  # Get the explicit full paths for each lipd file
  entries <- get_lipd_paths(path)
  
  if (isNullOb(entries)){
    # Files is empty. Either not lipd files were in that path, or we had an error somewhere
    print("LiPD file(s) not found in the given path")
    print(paste0("Path: ", path))
  } else {
    for (i in 1:length(entries)){
      j <- list()
      # Entry is one file path
      entry <- entries[[i]]
      print(paste0("reading: ", basename(entry)))
      # Do initial set up
      dir_source <- dirname(entry)
      # assign("directory_source", directory_source, envir = .GlobalEnv)
      setwd(dir_source)
      j <- lipd_read(entry)
      # Get the datasetname
      dsn <- get_datasetname(j, stripExtension(entry))
      # Set the data in D using the datasetname
      D[[dsn]] <- j
    }
    if(length(D) == 1){
      D <- D[[1]]
    }
  }

  return(D)
}
  


#' Write LiPD data onto disk as LiPD files
#' @export
#' @author Chris Heiser
#' @keywords internal
#' @param D LiPD datasets : list
#' @param path Destination path : char
#' @usage writeLipd(D, path)
#' @return none
#' @examples 
#' 
#' # write - without path argument
#' writeLipd(D)
#' 
#' # write - with path argument
#' writeLipd(D, "/Users/bobsmith/Desktop/lipd_files")
#' 
writeLipd <- function(D, path=NULL, ignore.warnings=FALSE,removeNamesFromLists = FALSE){
  tryCatch({
    if(missing(path)){
      path <- browse_dialog("d")
      setwd(path)
    }
    set_bagit()
    if ("paleoData" %in% names(D)){
      print(paste0("writing: ", D[["dataSetName"]]))
      lipd_write(D, path, D[["dataSetName"]], ignore.warnings, removeNamesFromLists = removeNamesFromLists)
    } else {
      dsns <- names(D)
      for (i in 1:length(dsns)){
        print(paste0("writing: ", basename(dsns[i])))
        entry <- dsns[[i]]
        lipd_write(D[[entry]], path, entry, ignore.warnings,removeNamesFromLists = removeNamesFromLists)
      }
    }
  }, error=function(cond){
    print(paste0("Error: writeLipd: ", cond))
  })
}