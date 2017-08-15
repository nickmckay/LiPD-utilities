#' Find all the time series entries that match a given search expression, 
#' and return vector of the indices that match. 
#' indices = queryTs(ts, "archiveType == marine sediment")
#' Valid operators : ==, =, <=, >=, <, >
#' @export
#' @author Chris Heiser
#' @param ts Time series : list
#' @param expression Search expression : char
#' @usage queryTs(ts, expression)
#' @return idxs: Matching indices : list
#' @examples 
#' 
#' # Time series
#' ts = [ object1, object2, object3, object4 ]
#'
#' # Example 1
#' idxs = filterTs(ts, "archiveType == marine sediment")
#' # result 
#' [1, 3, 4]
#' 
#' # Example 2
#' idxs = filterTs(ts, "paleoData_variableName == d18O")
#' # result
#' [2]
#' 
queryTs= function(ts, expression){
  ops = c("<", "<=", "==", "=", ">=", ">", "less than", "more than", "is")
  idxs <- list()
  m = stringr::str_match_all(expression, "([\\w\\s\\d]+)([<>=]+)([\\s\\w\\d\\.\\-]+)")
  results <- get_matches(ts, m)
  return(results[["idx"]])
}

#' Find all the time series objects that match a given search expression, 
#' and return a new time series with the matching objects
#' 
#' Valid operators : ==, =, <=, >=, <, >
#' @export
#' @author Chris Heiser
#' @param ts Time series
#' @param expression Search expression : char
#' @usage filterTs(ts, expression)
#' @return new.ts : Time series : list
#' @examples 
#' 
#' # Time series
#' ts = [ object1, object2, object3, object4 ]
#'
#' # Example 1
#' new.ts = filterTs(ts, "archiveType == marine sediment")
#' # result 
#' [object1, object3, object4]
#' 
#' # Example 2
#' new.ts = filterTs(ts, "paleoData_variableName == d18O")
#' # result
#' [object2]
#' 
#' 
filterTs= function(ts, expression){
  new.ts <- list()
  # use the regex to get the <key><operator><value> groups from the given expression
  m = stringr::str_match_all(expression, "([\\w\\s\\d]+)([<>=]+)([\\s\\w\\d\\.\\-]+)")
  results <- get_matches(ts, m)
  return(results[["new_ts"]])
}


#' Use the regex match groups and the time series to compile two lists: matching indices, and matching entries. 
#' @export
#' @author Chris Heiser
#' @keywords internal
#' @param ts Time series
#' @param m Regex match groups
get_matches <- function(ts, m){
  tmp = list()
  idx = list()
  new_ts = list()
  # m[[1]][[1]] is full match
  # m[[1]][[2]] is key
  # m[[1]][[3]] is operator
  # m[[1]][[4]] is value
  if(isNullOb(m[[1]])){
    print("Error: Invalid expression given")
  } else {
    tryCatch({
      # Get the separate pieces of the expression
      key = trimws(m[[1]][[2]])
      op = trimws(m[[1]][[3]])
      val = trimws(m[[1]][[4]])
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
                new_ts[[length(new_ts) + 1]] <- entry
                idx[[length(idx) + 1]] <- i
              }
            } else if (op == "<="){
              if (entry[[key]] < val || entry[[key]] == val){
                new_ts[[length(new_ts) + 1]] <- entry
                idx[[length(idx) + 1]] <- i
              }
            } else if (op == "==" || op == "="){
              if (entry[[key]] == val){
                new_ts[[length(new_ts) + 1]] <- entry
                idx[[length(idx) + 1]] <- i
              }
            } else if (op == ">="){
              if (entry[[key]] > val || entry[[key]] == val){
                new_ts[[length(new_ts) + 1]] <- entry
                idx[[length(idx) + 1]] <- i
              }
            } else if (op == ">"){
              if (entry[[key]] > val){
                new_ts[[length(new_ts) + 1]] <- entry
                idx[[length(idx) + 1]] <- i
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
  tmp[["new_ts"]] <- new_ts
  tmp[["idx"]] <- idx
  return(tmp)
}