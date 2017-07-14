#' Loads a LiPD file from local path. Unzip, read, and process data
#' Steps: create tmp, unzip lipd, read files into memory, manipulate data, move to original dir, delete tmp.
#' @export
#' @keywords internal
#' @param lpds_ext List of LiPD filenames to read (w/ .lpd extension)
#' @param working.dir Directory that contains the target files
#' @return d LiPD File
lipd_read <- function(path){
  j <- list()
  dir_original = getwd()
  tryCatch({
    dir_tmp <- createTmpDir()
    unzipper(path, tmp)
    setwd(dir_tmp)
    data_dir <- find_data_dir()
    setwd(data_dir)
    j <- read_jsonld()
    # TODO?
    # j = rm_empty_doi(j)
    j <- rm_empty_fields(j)
    # TODO 
    j <- update_lipd_version(j)
    j <- merge_csv_metadata(j)
    j <- idx_num_to_name(j)
    # TODO?
    # j = put_tsids(j)
    setwd(dir_original)
    unlink(dir_tmp, recursive=TRUE)
  }, error = function(cond){
    print(paste0("Error: lipd_read: ", cond))
  })
  # Move back to the inital directory (in case there was an error in the tryCatch)
  setwd(dir_original)
  return(d)
}


#' Saves current state of LiPD object data. Outputs to a LiPD file.
#' Steps: create tmp, create bag dir, get dsn, splice csv from json, write csv, clean json, write json, create bagit,
#' zip up bag folder, place lipd in target dst, move to original dir, delete tmp
#' @export
#' @keywords internal
#' @param list j: Metadata
#' @param char path: Destination path
#' @param char dsn: Dataset name
#' @return none:
lipd_write <- funciton(j, path, dsn){
  # Json is pass by reference. Make a copy so we don't mess up the original data.
  # _json_tmp = copy.deepcopy(_json)
  # dir_original = os.getcwd()
  # try:
  #   dir_tmp = create_tmp_dir()
  #   dir_bag = os.path.join(dir_tmp, "bag")
  #   os.mkdir(dir_bag)
  #   os.chdir(dir_bag)
  #   _json_tmp = check_dsn(name, _json_tmp)
  #   _dsn = _json_tmp["dataSetName"]
  #   _dsn_lpd = _dsn + ".lpd"
  #   _json_tmp, _csv = get_csv_from_metadata(_dsn, _json_tmp)
  #   write_csv_to_file(_csv)
  #   _json_tmp = rm_values_fields(_json_tmp)
  #   _json_tmp = put_tsids(_json_tmp)
  #   _json_tmp = idx_name_to_num(_json_tmp)
  #   write_json_to_file(_json_tmp)
  #   create_bag(dir_bag)
  #   rm_file_if_exists(path, _dsn_lpd)
  #   zipper(root_dir=dir_tmp, name="bag", path_name_ext=os.path.join(path, _dsn_lpd))
  #   os.chdir(dir_original)
  #   shutil.rmtree(dir_tmp)
  # except Exception as e:
  #   logger_lipd.error("lipd_write: {}".format(e))
  tryCatch({
    # verify name format
    name <- verifyOutputFilename(name)
    
    # Create the folder hierarchy for Bagit
    # Make the tmp folder and move into it
    initial.dir <- getwd()
    tmp <- createTmpDir()
    if (!dir.exists(tmp)){
      dir.create(tmp)
    }
    setwd(tmp)
    
    # Remove the lipd dir if it already exists
    if (dir.exists(name)){
      unlink(name, recursive=TRUE)
    }
    
    # Create a lipd dir
    dir.create(name, showWarnings=FALSE)
    lipd.dir <- file.path(tmp, name)
    setwd(name)
    
    # Need an extra (identical) level for zipping later.
    dir.create(name, showWarnings=FALSE)
    lipd2.dir <- file.path(tmp,name,"bag")
    setwd(name)
    
    # reverse columns to index by number
    j <- idx_name_to_num(j)
    
    # collect all csv data into an organized list
    all.data <- collectCsvs(name, d)
    
    # clean csv
    all.data[["csv"]] <- cleanCsv(all.data[["csv"]])
    
    # use the organized list to write out all csv files
    csv.success <- write_csv_to_file(all.data[["csv"]])
    
    # only continue if csv files were written
    if (csv.success){
      # remove all empty objs and null values
      j <- remove_empty_fields(all.data[["metadata"]])
      
      j <- confirmLipdVersion(j)
      
      # turn data structure into json
      j <- jsonlite::toJSON(j, pretty=TRUE, auto_unbox = TRUE)
      
      # filename.lpd
      # lpd.jsonld <- paste0(name, ".jsonld")
      
      # write json to file
      write(j, file="metadata.jsonld")
      
      # move up to lipd dir level
      setwd(lipd2.dir)
      
      # bag the lipd directory
      # lipd directory is lipd name without extension
      bag.success <- bagit(lipd2.dir, initial.dir)
      # if bagit success, zip the lipd.dir. if bagit failed, zip lipd.dir2
      if (bag.success){
        zipper(lipd.dir, tmp)
      } else if (!bag.success){
        zipper(lipd.dir2, lipd.dir)
      }
      
      # rename the file
      name.zip <- paste0(name, ".zip")
      name.lpd <- paste0(name, ".lpd")
      if (file.exists(name.zip)){
        file.rename(name.zip, name.lpd)
      }
      
      # move file to initial directory
      if(file.exists(name.lpd)){
        file.copy(name.lpd, initial.dir, overwrite=TRUE)
      }
      
    } # end csv.success
  }, error=function(cond){
    print(paste0("error write_lipds_file: ", cond))
  })
  
  # remove the tmp folder and contents
  unlink(tmp, recursive=TRUE)
  # return back to the initial directory
  setwd(initial.dir)
  return()
}