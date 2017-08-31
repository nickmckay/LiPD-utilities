#' Get csv "values" fields from metadata.
#' @export
#' @keywords internal
#' @param list d: Metadata
#' @param char dsn: Dataset name
#' @return list d2: Metadata / CSV
get_csv_from_metadata <- function(d, dsn){
  new <- list()
  new[["meta"]] <- d
  new[["csvs"]] <- list()
  if ("paleoData" %in% names(d)){
    new <- get_csv_from_section(new, "paleo", dsn)
  }
  if ("chronData" %in% names(d)){
    new <- get_csv_from_section(new, "chron", dsn)
  }
  return(new)
}

#' Get CSV from one section
#' csv.data format: [ some_filename.csv $columns.data ]
#' @export
#' @keywords internal
#' @param list dat: Metadata
#' @param char pc_1: paleo or chron
#' @param char dsn: Dataset name
#' @return list dat: Split data
get_csv_from_section <- function(dat, pc_1, dsn){
  new = list()
  d <- dat[["meta"]]
  csvs <- dat[["csvs"]]
  pc <- paste0(pc_1, "Data")
  tryCatch({
    if(pc %in% names(d)){
      if(!isNullOb(d[[pc]])){
        for (i in 1:length(d[[pc]])){
          crumbs_1 <- paste(dsn, pc_1, sep=".")
          if ("measurementTable" %in% names(d[[pc]][[i]])){
            crumbs_2 <- paste0(crumbs_1, i, "measurement")
            tmp <- get_csv_from_table(d[[pc]][[i]][["measurementTable"]], crumbs_2, csvs)
            d[[pc]][[i]][["measurementTable"]] <- tmp[["meta"]]
            csvs <- tmp[["csvs"]]
          } # end measurement
          
          
          if ("model" %in% names(d[[pc]][[i]])){
            crumbs_2 <- paste0(crumbs_1, i, "model")
            tmp <- get_csv_from_model(d[[pc]][[i]][["model"]], crumbs_2, csvs)
            d[[pc]][[i]][["model"]] <- tmp[["meta"]]
            csvs <- tmp[["csvs"]]
          }
        }
      }
    } 
  }, error=function(cond){
    print(paste0("Error: get_csv_from_section: ", cond))
    stop()
  })
  new[["meta"]] <- d
  new[["csvs"]] <- csvs
  return(new)
}
  
#' Parse metadata and csv from models
#' @export
#' @keywords internal
#' @param list models: Metadata
#' @param char crumbs: Crumbs
#' @param list csvs: CSV data
#' @return list new: Metadata / CSV
get_csv_from_model <- function(models, crumbs, csvs){
  new <- list()
  
  tryCatch({
    # Loop for each model
    for (i in 1:length(models)){
      
      # Summary
      if ("summaryTable" %in% names(models[[i]])){
        crumbs_2 <- paste0(crumbs, i, "summary")
        tmp <- get_csv_from_table(models[[i]][["summaryTable"]], crumbs_2, csvs)
        models[[i]][["summaryTable"]] <- tmp[["meta"]]
        csvs <- tmp[["csvs"]]
      }
      
      # Ensemble
      if ("ensembleTable" %in% names(models[[i]])){
        crumbs_2 <- paste0(crumbs, i, "ensemble")
        tmp <- get_csv_from_table(models[[i]][["ensembleTable"]], crumbs_2, csvs)
        models[[i]][["ensembleTable"]] <- tmp[["meta"]]
        csvs <- tmp[["csvs"]]
      }
      
      # Distribution
      if ("distributionTable" %in% names(models[[i]])){
        crumbs_2 <- paste0(crumbs, i, "distribution")
        tmp <- get_csv_from_table(models[[i]][["distributionTable"]], crumbs_2, csvs)
        models[[i]][["distributionTable"]] <- tmp[["meta"]]
        csvs <- tmp[["csvs"]]
      }
    }
  }, error=function(cond){
    print(paste0("Error: get_csv_from_model: ", cond))
  })
  new[["meta"]] <- models
  new[["csvs"]] <- csvs
  return(new)
}

#' Parse metadata and csv from list of tables
#' @export
#' @keywords internal
#' @param list tables: Metadata
#' @param char crumbs: Crumbs
#' @param list csvs: CSV data
#' @return list new: Metadata / CSV
get_csv_from_table <- function(tables, crumbs, csvs){
  new <- list()
  tryCatch({
    for (i in 1:length(tables)){
      crumbs_2 <- paste0(crumbs, i, ".csv")
      crumbs_3 <- paste0(crumbs, i)
      tmp <- get_csv_from_columns(tables[[i]])
      # Set csv in overall output
      csvs[[crumbs_2]] <- tmp[["csvs"]]
      # overwrite old table
      tables[[i]]<- tmp[["meta"]]
      # overwrite old filename
      tables[[i]][["filename"]]<- crumbs_2
      tables[[i]][["tableName"]] <- strsplit(crumbs_3, "\\.")[[1]][[2]]
    }
  }, error=function(cond){
    print(paste0("Error: get_csv_from_table: ", cond))
  })
  new[["meta"]] <- tables
  new[["csvs"]] <- csvs
  return(new)
}
  
#' Parse metadata and csv from columns
#' @export
#' @keywords internal
#' @param list table: Metadata
#' @return list new: Metadata / CSV
get_csv_from_columns <- function(table){
  tryCatch({
    # list to hold each column for this table
    vals <- list()
    new <- list()
    
    # if table and columns exist
    if (!is.null(table)){
      if (!is.null(table[["columns"]])){
        curr.num <- 1

        for (k in 1:length(table[["columns"]])){
          # add values for this column to the main list, then remove values
          if (!is.null(table[["columns"]][[k]][["values"]])){
            
            # Assume the table is an ensemble first, and get the 2nd dimension (cols) of the matrix
            len <- dim(table[["columns"]][[k]][["values"]])[[2]]
            if(is.null(len)){
              # Ah, it's NOT an ensemble table. Get the length of the values, which should always = 1. 
              len <- length(table[["columns"]][[k]][["values"]][[1]])
            }
            # remove the "number" entry for the column, then replace it with the index of this loop
            # however, if it's an ensemble table with many "numbers"/columns, then we'll keep it.
            if (len > 1){
              # Ensemble Table
              # the end of the range is the start col + the cols in the matrix
              # num.cols <- dim(table[["columns"]][[k]][["values"]])[2]
              # set the range as the number
              for (i in 1:len){
                vals[[length(vals)+1]] <- table[["columns"]][[k]][["values"]][,i]
              }
              nums <- create_range(curr.num, len)
              table[["columns"]][[k]][["number"]] <- nums
              # the beginning point for the next loop is right after the finish of this loop.
              curr.num <- curr.num + len
            }
            else if (len <= 1){
              vals[[curr.num]] <- table[["columns"]][[k]][["values"]]
              table[["columns"]][[k]][["number"]] <- curr.num
              curr.num <- curr.num + 1
            }
            # remove values from the column
            table[["columns"]][[k]][["values"]] <- NULL
          }
        }
      }
    }
  }, error=function(cond){
    print(paste0("Error: get_csv_from_columns: ", cond))
  })
  new[["meta"]] <- table
  new[["csvs"]] <- vals
  return(new)
}

