library(jsonlite)
library(stringr)
library(rjson)

# input : .jsonld & .csv
# output: .Rdata

convert_to_rdata <- function(json_files, csv_files){
  json = json_files
  setwd('~/GitHub/LiPD-utilities/R/test')
  for(i in json){
    json_data <- fromJSON(file = i)
    x = json_data
  }
  #print(json_data$chronData)
  #x <- data.frame(context = json_data$`@context`)
  #x$archiveType = json_data$archiveType
  #x$collectionName = json_data$collectionName
  #x$comments = json_data$comments
  #x$dataSetName = json_data$dataSetName
  #x$pubYear = json_data$pubYear
  #x$geo$geometry$type = json_data$geo$geometry$type
  #x$geo$geometry$coordinates = json_data$geo$geometry$coordinates
  #x$geo$properties$siteName = json_data$geo$properties$siteName
  #x$paleoData$paleoDataTableName = json_data$paleoData$paleoDataTableName
  #x$paleoData$filename = json_data$paleoData$filename
  #x$paleoData$columns = json_data$paleoData$columns
  #x$chronData$chronDataTableName = json_data$chronData$chronDataTableName
  #x$chronData$columns = json_data$chronData$columns
  #print(x)
  
  filename = x$dataSetName
  jsonld_to_r(x, filename)
}

jsonld_to_r <- function(json_data, filename){
  json = json_data
  json$filename = filename
  print(json)
  saveRDS(json, "test.Rdata")
}

csv_to_r <- function(){
  
  println("Will complete after jsonld_to_r is completed")
  
}

run <- function(){
  all_files = list()
  csv_files = list()
  json_files = list()
  count_json = 1
  count_csv = 1
  
  setwd("~/GitHub/LiPD-utilities/R")
  
  for(i in list.files("~/GitHub/LiPD-utilities/R/test")){
    if(substring(i, nchar(i)) == "d"){
      json_files[count_json] = i
      count_json = count_json + 1
    }
    if(substring(i, nchar(i)) == "v"){
      csv_files[count_csv] = i
      count_csv = count_csv + 1
    }
  
  }
  convert_to_rdata(json_files, csv_files)
}

run()