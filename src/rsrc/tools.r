### function checks  if there are zero cells in a factor term
checkZeroCell <- function(data, factors)
{
  t <- table(data[, match(factors, names(data))])
  if(length(which(t==0))>0)
  {
    message(paste("Some of the combinations of ", paste(factors,collapse=":"), " has no data, therefore this combination will not be part of the initial model"))
    cat("\n")
    return(TRUE)
  }
  
  return(FALSE)
}

### checks if the number of levels for an interaction term is equal to number of observations
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
    message(warning.str)
    cat("\n")
    return(TRUE)
  }
  return(FALSE)
}


### Function converts variables to factors
convertToFactors <- function(data, facs)
{
  #convert effects to factors
  for(fac in facs)
    data[,fac] <- as.factor(data[,fac])
  data
}



### Create an lmer model
createLMERmodel <- function(structure, data, response, fixed, random, corr)
{ 
  
  #construct formula for lmer model 
  #fma<-createFormula(structure, data, response, fixed, random)
  mf.final <- createFormulaAllFixRand(structure, data, response, fixed, random, corr) 
  model <- eval(substitute(lmer( mf.final, control=lmerControl(check.nobs.vs.rankZ = "ignore")),list( mf.final= mf.final)))
  #model <- as(model,"mer")
  #model <- update(model)
  
  #mf.final <- update.formula(formula(model),formula(model))
  #model <- eval(substitute(lmer(mf.final, data=data),list(mf.final=mf.final)))
  #model <- update(model, data=data ,REML=TRUE)
  
  return(model)
}

# check an interaction term for validity
checkComb <- function(data, factors)
{
  return(checkNumberInteract(data,factors) || checkZeroCell(data, factors))
}

.fixedrand <- function(model)
{
  effs <- attr(terms(formula(model)), "term.labels")
  neffs <- length(effs)
  randeffs <- effs[grep(" | ", effs)]
  fixedeffs <- effs[!(effs %in% randeffs)]
  return(list(randeffs=randeffs, fixedeffs=fixedeffs))
}

.fillpvalues <- function(x, pvalue)
{
  pvalue[rownames(x$anova.table),x$response] <- x$anova.table[,6]
  pvalue
}

############################################################################
#get formula for mixed effects model 
############################################################################
makeFormulaConsumer <- function(model, random)
{
  fmodel <- formula(model)
  terms.fm <- attr(terms.formula(fmodel),"term.labels")
  ind.rand.terms <- which(unlist(lapply(terms.fm,function(x) substring.location(x, "|")$first))!=0)
  terms.fm[ind.rand.terms] <- unlist(lapply(terms.fm[ind.rand.terms],function(x) paste("(",x,")",sep="")))  
  fm <- paste(fmodel)
  fm[3] <- paste(c(terms.fm[-ind.rand.terms], unlist(lapply(random,function(x) paste("(1|",x,")",sep="")))), collapse=" + ")
    if(fm[3]=="")
    fo <- as.formula(paste(fm[2],fm[1],1, sep=""))
  else
    fo <- as.formula(paste(fm[2],fm[1],fm[3], sep=""))
  return(fo)
}

createModelSaturWithRandCons <- function(data, model, random)
{ 
  
  #construct the model with all conjoint factors plu Consumer as fixed factor
  mf.final <- makeFormulaConsumer(model, random)
  

  #modelIndiv <- eval(substitute(lm(mf.final, data=data),list( mf.final= mf.final)))
  modelSaturWithRand <- eval(substitute(lmer(mf.final, data=data),list( mf.final= mf.final)))
  #model <- as(model,"mer")
  #model <- update(model)
  
  #mf.final <- update.formula(formula(model),formula(model))
  #model <- eval(substitute(lmer(mf.final, data=data),list(mf.final=mf.final)))
  #model <- update(model, data=data ,REML=TRUE)
  
  return(modelSaturWithRand)
}

