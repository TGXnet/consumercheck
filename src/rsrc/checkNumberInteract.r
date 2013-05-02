checkNumberInteract <- function(data, factors)
{
  # returns TRUE if number of levels is equal to nrow of data
 
  nlev <- 1
  for(i in 1:length(factors))
  {    
     if(!is.factor(data[, match(factors[i], names(data))]))
        next()
     nlev <- nlev * nlevels(data[, match(factors[i], names(data))])
  }
  if(nlev >= nrow(data))
  {
    warning.str <- "Number of levels for "
    if(length(factors) > 1)
      warning.str <- c(warning.str," interaction ", sep=" ")
    #for(i in length(factors))
    #    warning.str <- paste(warning.str, factors[i],sep=" ")  
    warning.str <- c(warning.str, paste(factors,collapse=":"), " is more or equal to the number of observations in data", sep=" ")    
    warning(warning.str)
    return(TRUE)
  }
  return(FALSE)
}