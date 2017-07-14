###############################################
## Read LiPDs - Merge
## Merge metadata and csv into one LiPD object
###############################################

#' Using the given metadata dictionary, retrieve CSV data from CSV files, and insert the CSV
#' values into their respective metadata columns. Checks for both paleoData and chronData tables.
#' @export
#' @keywords internal
#' @param list d: Metadata
#' @return list d: Metadata
merge_csv_metadata <- function(d){
  # Read in CSV data
  csv.data <- read_csv_from_file()
  # Run for each section that exists
  if ("paleoData" %in% names(d)){
    d[["paleoData"]] <- merge_csv_section(d[["paleoData"]], "paleoData", csv.data)
  }
  if ("chronData" %in% names(d)){
    d[["chronData"]] <- merge_csv_section(d[["chronData"]], "chronData", csv.data)
  }
  return(d)
}

#' Merge csv numeric data into the metadata columns
#' @export
#' @keywords internal
#' @param list d: Metadata
#' @param char pc: paleoData or chronData
#' @param list csv.data: CSV, sorted by filename
#' @return list d: Metadata
merge_csv_section <- function(section, pc){

    #top: d$paleoData[[i]]
    #meas: d$paleoData[[i]]measurementTable[[j]]
    #model: d$paleoData[[i]]model
  
    for (i in 1:length(section)){

      # measurement
      if ("measurementTable" %in% names(section[[i]])){
        for (j in 1:length(section[[i]][["measurementTable"]])){
          table <- section[[i]][["measurementTable"]][[j]]
          filename <- table[["filename"]]
          if (!is.null(filename)){
            csv.cols <- csv.data[[filename]]
            meta.cols <- table[["columns"]]
            section[[i]][["measurementTable"]][[j]][["columns"]] <- add_csv_to_columns(csv.cols, meta.cols)
          }
        }
      } # end measurement

      # model
      if("model" %in% names(section[[i]])){
        dat <- hasData(section[[i]], "model")
        if (!is.null(dat)){
          section[[i]][["model"]] <- merge_csv_model(models, pc, crumbs, csv.data)
        }

      }# end model

    } # end section
  return(section)
}


#' Add csv data to each column in chron model
#' @export
#' @keywords internal
#' @param  list models: Metadata
#' @param char pc: paleoData or chronData
#' @param char crumbs: Hierarchy crumbs
#' @return list models: Metadata
merge_csv_model <- function(models, pc, crumbs){
  #summary: models[[i]]summaryTable[[j]]
  #distribution: models[[i]]distributionTable[[j]]
  #ensemble: models[[i]]ensembleTable[[j]]
  
  model <- vector(mode="list",length=length(dat))
  
  for (j in 1:length(section[[i]][["model"]])){
    

    # summary
    table <- section[[i]][["model"]][[j]][["summaryTable"]]
    filename <- table[["filename"]]
    if (!is.null(filename)){
      csv.cols <- csv.data[[filename]]
      meta.cols <- table[["columns"]]
      columns <- add_csv_to_columns(csv.cols, meta.cols)
      toCopy <- which(names(table)!="columns")
      for(tt in toCopy){
        model[[j]]$summaryTable[[names(table)[tt]]] <- table[[names(table)[tt]]]
      }
      model[[j]]$summaryTable$columns <-columns
      
    }
    
    # ensemble table
    dat <- hasData(section[[i]][["model"]][[j]], "ensembleTable")
    if (!is.null(dat)){
      table <- section[[i]][["model"]][[j]][["ensembleTable"]]
      filename <- table[["filename"]]
      if (!is.null(filename)){
        csv.cols <- csv.data[[filename]]
        meta.cols <- table[["columns"]]
        columns <- add_csv_to_columns(csv.cols, meta.cols)
        toCopy <- which(names(table)!="columns")
        for(tt in toCopy){
          model[[j]]$ensembleTable[[names(table)[tt]]] <- table[[names(table)[tt]]]
        }
        model[[j]]$ensembleTable$columns <- columns
      }
    }
    
    # distribution tables
    # d$chronData[[i]]$model[[j]]$distributionTable
    dat <- hasData(section[[i]][["model"]][[j]], "distributionTable")
    if (!is.null(dat)){
      # data exists, create a new dist table of same length. 
      distributionTable <- vector(mode = "list",length = length(section[[i]][["model"]][[j]][["distributionTable"]]))
      if(length(distributionTable)>=1){
        for (k in 1:length(section[[i]][["model"]][[j]][["distributionTable"]])){
          table <- section[[i]][["model"]][[j]][["distributionTable"]][[k]]
          filename <- table[["filename"]]
          # filename required. if no filename, we cannot get csv data.
          if (!is.null(filename)){
            csv.cols <- csv.data[[filename]]
            meta.cols <- table[["columns"]]
            columns  <- add_csv_to_columns(csv.cols, meta.cols)
            toCopy <- which(names(table)!="columns")
            for(tt in toCopy){
              distributionTable[[k]][[names(table)[tt]]] <- table[[names(table)[tt]]]
            }
            distributionTable[[k]]$columns <- columns
          }
        } # end loop
        model[[j]]$distributionTable <- distributionTable
      } # end length
    } # end distribution
    
    #add in anything that we didn't recreate
    icm <- names(section[[i]][["model"]][[j]])
    cmnames <- names(model[[j]])
    toAdd <- which(!(icm %in% cmnames))
    for(ta in 1:length(toAdd)){
      model[[j]][[icm[toAdd[ta]]]] <- section[[i]][["model"]][[j]][[icm[toAdd[ta]]]]
    }
  } ##end model loop
}


#' Add csv data to each column in a list of columns
#' @export
#' @keywords internal
#' @param list csv.cols: Values, sorted by column
#' @param list meta.cols: Metadata, sorted by column
#' @return list meta.cols: Metadata
add_csv_to_columns <- function(csv.cols, meta.cols){

  col.ct <- length(meta.cols)
  # go through the columns
  for (i in 1:col.ct){

    # special case for ensemble tables - a "column" that holds many columns
    if (is.list(meta.cols[[i]][["number"]]) | length(meta.cols[[i]][["number"]]) > 1){
      tmp <- list()
      nums <- meta.cols[[i]][["number"]]
      for (j in 1:length(nums)){
        tmp[[j]] <- csv.cols[[nums[[j]]]]
      }
      # turn the columns into a matrix - transpose
      meta.cols[[i]][["values"]] <- t(do.call(rbind, tmp))
    }
    else {
      # assign values. already numeric
      meta.cols[[i]][["values"]] <- csv.cols[[meta.cols[[i]][["number"]]]]
    }

  }
  return(meta.cols)
}


