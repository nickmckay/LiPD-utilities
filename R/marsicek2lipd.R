marsicek2lipd = function(filename,writeLiPD = FALSE){
  
  library(readxl)
  generateTSid = function(){
    return(paste0("M2L",paste0(sample(c(letters,0:9),size = 8,replace = TRUE),collapse="")))
  }

  md = read_excel(filename,1)
  cd = read_excel(filename,2,skip = 3)
  pd = read_excel(filename,3)
  
  #initialize a new lipd object
  L = list()
  
  #pull sitename from filename
  ss=strsplit(filename,"_")
  siteName = paste(unlist(ss[[1]][-length(ss[[1]])]),sep="",collapse="_")
  
  #assign some default metadata
  L$LiPDVersion = 1.2
  L$archiveType = "lake sediment"
  
  #read in metadata
  
  L$investigator = md[1,2]
  lastName = substr(L$investigator,1,regexpr("[^A-Za-z]",L$investigator)[1]-1)
  L$lastUpdated = md[2,2]
  L$dataContributor = md[3,2]
  
  if(!is.na(md[5,2])){
    L$pub[[1]]$citation = md[5,2]
    pubYear = substr(md[5,2],regexpr("[0-9]",md[5,2])[1],regexpr("[0-9]",md[5,2])[1]+3)
  }else{
    pubYear = "0"
  }
  
  L$geo$location = md[10,2]
  
  L$neotomaCoreID = as.numeric(md[12,2])
  L$geo$latitude = as.numeric(md[14,2])
  L$geo$longitude = as.numeric(md[15,2])
  L$geo$elevation = as.numeric(md[17,2])
  
  proxy = md[19,2] #for later use
  calibration = list()
  calibration$method = md[19,4] #for later use
  taxaList = md[21,2] #for later use
  pn=1;
  for(p in 26:28){
    if(!is.na(md[p,2])){
      pn = pn+1
      L$pub[[pn]]=list()
      L$pub[[pn]]$citation = md[p,2]
      
    }
  }
  
  L$geo$notes = md[29,2]
  
  
  #create a dataset name
  L$dataSetName = paste(c(siteName,lastName,pubYear),collapse = ".")
  
  
  ##Now pull in the chron section. 
  
  #remove data where all is NA
  allna = which(apply(is.na(cd),1,all))
  if(length(allna)>0){
  cdg = cd[-allna,]
  }else{
    cdg = cd
  }
  
  if(all(cdg[,5]==cdg[,4])){#then remove the younger column
    cdg = cdg[,-5]
  }else{
    stop("the older and younger columns are not the same. Stopping...")
  }
  
  chron  = list()
  var.names = c("ageType","sampleID","depth","age14CUncertainty","age14C","measurementMaterial","notes")
  units = c(NA,NA,"cm","yr 14C","yr 14C BP",NA,NA)
  for(i in 1:length(var.names)){
    chron[[i]]=list()
    chron[[i]]$variableName = var.names[i]
    chron[[i]]$values = cdg[,i]
    chron[[i]]$units = units[i]
    chron[[i]]$TSid = paste0(generateTSid(),"C");
  }
  chron$missingValue = "NA"
  #setup lists
  chd=list()
  chd[[1]]=list()
  chronMeasurementTable=list()
  chronMeasurementTable[[1]]=list()
  chd[[1]]$chronMeasurementTable[[1]]=chron
  
  L$chronData = chd 
  
  
  #Now paleodata section.
  #remove data where all is NA
  allna = which(apply(is.na(pd),1,all))
  if(length(allna)>0){
    pdg = pd[-allna,]
  }else{
    pdg = pd
  }
  paleo  = list()
  
  var.names = c("depth","age","temperatureWarmest","temperatureColdest","temperatureAnnual","precipitation")
  units = c("cm","yr 14C BP","deg C","deg C","deg C","mm")
  ci.season = c(NA,NA,"warmest month","coldest month","annual","annual")
  ci.variable= c(NA,NA,"T","T","T","P")
  ci.variableDetail= c(NA,NA,"air@surface","air@surface","air@surface","@surface")
  ci.direction = c(NA,NA,"positive","positive","positive","positive")
  cal.uncertainty = c(NA,NA,1.9,3.3,2.2,NA)
  
  for(i in 1:length(var.names)){
    paleo[[i]]=list()
    paleo[[i]]$TSid = paste0(generateTSid(),"P");
    paleo[[i]]$variableName = var.names[i]
    paleo[[i]]$values = pdg[,i]
    paleo[[i]]$units = units[i]
    if(!is.na(ci.season[i])){#then it's a climate variable and we want more!
      paleo[[i]]$proxy = proxy
      #climate interpretation section
      paleo[[i]]$climateInterpretation$variable = ci.variable[i]
      paleo[[i]]$climateInterpretation$variableDetail = ci.variableDetail[i]
      paleo[[i]]$climateInterpretation$season = ci.season[i]
      paleo[[i]]$climateInterpretation$interpDirection = ci.direction[i]
      #calibration info
      paleo[[i]]$calibration$method = calibration$method
      paleo[[i]]$calibration$methodDetail = taxaList
      paleo[[i]]$calibration$uncertainty = cal.uncertainty[i]    
      paleo[[i]]$calibration$uncertaintyType = "RMSE"
    }
    
  }
  paleo$missingValue = "NA"
  
  #setup lists
  phd=list()
  phd[[1]]=list()
  paleoMeasurementTable=list()
  paleoMeasurementTable[[1]]=list()
  phd[[1]]$paleoMeasurementTable[[1]]=paleo
  
  L$paleoData = phd 
  
  if(writeLiPD){
    #write to lipd
    library(lipdR)
    saveLipdFile(L,L$dataSetName)
  }
  return(L)
}