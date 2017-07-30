###############################################
## Read/Write Lipds
###############################################

#' Read LiPD files into R workspace
#' @export
#' @keywords internal
#' @param path Source path (optional)
#' @return D LiPD data
readLipd <- function(path=NULL){
  D = list()
  # Warnings are annoying, we don't want them
  options(warn = -1)
  # Ask user where files are stored, or sort the given path parameter
  path <- get_src_or_dst(path)
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
      dsn <- get_datasetname(j, Kmisc::strip_extension(basename(entry)))
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
#' @keywords internal
#' @param list d: LiPD data
#' @param char path: Destination path
#' @return none:
writeLipd <- function(d, path=NULL){
  tryCatch({
    if(missing(path)){
      path <- browse_dialog("d")
      setwd(path)
    }
    if ("paleoData" %in% names(d)){
      print(paste0("writing: ", d[["dataSetName"]]))
      lipd_write(d, path, d[["dataSetName"]])
    } else {
      entries <- names(d)
      for (i in 1:length(entries)){
        print(paste0("writing: ", basename(entry)))
        entry <- dsns[[i]]
        lipd_write(d[[entry]], path, entry)
      }
    }
  }, error=function(cond){
    print(paste0("Error: writeLipd: ", cond))
  })
}