#' Lump metadata variables with other rows in Ts (treeTS)
#'
#' @param Ts 
#' @param sc 
#'
#' @return A lumped Ts
#' @export
#'
lumpTsMetaVariables <- function(Ts,sc=c("eps","rbar","ncores")){

#what variables will be used for id
dsn <- sapply(Ts,"[[","dataSetName")
tN <- sapply(Ts,"[[","tableNumber")
tT <- sapply(Ts,"[[","tableType")
mN <- sapply(Ts,"[[","modelNumber") #NPM: going to need to be smarter about this for when it's a mix of model and no model
if(is.list(mN)){#then at least some don't have modelNumbers... ignore for now.
  hasModel <- FALSE
}else{
  hasModel <- TRUE
}
#get a paleo/chron number
if(Ts[[1]]$mode=="paleo"){
  pN <- sapply(Ts,"[[","paleoNumber")
}else{
  pN <- sapply(Ts,"[[","chronNumber")
}


varNames <- sapply(Ts,"[[","paleoData_variableName")

for(v in 1:length(sc)){
  ind <- which(varNames == sc[v])
  for(i in 1:length(ind)){
    this <- Ts[[ind[i]]]
    
    #get identifying information...
    if(hasModel){
    wtp <- which(this$dataSetName == dsn & 
                   this$tableNumber == tN &
                   this$tableType == tT &
                   this$paleoNumber == pN &
                   this$modelNumber == mN)
    }else{
      wtp <- which(this$dataSetName == dsn & 
                     this$tableNumber == tN &
                     this$tableType == tT &
                     this$paleoNumber == pN )
    }
    
    for(w in wtp){#loop through the matching rows
      Ts[[w]][[sc[v]]] <- this$paleoData_values #assign in the values
      Ts[[w]][[paste0(sc[v],"-TSid")]]<- this$paleoData_TSid #assign in the TSid
      Ts[[w]][[paste0(sc[v],"-units")]]<- this$paleoData_units #assign in the TSid
    }
  }
}

#delete the original rows
return(Ts[-which(varNames %in% sc)])
}


