
#' Since we don't have a way of getting the bagit module in R,
#' all we can do is use the default bag function by calling the
#' full python file on a directory. This will create a bag.
#' Warning: This often has system call issues in windows OS.
#' 
#' @export
#' @keywords internal
#' @param char data.dir: The path to the directory that needs to be bagged
#' @return bool: Bagit success
bagit <- function(data.dir){
  tryCatch({
    os <- get_os()
    
    if(os=="osx" || os=="unix"){
      if(file.exists(file.path("exec", "bagit.py"))){
        # Found the bagit file included in the package.
        bagit.script <- system.file(package="lipdR", file.path("exec","bagit.py"))
      } else {
        if(!exists("bagit.script",where = .GlobalEnv)){
          # Didn't find the file, go another route
          print("Select your bagit.py file")
          bagit.script<-file.choose()
          assign("bagit.script", bagit.script, envir = .GlobalEnv)
        } else {
          bagit.script <- get('bagit.script', envir=.GlobalEnv)
        }
      }
      tryCatch({
        # give user permissions on bagit file
        Sys.chmod(bagit.script, "777")
        # do a system call for bagit on the tmp folder
        ret <- system(paste0(bagit.script, " ", data.dir), ignore.stdout = TRUE, ignore.stderr = TRUE)
        if (ret == 0){
          return(TRUE)
        }
      }, error=function(cond){
        print("Warning: Unable to use bagit module on LiPD data. Skipping...")
      })

    }
    else if(os =="windows"){
      print("Warning: OS - Windows. Unable to use bagit module on LiPD data. Skipping...")
    } else {
      print("Warning: OS - Unknown. Unable to use bagit module on LiPD data. Skipping...")
    }
    return(FALSE)
  }, error=function(cond){
    print("Error: Bagit failed. Skipping...")
    return(FALSE)
  })
}
