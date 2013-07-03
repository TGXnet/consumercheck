checkZeroCell <- function(data, factors)
{
  t <- table(data[, match(factors, names(data))])
  if(length(which(t==0))>0)
  {
    warning(paste("Some of the combinations of ", paste(factors,collapse=":"), " has no data "))
    return(TRUE)
  }
   
  return(FALSE)
}