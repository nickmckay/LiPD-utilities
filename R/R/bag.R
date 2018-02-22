
#' Look for the users bagit script file. If you can't find it, ask them for help and/or ask them 
#' to download it and locate the file 
#' 
#' @export
#' @keywords internal
#' @return none
set_bagit <- function(){
  tryCatch({
    os <- "windows"
    os <- get_os()
    if(os=="osx" || os=="unix"){
      if(file.exists(system.file(package="lipdR", file.path("exec","bagit.py")))){
        # Found the bagit file included in the package.
        bagit.script <- system.file(package="lipdR", file.path("exec","bagit.py"))
        assign("bagit.script", bagit.script, envir = .GlobalEnv)
      } else {
        if(!exists("bagit.script",where = .GlobalEnv) || get("bagit.script", envir=.GlobalEnv) == "none"){
          # Didn't find the file, go another route
          print("Select your bagit.py file")
          print("If you do not already have one, please go to the link and download the file by right-clicking the 'Raw' button")
          print("https://github.com/nickmckay/LiPD-utilities/blob/master/R/exec/bagit.py")
          bagit.script<-file.choose()
          assign("bagit.script", bagit.script, envir = .GlobalEnv)
        }
      }
    }
    else if(os =="windows" || os == "unknown"){
      print("Warning: Detected Windows/Unknown OS. Unable to use Bagit module.")
      assign("bagit.script", "none", envir = .GlobalEnv)
    }
  }, error=function(cond){
    print("Error: set_bagit: Failed to find or set the bagit path...")
    assign("bagit.script", "none", envir = .GlobalEnv)
  })
}


#' Since we don't have a way of getting the bagit module in R,
#' all we can do is use the default bag function by calling the
#' full python file on a directory. This will create a bag.
#' Warning: This often has system call issues in windows OS.
#' 
#' @export
#' @keywords internal
#' @param char dir_bag: The path to the directory that needs to be bagged
#' @return bool: Bagit success
bagit <- function(dir_bag){
  tryCatch({
    bagit.script <- get("bagit.script", .GlobalEnv)
    if(bagit.script != "none"){
      tryCatch({
        # give user permissions on bagit file
        Sys.chmod(bagit.script, "777")
        # do a system call for bagit on the tmp folder
        ret <- system(paste0(bagit.script, " ", dir_bag), ignore.stdout = TRUE, ignore.stderr = TRUE)
        if (ret != 0){
          print("Warning: Attempted to use Bagit but it was not successful. Skipping bagit...")
          fake_bagit(dir_bag)
        }
      }, error=function(cond){
        print("Warning: Attempted to use Bagit but it was not successful. Skipping bagit...")
        fake_bagit(dir_bag)
      })

    }
    else {
      # There is not a bagit script. Do a fake bagit
      print("Warning: No bagit script was set. Skipping bagit...")
      fake_bagit(dir_bag)
    }
  }, error=function(cond){
    print(paste0("Error: bagit: There was an error while prepping for Bagit: ", cond))
    fake_bagit(dir_bag)
  })
}


#' Run a fake version of bagit. No bagit txt files are created
#' 
#' @export
#' @keywords internal
#' @param char dir_bag: The path to the directory that needs to be bagged
#' @return none
fake_bagit <- function(dir_bag){
  tryCatch({
    # make the data dir
    dir.create(file.path(dir_bag, "data"))
    # move all the files from dir_bag to dir_data
    files <- list.files()
    for(i in 1:length(files)){
      file.rename(files[[i]], file.path(dir_bag, "data", files[[i]]))
    }
  }, error=function(cond){
    print(paste0("Error: fake_bagit: ", cond))
  })
}