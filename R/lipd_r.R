library(jsonlite)
library(stringr)
library(rjson)

# input : .jsonld & .csv
# output: .Rdata

convert_to_rdata <- function(json_files, csv_files, j){
  json = json_files
  csv = csv_files
  name = j
  
  # set the directory
  setwd(paste('~/GitHub/LiPD-utilities/R/test/', name, sep = ""))
  
  for(i in json){
    json_data <- fromJSON(file = i)
    
    if(json_data$chronData != ""){
      chron_filename = json_data$chronData$filename
    }
    
    if(json_data$paleoData != ""){
      paleo_filename = json_data$paleoData$filename
    }
    
    filenames = c(chron_filename, paleo_filename)
    
    # put all of the .jsonld and .csv data together
    returned_data = csv_to_r(csv, json_data, filenames)

    # get final product once all of the data is together
    to_r(returned_data)
  }
}

csv_to_r <- function(csv, x, filenames){

  csv_files = csv
  json = x
  files = filenames
  
  for(i in csv_files){
    paleoDataTableName = json$paleoData$paleoDataTableName
    chronDataTableName = json$chronData$chronDataTableName
    
    paleoName = json$paleoData$filename
    chronName = json$chronData$filename
    
    paleo_data = list()
    chron_data = list()
    
    for(j in length(1:20)){
      # build individual columns from the csv files
      d = get_column_data(paleoName, csv_files, j)
      if(d != ""){
        paleo_data[j] = d
      }
    }
    
    json$paleoDataTableName = paleo_data
    json$chronDataTableName = chron_data
  }
  return(json)
}

# get the *.csv data from the corresponding column
get_column_data <- function(filename, csv_files, j){
  name = filename
  csv = csv_files
  num = 1
  
  columns = list()
  
  file = read.csv(name)
  for(i in read.csv(name)[ ,num:num]){
    if(is.integer(i)){
      columns[j] = i
    }
  }
  
  return(columns)
}

# Final output of .Rdata file
# Takes in all .jsonld and .csv files
to_r <- function(returned_data){
  toR = returned_data
  #print(toR)
  setwd("~/GitHub/LiPD-utilities/R")
  saveRDS(toR, "test.Rdata")
  print(toR)
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
      new_dir = paste("~/GitHub/LiPD-utilities/R/test/", j, sep = "")
      setwd(new_dir)
      for(k in list.files(new_dir)){
        if(substring(k, nchar(k)) == "d"){
          json_files[count_json + 1] = k
          count_json = count_json + 1
        }
      
        # if a .csv file, add to csv_files
        if(substring(k, nchar(k)) == "v"){
          csv_files[count_csv + 1] = k
          count_csv = count_csv + 1
        }
      }
      # if there are .jsonld files, then run. Otherwise stop.
      if(count_json > 0){
        convert_to_rdata(json_files, csv_files, j)
      }
    }
  }
}

run()