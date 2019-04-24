
#' Create a random TSid
#' @return TSid
#' @export
createTSid <- function(x = 1){
  
  return(paste(c("R",sample(c(letters,LETTERS,seq(0,9)),size = 10,replace=TRUE)),collapse = ""))
}

#' Add TSid where missing in a LiPD file
#' @param L LiPD file
#' @return a Lipd file
#' @export
addTSidToLipd <- function(L){
  mts <- lipdR::extractTs(L)
  for(i in 1:length(mts)){
    if(length(mts[[i]]$paleoData_TSid)==0){
      mts[[i]]$paleoData_TSid <- createTSid()
    }
  }
  
  L <- collapseTs(mts)
  
  # #try do it with chronData too
  # cts <- try(lipdR::extractTs(L,whichtables = "meas",mode = "chron"))
  # if(class(cts)=="list"){
  #   for(i in 1:length(cts)){
  #     if(length(cts[[i]]$chronData_TSid)==0){
  #       cts[[i]]$chronData_TSid <- createTSid()
  #     }
  #   }
  #   L <- collapseTs(cts)
  # }
  
  return(L)
}