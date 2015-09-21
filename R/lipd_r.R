library(jsonlite)
library(stringr)
library(rjson)

# input : .jsonld & .csv
# output: .Rdata

convert_to_rdata <- function(json_files, csv_files){
  json = json_files
  csv = csv_files
  
  # set the directory
  setwd('~/GitHub/LiPD-utilities/R/test')
  
  for(i in json){
    json_data <- fromJSON(file = i)
    x = json_data
    x <- data.frame(context = json_data$`@context`)
    #print(json_data)
    filename = json_data$chronData$filename
    #print(filename)
    
    # put all of the .jsonld and .csv data together
    returned_data = csv_to_r(csv, x, filename)
    
    # get final product once all of the data is together
    to_r(returned_data)
  }
}

csv_to_r <- function(csv, x, filename){
  csv_files = csv
  json = x
  n = filename
  
  for(i in csv_files){
    paleoDataTableName = json_data$paleoData$paleoDataTableName
    for(j in length(1:20)){
      data[j] = get_column_data(n, csv_files)
    }
    json$paleoDataTableName = data
  }
}

# this is to get the names that the .csv files will be labeled as
get_json_data <- function(filename){
  print("Skip")
}

# get the *.csv data from the corresponding column
get_column_data <- function(filename, csv_files){
  name = filename
  csv = csv_files
  columns = list()
  for(i in csv){
    if(length(grep(name, i)) > 0){
      for(j in length(1:20)){
        col = read.csv(i)
        print(col)
        for(k in col){
          if(is.integer(k)){
            columns[j] = col
            print(columns)
          }
        }
      }
    }
    return(columns)
  }
}

# Final output of .Rdata file
# Takes in all .jsonld and .csv files
to_r <- function(returned_data){
  toR = returned_data
  saveRDS(toR, "test.Rdata")
  #print(toR)
}

run <- function(){
  
  setwd("~/GitHub/LiPD-utilities/R")
  
  for(i in list.files("~/GitHub/LiPD-utilities/R/test")){
    # get all of the different folders
    csv_files = list()
    json_files = list()
    file_list = list()
    
    count_json = 0
    count_csv = 0
    count_files = 0

    file_list[count_files + 1] = i
    for(j in file_list){
      # if a .jsonld file, add to json_files
      new_dir = paste("~/GitHub'LiPD-utilities/R/test/", j)
      for(k in new_dir){
        if(substring(i, nchar(i)) == "d"){
          json_files[count_json + 1] = i
          count_json = count_json + 1
        }
        # if a .csv file, add to csv_files
        if(substring(i, nchar(i)) == "v"){
          csv_files[count_csv + 1] = i
          count_csv = count_csv + 1
        }
      }
      # if there are .jsonld files, then run. Otherwise stop.
      if(count_json > 0){
        convert_to_rdata(json_files, csv_files)
      }
    }
  }
}

run()