#' Unzip LiPD file to the temporary directory
#' @export
#' @keywords internal
#' @param char path: Path
#' @param char tmp: Temporary directory
#' @return none
unzipper <- function(path, dir_tmp){
  if(length(path)>0){
    unzip(path, exdir = dir_tmp)
  }
}

#' Zip a directory, and move up a level
#' @export
#' @keywords internal
#' @param char dir_tgt: Directory to be zipped
#' @param char dir_tmp  Directory that holds resulting zip file
#' @return none
zipper <- function(dir_original, dir_tgt, dir_tmp, bag.success, dsn){
  # bagit didn't work. do a fake bag
  # if(!bag.success){
  #   dir_tmp <- dir_tgt
  #   dir_tgt <- file.path(dir_tgt, "bag")
  # }
  # zip the top lipd directory. zip file is create one level up
  setwd(dir_tgt)
  include.files <- list.files(getwd(), recursive = TRUE)
  BBmisc::suppressAll(zip(dir_tgt, include.files))
  setwd(dir_tmp)
  # rename
  if (file.exists("bag.zip")){
    file.rename("bag.zip", paste0(dsn, ".lpd"))
  }
  # move
  if(file.exists(paste0(dsn, ".lpd"))){
    file.copy(paste0(dsn, ".lpd"), dir_original, overwrite=TRUE)
  }
}
