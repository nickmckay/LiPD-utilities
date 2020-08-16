#' Extract time series from LiPD data
#' @export
#' @author Chris Heiser
#' @description Create a time series from a library of LiPD datasets. A Time series is a flattened version of LiPD data that can be queried and filtered for easier data analysis.
#' @param D LiPD data, sorted by dataset name : list
#' @param whichtables : char: Options: "all", "summ", "meas", "ens" : Table type to output in the time series.
#' @param mode : char: Options: "paleo", "chron"
#' @return ts:  Time series : list
#' @examples 
#' D <- readLipds()
#' ts <- extractTs(D)
#' 
extractTs= function(D, whichtables = "all", mode = "paleo"){
  
  TS <- list()
  # TOP FUNCTION
  # Check if this is one or multiple datasets. 
  # Backup full data to lipd space (for collapseTs). 
  # Loop datasets and send to next function (extract1) ONE at a time for processing
  time_id = set_ts_lipd(D)
  # Flag that stops looping if this is a single dataset. Otherwise, flag never sets and continues looping for N datasets.
  breakFlag=FALSE
  
  # Loop for each dataset
  for(d in 1:length(D)){
    if(breakFlag){
      break
    }
    # Single dataset? We'll know if the dataSetName is in the root.
    if(any(names(D)=="dataSetName")){
      L=D # set as the only dataset
      breakFlag= TRUE
    }
    # Multiple Datasets? The only other option.
    else{
      L = D[[d]] # grab one dataset
    }
    
    #skip if missing paleo or chronData
    if(!any(names(L) == paste0(mode,"Data"))){
      next
    }
    
    
    # Test that a DSN exists, and 'whichtables'    
    validate_parameters(D, L, whichtables, mode)
    
    # Run ONE dataset through for processing
    new_entries <- extract(L, whichtables, mode, time_id)
    for(add in 1:length(new_entries)){
      step1 <- try(new_entries[[add]])
      if(class(step1)=="try-error"){
       print("uhoh") 
      }else{
      TS[[length(TS)+1]] <- new_entries[[add]] 
      }
    }
  }
  
  return(TS)
}

extract=function(L, whichtables, mode, time){
  # Processes ONE dataset into multiple TimeSeries entries
  root <- list()
  
  ### TS META
  root[["mode"]] <- mode
  root[["timeID"]] <- time
  root[["whichtables"]] <-whichtables
  
  root <- extract_root(L, root)
  root <- extract_geo(L, root)
  root <- extract_pub(L, root)
  root <- extract_funding(L, root)
  
  # Now start processing the data tables and making TSOs
  new_tsos <- extract_pc(L, root, whichtables, mode)
  
  return(new_tsos)
}

extract_pc=function(L, root, whichtables, mode){
  TS <- list()
  # Creates TimeSeries entries from the target tables within ONE dataset
  pc <- "paleoData"
  if(mode == "chron"){
    pc <- "chronData"
  }
  
  #Loop through paleoData objects
  for(p1 in 1:length(L[[pc]])){
    if(whichtables %in% c("all", "meas")){
      if(length(L[[pc]][[p1]]$measurementTable) > 0){
        for(p2 in 1:length(L[[pc]][[p1]]$measurementTable)){
          TABLE = L[[pc]][[p1]]$measurementTable[[p2]]
          if(!is.null(TABLE)){
            current = root
            current[[paste0(mode,"Number")]] <- p1
            current[["tableNumber"]] <-p2
            TS = extract_table(TABLE, "meas", pc, TS, current)
          }
        }
      }
    }
    if(whichtables != "meas"){
      for(p2 in 1:length(L[[pc]][[p1]]$model)){
        # Get ONE model entry
        MODEL <- L[[pc]][[p1]]$model[[p2]]
        # Make a copy of root
        current = root
        # Get the method data, to pair with the ens and summ tables. 
        current = extract_method(MODEL$method, current)
        # Process summaryTables as needed
        if(whichtables %in% c("all", "summ")){
          # loop for each summaryTable entry
          for(p3 in 1:length(MODEL$summaryTable)){
            TABLE <- MODEL$summaryTable[[p3]]
            if(!is.null(TABLE)){
              current[[paste0(mode,"Number")]] <- p1
              current[["modelNumber"]] <- p2
              current[["tableNumber"]] <- p3
              TS <- extract_table(TABLE, "summ", pc, TS, current)
            }
          }
        }
        if(whichtables %in% c("all", "ens")){
          # loop for each ensembleTable entry
          if(length(MODEL$ensembleTable) > 0){
            for(p3 in 1:length(MODEL$ensembleTable)){
              TABLE <- MODEL$ensembleTable[[p3]]
              if(!is.null(TABLE)){
                current[[paste0(mode,"Number")]] <- p1
                current[["modelNumber"]] <- p2
                current[["tableNumber"]] <- p3
                TS <- extract_table(TABLE, "ens", pc, TS, current)
              }
            }
          }
        }
      }
    }#end loop through paleo measurement tables
  }#end loop through paleoData objects
  
  return(TS)
}

extract_table=function(table_data, table_type, pc, TS, current){
  idx <- length(TS)
  current[["tableType"]] <- table_type
  # Extract all the special columns
  current = extract_special(table_data, current)
  # Extract all table root items. Anything that is not a column
  current <- extract_table_root(table_data, current, pc)
  
  # Do not exclude the special columns. We need time series entries for those as well. ALL columns. 
  columnsToGrab = which(sapply(table_data,is.list))
  for(ctg in columnsToGrab){
    idx <- idx + 1
    ## Grab a column, and for the current root data. We'll add on the column data, and that's it! it'll be a full TSO
    column = table_data[[ctg]]
    current_fork = current
    current_fork = extract_column(column, current_fork, pc)
    TS[[idx]] <- current_fork
  }
  return(TS)
}


extract_special= function(table_data, current){
  # Special columns need to be included with all time series entries
  specialColumns = c("age","year","depth","ageEnsemble")
  specCols = which((tolower(names(table_data)) %in% tolower(specialColumns)) & sapply(table_data,is.list))
  for(sc in specCols){
    #only assign in values and units for now
    #use the correct names
    nameToUse <- specialColumns[which(tolower(names(table_data)[sc]) == tolower(specialColumns))]
    current[[paste0(nameToUse,"Units")]] = table_data[[sc]]$units
    current[[nameToUse]] = table_data[[sc]]$values
  }
  return(current)
}

extract_column=function(column, current_fork, pc){
  
  #grab data and metadata from this column
  excludeColumn = c("number", "tableName")
  
  # get any items that are NOT a list, and add them to this TS entry. i.e. anything that's NOT interpretation blocks or other indexed blocks.
  colGrab = which(!(names(column) %in% excludeColumn) & !sapply(column,is.list))
  #assign in needed column data and metadata
  for(colc in colGrab){
    current_fork[[paste0(pc, "_",names(column)[colc])]] = column[[colc]] 
  }
  
  #look through subsequent lists for hierarchical indexed metadata - i.e. interpretation
  hierData = which(sapply(column,is.list))
  #loop through all of these. 
  #Currently, this only handles numbered instances (like interpretation) at the second level...
  for(hi in hierData){
    thisHierData = column[[hi]]
    
    for(hieri in 1:length(thisHierData)){
      #is it an unnamed, instanced, list?
      if(is.null(names(thisHierData))){
        # yes, we want to add in a number:
        thdNumber = as.character(hieri)
      }else{
        # no, no number
        thdNumber = ""
      }
      
      if(!is.list(thisHierData[[hieri]])){
        #assign in non lists
        current_fork[[paste0(names(column)[hi],thdNumber,"_",names(thisHierData)[hieri])]] = thisHierData[[hieri]] 
      }else{
        #grab everything inside that list
        doubleHierGrab = 1:length(thisHierData[[hieri]]) 
        
        #assign in
        for(dhieri in doubleHierGrab){
          # unnamed list, i.e. interpretation 
          if(is.null(names(thisHierData[[hieri]]))){
            #if so, we want to add in a number:
            for(unni in 1:length(thisHierData[[hieri]])){
              for(inunni in 1:length(names(thisHierData[[hieri]][[dhieri]]))){
                current_fork[[paste0(names(column)[hi],thdNumber,"_",names(thisHierData)[hieri],as.character(unni),"_",names(thisHierData[[hieri]][[dhieri]])[inunni])]] = thisHierData[[hieri]][[dhieri]][[inunni]]
              }
            }
            
          }else{
            # named list, i.e. calibration | physicalSample | hasResolution
            current_fork[[paste0(names(column)[hi],thdNumber,"_",names(thisHierData[[hieri]])[dhieri])]] = thisHierData[[hieri]][[dhieri]]
          }
          
        }#end second hierarchy assignment loop
      }#end second hierarchy  loop
    }
  }#end hier data loop
  return(current_fork)
}

# Extract the method data from a model, and flatten it for the TS
extract_method=function(model, root){
  method <- model$method
  excludeMethod = c()
  metGrab = which(!(names(method) %in% excludeMethod) & !sapply(method,is.list))
  for(m in metGrab){#assign in needed paleo stuff
    root[[paste0("method_",names(method)[m])]] = method[[m]] 
  }
  return(root)
}

extract_table_root=function(table_data, current, pc){
  ##Paleo data table level
  #grab metadata from this measurement table
  excludePaleo = c()
  tableGrab = which(!(names(table_data) %in% excludePaleo) & !sapply(table_data,is.list))
  for(entry in tableGrab){#assign in needed paleo stuff
    current[[paste0(pc, "_",names(table_data)[entry])]] = table_data[[entry]] 
  }
  return(current)
}

validate_parameters=function(D, L, whichtables, mode){
  
  # dataSetName not provided. Exit(1), we can't continue without it. 
  if(!any(names(L)=="dataSetName")){
    stop(names(L),"has no dataSetName. This is forbidden.")
  }
  # The target paleo or chron is not provided. Exit(1), Cannot process what's not there.
  if(!any(names(L)=="paleoData") && mode == "paleo"){
    stop(paste(L$dataSetName),"has no paleoData. This is forbidden.")
  } else if(!any(names(L)=="chronData") && mode == "chron"){
    stop(paste(L$dataSetName),"has no chronData. This is forbidden.")
  }
  
  # Was a valid mode given? 
  if(!(mode %in% c("paleo", "chron"))){
    stop("Mode must be either 'paleo' or 'chron'")
  }
  # Was a valid table type given?
  if(!(whichtables %in% c("all", "ens", "meas", "summ"))){
    stop("Try again: whichtables parameter must be 'all', 'ens', 'summ' or 'meas'")
  }
  
  return()
}

set_ts_lipd=function(L){
  # We want consistency across TMP storage. Create a hierarchy of "TMP_ts_storage$<timeID>$<dataSetName>$<data>...." regardless of single or multi dataset. 
  if("dataSetName" %in% names(L)){
    # Single dataset. Create a DSN layer above the data before assigning to lipd Env
    D <- list()
    D[[L$dataSetName]] <- L
  } else {
    # Multi datasets are organized by DSN. No work needed
    D <- L
  }
  # Generate a timestamp
  # time_id = as.character(as.numeric(Sys.time()))
  time_id = format(Sys.time(), "%m%d%y-%H%M%S")
  
  # Look for an existing timeseries storage in the lipd space
  tmp_storage <- list()
  if(exists("TMP_ts_storage", where = lipdEnv)){
    tmp_storage <- get("TMP_ts_storage", envir=lipdEnv)
  }
  # assign data to lipd space
  tmp_storage[[time_id]] <- D
  assign("TMP_ts_storage", tmp_storage, envir=lipdEnv)
  
  return(time_id)
}

extract_root=function(L, root){
  ### ROOT
  excluderoot = c("@context")
  rootGrab = which(!(names(L) %in% excluderoot) & !sapply(L,is.list))
  for(b in rootGrab){#assign in needed rootlevel stuff
    root[[names(L)[b]]] = L[[b]] 
  }
  return(root)
}

extract_funding=function(L,root){
  ### FUNDING
  for(fu in 1:length(L$funding)){
    FU = L$funding[[fu]]
    funGrab = which( (names(FU) %in% names(FU)) & !sapply(FU,is.list))#grab everything here
    for(ffu in funGrab){#assign in needed rootlevel stuff
      root[[paste0("funding",as.character(fu),"_",names(FU)[ffu])]]  = FU[[ffu]] 
    }
  }
  return(root)
}

extract_pub=function(L,root){
  ### PUB
  # NOTE - I'm not currently differentiating between pub and dataPub. NPM 4.17.17
  for(pu in 1:length(L$pub)){
    PUB = L$pub[[pu]]
    #pull DOI out if needed
    if(any(names(PUB)=="identifier")){
      if(is.list(PUB$identifier)){
        PUB$doi = PUB$identifier[[1]]$id
      }
    }
    #pull out authors
    if(any(names(PUB)=="author")){
      if(is.list(PUB$author)){
        root[[paste0("pub",as.character(pu),"_author")]] = PUB$author
      }
    }else if(any(names(PUB)=="authors")){#this is here for common misterminology. 
      if(is.list(PUB$authors)){
        root[[paste0("pub",as.character(pu),"_author")]] = PUB$authors
      }
    }
    
    pubGrab = which( (names(PUB) %in% names(PUB)) & !sapply(PUB,is.list))#grab everything here
    for(ppu in pubGrab){#assign in needed rootlevel stuff
      root[[paste0("pub",as.character(pu),"_",names(PUB)[ppu])]]  = PUB[[ppu]] 
    }
  }
  return(root)
}

extract_geo=function(L,root){
  ### GEO
  excludeGeo = c("type")
  geoGrab = which(!(names(L$geo) %in% excludeGeo) & !sapply(L$geo,is.list))
  for(g in geoGrab){#assign in needed geo stuff
    root[[paste0("geo_",names(L$geo)[g])]] = L$geo[[g]] 
  }
  return(root)
}

#' Split interpretation by scope
#' @export
#' @param TS 
#' @import stringr
#' @return split TS
#' @export
splitInterpretationByScope <- function(TS){

  sTS <- TS
  
  for(i in 1:length(TS)){
    #how many interpretations?
    mts <- TS[[i]]
    tsNames <- names(mts)
    iNames <- tsNames[which(grepl("^interpretation[0-9]_",tsNames))]
    
    if(length(iNames) > 0){#there are some
      snames <- str_split(iNames,"_")
      upref <- unique(sapply(snames,"[[",1))
      ro <- str_split(upref,"interpretation")
      
      maxIntNum <- max(as.numeric(sapply(ro,"[[",2)))
      lenIntNum <- length(upref)
      
      
      
      if(maxIntNum==lenIntNum){
        nInt <- lenIntNum
      }else{
        stop("theres a discrepancy about the number of interpretations")
      }
      
      scopeType <- as.data.frame(matrix(NA,nrow = nInt,ncol = 2))
      for(n in 1:nInt){
        thisScope <- mts[[str_c("interpretation",as.character(n),"_scope")]]
        if(is.null(thisScope)){
          #normally
          #stop("All interpretations must have a scope")
          thisScope <- "climate"
        }
        
        scopeType[n,1] <- thisScope
        
        
        if(n==1){
          scopeType[n,2] <- 1
        }else{#count how many others match this scope
          prev <- sum(thisScope==scopeType[,1],na.rm = T)
          scopeType[n,2] <- prev
        }
        
        
        #loop through all the variables and assign
        sch <- str_c("interpretation",as.character(n))
        ti <-  tsNames[grepl(sch,tsNames)]
        #remove scope from this
        # ti <- ti[-which(ti==str_c(sch,"_scope"))]
        
        
        #add them in
        for(v in ti){
          thisVar <- str_remove(v,sch)
          mts[[str_c(scopeType[n,1],"Interpretation",as.character(scopeType[n,2]),thisVar)]] <- mts[[v]]
          mts[[v]] <- NULL
        }
        
      }#end loop through interpretations
      
    }#end Has interpretations
    sTS[[i]] <- mts
  }#end loop through TS
  
  return(sTS)
}



#' Combine interpretations by scope
#' @export
#' @importFrom stats na.omit
#' @param sTS 
#' @return a regular Timeseries structure
combineInterpretationByScope <- function(sTS){
  
  cTS <- sTS
  scopes = c('climate','isotope','ecology','chronology');
  
  for(i in 1:length(sTS)){
    mts <- sTS[[i]]
    
    fnames <- names(mts)
    #remove any preexisting fields
    interpNames <- str_which(fnames,"interpretation[0-9]")
    if(length(interpNames>0)){
      print("Removing 'interpretationX_*' fields, which we are about to create...")
      mts[interpNames] <- NULL
    }
    fnames <- names(mts)
    ti <- 0
    for(s in scopes){
      sts <- str_c(s,'Interpretation')
      
      #how many interpertaions with this scope
      
      nInterp <- length(unique(na.omit(str_extract(fnames,str_c(sts,"[0-9]")))))
      if(nInterp>0){
        for(ni in 1:nInterp){
          ti <- ti+1 #new interp number
          
          inames <- fnames[str_which(fnames,str_c(sts,as.character(ni),"_"))]
          for(ini in inames){
            varName <- str_remove(ini,str_c(sts,as.character(ni)))
            newName <- str_c("interpretation",as.character(ti),varName)
            mts[[newName]] <- mts[[ini]]
            mts[[ini]] <- NULL
            
          }
          mts[[str_c("interpretation",as.character(ti),"_scope")]] <- s
          
        }
      }
      
    }
    cTS[[i]] <- mts
  }
  
  return(cTS)
}  
