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
    
    for (i in which(names(out_names)!="notes")) {
      if(is.numeric(D[[num]]$paleoData$s1[[i]]$values)){
        tryCatch(x <- D[[num]]$paleoData$s1[[i]]$values, error=function(e) NULL)
        tryCatch(bind[[i]] <- x, error=function(e) NULL)
      }
    }
    
    #print(bind[[2]])
    longest_column <- get_longest_column(bind)
    print(longest_column)
    new <- bind[[1]]
    count <- 1
    for(i in 2:length(bind)){
      new[[count]] <- cbind(bind[[i]])
      count <- count + 1
    }
    
    print(new)
    
    #creating the csv file
    directory <- paste('output/', current, '/', sep = "")
    path <- paste(directory, current, '.csv', sep = "")
    dir.create(directory, showWarnings = FALSE,  mode = "0777")
    file.create(path, showWarnings = FALSE)
    
    write.csv(new, file = path, row.names = FALSE, col.names = FALSE)
    
    print(current)
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
  "geo" : {
      "geometry" : {
          "coordinates" : {
              "latitude" : "",
              "longitude" : "",
              "elevation" : ""
          },
          "type" : ""
      },
      "properties" : {
          "siteName" : ""
      }
  },
  "paleoData" : {
      "columns" : [],
      "filename" : "",
      "paleoDataTableName" : ""
  },
  "pub" : {
  }
}'
  
  json_data <- fromJSON(template)
  
  
  # sets all of the json data in the .jsonld file
  json_data$archiveType <- D[[count]]$archiveType
  json_data$collectionName <- ""
  json_data$comments <- ""
  json_data$dataSetName <- D[[count]]$dataSetName
  json_data$geo$geometry$coordinates$latitude <- D[[count]]$geo$latitude
  print(D[[count]]$geo$latitude)
  json_data$geo$geometry$coordinates$longitude <- D[[count]]$geo$longitude
  json_data$geo$geometry$coordinates$elevation <- D[[count]]$geo$elevation
  json_data$geo$geometry$type <- D[[count]]$geo$type
  json_data$geo$properties$siteName <- D[[count]]$geo$siteName
  json_data$paleoData$columns <- make_columns(count)
  json_data$paleoData$filename <- paste(file_name, ".csv")
  #json_data$paleoData$paleoDataTableName <-
  
  doi <- ""
  json_data$pub <- make_pub(count, doi)
  
  #json_data$pub$pubYear <- D[[count]]$pubYear
  x <- toJSON(json_data, pretty = TRUE, byrow = TRUE)
  directory <- paste('output/', file_name, '/', sep="")
  path <- paste(directory, file_name, '.jsonld', sep="")
  print(path)
  dir.create(directory, showWarnings = FALSE,  mode = "0777")
  file.create(path, showWarnings = FALSE, mode = "0777")
  writeLines(x, path)
  print(file_name)
}

# make_columns will return the correct amount of paleoData columns
make_columns <- function(count){
  num <- count
  index <- 0
  
  json <- '{
    "number": "",
    "dataType": "",
    "shortName": "",
    "longName": "",
    "units": "",
    "parameter": "",
    "climateInterpretation": {
    } 
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
      json_data$longName <- ''
      tryCatch(json_data$units <- D[[num]]$paleoData$s1[[count]]$units, error=function(e) NULL)
      tryCatch(json_data$parameter <- D[[num]]$paleoData$s1[[count]]$parameter, error=function(e) NULL)
      climInterp = ""
      json_data$climateInterpretation <- make_climateInterpretation(count, climInterp)
      #tryCatch(json_data$climateInterpretation$parameter <- D[[num]]$paleoData$s1[[count]]$parameter, error=function(e) NULL)
      
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

# make_climateInterpretation will eventually return the correct 
# climateInterpretation information
make_climateInterpretation <- function(count, climInterp){
  num <- count
  ci <- climInterp
  index <- 0
  
  if(ci == ""){
    return("")
  }
  else{
    json <- '{
      "parameter": "",
      "interpDirection": "",
      "parameterDetail": "",
      "seasonality": ""
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

# get_longest_column returns the length of the longest columns
# of the csv columns. May be unneeded now
get_longest_column <- function(bind){
  longest_length <- 0
  for(i in 1:length(bind)){
    if(longest_length < length(bind[[i]])){
      longest_length <- length(bind[[i]])
    }
  }
  return(longest_length)
}

run <- function(){
  direct <- getwd()
  if(direct != "/Users/austin/Desktop/R"){
    setwd("Desktop/R")
  }
  file_names <- names(D)
  num <- 1
  for (i in 1:length(file_names)) {
    #jsonld_out(names(D)[i], i)
    csv_out(names(D)[i], i)
  }
}
run()