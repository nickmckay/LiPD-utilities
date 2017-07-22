#' Replace all blank values in csv matrices
#' @export
#' @keywords internal
#' @param csv All csv data
#' @return csv All csv data
clean_csv <- function(csv){
  tryCatch({
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
  }, error=function(cond){
    print(paste0("Error: clean_csv: ", cond))
  })
  return(csv)
}

#' Opens the target CSV file and creates a dictionary with one list for each CSV column.
#' @export
#' @importFrom utils read.csv
#' @keywords internal
#' @return data.list List of data for one LiPD file
read_csv_from_file <- function(){
  c <- list_files_recursive("csv")
  c.data=vector(mode="list",length=length(c))
  # import each csv file
  for (ci in 1:length(c)){
    df=read.csv(c[ci], header=FALSE, blank.lines.skip = FALSE,na.strings = c("nan", "NaN", "NAN", "NA"))
    c.data[[c[ci]]]=df
  }
  return(c.data)
}


#' Write out each CSV file for this LiPD recorde
#' csv.data format: [ some_filename.csv $columns.data ]
#' @export
#' @keywords internal
#' @param csv.data List of Lists of csv column data
#' @return success Boolean for successful csv write
write_csv_to_file <- function(csv.data){
  tryCatch({
    success <- TRUE
    csv.data <- clean_csv(csv.data)
    csv.names <- names(csv.data)
    
    # loop for csv file
    for (f in 1:length(csv.names)){
      tmp <- matrix()
      
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
          print(paste0("Error: write_csv_to_file: write.table: ", ref.name, cond))
          print("Check data for unequal row or column lengths")
          return(NULL)
        })
      }
    }
  }, error=function(cond){
    print(paste0("Error: write_csv_to_file: ", cond))
  })
  return()
}
