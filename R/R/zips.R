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
#' @param dir Directory to be zipped
#' @param tmp Directory that holds resulting zip file
#' @return none
zipper <- function(dir, tmp){
  # zip the top lipd directory. zip file is create one level up
  setwd(dir)
  include.files <- list.files(getwd(), recursive = TRUE)
  BBmisc::suppressAll(zip(dir, include.files))
  setwd(tmp)
}
