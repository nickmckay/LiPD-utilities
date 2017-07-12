
#' Create a temporary working directory
#' @export
#' @keywords internal
#' @return d Temporary directory path
createTmpDir <- function(){
  d <- tempdir()
  return(d)
}

#' Open a file browsing gui to let the user pick a location
#' @export
#' @keywords internal
#' @param ans Single or multiple files
#' @return path Path to file
browseDialog <- function(ans){
  tryCatch(
    { path <- file.choose() },
    error=function(cond){
      print("File/Directory not chosen")
      quit(1)
    })
  
  # parse the dir path. don't keep the filename
  if (ans == "m" || is.null(ans)){
    dir.path = dirname(path)
    one.file = NULL
  }
  # parse the dir path and the filename
  else if (ans == "s"){
    dir.path = dirname(path)
    one.file = basename(path)
  }
  out.list <- list("dir" = dir.path, "file"= one.file)
  return(out.list)
}

#' Ask user where local file/folder location is.
#' @export
#' @keywords internal
#' @param path Target path (optional)
#' @return path.and.file Path to files
get_src_or_dst<- function(path){
  if (isNullOb(path)){
    # Path was not given. Start prompts
    ans <- askHowMany()
    path.and.file <- browseDialog(ans)
  } else {
    # Path was given. Is it a directory or a file?
    dir <- isDirectory(path)
    if (dir){
      # It's a directory. Set the path as the directory
      path.and.file <- list("dir" = path, "file"= NULL)
    } else {
      # It's a file. Split the directory and the filename
      path.and.file <- list("dir" = dirname(path), "file"= basename(path))
    }
  }
  return(path.and.file)
}

