#' Ask if user wants to read one file or a directory with multiple files.
#' @export
#' @keywords internal
#' @return ans Answer to prompt (s/m)
ask_how_many <- function(){
  ans <- readline(prompt="Do you want to load a single file (s) or directory (d)? ")
  # Test if input matches what we expect. Keep prompting until valid input.
  if(!grepl("\\<s\\>",ans) & !grepl("\\<d\\>", ans))
  { return(ask_how_many()) }
  # Return a valid answer
  return(as.character(ans))
}


#' Open a file browsing gui to let the user pick a file or directory
#' @export
#' @keywords internal
#' @param char ans single (s) or directory (d) 
#' @return char path Directory or file path
browse_dialog <- function(ans){
  tryCatch(
    { path <- file.choose() },
    error=function(cond){
      print("Error: File must be selected")
      quit(1)
    })
  
  # Since R cannot choose directories, we have to manually get the directory path from the file that was chosen
  if (ans == "d" || is.null(ans)){
    path = dirname(path)
  }
  return(path)
}

#' 'Create' a temp directory (really its the same directory path for the whole R session, so it's not that new)
#' Recreate it if it's non-existant 
#' @export
#' @keywords internal
#' @return char path: 
create_tmp_dir <- function(){
  dir_tmp <- tempfile()
  if(!dir.exists(dir_tmp)){
    dir.create(dir_tmp)
  }
  return(dir_tmp)
}

#' Ask user where local file/directory location is.
#' @export
#' @keywords internal
#' @param char path Target path
#' @return char path Directory or file path
get_src_or_dst<- function(path){
  tryCatch({
    if (!(isNullOb(path))){
      # If the provided path is not a directory and not a lipd file path, then it's not valid
      if (!isDirectory(path) && tools::file_ext(path) != "lpd"){
        # Not a lipd file and not a directory. Stop execution and quit. 
        stop("Error: The provided path must be a directory or a LiPD file")
      } 
    } else {
      # Path was not given. Start prompts
      ans <- ask_how_many()
      path <- browse_dialog(ans)
    }
  }, error=function(cond){
    print(paste0("Error: get_src_or_dst: ", cond))
  })

  return(path)
}

#' Get a list of paths to LiPD files
#' @export
#' @keywords internal
#' @param path Directory or file path
#' @return list files File paths to LiPD files
get_lipd_paths <- function(path){
  files <- list()
  if (isDirectory(path)){
    files <- list.files(path=path, pattern='\\.lpd$', full.names = TRUE)
  } else if(tools::file_ext(path) == "lpd"){
    files[[1]] <- path
  }
  return(files)
}

#' Recursive file list for current directory and below
#' @export
#' @keywords internal
#' @param char x: File type
#' @return char files: Matching file paths
list_files_recursive <- function(x){
  # create the file type filter string
  ft <- paste0("\\.", x, "$")
  # get the list of filenames from the current directory and below
  files <- list.files(path=getwd(), pattern=ft, recursive=TRUE)
  return(files)
}


#' Use a recursive file search to find the "data" directory of a LiPD file
#' @export
#' @keywords internal
#' @param char x: File type
#' @return char files: Matching file paths
find_data_dir <- function(){
  # If there is a jsonld file, then that means we're in the data directory
  files <- list.files(path=getwd(), pattern="\\.jsonld$", recursive=TRUE)
  if (isNullOb(files)){
    stop("Error: Unable to find the 'data' directory in the LiPD file")
  }
  # Use the directory name from the jsonld path
  dir_data <- dirname(files[[1]])
  return(dir_data)
}

#' Checks if a path is a directory or not a directory
#' @export
#' @keywords internal
#' @param s Target path
#' @return boolean
isDirectory <- function(s){
  # Get the basename (last item in file path), and check it for a file extension
  # If there is not a file extension (like below), then we can assume that it's a directory
  if (tools::file_ext(basename(s)) == ""){
    return(FALSE)
  }
  # No file extension. Assume it's a file and not a directory
  return(TRUE)
} 


