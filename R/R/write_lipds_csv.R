#' Collect csvs main. Collect and remove csv "values" fields.
#' @export
#' @keywords internal
#' @param dsn Dataset name
#' @param d Metadata
#' @return all.data Final split of metadata and csv data
collectCsvs <- function(dsn, d){

  # Combine csv and metadata into a list so we can return multiple items in collect.csvs.section
  all.data <- list()
  all.data[["metadata"]] <- d
  all.data[["csv"]] <- list()
  
  # Traverse one section at a time
  # Parallel: Get CSV from metadata, and remove CSV from metadata
  all.data <- collectCsvSection(all.data, "paleoData", dsn)
  all.data <- collectCsvSection(all.data, "chronData", dsn)

  return(all.data)
}

#' Collect and remove csv from one section: Paleo or chron
#' csv.data format: [ some_filedsn.csv $columns.data ]
#' @export
#' @keywords internal
#' @param d Metadata w. values
#' @param pc paleoData or chronData
#' @param csv.data Running collection of csv data
#' @param dsn Dataset name
#' @return all.data List holding the running collection of separated csv and metadata
collectCsvSection <- function(all.data, pc, dsn){
  d <- all.data[["metadata"]]
  csv.data <- all.data[["csv"]]
  tryCatch({
    if(pc %in% names(d)){
      if(!isNullOb(d[[pc]])){
        # dsn
        crumb.pd <- paste(dsn, pc, sep=".")
        pd <- d[[pc]]
        
        # dsn.paleoData
        for (i in 1:length(pd)){
          
          # dsn.paleoData1
          crumb.pd.i <- paste0(crumb.pd, i)
          pd.i <- pd[[i]]
          
          # dsn.paleoData1.paleoMeasurementTable
          crumb.pd.meas <- paste(crumb.pd.i, "measurement", sep=".")
          pd.meas <- pd.i[["measurementTable"]]
          
          for (j in 1:length(pd.meas)){
            
            # dsn.paleoData1.paleoMeasurementTable1
            # this will be the ending filename for this table
            crumb.meas.filename <- paste0(crumb.pd.meas, j, ".csv")
            pd.meas.i <- pd.meas[[j]]
            tmp.dat <- parseTable(pd.meas.i)
            
            # only set items if table has data
            if (!is.null(tmp.dat[["table"]])){
              # Set csv in overall output
              csv.data[[crumb.meas.filename]] <- tmp.dat[["csv"]]
              # overwrite old table
              d[[pc]][[i]][["measurementTable"]][[j]]<- tmp.dat[["table"]]
              # overwrite old filename
              d[[pc]][[i]][["measurementTable"]][[j]][["filename"]]<- crumb.meas.filename
            } # end measurement[i]
            
          } # end measurement
          
          # dsn.paleoData1.paleoModel
          crumb.pd.mod <- paste(crumb.pd.i, "model", sep=".")
          pd.mod <- pd.i[["model"]]
          
          for (j in 1:length(pd.mod)){
            
            # dsn.paleoData1.paleoModel1
            crumb.pd.mod.i <- paste0(crumb.pd.mod, j)
            pd.mod.i<- pd.mod[[j]]
            
            
            # SUMMARY TABLE
            
            # dsn.paleoData1.paleoModel1.summaryTable
            crumb.sum.filename <- paste0(crumb.pd.mod.i, "summary", ".csv")
            pd.sum <- pd.mod.i[["summaryTable"]]
            tmp.dat <- parseTable(pd.sum)
            
            # only set items if table has data
            if (!is.null(tmp.dat[["table"]])){
              # Set csv in overall output
              csv.data[[crumb.sum.filename]] <- tmp.dat[["csv"]]
              # overwrite old table
              d[[pc]][[i]][["model"]][[j]][["summaryTable"]]<- tmp.dat[["table"]]
              # overwrite old filename
              d[[pc]][[i]][["model"]][[j]][["summaryTable"]][["filename"]]<- crumb.sum.filename
            } # end summary
            
            
            # ENSEMBLE TABLE
            
            # dsn.paleoData1.paleoModel1.ensembleTable
            crumb.ens.filename <- paste0(crumb.pd.mod.i, "ensemble", ".csv")
            pd.ens <- pd.mod.i[["ensembleTable"]]
            tmp.dat <- parseTable(pd.ens)
            
            # only set items if table has data
            if (!is.null(tmp.dat[["table"]])){
              # Set csv in overall output
              csv.data[[crumb.ens.filename]] <- tmp.dat[["csv"]]
              # overwrite old table
              d[[pc]][[i]][["model"]][[j]][["ensembleTable"]]<- tmp.dat[["table"]]
              # overwrite old filename
              d[[pc]][[i]][["model"]][[j]][["ensembleTable"]][["filename"]]<- crumb.ens.filename
              
            } # end ensemble
            
            
            # DISTRIBUTION TABLES
            
            # dsn.paleoData1.paleoModel1.distributionTable
            crumb.dist <- paste0(crumb.pd.mod.i, "distribution")
            pd.dist <- pd.mod.i[["distributionTable"]]
            
            for (k in 1:length(pd.dist)){
              
              # dsn.paleoData1.distributionTable1
              # this will be the ending filename for this table
              crumb.dist.filename <- paste0(crumb.dist, k, ".csv")
              pd.dist.i <- pd.dist[[k]]
              tmp.dat <- parseTable(pd.dist.i)
              
              # only set items if table has data
              if (!is.null(tmp.dat[["table"]])){
                # Set csv in overall output
                csv.data[[crumb.dist.filename]] <- tmp.dat[["csv"]]
                # overwrite old table
                d[[pc]][[i]][["model"]][[j]][["distributionTable"]][[k]]<- tmp.dat[["table"]]
                # overwrite old filename
                d[[pc]][[i]][["model"]][[j]][["distributionTable"]][[k]][["filename"]]<- crumb.dist.filename
              } # end distribution[i]
              
            } # end distribution
            
          } # end model tables
          
        } # end chronDatas
        
        # Can only return one item, so add our two items to a list and use that.
        new.data = list()
        new.data[["metadata"]] <- d
        new.data[["csv"]] <- csv.data
        return(new.data)
      }
    } #if pc in d
  }, error=function(cond){
    print(sprintf("error in write_lipds_csv:collectCsvSection %s", cond))
  })
  return(all.data)
  }
  
#' Parse the csv value columns from the table, then split the metadata from the csv
#' @export
#' @keywords internal
#' @param table Table of data
#' @return table Table w/o csv, csv Value columns
parseTable <- function(table){

  tryCatch({
    # list to hold each column for this table
    vals <- list()
    out <- list()
    
    # if pd.sum exists
    if (!is.null(table)){
      
      # if a columns entry exists
      if (!is.null(table[["columns"]])){
        curr.num <- 1
        # dsn.paleoData1.paleoModel1.summaryTable $columns
        for (k in 1:length(table[["columns"]])){
          # add values for this column to the main list, then remove values
          if (!is.null(table[["columns"]][[k]][["values"]])){
            vals[[k]] <- table[["columns"]][[k]][["values"]]
            len <- NCOL(table[["columns"]][[k]][["values"]])
            # remove the "number" entry for the column, then replace it with the index of this loop
            # however, if it's an ensemble table with many "numbers"/columns, then we'll keep it.
            if (len > 1){
              # this is multiple columns in one. most likely an ensemble
              # the end of the range is the start col + the cols in the matrix
              num.cols <- dim(table[["columns"]][[k]][["values"]])[2]
              # set the range as the number
              nums <- createRange(curr.num, num.cols)
              table[["columns"]][[k]][["number"]] <- nums
              # the beginning point for the next loop is right after the finish of this loop.
              curr.num <- curr.num + num.cols
            }
            else if (len <= 1){
              table[["columns"]][[k]][["number"]] <- curr.num
              curr.num <- curr.num + 1
            }
            # remove 'values' from the column
            table[["columns"]][[k]][["values"]] <- NULL
          }
        }
      }
    }
    out[["table"]] <- table
    out[["csv"]] <- vals
    
  }, error=function(cond){
    print(sprintf("error in write_lipds_csv:parseTable: %s", cond))
  })
  return(out)
}

