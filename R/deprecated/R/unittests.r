#' @export
test_lipdread <- function(path){
  tryCatch({
    D <- readLipd(path)
    return(0)
  }, error=function(cond){
    print(cond)
    return(-1)
  })
}

#' @export
test_extractTs <- function(path){
  tryCatch({
    L <- readLipd(path)
    ts <- extractTs(L)
    return(0)
  }, error=function(cond){
    print(cond)
    return(-1)
  })
}

#' @export
test_extractTsCorrectCount <- function(path){
  tryCatch({
    L <- readLipd(path)
    ts <- extractTs(L)
    return(length(ts))
  }, error=function(cond){
    print(cond)
    return(-1)
  })
}

#' @export
test_extractTsUniqueTsids <- function(path){
  tryCatch({
    L <- readLipd(path)
    ts <- extractTs(L)
    ids <- geoChronR::pullTsVariable(ts, "paleoData_TSid")
    if(any(duplicated(ids))){
      return(-1)
    }
    return(0)
  }, error=function(cond){
    print(cond)
    return(-1)
  })
}