#' Find all the time series entries that match a given search expression, 
#' and return vector of the indices that match. 
#' @export
#' @example indices = queryTs(ts, "archiveType == marine sediment")
#' @param ts Time series
#' @param expression Search expression
#' @return idx Matching indices
queryTs= function(ts, expression){
  ops = c("<", "<=", "==", "=", ">=", ">", "less than", "more than", "is")
  idxs <- list()
  # m[[1]][[1]] is full match
  # m[[1]][[2]] is key
  # m[[1]][[3]] is operator
  # m[[1]][[4]] is value
  m = stringr::str_match_all(expression, "([\\w\\s\\d]+)([<>=]+)([\\s\\w\\d\\.\\-]+)")
  if(isNullOb(m[[1]])){
    print("Error: Invalid expression given")
  } else {
    tryCatch({
      # Get the separate pieces of the expression
      key = base::trimws(m[[1]][[2]])
      op = base::trimws(m[[1]][[3]])
      val = base::trimws(m[[1]][[4]])
      # Attempt to cast value to numeric. If the result is NOT "NA", then keep it. Otherwise, it's not a numeric at all. 
      if (!is.na(as.numeric(val))){
        val = as.numeric(val)
      }
      # Loop for every entry in the time series
      for (i in 1:length(ts)){
        tryCatch({
          entry <- ts[[i]]
          if (key %in% names(entry)){
            if(op == "<"){
              if (entry[[key]] < val){
                idxs[[length(idxs) + 1]] <- i
              }
            } else if (op == "<="){
              if (entry[[key]] < val || entry[[key]] == val){
                idxs[[length(idxs) + 1]] <- i
              }
            } else if (op == "==" || op == "="){
              if (entry[[key]] == val){
                idxs[[length(idxs) + 1]] <- i
              }
            } else if (op == ">="){
              if (entry[[key]] > val || entry[[key]] == val){
                idxs[[length(idxs) + 1]] <- i
              }
            } else if (op == ">"){
              if (entry[[key]] > val){
                idxs[[length(idxs) + 1]] <- i
              }
            }
          }
        }, error=function(cond){
          print(paste0("Error: timeseries entry: ", i,", ",  cond))
        })
      }
    },error=function(cond){
      print(paste0("Error: ", cond))
    })

  }
  return(idxs)
}