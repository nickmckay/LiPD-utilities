#' Main indexing. Convert all index-by-name to index-by-number.
#' @export
#' @keywords internal
#' @param d Metadata
#' @return d Modified metadata
indexByNumberWrite <- function(d){

  paleos <- c("paleoData", "paleoMeasurementTable", "paleoModel")
  chrons <- c("chronData", "chronMeasurementTable", "chronModel")

  # convert single entries to lists. matching structure to 1.2
  d <- indexSectionWrite(d, paleos)
  d <- indexSectionWrite(d, chrons)
  d <- unindexGeo(d)

  return(d)
}

#' Index a single section. Paleo or Chron
#' @export
#' @keywords internal
#' @param d LiPD Metadata
#' @param keys Section keys
#' @return d Modified metadata
indexSectionWrite <- function(d, keys){
  
  tryCatch({
    key1 <- keys[[1]]
    key2 <- keys[[2]]
    key3 <- keys[[3]]
    
    if(key1 %in% names(d)){
      
      if(!isNullOb(d[[key1]])){
        # d$paleoData
        for (i in 1:length(d[[key1]])){
          
          # d$paleoData[[i]]
          
          # d$paleoData[[i]]paleoMeasurementTable
          for (j in 1:length(d[[key1]][[i]][[key2]])){
            
            # d$paleoData[[i]]paleoMeasurementTable[[j]]
            table <- d[[key1]][[i]][[key2]][[j]]
            
            if(!is.null(table)){
              new <- moveColsDownWrite(table)
              d[[key1]][[i]][[key2]][[j]] <- new
            }
            
          } # end meas
          
          # d$paleoData[[i]]paleoModel
          for (j in 1:length(d[[key1]][[i]][[key3]])){
            
            # d$paleoData[[i]]paleoModel[[j]]
            
            # d$paleoData[[i]]paleoModel[[j]]$summaryTable - should only be one
            table <- d[[key1]][[i]][[key3]][[j]][["summaryTable"]]
            if (!is.null(table)){
              new <- moveColsDownWrite(table)
              d[[key1]][[i]][[key3]][[j]][["summaryTable"]] <- new
            }
            
            # d$paleoData[[i]]paleoModel[[j]]$ensembleTable - should only be one
            table <- d[[key1]][[i]][[key3]][[j]][["ensembleTable"]]
            if (!is.null(table)){
              new <- moveColsDownWrite(table)
              d[[key1]][[i]][[key3]][[j]][["ensembleTable"]] <- new
            }
            # d$paleoData[[i]]paleoModel[[j]]$distributionTable - can be one or many
            for (k in 1:length(d[[key1]][[i]][[key3]][[j]][["distributionTable"]])){
              
              # d$paleoData[[i]]paleoModel[[j]]$distributionTable[[k]]
              table <- d[[key1]][[i]][[key3]][[j]][["distributionTable"]][[k]]
              if (!is.null(table)){
                new <- moveColsDownWrite(table)
                # only add if the table exists
                d[[key1]][[i]][[key3]][[j]][["distributionTable"]][[k]] <- new
              }
              
            } # end distribution
            
          } # end model
          
          # if d[[key1]] contains a bunch of table names, then use moveTableUp.
          # if d[[key1]] contains an array of data tables, then we're all set and no need to do this part.
          if (!is.null(d[[key1]]) && !isNullOb(names(d[[key1]])) && !key2 %in% names(d[[key1]])){
            # Table(s) indexed by name. Move table(s) up 2and move the tableName inside the table
            d[[key1]] = moveTableUp(d[[key1]], key1, key2)
          }
        }
      } # end section
    }
  }, error=function(cond){
    print(paste0("error write_lipds_indexing:indexSection: ", cond))
  })
  return(d)
}

#' Unindex tables by name. Move to index by number. 
#' @export
#' @keywords internal
#' @param table Table data
#' @return table Modified table data
moveTableUpWrite <- function(table, pc, tableType){
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
    print(paste0("error write_lipds_indexing: moveTableUp: ", cond))
  })
  return(table)
}


#' Remove column names indexing. Set them to index by their column number
#' Place the new columns under a "columns" list
#' @export
#' @keywords internal
#' @param table Table data
#' @return table Modified table data
moveColsDownWrite <- function(table){

  tmp <- list()
  new.cols <- list()

  # get a list of variableNames from the columns
  tnames <- names(table)
  tryCatch({
    for (i in 1:length(table)){
      # if it's a list (column), then add it to tmp by index number
      if (is.list(table[[i]])){
        # tmp[[i]] <- try({
        #   tmp[[i]] <- table[[i]][["variableName"]]
        # })
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
    
    # # remove all null elements
    # tmp <- tmp[!sapply(tmp, is.null)]
    #
    # # make new list by number
    # if (length(tmp)>0){
    #   for (i in 1:length(tmp)){
    #     # get col data
    #     if (!is.null(tmp[[i]])){
    #       one.col <- table[[tmp[[i]]]]
    #       # move data to new cols list
    #       new.cols[[i]] <- one.col
    #       # remove entry from table
    #       table[[tmp[[i]]]] <- NULL
    #     }
    #   }
    # }
    
    # set columns inside [["columns"]] list in table
    # table[["columns"]] <- new.cols
    tmp[["columns"]] <- new.cols
    
  }, error=function(cond){
    print(paste0("error write_lipds_indexing: moveColsDown ", cond))
  })
  return(tmp)
}

