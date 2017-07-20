###############################################
## Read LiPDs - Merge
## Merge metadata and csv into one LiPD object
###############################################

#' Using the given metadata dictionary, retrieve CSV data from CSV files, and insert the CSV
#' values into their respective metadata columns.
#' @export
#' @keywords internal
#' @param list d: Metadata
#' @return list d: Metadata
merge_csv_metadata <- function(d){
  # Read in CSV data
  csvs <- read_csv_from_file()
  # Run for each section that exists
  if ("paleoData" %in% names(d)){
    d[["paleoData"]] <- merge_csv_section(d[["paleoData"]], "paleo", csvs)
  }
  if ("chronData" %in% names(d)){
    d[["chronData"]] <- merge_csv_section(d[["chronData"]], "chron", csvs)
  }
  return(d)
}

#' Merge CSV into each section
#' @export
#' @keywords internal
#' @param list section: Metadata
#' @param char crumbs: paleo or chron
#' @param list csvs: CSV, sorted by filename
#' @return list section: Metadata
merge_csv_section <- function(section, crumbs, csvs){
  for (i in 1:length(section)){
    # Measurement
    if ("measurementTable" %in% names(section[[i]])){
      section[[i]][["measurementTable"]] <- merge_csv_table(section[[i]][["measurementTable"]], paste0(crumbs, i, "measurement"), csvs)
    }
    # Model
    if("model" %in% names(section[[i]])){
      section[[i]][["model"]] <- merge_csv_model(models, paste0(crumbs, i, "model"), csvs)
    }
  }
  return(section)
}


#' Merge CSV into each model
#' @export
#' @keywords internal
#' @param  list models: Metadata
#' @param char crumbs: Crumbs
#' @param list csvs: CSV data
#' @return list models: Metadata
merge_csv_model <- function(models, crumbs, csvs){

  # ?????
  # model <- vector(mode="list",length=length(dat))
  for (i in 1:length(models)){
    if("summaryTable" %in% names(models[[i]])){
      models[[i]][["summaryTable"]] <- merge_csv_table(models[[i]][["summaryTable"]], paste0(crumbs, i, "measurement"), csvs)
    }
    if("ensembleTable" %in% names(models[[i]])){
      models[[i]][["ensembleTable"]] <- merge_csv_table(models[[i]][["ensembleTable"]], paste0(crumbs, i, "ensemble"), csvs)
    }
    if("distributionTable" %in% names(models[[i]])){
      models[[i]][["distributionTable"]] <- merge_csv_table(models[[i]][["distributionTable"]], paste0(crumbs, i, "distribution"), csvs)
    }
  }
  return(models) 
}

  
#' Merge CSV data into each table
#' @export
#' @keywords internal
#' @param  list models: Metadata
#' @param char crumbs: Crumbs
#' @param list csvs: CSV data
#' @return list models: Metadata
merge_csv_table <- function(tables, crumbs, csvs){
  for (i in 1:length(tables)){
    filename <- tables[[i]][["filename"]]
    if (!is.null(filename)){
      csv.cols <- csvs[[filename]]
      meta.cols <- tables[[i]][["columns"]]
      tables[[i]][["columns"]] <- merge_csv_columns(csv.cols, meta.cols)
      # insert crumbs. this is the standardized table name
      tables[[i]][["tableName"]] <- paste0(crumbs, i)
      # remove filename. we have the values imported, so we dont need it anymore. we'll make a new standarized one!
      tables[[i]][["filename"]] <- NULL
    }
  }
  return(tables)
}


#' Merge values into each column
#' @export
#' @keywords internal
#' @param list csv.cols: Values, sorted by column
#' @param list meta.cols: Metadata, sorted by column
#' @return list meta.cols: Metadata
merge_csv_columns <- function(csv.cols, meta.cols){
  for (i in 1:length(meta.cols)){
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


