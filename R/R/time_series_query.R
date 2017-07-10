#' Find all the time series entries that match a given search expression, 
#' and return a new time series with the matching entries
#' @export
#' @example indices = queryTs(ts, "archiveType == marine sediment")
#' @param ts Time series
#' @param expression Search expression
#' @return ts Time series
queryTs= function(ts, expression){
  ops = c("<", "<=", "==", "=", ">=", ">", "less than", "more than", "is")
  
  
  
  for (entry in 1:length(ts)){
    
  }
}