#' Change index-by-number to index-by-variableName
#' @export
#' @keywords internal
#' @param list d: Metadata
#' @return list d: Metadata
idx_num_to_name <- function(d){
  if ("paleoData" %in% names(d)){
    d[["paleoData"]] <- import_section(d[["paleoData"]])
  }
  if ("chronData" %in% names(d)){
    d[["chronData"]] <- import_section(d[["chronData"]])
  }
  d <- index_geo(d)
  return(d)
}

#' Change index-by-number for one section
#' @export
#' @keywords internal
#' @param list section: Metadata
#' @return list section: Metadata
import_section<- function(section){
  # section
  tryCatch({
    if (!is.null(section)){
      for (i in 1:length(section)){
        if("measurementTable" %in% names(section[[i]])){
          section[[i]][["measurementTable"]] <- idx_table_by_name(section[[i]][["measurementTable"]])
        }
        if("model" %in% names(section[[i]])){
          section[[i]][["model"]] <- import_model(section[[i]][["model"]])
        }
      }
    }
  }, error=function(cond){
    print(paste0("Error: import_section: ", cond));
  })
  return(section)
}

#' Index model tables
#' @export
#' @keywords internal
#' @param list models: Metadata
#' @return list models: Metadata
import_model <- function(models){
  tryCatch({
    for (i in 1:length(models)){
      if ("summaryTable" %in% names(models[[i]])){
        models[[i]][["summaryTable"]] <- idx_table_by_name(models[[i]][["summaryTable"]])
      }
      if ("ensembleTable" %in% names(models[[i]])){
        models[[i]][["ensembleTable"]] <- idx_table_by_name(models[[i]][["ensembleTable"]])
      }
      if ("distributionTable" %in% names(models[[i]])){
        models[[i]][["distributionTable"]] <- idx_table_by_name(models[[i]][["distributionTable"]])
      }
    }
  }, error=function(cond){
    print(paste0("Error: import_model: ", cond))
  })
  return(models)
}

#' Index tables in a loop
#' @export
#' @keywords internal
#' @param list tables: Metadata
#' @return list tables: Metadata
idx_table_by_name <- function(tables){
  for (i in 1:length(tables)){
    table <- tables[[i]]
    if (!is.null(table)){
      new <- idx_col_by_name(table)
      tables[[i]] <- new
    }
  }
  return(tables)
}

#' Get rid of "columns" layer so that the columns data is directly beneath its corresponding table
#' @export
#' @keywords internal
#' @param table Table to be reorganized
#' @return table Modified table
idx_col_by_name <- function(table){
  tryCatch({
    #look for columns
    if(is.null(table[["columns"]])){
      #already been removed - just needs to be named
      stop("there should be a columns variable in here")
    }else{
      # create a list
      new.cols <- list()
      col.len <- length(table[["columns"]])
      
      # loop for each column
      for (i in 1:col.len){
        # get the variable name
        try(vn <- table[["columns"]][[i]][["variableName"]])
        if (is.null(vn)){
          table[[i]] <- table[["columns"]][[i]]
        } else {
          # edge case: more than one column have the same variablename. append a number so there aren't any overwrite conflicts.
          if (vn %in% names(table)){
            idx <- 1
            vn.tmp <-paste0(vn, "-", as.character(idx))
            while(vn.tmp %in% names(table)){
              idx <- idx + 1
              vn.tmp <-paste0(vn, "-", as.character(idx))
            }
            table[[vn.tmp]] = table[["columns"]][[i]]
          }
          # normal case: place the column data in the table
          else {
            table[[vn]] <- table[["columns"]][[i]]
          }
        }
      }
      # remove the columns item from table
      table[["columns"]] <- NULL
    }
    return(table)
  }, error=function(cond){
    stop(paste0("index_col_by_name: " + cond))
  })
  
}



