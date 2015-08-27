library(jsonlite)
library(stringr)
library(rjson)

# input : .jsonld & .csv
# output: .Rdata

jsonld_to_r <- function(json_data){
  json = json_data
  saveRDS(json, "test.Rdata")
}

csv_to_r <- function(){
  
  println("Will complete after jsonld_to_r is completed")
  
}

run <- function(){
  directory = "/test"
  all_files = list()
  csv_files = list()
  json_files = list()
  count = 1
  
  setwd("~/GitHub/LiPD-utilities/R/test")
  
  for(i in "~/GitHub/LiPD-utilities/R/test"){
    all_files[count] = i
    count = count + 1
  }
  count = 1
  for(i in all_files){
    if(substring(i, nchar(i)) == ".jsonld"){
      json_files[count] = i
      count = count + 1
    }
  }
  count = 1
  for(i in all_files){
    if(substring(i, nchar(i)) == ".csv"){
      csv_files[count] = i
      count = count + 1
    }
  }
  
  print(json_files)
  print(csv_files)
}

run()