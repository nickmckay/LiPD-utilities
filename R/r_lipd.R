library(jsonlite)
library(stringr)

# input : .Rdata
# output: .jsonld & .csv in new folder
# new update

csv_out_paleoData <- function(current, num, n){
  name = n
  
  out_names <- D[[num]]$paleoData[[name]]
  
  if(length(names(out_names)) == 0){
    print("empty")
  }
  else{
    bind <- list()
    
    for (i in 1:length(out_names)) {
      tryCatch(if(is.numeric(D[[num]]$paleoData[[name]][[i]]$values) || is.character(D[[num]]$paleoData[[name]][[i]]$values)){
        tryCatch(x <- D[[num]]$paleoData[[name]][[i]]$values, error=function(e) NULL)
        tryCatch(bind[[i]] <- x, error=function(e) NULL)
      }, error=function(e) NULL)
    }
    
    new <- bind[[1]]
    for(i in 2:length(bind)){
      new=cbind(new,bind[[i]])
    }
    
    #creating the csv file
    #check if output folder
    dir.create("output", showWarnings = FALSE,  mode = "0777")    
    directory <- paste('output/', current, '/', sep = "")
    path <- paste(directory, current, name, '.csv', sep = "")
    print(directory)
    dir.create(directory, showWarnings = FALSE,  mode = "0777")
    file.create(path, showWarnings = FALSE)
    write.table(new, file = path, row.names = FALSE, col.names = FALSE,sep=",")
    
  }
}

csv_out_chronData <- function(current, num, n){
  name = n
  
  print(name)
  
  out_names <- D[[num]]$chronData[[name]]
  
  if(length(names(out_names)) == 0){
    print("empty")
  }
  
  else{
    bind <- list()
    
    for (i in 1:length(out_names)) {
      tryCatch(if(is.numeric(D[[num]]$chronData[[name]][[i]]$values) || is.character(D[[num]]$chronData[[name]][[i]]$values)){
        tryCatch(x <- D[[num]]$chronData[[name]][[i]]$values, error=function(e) NULL)
        tryCatch(bind[[i]] <- x, error=function(e) NULL)
      }, error=function(e) NULL)
    }
    
    tryCatch(new <- bind[[1]], error=function(e) NULL)
    
    if(length(bind) > 1){
      for(i in 2:length(bind)){
        new = cbind(new, bind[[i]])
      }
    }
    
    #creating the csv file
    #check if output folder
    dir.create("output", showWarnings = FALSE,  mode = "0777")    
    directory <- paste('output/', current, '/', sep = "")
    path <- paste(directory, current, name, '.csv', sep = "")
    print(directory)
    dir.create(directory, showWarnings = FALSE,  mode = "0777")
    file.create(path, showWarnings = FALSE)
    tryCatch(write.table(new, file = path, row.names = FALSE, col.names = FALSE, sep=","), error=function(e) NULL)
  }
}

jsonld_out <- function(current, num){
  
  file_name <- current
  
  count <- num
  
  #json_data <- fromJSON(template)
  
  json_data=list()
  # sets all of the json data in the .jsonld file
  json_data$archiveType <- D[[count]]$archiveType
  json_data$dataSetName <- D[[count]]$dataSetName
  for (p in 1:length(D[[count]]$pub)){
    json_data$pub[[p]]$pubYear <- D[[count]]$pub[p]$pubYear
  }
  json_data$geo$geometry$coordinates <- get_coordinates(count)
  json_data$geo$geometry$type =D[[count]]$geo$type  
  json_data$geo$properties$siteName <- D[[count]]$geo$siteName
  
  
  for(i in length(D[[count]]$paleoData)){
    paleoDataTableName = names(D[[count]]$paleoData)[i]
    json_data$paleoData[[i]]$paleoDataTableName <- paleoDataTableName
    json_data$paleoData[[i]]$filename <- paste(file_name, paleoDataTableName, ".csv", sep = "")
    json_data$paleoData[[i]]$columns <- make_columns_paleoData(count, i)
    csv_out_paleoData(names(D)[num], num, names(D[[num]]$paleoData)[i])
  }
  
  if(length(D[[count]]$chronData) != 0){
    for(i in length(D[[count]]$chronData)){
      chronDataTableName = names(D[[count]]$chronData)[i]
      json_data$chronData[[i]]$chronDataTableName <- chronDataTableName
      json_data$chronData[[i]]$filename <- paste(file_name, chronDataTableName, ".csv", sep = "")
      json_data$chronData[[i]]$columns <- make_columns_chronData(count, i)
      csv_out_chronData(names(D)[num], num, names(D[[num]]$chronData)[i])
    }
  }
  
  x <- toJSON(json_data, pretty = TRUE, byrow = TRUE,auto_unbox=TRUE)
  setwd('~/GitHub/LiPD-utilities/R/')
  dir.create("output", showWarnings = FALSE,  mode = "0777")    
  directory <- paste('output/', current, '/', sep = "")
  print(directory)
  path <- paste(directory, current, '.jsonld', sep = "")
  dir.create(directory, showWarnings = FALSE,  mode = "0777")
  file.create(path, showWarnings = FALSE, mode = "0777")
  
  print(path)
  writeLines(x, path)
  print(file_name)
  }

# returns [latitude, longitude, elevation]
get_coordinates <- function(count){
  
  longitude = D[[count]]$geo$longitude
  latitude = D[[count]]$geo$latitude
  elevation = D[[count]]$geo$elevation
  
  if(is.null(elevation) | is.na(elevation)){
    coordinates = c(longitude, latitude)
  }else{
    coordinates = c(longitude, latitude, elevation)
  }
  
  #print(coordinates)
  return(coordinates)
}

# make_columns will return the correct amount of paleoData columns
make_columns_paleoData <- function(count, i){
  num <- count
  index <- 0
  name <- i
  
  
  #json <- '{}'
  
  
  file <- D[[num]]$paleoData[[names(D[[num]]$paleoData)[name]]]
  
  for (i in D[[num]]$paleoData[[names(D[[num]]$paleoData)[name]]]){
    index <- index + 1
  }
  
  return_value <- vector("list", index)
  
  if (index == 0){
    return('')
  }
  
  else {
    int <- 1
    count <- 1
    for(i in 1:index){
      json_data <- list()
      tryCatch(json_data$shortName <- D[[num]]$paleoData[[names(D[[num]]$paleoData)[name]]][[count]]$parameter, error=function(e) NULL)
      tryCatch(json_data$dataType <- class(D[[num]]$paleoData[[names(D[[num]]$paleoData)[name]]][[count]]$values[1]), error=function(e) NULL)
      tryCatch(json_data$units <- D[[num]]$paleoData[[names(D[[num]]$paleoData)[name]]][[count]]$units, error=function(e) NULL)
      tryCatch(json_data$climateInterpretation$parameter <- D[[num]]$paleoData[[names(D[[num]]$paleoData)[name]]][[count]]$climateInterpretation$parameter, error=function(e) NULL)
      tryCatch(json_data$climateInterpretation$interpDirection <- D[[num]]$paleoData[[names(D[[num]]$paleoData)[name]]][[count]]$climateInterpretation$interpDirection, error=function(e) NULL)
      tryCatch(json_data$climateInterpretation$parameterDetail <- D[[num]]$paleoData[[names(D[[num]]$paleoData)[name]]][[count]]$climateInterpretation$parameterDetail, error=function(e) NULL)
      tryCatch(json_data$climateInterpretation$seasonality <- D[[num]]$paleoData[[names(D[[num]]$paleoData)[name]]][[count]]$climateInterpretation$seasonality, error=function(e) NULL)
      print(json_data)
      if(length(json_data) == 0){
        print("emtpy")
      }
      else{
        json_data$number = int
        return_value[[int]] <- json_data
        int = int + 1
      }
      count <- count + 1
      
    }
    return(return_value)
  }
}

make_columns_chronData <- function(count, i){
  num <- count
  index <- 0
  name <- i
  

  
  json_data <- list()
  
  file <- D[[num]]$chronData[[names(D[[num]]$chronData)[name]]]
  
  for (i in D[[num]]$chronData[[names(D[[num]]$chronData)[name]]]){
    index <- index + 1
  }
  
  return_value <- vector("list", index)
  
  if (index == 0){
    return('')
  }
  
  else {
    count <- 1
    for(i in 1:index){
      json_data$number <- count
      tryCatch(json_data$dataType <- class(D[[num]]$chronData[[names(D[[num]]$chronData)[name]]][[count]]$values[1]), error=function(e) NULL)
      tryCatch(json_data$shortName <- D[[num]]$chronData[[names(D[[num]]$chronData)[name]]][[count]]$parameter, error=function(e) NULL)
      tryCatch(json_data$units <- D[[num]]$chronData[[names(D[[num]]$chronData)[name]]][[count]]$units, error=function(e) NULL)
      tryCatch(json_data$parameter <- D[[num]]$chronData[[names(D[[num]]$chronData)[name]]][[count]]$parameter, error=function(e) NULL)
      tryCatch(json_data$climateInterpretation$parameter <- D[[num]]$chronData[[names(D[[num]]$chronData)[name]]][[count]]$climateInterpretation$parameter, error=function(e) NULL)
      tryCatch(json_data$climateInterpretation$interpDirection <- D[[num]]$chronData[[names(D[[num]]$chronData)[name]]][[count]]$climateInterpretation$interpDirection, error=function(e) NULL)
      tryCatch(json_data$climateInterpretation$parameterDetail <- D[[num]]$chronData[[names(D[[num]]$chronData)[name]]][[count]]$climateInterpretation$parameterDetail, error=function(e) NULL)
      tryCatch(json_data$climateInterpretation$seasonality <- D[[num]]$chronData[[names(D[[num]]$chronData)[name]]][[count]]$climateInterpretation$seasonality, error=function(e) NULL)
      
      return_value[[i]] <- json_data
      count <- count + 1
    }
    return(return_value)
  }
  
  }

# make_pub will return all of the DOI information if there is any
make_pub <- function(count, doi){
  num <- count
  DOI <- doi
  index <- 0
  
  if(DOI == ""){
    return("")
  }
  else{
    json <- '{
    "DOI": "",
    "author": {},
    "edition": "",
    "identifier": {},
    "journal": "",
    "pages": "",
    "publisher": "",
    "title": "",
    "volume": ""
  }'
    
    json_data <- fromJSON(json)
    
    
    file <- D[[num]]$paleoData$s1
    
    for (i in D[[num]]$paleoData$s1){
      index <- index + 1
    }
    
    return_value <- vector("list", index)
    
    if (index == 0){
      return('')
    }
  }
}

run <- function(){
  file_names <- names(D)
  #for (i in 1:length(file_names)) {
   # print(i)
    jsonld_out(names(D)[1], 1)
  #}
}

load("~/GitHub/LiPD-utilities/R/LiPD_R_Data.Rdata")
run()