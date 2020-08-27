#' Pull a single entry list object ot the top level (internal use)
#'
#' @param x 
#'
#' @return
tsPluck <- function(x){
  dopluck <- FALSE
  if(is.list(x)){
    ml <- max(purrr::map_dbl(x,~length(.x)))
    
    if(ml == 1){
      dopluck <- TRUE
    }
  }
  
  if(dopluck){
    x2 <- purrr::modify(x,.f = ~ ifelse(is.null(.x),NA,.x))
    x3 <- unlist(x2)
    if(length(x3) == length(x)){
    return(x3)
    }else{
      return(x)
    }
  }else{
    return(x)
  }
}

#' Convert a LiPD TS object into an equivalent nested tibble
#'
#' @param TS 
#' @importFrom purrr transpose 
#' @importFrom purrr modify 
#' @importFrom tibble as_tibble 
#' @return a nested tibble
#' @export
ts2tibble <- function(TS){
  
  tibbleTS <- TS %>%
    purrr::transpose(.names = sort(unique(unlist(purrr::map(TS,names))))) %>%
    tibble::as_tibble() %>% 
    purrr::modify(tsPluck) # this pulls all the single entry lists to the top level, and tries to use appropriate calsses
  
  #check for TSid
  if(all(tibbleTS$mode == "chron")){
    if(is.null(tibbleTS$chronData_TSid)){
      tibbleTS$chronData_TSid <- NA
    }
  }
  
  win <- which(is.na(tibbleTS$chronData_TSid))
  if(length(win > 0)){
    tibbleTS$chronData_TSid[win] <- paste0(tibbleTS$dataSetName[1],"-chron-NA",seq_along(win))
  }
  
  if(all(tibbleTS$mode == "paleo")){
    if(is.null(tibbleTS$paleoData_TSid)){
      tibbleTS$paleoData_TSid <- paste0("NA",seq_len(nrow(tibbleTS)))
    }
  }
    
  win <- which(is.na(tibbleTS$paleoData_TSid))
  if(length(win > 0)){
    tibbleTS$paleoData_TSid[win] <- paste0(tibbleTS$dataSetName[1],"-paleo-NA",seq_along(win))
  }
  
  return(tibbleTS)
}


#' @family LiPD manipulation
#' @title create tidy data.frame from TS (old version)
#' @description Deprecated. The new version `tidyTs()` is *much* faster. takes a TS object and turns it into a long, tidy, data.frame. Useful for data manipulation and analysis in the tidyverse and plotting
#' @importFrom tidyr unchop
#' @param TS a LiPD Timeseries object
#' @param age.var 
#' @return a tidy data.frame
#' @export
tidyTs <- function(TS,age.var = "age"){
  tts <- TS %>% 
    ts2tibble() %>% 
    tidyr::unchop(c(age.var,"paleoData_values"))
}

  

