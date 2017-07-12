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
  
  dir_original <- getwd()
  # setModules()
  options(warn = -1)
  D = list()

  # Ask user where files are stored, or sort the given path parameter
  path.and.file <- get_src_or_dst(path)

  # Do initial set up
  working.dir <- path.and.file[["dir"]]
  assign("working.dir", working.dir, envir = .GlobalEnv)
  setwd(working.dir)

  # Get names of lipd files present
  lpds_ext <- getListLpdExt(path.and.file)
  
  if (isNullOb(lpds_ext)){
    print("LiPD file(s) not found in the given path")
  } else {
    if (!is.null(path.and.file$file)){
      # Read one file. Reads data directly into variable
      # tryCatch({
      D <- singleRead(lpds_ext[[1]], working.dir)
      # }, error=function(cond){
      #   print(paste0("read_lipds_main: readLipd: Failed to import with singleRead(), ", cond))
      # })
    } else {
      # Read multiple files. Reads files into a list by filename.
      D <- multiRead(lpds_ext, working.dir)
    }
  }
  return(D)
}
  

#' Loop over multiple LiPD files. Read one at a time. 
#' @export
#' @keywords internal
#' @param lpds_ext List of LiPD filenames to read (w/ .lpd extension)
#' @param working.dir Directory that contains the target files
#' @return D LiPD Library
multiRead <- function(lpds_ext, working.dir){
  # library to store all lpd data, indexed by lpd dataset name (no extension)
  D <- list()
  tryCatch({
    # loop and import for each file given
    for(i in 1:length(lpds_ext)){
      lpd_noext <- stripExtension(lpds_ext[[i]])
      # place data into the output list by lpd dataset name
      D[[lpd_noext]] <- singleRead(lpds_ext[[i]], working.dir)
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
#' @return d LiPD File
singleRead <- function(lpd, working.dir){
  
  # _j = {}
  # dir_original = os.getcwd()
  # try:
      # dir_tmp = create_tmp_dir()
      # unzipper(path, dir_tmp)
      # os.chdir(dir_tmp)
      # _dir_data = find_files()
      # os.chdir(_dir_data)
      # _j = read_jsonld()
      # _j = rm_empty_fields(_j)
      # _j = check_dsn(path, _j)
      # _j = update_lipd_version(_j)
      # _j = idx_num_to_name(_j)
      # _j = rm_empty_doi(_j)
      # _j = rm_empty_fields(_j)
      # _j = put_tsids(_j)
      # _j = merge_csv_metadata(_j)
      # os.chdir(dir_original)
      # shutil.rmtree(dir_tmp)
      
  j <- list()
  dir_original = getwd()
  tryCatch({
    dir_tmp <- createTmpDir()
    
    # Unzip the lipd files to the temp workspace
    unzipper(lpd, tmp)

    # Start importing data from the unpacked temp workspace
    j <- readLipdFile(lpd_noext, tmp)

    # Update metadata to newest LiPD version
    j <- update_lipd_version(j)

    # All the data is in memory, place data from csv into columns
    j <- addCsvToMetadataRead(j)

    # Change columns and tables to index-by-name
    j <- idx_num_to_name(j)

    # We no longer need the csv and metadata separate parts. Link straight to the data.
    j <- removeLayers(j)

  }, error = function(cond){
    print(paste0("error read_lipds_main: singleRead: ", cond))
  })

  # Move back to the inital directory (Prior to temp folder)
  setwd(working.dir)

  return(d)
}
