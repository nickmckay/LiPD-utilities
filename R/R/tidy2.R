#' Pull a single entry list object ot the top level (internal use)
#'
#' @param x 
#'
#' @return
tsPluck <- function(x){
  dopluck <- FALSE
  if(is.list(x)){
    ml <- max(map_dbl(x,~length(.x)))
    
    if(ml == 1){
      dopluck <- TRUE
    }
  }
  
  if(dopluck){
    x2 <- modify(x,.f = ~ ifelse(is.null(.x),NA,.x))
    return(unlist(x2))
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
    purrr::transpose() %>%
    tibble::as_tibble() %>% 
    purrr::modify(tsPluck) # this pulls all the single entry lists to the top level, and tries to use appropriate calsses
    
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

  

