library(jsonlite)
library(stringr)
library(rjson)
library(TestPackage)

# input : .jsonld & .csv
# output: .Rdata

convert_to_rdata <- function(json_files, csv_files, j){
  old_json = json_files
  csv = csv_files
  name = j
  toR = list()
  json = list()

  new_dir = paste('~/Github/LiPD-utilities/R/test/', name, sep = "")

  # set the directory
  setwd(new_dir)

  for(i in old_json){
    old_json_data <- fromJSON(file = i)

    filename = old_json_data$dataSetName

    json$context = old_json_data$'@context'
    if(old_json_data$archiveType != ""){
      json$archiveType = old_json_data$archiveType
    }
    if(old_json_data$collectionName != ""){
      json$collectionName = old_json_data$collectionName
    }
    if(old_json_data$comments != ""){
      json$comments = old_json_data$comments
    }
    if(old_json_data$dataSetName != ""){
      json$dataSetName = old_json_data$dataSetName
    }
    if(old_json_data$pubYear != ""){
      json$pub$pubYear = old_json_data$pubYear
    }
    if(old_json_data$geo != ""){
      json$geo = old_json_data$geo
    }

    # get the paleoData column data from .jsonld file
    for(i in old_json_data$paleoData){
      if(i == old_json_data$paleoData$paleoDataTableName){
        json$paleoData[[i]]$filename = old_json_data$paleoData$filename
        for(j in 1:length(old_json_data$paleoData$columns)){
          for(k in old_json_data$paleoData$columns[[j]]$shortName){
            json$paleoData[[i]][[k]]$parameter = k
            json$paleoData[[i]][[k]]$units = old_json_data$paleoData$columns[[j]]$units
            json$paleoData[[i]][[k]]$dataType = old_json_data$paleoData$columns[[j]]$dataType
            if(length(json$paleoData[[i]][[k]]$units) != 0){
              json$paleoData[[i]][[k]]$values = csv_to_r(json$paleoData[[i]]$filename, json, j, json$paleoData[[i]][[k]]$units)
            }
          }
        }
      }
    }

    # get the chronData column data form .jsonld file
    for(i in old_json_data$chronData){
      if(i == old_json_data$chronData$chronDataTableName){
        json$chronData[[i]]$filename = old_json_data$chronData$filename
        for(j in 1:length(old_json_data$chronData$columns)){
          for(k in old_json_data$chronData$columns[[j]]$shortName){
            json$chronData[[i]][[k]]$parameter = k
            json$chronData[[i]][[k]]$units = old_json_data$chronData$columns[[j]]$units
            json$chronData[[i]][[k]]$dataType = old_json_data$chronData$columns[[j]]$dataType
            if(length(json$chronData[[i]][[k]]$units) != 0){
              json$chronData[[i]][[k]]$values = csv_to_r(json$chronData[[i]]$filename, json, j, json$chronData[[i]][[k]]$units)
            }
          }
        }
      }
    }

    print(json)

    if(old_json_data$chronData != ""){
      chron_filename = old_json_data$chronData$filename
    }

    if(old_json_data$paleoData != ""){
      paleo_filename = old_json_data$paleoData$filename
    }

    filenames = c(chron_filename, paleo_filename)

    toR[[filename]] = json

    # get final product once all of the data is together
    to_r(toR)
  }
}

csv_to_r <- function(filename, x, j, u){

  csv_file = filename
  json = x
  col_num = j
  units = u

  if(length(units) == 0){
    return("")
  }

  else{
    data = list()

    csv_table = read.csv(csv_file)
    csv = as.matrix(csv_table)

    #print(csv[, 1])

    data = csv[, col_num]
    #print(data)
    return(data)
  }
}

# pull out the csv table name from the filename
# i.e. 'ARC3.vare.2010s1.csv' -> 'returns s1' and
get_table_name <- function(json, filename){
  j = json
  file = filename
  remove = j$dataSetName

  if(grepl(remove, file)){
    name = unlist(strsplit(file, split = remove, fixed = TRUE))[2]
    n = unlist(strsplit(name, split = '.', fixed = TRUE))[1]
  }
  return(n)
}

# Final output of .Rdata file
# Takes in all .jsonld and .csv files
to_r <- function(toR){
  set = toR
  setwd('~/Github/LiPD-utilities/R/')
  saveRDS(set, "test.Rdata")
}

lipd_to_r <- function(directory){
  #just_in_case = '~/Github/LiPD-utilities/R/test'
  d = directory
  setwd(d)

  for(i in list.files(d)){
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
      new_dir = paste(d, j, sep = "")
      #print(new_dir)
      #print(getwd())
      #setwd(new_dir)
      for(k in list.files(new_dir)){
        # if the file ends in 'd' then it is a .jsonld file
        if(substring(k, nchar(k)) == "d"){
          json_files[count_json + 1] = k
          count_json = count_json + 1
        }

        # if the file ends in 'v' then it is a .csv file
        if(substring(k, nchar(k)) == "v"){
          csv_files[count_csv + 1] = k
          count_csv = count_csv + 1
        }
      }
      # if there are .jsonld files, then run, otherwise stop
      if(count_json > 0){
        convert_to_rdata(json_files, csv_files, j)
      }
    }
  }
}
