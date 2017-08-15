#' Extract time series from LiPD data
#' @export
#' @author Nick McKay
#' @description Create a time series from a library of LiPD datasets. A Time series is a flattened version of LiPD data that can be queried and filtered for easier data analysis.
#' @param D LiPD data, sorted by dataset name : list
#' @return ts:  Time series : list
#' @examples 
#' D <- readLipds()
#' ts <- extractTs(D)
#' 
extractTs= function(D, chron=NULL){
  
  TS=list()
  ts=0
  mode <- "paleo"
  if(!missing(chron)){
    if(chron==TRUE){
      mode <- "chron"}
  }

  breakFlag=FALSE
  
  for(d in 1:length(D)){
    if(breakFlag){
      break
    }
    # Is this a single dataset? We'll know if the dataSetName is in the root.
    if(any(names(D)=="dataSetName")){
      L=D
      breakFlag= TRUE
    }
    # Dataset library? That's our only other assumption if the first "if" doesn't work.  
    else{
      L = D[[d]] #grab just one LiPD file
    }
    
    # dataSetName not provided. Exit(1), we can't continue without it. 
    if(!any(names(L)=="dataSetName")){
      stop(names(D)[d],"has no dataSetName. This is forbidden.")
    }
    
    # paleoData not provided. Exit(1), we can't continue without it.
    if(!any(names(L)=="paleoData")){
      stop(paste(L$dataSetName),"has no paleoData. This is forbidden.")
    }
    
    #Loop through paleoData objects
    for(p in 1:length(L$paleoData)){
      #Loop through paleoMeasurementTables
      for(pm in 1:length(L$paleoData[[p]]$measurementTable)){
        PM = L$paleoData[[p]]$measurementTable[[pm]]#grab this measurmentTable
        # Special columns need to 
        specialColumns = c("age","year","depth","ageEnsemble")
        # columnsToGrab = which(!(names(PM) %in% specialColumns) & sapply(PM,is.list))
        # Do not exclude the special columns. We need time series entries for those as well. ALL columns. 
        columnsToGrab = which(sapply(PM,is.list))
        for(ctg in columnsToGrab){#which columns to grab? These are your timeseries objets
          ts = ts+1
          TS[[ts]]=list()
          ###BASE LEVEL
          excludeBase = c("@context")
          TS[[ts]][["mode"]] <- mode
          baseGrab = which(!(names(L) %in% excludeBase) & !sapply(L,is.list))
          for(b in baseGrab){#assign in needed baselevel stuff
            TS[[ts]][[names(L)[b]]] = L[[b]] 
          }
          
          
          ###PUB
          #NOTE - I'm not currently differentiating between pub and dataPub. NPM 4.17.17
          for(pu in 1:length(L$pub)){
            PUB = L$pub[[pu]]
            #pull DOI out if needed
            if(any(names(PUB)=="identifier")){
              if(is.list(PUB$identifier)){
                PUB$DOI = PUB$identifier[[1]]$id
              }
            }
            pubGrab = which( (names(PUB) %in% names(PUB)) & !sapply(PUB,is.list))#grab everything here
            for(ppu in pubGrab){#assign in needed baselevel stuff
              TS[[ts]][[paste0("pub",as.character(pu),"_",names(PUB)[ppu])]]  = PUB[[ppu]] 
            }
          }#END PUB
          
          ###FUNDING
          for(fu in 1:length(L$funding)){
            FU = L$funding[[fu]]
            funGrab = which( (names(FU) %in% names(FU)) & !sapply(FU,is.list))#grab everything here
            for(ffu in funGrab){#assign in needed baselevel stuff
              TS[[ts]][[paste0("funding",as.character(fu),"_",names(FU)[ffu])]]  = FU[[ffu]] 
            }
          }#END FUNDING
          
          ####GEO
          excludeGeo = c("type")
          geoGrab = which(!(names(L$geo) %in% excludeBase) & !sapply(L$geo,is.list))
          for(g in geoGrab){#assign in needed geo stuff
            TS[[ts]][[paste0("geo_",names(L$geo)[g])]] = L$geo[[g]] 
          }
          ###END GEO
          
          ##PaleoData
          
          ##Paleo data table level
          #assign in paleo and measurementTable Numbers
          TS[[ts]]$paleoData_paleoNumber = p
          TS[[ts]]$paleoData_measurementTableNumber = pm
          
          #grab metadata from this measurement table
          pal = L$paleoData[[p]]$measurementTable[[pm]]
          excludePaleo = c()
          palGrab = which(!(names(pal) %in% excludePaleo) & !sapply(pal,is.list))
          for(palp in palGrab){#assign in needed paleo stuff
            TS[[ts]][[paste0("paleoData_",names(pal)[palp])]] = pal[[palp]] 
          }
          
          ##Paleodata Column level
          coldata = pal[[ctg]]
          
          #grab data and metadata from this column
          excludeColumn = c("number", "tableName")
          colGrab = which(!(names(coldata) %in% excludeColumn) & !sapply(coldata,is.list))
          
          for(colc in colGrab){#assign in needed column data and metadata
            TS[[ts]][[paste0("paleoData_",names(coldata)[colc])]] = coldata[[colc]] 
          }
          
          #look through subsequent lists for hierarchical metadata
          hierData = which(sapply(coldata,is.list))
          #loop through all of these. 
          for(hi in hierData){#Currently, this only handles numbered instances (like interpretation) at the second level...
            thisHierData = coldata[[hi]]
            #hierGrab = which(!sapply(thisHierData,is.list))
            hierGrab = 1:length(thisHierData)
            
  
            
            
            for(hieri in hierGrab){
              
              #is it an unnamed, instanced, list?
              if(is.null(names(thisHierData))){#if so, we want to add in a number:
                thdNumber = as.character(hieri)
              }else{
                thdNumber = ""
              }
              
              
              
              
              if(!is.list(thisHierData[[hieri]])){
              #assign in non lists
              TS[[ts]][[paste0(names(coldata)[hi],thdNumber,"_",names(thisHierData)[hieri])]] = thisHierData[[hieri]] 
              
              }else{
              #hierListGrab = which(sapply(thisHierData,is.list))#find lists within the hierData (this is the last level for now)
              #for(hieriListi in hierListGrab){
                doubleHierGrab = 1:length(thisHierData[[hieri]]) #grab everything inside that list
                
                
                
                #assign in
                for(dhieri in doubleHierGrab){
                  #is it an unnamed, instanced, list?
                  if(is.null(names(thisHierData[[hieri]]))){#if so, we want to add in a number:
                    for(unni in 1:length(thisHierData[[hieri]])){
                      for(inunni in 1:length(names(thisHierData[[hieri]][[dhieri]])))
                        TS[[ts]][[paste0(names(coldata)[hi],thdNumber,"_",names(thisHierData)[hieri],as.character(unni),"_",names(thisHierData[[hieri]][[dhieri]])[inunni])]] = thisHierData[[hieri]][[dhieri]][[inunni]]
                    }
                    
                  }else{#then just assign in normally
                    TS[[ts]][[paste0(names(coldata)[hi],thdNumber,"_",names(thisHierData[[hieri]])[dhieri])]] = thisHierData[[hieri]][[dhieri]]
                    
                  }
                  
                }#end second hierarchy assignment loop
              }#end second hierarchy  loop
            }
          }#end hier data loop
          
          
          #now special columns
          specCols = which((names(PM) %in% specialColumns) & sapply(PM,is.list))
          for(sc in specCols){
            #only assign in values and units for now
            TS[[ts]][[paste0(names(PM)[sc],"Units")]] = PM[[sc]]$units
            TS[[ts]][[names(PM)[sc]]] = PM[[sc]]$values
            
          }
           
          
          ##END PALEODATA!! Woohoo!
          
          # Raw chronData
          TS[[ts]][["raw"]] <- L
          # if(any(names(L)=="chronData")){
          #   TS[[ts]]["chronData"] = L$chronData
          # }
          # # Raw paleoData
          # TS[[ts]]["paleoData"] = L$paleoData
          
        }#end columns to grab (each TS entry)
        
      }#end loop through paleo measurement tables
    }#end loop through paleoData objects
    
    
    
    
  }
  
  return(TS)
}