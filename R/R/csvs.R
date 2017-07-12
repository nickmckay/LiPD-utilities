#' Replace all blank values in csv matrices
#' @export
#' @keywords internal
#' @param csv All csv data
#' @return csv All csv data
cleanCsv <- function(csv){
  blanks <- c("", " ", "NA", "NaN", "NAN", "nan")
  file.len <- length(csv)
  if (file.len>0){
    for (file in 1:file.len){
      col.len <- length(csv[[file]])
      if (col.len>0){
        for (cols in 1:col.len){
          # get one column (matrix)
          col <- csv[[file]][[cols]]
          # replace all blanks in it
          col[is.na(col) | is.nan(col)] <- NA
          # set column back in columns
          csv[[file]][[cols]] <- col
        }
      }
    }
  }
  return(csv)
}

#' Write out each CSV file for this LiPD record
#' csv.data format: [ some_filename.csv $columns.data ]
#' @export
#' @keywords internal
#' @param csv.data List of Lists of csv column data
#' @return success Boolean for successful csv write
writeCsvs <- function(csv.data){
  
  success <- TRUE
  csv.names <- names(csv.data)
  
  # loop for csv file
  for (f in 1:length(csv.names)){
    tmp <- matrix()
    
    # only keep writing if all csvs have been successful.
    if (!is.null(success)){
      # one csv file: list of lists. [V1: [column values], V2: [columns values], etc.]
      ref.name <- csv.names[[f]]
      if(!isNullOb(csv.data[[ref.name]])){
        for (i in 1:length(csv.data[[ref.name]])){
          col <- csv.data[[ref.name]][[i]]
          
          # convert to numeric if needed
          if (is.list(col)){
            col <- as.numeric(col)
            # replace all NA values with "NaN" before writing to file
            col <- replace(col, is.na(col), "NaN")
          }
          # check if tmp matrix has data or is fresh.
          if(all(is.na(tmp))){
            # fresh, so just bind the col itself
            tmp <- tryCatch({
              cbind(col, deparse.level = 0)
            }, error = function(cond){
              print(sprintf("cbind error: %s", ref.name))
              return(NULL)
            })
          }else{
            # not fresh, bind the existing with the col
            tmp <- tryCatch({
              cbind(tmp, col, deparse.level = 0)
            }, error = function(cond){
              if(is.matrix(col)){
                tmp <- tryCatch({
                  col <- t(col)
                  cbind(tmp, col, deparse.level = 0)
                }, error = function(cond){
                  print(sprintf("cbind error: %s", ref.name))
                  return(NULL)
                })
              }
              else{
                return(NULL)
              }
            })
            # cbind didn't work here, it's possible the matrix is transposed wrong.
            # give it another try after transposing it.
            if (is.null(tmp) & is.matrix(col)){
              
            }
          }
        }
      }
      if (!is.null(tmp)){
        success <- tryCatch({
          write.table(tmp, file=ref.name, col.names = FALSE, row.names=FALSE, sep=",")
          success <- TRUE
        }, error=function(cond){
          print(sprintf("Error writing csv: %s", ref.name))
          print("Check data for unequal row or column lengths")
          return(NULL)
        })
        # end try
      } # end write success
    } # end if success
  } # end loop
  
  if (is.null(success)){
    success <- FALSE
  }
  
  return(success)
}
