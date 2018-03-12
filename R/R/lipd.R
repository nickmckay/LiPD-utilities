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
    dir_tmp <- create_tmp_dir()
    unzipper(path, dir_tmp)
    setwd(dir_tmp)
    data_dir <- find_data_dir()
    setwd(data_dir)
    j <- read_jsonld()
    # j = rm_empty_doi(j)
    j <- rm_empty_fields(j)
    j <- update_lipd_version(j)
    j <- merge_csv_metadata(j)
    j <- idx_num_to_name(j)
    # j = put_tsids(j)
    setwd(dir_original)
    unlink(dir_tmp, recursive=TRUE)
  }, error = function(cond){
    print(paste0("Error: lipd_read: ", cond))
    setwd(dir_original)
    unlink(dir_tmp, recursive=TRUE)
  })
  return(j)
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
lipd_write <- function(j, path, dsn, ignore.warnings){
  tryCatch({
    # dsn <- replace_invalid_chars(dsn)
    dir_original <- getwd()
    dir_tmp <- create_tmp_dir()
    setwd(dir_tmp)
    # Create a lipd dir
    dir.create("zip", showWarnings=FALSE)
    dir_zip <- file.path(dir_tmp, "zip")
    setwd("zip")
    # Need an extra (identical) level for zipping later.
    dir.create("bag", showWarnings=FALSE)
    dir_bag <- file.path(dir_zip, "bag")
    setwd("bag")
    
    # look for ensemble data in PaleoData, and ask if you want to remove this data before writing the file.
    j <- warn_ensembles_in_paleo(j, ignore.warnings)
  
    j <- idx_name_to_num(j)
    tmp <- get_lipd_version(j)
    j <- tmp[["meta"]]
    dat <- get_csv_from_metadata(j, dsn)
    write_csv_to_file(dat[["csvs"]])
    j <- rm_empty_fields(dat[["meta"]])
    j <- jsonlite::toJSON(j, pretty=TRUE, auto_unbox = TRUE)
    write(j, file="metadata.jsonld")
    bagit(dir_bag)
    zipper(path, dir_tmp, dsn)
    unlink(dir_tmp, recursive=TRUE)
    setwd(dir_original)
  }, error=function(cond){
    print(paste0("Error: lipd_write: ", cond))
    unlink(dir_tmp, recursive=TRUE)
    setwd(dir_original)
  })
}