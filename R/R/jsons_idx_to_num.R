#' Switch all indexing from names to numbers. 
#' @export
#' @keywords internal
#' @param list d: Metadata
#' @return list d: Metadata
idx_name_to_num <- function(d){
  if ("paleoData" %in% names(d)){
    d[["paleoData"]] <- export_data(d[["paleoData"]], "paleoData")
  }
  if ("chronData" %in% names(d)){
    d[["chronData"]] <- export_data(d[["chronData"]], "chronData")
  }
  d <- unindexGeo(d)
  return(d)
}

#' Index a section. paleoData or chronData
#' @export
#' @keywords internal
#' @param list section: Metadata
#' @param char pc: paleoData or chronData
#' @return list d: Metadata
export_data <- function(section, pc){
  tryCatch({
      if(!isNullOb(section)){
        for (i in 1:length(section)){
          if("measurementTable" %in% names(section[[i]])){
            section[[i]][["measurementTable"]] <- idx_table_by_num(section[[i]][["summaryTable"]])
          }
          if("model" %in% names(section[[i]])){
            section[[i]][["model"]] <- export_model(section[[i]][["model"]], pc)
          }
          # TODO WHAT IS THIS???          
          # if section contains a bunch of table names, then use idx_table_by_num.
          # if section contains an array of data tables, then we're all set and no need to do this part.
          if (!is.null(section) && !isNullOb(names(section)) && !"measurementTable" %in% names(section)){
            # Table(s) indexed by name. Move table(s) up and move the tableName inside the table
            section = idx_table_by_num_what(section, key1, "measurementTable")
          }
        }
      } # end section
  }, error=function(cond){
    print(paste0("Error: export_data: ", cond))
  })
  return(section)
}

#' Index model tables
#' @export
#' @keywords internal
#' @param list models: Metadata
#' @param char pc: paleoData or chronData
#' @return list models: Metadata
export_model <- function(models, pc){
  tryCatch({
    for (i in 1:length(models)){
      if ("summaryTable" %in% names(models[[i]])){
        models[[i]][["summaryTable"]] <- idx_table_by_num(models[[i]][["summaryTable"]])
      }
      if ("ensembleTable" %in% names(models[[i]])){
        models[[i]][["ensembleTable"]] <- idx_table_by_num(models[[i]][["ensembleTable"]])
      }
      if ("distributionTable" %in% names(models[[i]])){
        models[[i]][["distributionTable"]] <- idx_table_by_num(models[[i]][["distributionTable"]])
      }
    }
  }, error=function(cond){
    print(paste0("Error: export_model: ", cond))
  })
  return(models)
}

#' Index tables in a loop
#' @export
#' @keywords internal
#' @param list tables: Metadata
#' @return list tables: Metadata
idx_table_by_num <- function(tables){
  for (i in 1:length(tables)){
    table <- tables[[k]]
    if (!is.null(table)){
      new <- idx_col_by_num(table)
      tables[[k]] <- new
    }
  }
  return(tables)
}

#' Remove column names indexing. Set them to index by their column number
#' Place the new columns under a "columns" list
#' @export
#' @keywords internal
#' @param list table: Metadata
#' @return list table: Metadata
idx_col_by_num <- function(table){

  tmp <- list()
  new.cols <- list()

  # get a list of variableNames from the columns
  tnames <- names(table)
  tryCatch({
    for (i in 1:length(table)){
      # if it's a list (only list types *should* be columns), then add it to tmp by index number
      if (is.list(table[[i]])){
        # set the column data into the new.cols at the current index
        new.cols[[i]] <- table[[i]]
        # attempt to get the variable name from this table column
        vn <- tryCatch({
          vn <- table[[i]][["variableName"]]
        }, error = function(cond){
          # if you don't get the variable name beacuse it's missing the key, return none.
          return(NULL)
        })
        # variableName not found, 
        if (is.null(vn)){
          new.cols[[i]][["variableName"]] <- tnames[[i]]
        }
      }
      else {
        # table item is not a column (list). Therefore, it's a root item so set it at the root of the new table
        tmp[[tnames[[i]]]] <- table[[i]]
      }
    }
    
    # set columns inside [["columns"]] list in table
    tmp[["columns"]] <- new.cols
    
  }, error=function(cond){
    print(paste0("Error: idx_col_by_num ", cond))
  })
  return(tmp)
}

#' Unindex tables by name. Move to index by number. 
#' @export
#' @keywords internal
#' @param table Table data
#' @return table Modified table data
idx_table_by_num_what <- function(table, pc, tableType){
  d = list()
  tryCatch({
    tableNameKey = paste0(pc, "Name")
    # loop, in case of multiple tables
    for(i in 1:length(table)){
      # the table name at the top level
      tableNameVal = names(table)[[i]]
      # Insert the table name into the table
      table[[i]][[tableType]][[1]][[tableNameKey]] = tableNameVal
      d[[i]] = table[[i]]
    }
    # table is still not sorted correctly. fix it here. s1 is still at top
    return(d)
  }, error=function(cond){
    print(paste0("Error: idx_table_by_num: ", cond))
  })
  return(table)
}
