#' Find jsonld file in the cwd (or within a 2 levels below cwd), and load it in.
#' @export
#' @importFrom utils read.csv
#' @keywords internal
#' @return data.list List of data for one LiPD file
read_jsonld <- function(){
  # jsonld file - only one per lpd
  j <- list_files_recursive("jsonld")
  # import jsonld file
  if (length(j)>1){
    print("Error: read_jsonld: Too many jsonld files in LiPD. There should only be one.")
    for(i in 1:length(j)){
      print(j[[i]])
    }
    # Stop execution here, because it'll just cause more problems down the line
    stop()
  } else {
    # use jsonlite to parse json from file
    tryCatch({
      # Read in jsonld data as a char
      j.string <- readLines(j)
      # Remove all invalid unicode chars that would break fromJSON()
      j.string.clean <- gsub("[\001-\037]", "", j.string)
      # Parse the jsonld string data as a list
      j.data <- jsonlite::fromJSON(j.string.clean, simplifyDataFrame = FALSE)
    }, error=function(cond){
      print(paste0("Error: read_jsonld: Unable to import metadata in JSONLD file. Check that it is valid JSON: ", cond))
    })
  }
  return(j.data)
}