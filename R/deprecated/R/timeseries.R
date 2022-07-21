#' Find all the time series entries that match a given search expression, 
#' and return vector of the indices that match. 
#' indices = queryTs(ts, "archiveType == marine sediment")
#' Valid operators : ==, =, <=, >=, <, >
#' @export
#' @author Chris Heiser
#' @param ts Time series : list , Time Series data
#' @param expression Search expression : char (single query) or list (multiple query)
#' @param exact Key match : char. Is the provided key an exact key match or a piece of the key? ie. paleoData_variableName or variableName?
#' @usage queryTs(ts, expression)
#' @return idxs: Matching indices : list
#' @examples 
#' \dontrun{
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
#' }
queryTs= function(ts, expression, exact=FALSE){
  results <- suppressWarnings(process_expression(ts, expression, exact))
  return(results[["idx"]])
}

#' Find all the time series objects that match a given search expression, 
#' and return a new time series with the matching objects
#' Valid operators : ==, =, <=, >=, <, >
#' @export
#' @author Chris Heiser
#' @param ts Time series : list , Time series data
#' @param expression Search expression : char (single query) or list (multiple query)
#' @param exact Key match : char. Is the provided key an exact key match or a piece of the key? ie. paleoData_variableName or variableName?
#' @usage filterTs(ts, expression)
#' @return new.ts : Time series : list
#' @examples 
#' \dontrun{

#' # Time series
#' ts = [ object1, object2, object3, object4 ]
#'
#' # Example 1
#' new.ts = filterTs(ts, "archiveType == marine sediment")
#' # result 
#' [object1, object3, object4]
#' 
#' # Example 2
#' new.ts = filterTs(ts, ["paleoData_variableName == d18O", "archiveType == marine sediment"])
#' # result
#' [object2]
#' 
#' }
filterTs= function(ts, expression, exact=FALSE){
  results <- suppressWarnings(process_expression(ts, expression, exact))
  return(results[["new_ts"]])
}

#' Worker function that sends through the query expressions for finding matching entries in the time series
#' @export
#' @author Chris Heiser
#' @param ts Time series : list , Time Series data
#' @param expression Search expression : char (single query) or list (multiple query)
#' @param exact Key match : char. Is the provided key an exact key match or a piece of the key? ie. paleoData_variableName or variableName?
#' @return results: list , Contains list of matching time series entries and a list of matching time series indicies. 
process_expression <- function(ts, expression, exact=FALSE){
  # Create a copy of the time series for processing
  results <- list()
  results[["idx"]] <- list()
  results[["new_ts"]] <- ts

    # Single query
  if(is.character(expression)){
    # use the regex to get the <key><operator><value> groups from the given expression
    m = stringr::str_match_all(expression, "([\\w\\s\\d]+)([<>=]+)([\\s\\w\\d\\.\\-\\/]+)")
    results <- get_matches(results[["new_ts"]], m, exact)
    print(paste0(length(results[["new_ts"]]), " results after query: ", expression))
  } 
  # Multiple queries
  else if (is.list(expression)){
    # Loop for each query given
    for(i in 1:length(expression)){
      # Current query expression
      curr_expr = expression[[i]]
      # use the regex to get the <key><operator><value> groups from the given expression
      m = stringr::str_match_all(curr_expr, "([\\w\\s\\d]+)([<>=]+)([\\s\\w\\d\\.\\-\\/]+)")
      # Gather the results. We will use these results in the next loop to continue narrowing down the time series match results
      results <- get_matches(results[["new_ts"]], m, exact)
      print(paste0(length(results[["new_ts"]]), " results after query: ", curr_expr))
    }
  }
  # Return the results
  return(results)
}


#' Use the regex match groups and the time series to compile two lists: matching indices, and matching entries. 
#' @export
#' @author Chris Heiser
#' @keywords internal
#' @param ts Time series : list , Time series data
#' @param m Regex match groups : list , The query string split according to the regex matches.
#' @param exact Key match : char. Is the provided key an exact key match or a piece of the key? ie. paleoData_variableName or variableName?
get_matches <- function(ts, m, exact){
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
          if (exact && key %in% names(entry)){
            res <- check_match(entry, new_ts, idx, key, op, val, i)
            idx <- res[["idx"]]
            new_ts <- res[["new_ts"]]
          }
          else if (!exact){
            for(j in 1:length(entry)){
              entry_key <- names(entry)[[j]]
              if(grepl(key, entry_key) || key == entry_key){
                res <- check_match(entry, new_ts, idx, entry_key, op, val, i)
                idx <- res[["idx"]]
                new_ts <- res[["new_ts"]]
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


#' Compare the query value to the time series value. Does it meet the conditions? If so, add it to the output "new_ts" items. 
#' @export
#' @author Chris Heiser
#' @keywords internal
#' @param entry Time series entry: list , Current time series entry being checked.
#' @param new_ts New time series: list , The list of successful query matches so far.
#' @param idx Index : numeric , The index of this given entry within the time series list
#' @param key Key : char , The 
#' @param exact Key match : char. Is the provided key an exact key match or a piece of the key? ie. paleoData_variableName 
check_match <- function(entry, new_ts, idx, key, op, val, i){
  res <- list()
  # We can't parse the operator into the expression, so we have to manually make "switch"-like statments depending on the operator. 
  if(op == "<"){
    # If the entry value is less than the query value
    if (entry[[key]] < val){
      # Data fit the query requirements. Add this entry to output
      new_ts[[length(new_ts) + 1]] <- entry
      idx[[length(idx) + 1]] <- i
    }
  } else if (op == "<="){
    # If the entry value is less than or equal to the query value
    if (entry[[key]] < val || entry[[key]] == val){
      # Data fit the query requirements. Add this entry to output
      new_ts[[length(new_ts) + 1]] <- entry
      idx[[length(idx) + 1]] <- i
    }
  } else if (op == "==" || op == "="){
    # If the entry value is equal to the query value
    if (entry[[key]] == val){
      # Data fit the query requirements. Add this entry to output
      new_ts[[length(new_ts) + 1]] <- entry
      idx[[length(idx) + 1]] <- i
    }
  } else if (op == ">="){
    # If the entry value is greater than or equal to the query value
    if (entry[[key]] > val || entry[[key]] == val){
      # Data fit the query requirements. Add this entry to output
      new_ts[[length(new_ts) + 1]] <- entry
      idx[[length(idx) + 1]] <- i
    }
  } else if (op == ">"){
    # If the entry value is greater than the query value
    if (entry[[key]] > val){
      # Data fit the query requirements. Add this entry to output
      new_ts[[length(new_ts) + 1]] <- entry
      idx[[length(idx) + 1]] <- i
    }
  }
  # Combine the two lists into a single output
  res[["new_ts"]] <- new_ts
  res[["idx"]] <-idx
  return(res)
}