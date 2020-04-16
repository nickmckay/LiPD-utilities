#' Unzip LiPD file to the temporary directory
#' @export
#' @importFrom utils unzip
#' @keywords internal
#' @param char path: Path
#' @param char tmp: Temporary directory
#' @return none
unzipper <- function(path, dir_tmp){
  if(length(path)>0){
    success <- unzip(path, exdir = dir_tmp)
    if(length(success) == 0){
      stop(paste0("No LiPD file at the given path: ", path))
    }
  }
}

#' Zip a directory, and move up a level
#' @export
#' @importFrom utils zip
#' @keywords internal
#' @param char dir_original: Directory to move the LiPD to
#' @param char dir_tmp:  Temp directory
#' @return none
zipper <- function(dir_original, dir_tmp, dsn){
  # zip the top lipd directory. zip file is create one level up
  setwd(file.path(dir_tmp, "zip"))
  include.files <- list.files(getwd(), recursive = TRUE)
  tryCatch({
    zip(getwd(), include.files)
    setwd(dir_tmp)
    # rename
    if (file.exists("zip.zip")){
      file.rename("zip.zip", paste0(dsn, ".lpd"))
    }
    # move
    if(file.exists(paste0(dsn, ".lpd"))){
      file.copy(paste0(dsn, ".lpd"), dir_original, overwrite=TRUE)
    }
  }, error=function(cond){
    print(paste0("Zipping failed: ", cond))
  })

}
