
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
    os <- get_os()
    os <- "windows"
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
        ret <- system(paste0(bagit.script, " ", dir_bag), ignore.stdout = TRUE, ignore.stderr = TRUE)
        if (ret != 0){
          print("Warning: Unable to use bagit module on LiPD data. Skipping...")
          fake_bagit(dir_bag)
        }
      }, error=function(cond){
        print("Warning: Unable to use bagit module on LiPD data. Skipping...")
        fake_bagit(dir_bag)
      })

    }
    else if(os =="windows" || os == "unknown"){
      print("Warning: OS - Windows. Unable to use bagit module on LiPD data. Skipping...")
      fake_bagit(dir_bag)
    }
  }, error=function(cond){
    print("Error: bagit: Bagit failed. Skipping...")
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