

assignColumnsToTable = function(MT){
  if(any(names(MT)=="columns")){
    cols = MT$columns
    for(i in 1:length(cols)){
      col = cols[[i]]
      if(is.list(col)){
        #make sure name is unique
        unames = make.unique(c(names(MT),col$variableName))
        uname = unames[length(unames)]
        MT[[uname]]=col
        
        
      }else{
        stop("I think this should be a list")
      }
    }
  }
  MT$columns=NULL
  return(MT)
}


#deal with the columns problem.
for(d in 1:length(D)){
  for(p in 1:length(D[[d]]$paleoData)){
    for(pt in 1:length(D[[d]]$paleoData[[p]]$paleoMeasurementTable)){
      D[[d]]$paleoData[[p]]$paleoMeasurementTable[[pt]] = assignColumnsToTable(D[[d]]$paleoData[[p]]$paleoMeasurementTable[[pt]])
    }
  }
  for(c in 1:length(D[[d]]$chronData)){
    for(ct in 1:length(D[[d]]$chronData[[c]]$chronMeasurementTable)){
      D[[d]]$chronData[[c]]$chronMeasurementTable[[ct]] = assignColumnsToTable(D[[d]]$chronData[[c]]$chronMeasurementTable[[ct]])
    }
    for(cm in 1:length(D[[d]]$chronData[[c]]$chronModel)){
      D[[d]]$chronData[[c]]$chronModel[[cm]]$ensembleTable = assignColumnsToTable(  D[[d]]$chronData[[c]]$chronModel[[cm]]$ensembleTable)
      D[[d]]$chronData[[c]]$chronModel[[cm]]$summaryTable = assignColumnsToTable(  D[[d]]$chronData[[c]]$chronModel[[cm]]$summaryTable)
      
    }
    
    
    
  }
}
