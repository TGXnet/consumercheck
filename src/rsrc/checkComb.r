checkComb <- function(data, factors)
{
  return(checkNumberInteract(data,factors) || checkZeroCell(data, factors))
}