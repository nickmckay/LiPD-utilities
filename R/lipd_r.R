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
  json_file = "test.jsonld"
  json_data = fromJSON(file = json_file)
  jsonld_to_r(json_data)
}
load("~/GitHub/LiPD-utilities/R/LiPD_R_Data.Rdata")
run()