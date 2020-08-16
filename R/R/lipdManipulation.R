
#' @export
#' @importFrom dplyr bind_cols bind_rows group_by
#' @importFrom rlang .data
#' @import tibble data.table
#' @importFrom purrr map_df
#' @importFrom utils setTxtProgressBar txtProgressBar
#' @import arsenal
#' @import data.table
#' @family LiPD manipulation
#' @title create tidy data.frame from TS (old version)
#' @description Deprecated. The new version `tidyTs()` is *much* faster. takes a TS object and turns it into a long, tidy, data.frame. Useful for data manipulation and analysis in the tidyverse and plotting
#' @param TS a LiPD Timeseries object
#' @return a tidy data.frame
tidyTsOld <- function(TS){
  options(warn = -2)
  pb <- txtProgressBar(min=0,max=length(TS),style=3)
  print(paste("Tidying your ",length(TS)," timeseries"))
  
  #preallocate 
  nprows <- sum(sapply(TS,function(x){length(x$paleoData_values)}))
  
  pcolnames <- unique(unlist(sapply(TS,names)))
  
  
  
  
  additional.names <- c("paleoData_values_char")
  
  pcolnames <- c(pcolnames,additional.names)
  tidyData <- suppressWarnings(as.data.table(matrix(data = NA,nrow = nprows,ncol = length(pcolnames))))
  
  names(tidyData) <- pcolnames
  
  #determine classes
  for(cc in 1:length(pcolnames)){
    if(cc==length(pcolnames)){
      class(tidyData[[pcolnames[cc]]]) = "character"
    }else{
      
      
      pv <- pullTsVariable(TS,pcolnames[cc])
      if(is.character(pv)){
        class(tidyData[[pcolnames[cc]]]) = "character"
      }else if(is.numeric(pv)){
        class(tidyData[[pcolnames[cc]]]) = "numeric"
      }else if(is.list(pv)){
        if(is.numeric(pv[[1]])){
          class(tidyData[[pcolnames[cc]]]) = "numeric"
        }else{
          class(tidyData[[pcolnames[cc]]]) = "character"
        }
      }else{
        class(tidyData[[pcolnames[cc]]]) = "character"
      }
    }
  }
  
  #specify some classes
  class(tidyData$paleoData_values) <- "numeric"
  class(tidyData$paleoData_values_char) <- "character"
  
  
  
  sr <- 1
  
  for(i in 1:length(TS)){
    setTxtProgressBar(pb, i)
    
    ti <- TS[[i]]
    
    #get all classes
    classes <- sapply(ti,class)
    
    
    
    #exclude any ensembles (For now)
    is.mat <- sapply(ti,is.matrix)
    ncolumns <- rep(0,length = length(is.mat)) 
    ncolumns[which(is.mat)] <- sapply(ti[which(is.mat)],ncol)
    
    if(any(ncolumns>1)){
      ti <- ti[-which(ncolumns>1)]
    }   
    
    
    #find which entries are vectors. Year and value should be. There could be more.
    al <- sapply(ti,length)
    
    #going to assume that we only want the longest ones here
    long <- which(al==max(al))
    
    if(!any(names(long)=="paleoData_values")){
      stop(paste0(as.character(i),": paleoData_values didn't show up as being the longest vector"))
    }
    
    if(!(any(names(long)=="year") | any(names(long)=="age") | any(names(long)=="depth") )){
      stop(paste0(as.character(i),": There must be an 'age', 'year', or 'depth' column that's the same length as paleoData_values"))
    }
    
    sdf <- suppressWarnings(tibble::as.tibble(ti[long]))
    
    #separate numeric and character values
    if(is.character(sdf$paleoData_values)){
      sdf$paleoData_values_char <- sdf$paleoData_values
      sdf$paleoData_values <- NA
    }
    
    
    #handle ts variables that are longer than 1, but not the full length by concatenating
    med <- ti[which(al<max(al) & al>1)]
    collapsed <- sapply(med, paste,collapse = ", ")
    ti[which(al<max(al) & al>1)] <- collapsed
    
    #check length again
    al2 <- sapply(ti,length)
    
    #replicate the metadata to each observation row
    short <- which(al2==1)
    mdf <- suppressWarnings(as.data.frame(ti[short]))
    
    #any columns in mdf not in pcolnames?
    if(any(!names(mdf) %in% pcolnames)){#if so, remove that from mdf
      nname <- names(mdf)[!names(mdf) %in% pcolnames]
      mdf <- dplyr::select(mdf, -nname) 
    }
    
    meta.df <- purrr::map_df(seq_len(nrow(sdf)), ~mdf)
    
    #combine them together
    tdf <- dplyr::bind_cols(sdf,meta.df)
    er <- nrow(tdf)+sr-1
    
    

    
    nm <- match(names(tdf),pcolnames)
    #if(i == 1){

    
    set(tidyData, i= sr:er,j = nm, tdf)
    
    # }else{
    #   
    #   set(tidyData,i = sr:er, j = which(pcolnames %in% names(tdf)),tdf$year)
    #   # nt <- try(set(tidyData,i = sr:er, j = which(names(tdf) %in% pcolnames),tdf),silent = T)
    #   # if(is.data.table(nt)){
    #   #   tidyData <- nt
    #   # }else{#try to fix it.
    #   #   comp <- arsenal::compare(tidyData,tdf)
    #   #   class1 <- unlist(comp$vars.summary$class.x)
    #   #   class2 <- unlist(comp$vars.summary$class.y)
    #   #   tc <- comp$vars.summary$var.x[which(class1 == "character" & class2 == "numeric")]
    #   #   for(tci in 1:length(tc)){
    #   #     tdf[tc[tci]] <- as.character(tdf[tc[tci]])
    #   #   }
    #   #   set(tidyData,i = sr:er, j = which(names(tdf) %in% pcolnames),tdf)
    #   #   }
    # }
    # 
    sr = er+1
    
  }
  #tidyData <- as.tibble(tidyData)
  tidyData <- dplyr::group_by(tidyData, .data$paleoData_TSid)
  return(tidyData)
}



#' @export
#' @family LiPD manipulation
#' @title pull variable out of TS object
#' @description pulls all instances of a single variable out of a TS
#' @param TS a LiPD Timeseries object
#' @param variable the name of variable in a TS object
#' @return a vector of the values, with NA representing instances without this variable.
pullTsVariable = function(TS,variable){
  allNames <- unique(unlist(sapply(TS,names)))
  
  #test for exact match
  which.var <- which(variable == allNames)
  if(length(which.var) == 0){#try a fuzzier search
    which.var <- which(grepl(pattern = variable,x = allNames,ignore.case = TRUE))
    if(length(which.var) == 1){#
      warning(paste0("Couldn't find exact match for '",variable,"', using ",allNames[which.var]," instead."))
    }else if(length(which.var) == 0){
      stop(paste0("Couldn't find any matches for '",variable,"', stopping"))
    }else{
      stop(paste0("Found no exact, but multiple near matches for '",variable,"'. Here they are: \n",paste0(allNames[which.var],collapse = "\n")))
    }
    variable <- allNames[which.var]  
  }
  
  #pull out the variable
  var <- sapply(TS,"[[",variable)
  
  
  if(is.list(var) & !grepl("author",variable) &!grepl("inCompilationBeta[0-9]+_compilationVersion",variable)){#if it's a list, try to unpack it. Unless it's author then don't
    if(length(unlist(var)) < length(var)){#there are some NULlS
      newVar <- matrix(NA,nrow = length(var))
      isNull <- sapply(var, is.null)
      newVar[which(!isNull)] <- unlist(var)
      var <- newVar
    }
  }
  
  return(var)
  
}
#' @export
#' @family LiPD manipulation
#' @title push variable into of TS object
#' @description pulls all instances of a single variable out of a TS
#' @param TS a LiPD Timeseries object
#' @param variable the name of variable in a TS object
#' @param vec a vector of data to be added to the TS object
#' @param createNew allow the function to create a new variable in the TS?
#' @return a vector of the values, with NA representing instances without this variable.
pushTsVariable = function(TS,variable,vec,createNew = FALSE){
  allNames <- unique(unlist(sapply(TS,names)))
  
  if(length(TS) != length(vec)){
    stop("the lengths of TS and vec must match!")
  }
  
  if(!createNew){
    #test for exact match
    which.var <- which(variable == allNames)
    
    if(length(which.var) == 0){#try a fuzzier search
      which.var <- which(grepl(pattern = variable,x = allNames,ignore.case = TRUE))
      if(length(which.var) == 1){#
        warning(paste0("Couldn't find exact match for '",variable,"', using ",allNames[which.var]," instead."))
      }else if(length(which.var) == 0){
        stop(paste0("Couldn't find any matches for '",variable,"', stopping"))
      }else{
        stop(paste0("Found no exact, but multiple near matches for '",variable,"'. Here they are: \n",paste0(allNames[which.var],collapse = "\n")))
      }
      variable <- allNames[which.var]  
    }
  }
  #loop over the variable (Is there a better solution for this? I couldn't find one.)
  for(i in 1:length(TS)){
    TS[[i]][[variable]] <- vec[i]
  }
  
  return(TS)
  
}

