library(jsonlite)
library(stringr)

# input : .Rdata
# output: .jsonld & .csv in new folder

csv_out <- function(current, num){
  #print(num)
  
  out_names <- D[[num]]$paleoData$s1
  
  if(length(names(out_names)) == 0){
    print("empty")
  }
  else{
    bind <- list()
    
    for (i in 1:length(out_names)) {
      try(if(is.numeric(D[[num]]$paleoData$s1[[i]]$values)){
        tryCatch(x <- D[[num]]$paleoData$s1[[i]]$values, error=function(e) NULL)
        tryCatch(bind[[i]] <- x, error=function(e) NULL)
      }
      )
    }
      
new <- bind[[1]]
for(i in 2:length(bind)){
  new=cbind(new,bind[[i]])
}

#creating the csv file
#check if output folder
dir.create("output", showWarnings = FALSE,  mode = "0777")    
directory <- paste('output/', current, '/', sep = "")
#print(directory)
path <- paste(directory, current, '.csv', sep = "")
dir.create(directory, showWarnings = FALSE,  mode = "0777")
file.create(path, showWarnings = FALSE)
write.table(new, file = path, row.names = FALSE, col.names = FALSE,sep=",")

  }

}

jsonld_out <- function(current, num){
  
  file_name <- current
  
  count <- num
  
  
  template <- '{

  "@context" : "context.jsonld",
  "archiveType" : "",
  "collectionName" : "",
  "comments" : "",
  "dataSetName" : "",
  "pubYear" : "",
  "geo" : {
      "geometry" : {
          "type" : "",
          "coordinates" : ""
      },
      "properties" : {
          "siteName" : ""
      }
  },
  "paleoData" : {
      "paleoDataTableName" : "",
      "filename" : "",
      "columns" : []
  }
}'
  
  json_data <- fromJSON(template)
  
  
  # sets all of the json data in the .jsonld file
  json_data$archiveType <- D[[count]]$archiveType
  json_data$collectionName <- ""
  json_data$comments <- ""
  json_data$dataSetName <- D[[count]]$dataSetName
  json_data$pubYear <- D[[count]]$pub$pubYear
  json_data$geo$geometry$coordinates <- get_coordinates(count)
  json_data$geo$geometry$type <- D[[count]]$geo$type
  json_data$geo$properties$siteName <- D[[count]]$geo$siteName
  paleoDataTableName = names(D[[count]]$paleoData)
  json_data$paleoData$paleoDataTableName <- paleoDataTableName
  json_data$paleoData$filename <- paste(file_name, ".csv", sep = "")
  json_data$paleoData$columns <- make_columns(count)
  
  #doi <- ""
  #json_data$pub <- make_pub(count, doi)
  
  x <- toJSON(json_data, pretty = TRUE, byrow = TRUE)
  setwd('/Users/austin/Desktop/R')
  dir.create("output", showWarnings = FALSE,  mode = "0777")    
  directory <- paste('output/', current, '/', sep = "")
  #print(directory)
  path <- paste(directory, current, '.jsonld', sep = "")
  dir.create(directory, showWarnings = FALSE,  mode = "0777")
  file.create(path, showWarnings = FALSE, mode = "0777")
  writeLines(x, path)
  print(file_name)
}

get_coordinates <- function(count){
  
  longitude = D[[count]]$geo$longitude
  latitude = D[[count]]$geo$latitude
  elevation = D[[count]]$geo$elevation
  
  coordinates = list(longitude, latitude, elevation)
  
  print(coordinates)
  return(coordinates)
}

# make_columns will return the correct amount of paleoData columns
make_columns <- function(count){
  num <- count
  index <- 0
  
  json <- '{
    "number": "",
    "dataType": "",
    "shortName": "",
    "units": "",
    "parameter": ""
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
  
  else {
    count <- 1
    for(i in 1:index){
      json_data$number <- count
      tryCatch(json_data$dataType <- class(D[[num]]$paleoData$s1[[count]]$values[1]), error=function(e) NULL)
      tryCatch(json_data$shortName <- D[[num]]$paleoData$s1[[count]]$parameter, error=function(e) NULL)
      tryCatch(json_data$units <- D[[num]]$paleoData$s1[[count]]$units, error=function(e) NULL)
      tryCatch(json_data$parameter <- D[[num]]$paleoData$s1[[count]]$parameter, error=function(e) NULL)
      tryCatch(json_data$climateInterpretation$parameter <- D[[num]]$paleoData$s1[[count]]$climateInterpretation$parameter, error=function(e) NULL)
      tryCatch(json_data$climateInterpretation$interpDirection <- D[[num]]$paleoData$s1[[count]]$climateInterpretation$interpDirection, error=function(e) NULL)
      tryCatch(json_data$climateInterpretation$parameterDetail <- D[[num]]$paleoData$s1[[count]]$climateInterpretation$parameterDetail, error=function(e) NULL)
      tryCatch(json_data$climateInterpretation$seasonality <- D[[num]]$paleoData$s1[[count]]$climateInterpretation$seasonality, error=function(e) NULL)
      
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
    
    #else {
    #count <- 1
    #       for(i in 1:index){
    #         json_data$number <- count
    #         tryCatch(json_data$dataType <- class(D[[num]]$paleoData$s1[[count]]$values[1]), error=function(e) NULL)
    #         tryCatch(json_data$shortName <- D[[num]]$paleoData$s1[[count]]$parameter, error=function(e) NULL)
    #         json_data$longName <- ''
    #         tryCatch(json_data$units <- D[[num]]$paleoData$s1[[count]]$units, error=function(e) NULL)
    #         tryCatch(json_data$parameter <- D[[num]]$paleoData$s1[[count]]$parameter, error=function(e) NULL)
    #         #tryCatch(json_data$climateInterpretation$parameter <- D[[num]]$paleoData$s1[[count]]$parameter, error=function(e) NULL)
    #         json_data$climateInterpretation$interpDirection <- ''
    #         json_data$climateInterpretation$parameterDetail <- ''
    #         json_data$climateInterpretation$seasonality <- ''
    #         
    #         return_value[[i]] <- json_data
    #         count <- count + 1
    #       }
    #       return(return_value)
    #     }
  }
}

run <- function(){
 # print(getwd())
  file_names <- names(D)
  num <- 1
  for (i in 1:length(file_names)) {
    jsonld_out(names(D)[i], i)
    csv_out(names(D)[i], i)
  }
}
#setwd("~/Desktop/R")
load("~/GitHub/LiPD-utilities/R/LiPD_R_Data.Rdata")
run()