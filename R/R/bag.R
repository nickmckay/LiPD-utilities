
#' Since we don't have a way of getting the bagit module in R,
#' all we can do is use the default bag function by calling the
#' full python file on a directory. This will create a bag.
#' @export
#' @keywords internal
#' @param char data.dir: The path to the directory that needs to be bagged
#' @return bool: Bagit success
bagit <- function(data.dir){
  # if the bagit path isn't loaded into the global env yet (first run), then locate it and write the location
  if(!exists("bagit.script",where = .GlobalEnv)){
    # locate the bagit py file included with the lipdR package
    bagit.script <- system.file(package="lipdR", "exec/bagit.py")
    # was the package bagit file found ?
    if(!file.exists(bagit.script)){
      # not found. user locate file with gui
      print("Select your bagit.py file")
      # write path to global env
      bagit.script<-file.choose()
      assign("bagit.script", bagit.script, envir = .GlobalEnv)
    }
  }
  # give user permissions on bagit file
  Sys.chmod(bagit.script, "777")
  # do a system call for bagit on the tmp folder
  ret <- system(paste0(bagit.script, " ", data.dir), ignore.stdout = TRUE, ignore.stderr = TRUE)
  # do soft bagit if system call status returns 1 (error)
  if (ret == 1){
    return(FALSE)
  }
  return(TRUE)
}


create_bagit <- function(){
  
}