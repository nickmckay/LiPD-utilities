###############################################
## Load LiPDs - Merge
## Merge metadata and csv into one LiPD object
###############################################

#' Merge Main. Call the individual steps of merge for each file.
#' @export
#' @keywords internal
#' @param d LiPD Metdata
#' @return d Modfified LiPD Metadata
addCsvToMetadataLoad <- function(d){
  paleo <- c("paleoData", "paleoMeasurementTable", "paleoModel")
  chron <- c("chronData", "chronMeasurementTable", "chronModel")
  d <- mergeDataLoad(d, paleo)
  d <- mergeDataLoad(d, chron)
  return(d)
}

#' Merge csv numeric data into the metadata columns
#' @export
#' @keywords internal
#' @param d LiPD metadata
#' @param keys Paleo or Chron keys
#' @return d Modified LiPD metadata
mergeDataLoad <- function(d, keys){

    key1 <- keys[[1]]
    key2 <- keys[[2]]
    key3 <- keys[[3]]

    # d$chronData
    pc <- d[["metadata"]][[key1]]

    # section
    # d$chronData[[i]]
    for (i in 1:length(pc)){

      # measurement tables
      # d$chronData[[i]]chronMeasurementTable
      for (j in 1:length(pc[[i]][[key2]])){

        # d$chronData[[i]]chronMeasurementTable[[j]]
        table <- pc[[i]][[key2]][[j]]

        filename <- tryCatch(
          {path2 <- table[["filename"]]},
          error=function(cond){
            return(NULL)
          })
        if (!is.null(filename)){
          csv.cols <- d[["csv"]][[filename]]
          meta.cols <- table[["columns"]]
          d[["metadata"]][[key1]][[i]][[key2]][[j]][["columns"]] <- mergeCsvLoad(csv.cols, meta.cols)
        }
      } # end measurement tables

      # model tables
      if(any(names(pc[[i]])==key3)){

        # loop in models
        dat <- hasData(pc[[i]], key3)
        if (!is.null(dat)){
          chronModel <- vector(mode="list",length=length(dat))

          # d$chronData[[i]]$chronModel
          for (j in 1:length(pc[[i]][[key3]])){

            # d$chronData[[i]]$chronModel[[j]]

            # summary table
            # d$chronData[[i]]$chronModel[[j]]$summaryTable[[1]] - only one per model
            table <- pc[[i]][[key3]][[j]][["summaryTable"]]
            filename <- table[["filename"]]
            if (!is.null(filename)){
              csv.cols <- d[["csv"]][[filename]]
              meta.cols <- table[["columns"]]
              columns <- mergeCsvLoad(csv.cols, meta.cols)
              toCopy <- which(names(table)!="columns")
              for(tt in toCopy){
                chronModel[[j]]$summaryTable[[names(table)[tt]]] <- table[[names(table)[tt]]]
              }
              chronModel[[j]]$summaryTable$columns <-columns

            }

            # ensemble table
            # d$chronData[[i]]$chronModel[[j]]$ensembleTable[[1]] - only one per model
            dat <- hasData(pc[[i]][[key3]][[j]], "ensembleTable")
            if (!is.null(dat)){
              table <- pc[[i]][[key3]][[j]][["ensembleTable"]]
              # get filename
              filename <- table[["filename"]]
              if (!is.null(filename)){
                csv.cols <- d[["csv"]][[filename]]
                meta.cols <- table[["columns"]]
                columns <- mergeCsvLoad(csv.cols, meta.cols)
                toCopy <- which(names(table)!="columns")
                for(tt in toCopy){
                  chronModel[[j]]$ensembleTable[[names(table)[tt]]] <- table[[names(table)[tt]]]
                }
                chronModel[[j]]$ensembleTable$columns <- columns
              }
            }

            # distribution tables
            # d$chronData[[i]]$chronModel[[j]]$distributionTable - possibly multiple per model
              dat <- hasData(pc[[i]][[key3]][[j]], "distributionTable")
              if (!is.null(dat)){
                # data exists, create a new dist table of same length. 
                distributionTable <- vector(mode = "list",length = length(pc[[i]][[key3]][[j]][["distributionTable"]]))
                if(length(distributionTable)>=1){
                  for (k in 1:length(pc[[i]][[key3]][[j]][["distributionTable"]])){
                    table <- pc[[i]][[key3]][[j]][["distributionTable"]][[k]]
                    filename <- table[["filename"]]
                    # filename required. if no filename, we cannot get csv data.
                    if (!is.null(filename)){
                      csv.cols <- d[["csv"]][[filename]]
                      meta.cols <- table[["columns"]]
                      columns  <- mergeCsvLoad(csv.cols, meta.cols)
                      toCopy <- which(names(table)!="columns")
                      for(tt in toCopy){
                        distributionTable[[k]][[names(table)[tt]]] <- table[[names(table)[tt]]]
                      }
                      distributionTable[[k]]$columns <- columns
                    }
                  } # end loop
                  chronModel[[j]]$distributionTable <- distributionTable
                } # end length
              } # end distribution

            #add in anything that we didn't recreate
            icm <- names(pc[[i]][[key3]][[j]])
            cmnames <- names(chronModel[[j]])
            toAdd <- which(!(icm %in% cmnames))
            for(ta in 1:length(toAdd)){
              chronModel[[j]][[icm[toAdd[ta]]]] <- pc[[i]][[key3]][[j]][[icm[toAdd[ta]]]]
            }
          } ##end chronModel loop
          d[["metadata"]][[key1]][[i]]$chronModel <- chronModel

        } # end chronModel check

      }#end chronModel

    } ## end chrondata
  return(d)
}


#' Merge CSV data into the metadata
#' @export
#' @keywords internal
#' @param csv.cols CSV data for this file
#' @param meta.cols Target metadata columns
#' @return meta.cols Modified metadata columns
mergeCsvLoad <- function(csv.cols, meta.cols){

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


