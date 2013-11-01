##############################################################################
### performs  Conjoint Analysis for lmer object
##############################################################################

### conjoint<-function(structure=1, consum.attr, design.matr, list.consum.liking, response, fixed, random, facs, corr = FALSE, alpha.rand = 0.1, alpha.fix = 0.05, plot=FALSE)

source("tools.r")
source("createFormulaAllFixRand.r")

ConjointNoMerge <- function(structure=1, data1, response, fixed, random, facs, corr = FALSE, alpha.random = 0.1, alpha.fixed = 0.05)
{
#structure=1  (default structure) : Analysis of main effects, Random consumer effect AND interaction 
#         between consumer and the main effects. 
#        (Automized reduction in random part, NO reduction in fixed part).
#structure=2 : Main effects AND all 2-factor interactions. 
#         Random consumer effect AND interaction between consumer and 
#         all fixed effects (both main and interaction ones). 
#         (Automized reduction in random part, NO reduction in fixed part). 
#structure=3 : Full factorial model with ALL possible fixed and random effects. 
#         (Automized reduction in random part, AND automized reduction in fixed part).

  
#the result that will be returned
resultFULL <- vector("list",length(response))

#convert some of the variables specified by user to factors
data1  <-  convertToFactors(data1, facs)

#print(data)
attach(data1)

for(ind.resp in 1:length(response))
{

  print(paste("Calculating ", response[ind.resp],"...", sep=" "))

  
  
  model <- createLMERmodel(structure, data1, response[ind.resp], fixed, random, corr)
  
#check if reduction of the fixed part is required
if(structure==1 || structure==2)
 isFixReduce <- FALSE
else
 isFixReduce <- TRUE
isRandReduce <- TRUE
isLsmeans <- TRUE
  
  #check if there are correlations between intercepts and slopes
  checkCorr <- function(model)
  {
    corr.intsl <- FALSE
    lnST <- length(getME(model, "ST"))
    for(i in 1:lnST)
    {    
      if(nrow(getME(model, "ST")[[i]])>1)
        corr.intsl <- TRUE
    } 
    return(corr.intsl) 
  }

if(checkCorr(model))
  isRandReduce <- FALSE

#print(model)
#print(data)
#print(model)
 
t <- step(model, reduce.fixed=isFixReduce, reduce.random=isRandReduce, alpha.random=alpha.random, alpha.fixed=alpha.fixed)


fillresult <- function(t)
{
  result  <-  NULL
  result$rand.table <- t$rand.table
  result$anova.table <- t$anova.table
  result$lsmeans.table <- t$lsmeans.table
  result$diffs.lsmeans.table <- t$diffs.lsmeans.table
  ### calculate p adjusted  
  if("elim.num" %in% colnames(t$anova.table))
    final.facs <- rownames(t$anova.table)[t$anova.table[,"elim.num"]=="keep"]
  else
    final.facs <- rownames(t$anova.table)
  rnames <- rownames(t$diffs.lsmeans.table)
  diffs.facs <- sapply(rnames, function(x) substring(x, 1, substring.location(x, " ")$first[1]-1), USE.NAMES = FALSE)
  pv.adjust <- rep(0, length(diffs.facs))
  for(i in 1:length(final.facs))
  {
    find.fac <- diffs.facs %in% final.facs[i]
    pv.adjust[find.fac] <- p.adjust(t$diffs.lsmeans.table$"p-value"[find.fac], method="bonferroni")
  }
  result$diffs.lsmeans.table$"p-value.adjust" <- pv.adjust
  
  res <- lm(t$model, data=data1)$residuals
  result$residuals <- res
  
  modelIndiv <- createLMmodel(data1, t$model, random)
  result$residuals_Indiv <- modelIndiv$residuals
    
  #format p-values
  if(!is.null(result$rand.table))
  {
    rownames(result$rand.table) <- unlist(lapply(rownames(result$rand.table), function(x) substring2(x, 2, nchar(x)-1)))
    result$rand.table[,which(colnames(result$rand.table)=="p.value")] <- format.pval(result$rand.table[,which(colnames(result$rand.table)=="p.value")], digits=3, eps=1e-3)
  }
  if(class(t$model)!="lm")
    result$anova.table[,which(colnames(result$anova.table)=="Pr(>F)")] <- format.pval(result$anova.table[,which(colnames(result$anova.table)=="Pr(>F)")], digits=3, eps=1e-3)
  
  
  return(result)
}

resultFULL[[ind.resp]] <- fillresult(t)

}


detach(data1)
names(resultFULL) <- response
return(resultFULL)
}


OLDConjointNoMerge <- function(structure=1, data1, response, fixed, random, facs, corr = FALSE, alpha.random = 0.1, alpha.fixed = 0.05)
{
  ##structure=1  (default structure) : Analysis of main effects, Random consumer effect AND interaction 
  ##         between consumer and the main effects.
  ##        (Automized reduction in random part, NO reduction in fixed part).
  ##structure=2 : Main effects AND all 2-factor interactions.
  ##         Random consumer effect AND interaction between consumer and
  ##         all fixed effects (both main and interaction ones).
  ##         (Automized reduction in random part, NO reduction in fixed part).
  ##structure=3 : Full factorial model with ALL possible fixed and random effects. 
  ##         (Automized reduction in random part, AND automized reduction in fixed part).

  source("createLMERmodel.r")
  source("convertToFactors.r")
  ##source("dataPrep.r")

  ##the result that will be returned
  resultFULL<-vector("list",length(response))

  ##data<-makeDataForConjoint(design.matr, list.consum.liking, consum.attr)
  ##data<-convertToFactors(data,c(fixed,random))

  ##convert some of the variables specified by user to factors
  data1<-convertToFactors(data1, facs)

  ##print(data)
  attach(data1)

  for(ind.resp in 1:length(response))
    {

      print(paste("Calculating ", response[ind.resp],"...", sep=" "))

      model <- createLMERmodel(structure, data1, response[ind.resp], fixed, random, corr)

      ##check if reduction of the fixed part is required
      if(structure==1 || structure==2)
        isFixReduce<-FALSE
      else
        isFixReduce<-TRUE
      isRandReduce<-TRUE
      isLsmeans<-TRUE

      ##check if there are correlations between intercepts and slopes
      checkCorr<-function(model)
        {
          corr.intsl<-FALSE
          lnST<-length(model@ST)
          for(i in 1:lnST)
            {
              if(nrow(model@ST[[i]])>1)
                corr.intsl<-TRUE
            }
          return(corr.intsl) 
        }

      if(checkCorr(model))
        isRandReduce<-FALSE

      ##print(model)
      ##print(data)
      ##print(model)

      ##t<-totalAnovaRandLsmeans(model, data,  alpha.rand = 0.05, alpha.fix = 0.05, isFixReduce = FALSE, isRandReduce = FALSE, isTotal=TRUE, isAnova=FALSE, isRand=FALSE, isLSMEANS=FALSE, test.effs=NULL, plot=FALSE)

      ##t<-totalAnalysis(model, data, isFixReduce=isFixReduce, isRandReduce=isRandReduce, isLsmeans=isLsmeans , plot=plot, alpha.rand=alpha.rand, alpha.fix=alpha.fix)

      t <- step(model, reduce.fixed=isFixReduce, reduce.random=isRandReduce, alpha.random=alpha.random, alpha.fixed=alpha.fixed)

      ##getFormula<-function(model, withRand=TRUE)
      ##{
      ##  fmodel<-formula(model)
      ##  terms.fm<-attr(terms(fmodel),"term.labels")
      ##  ind.rand.terms<-which(unlist(lapply(terms.fm,function(x) substring.location(x, "|")$first))!=0)
      ##  terms.fm[ind.rand.terms]<-unlist(lapply(terms.fm[ind.rand.terms],function(x) paste("(",x,")",sep="")))
      ##  fm<-paste(fmodel)
      ##  if(withRand)
      ##    fm[3]<-paste(terms.fm,collapse=" + ")
      ##  else
      ##    fm[3]<-paste(terms.fm[-ind.rand.terms],collapse=" + ")
      ##  return(fm)
      ##}

      fillresult<-function(t)
        {
          result <- NULL
          result$rand.table <- t$rand.table
          result$anova.table <- t$anova.table
          result$lsmeans.table <- t$lsmeans.table
          result$diffs.lsmeans.table <- t$diffs.lsmeans.table
          ##fm<-getFormula(t$model, withRand=FALSE)
          ##if(fm[3]=="")
          ##  res<-lm(as.formula(paste(fm[2],fm[1],1, sep="")), data=data)$residuals
          ##else
          ##  res<-lm(as.formula(paste(fm[2],fm[1],fm[3], sep="")), data=data)$residuals
          res <- lm(t$model, data=data1)$residuals
          result$residuals <- res

          ##format p-values
          if(!is.null(result$rand.table))
            {
              rownames(result$rand.table)<-unlist(lapply(rownames(result$rand.table), function(x) substring2(x, 6, nchar(x)-1)))
              result$rand.table[,which(colnames(result$rand.table)=="p.value")]<-format.pval(result$rand.table[,which(colnames(result$rand.table)=="p.value")], digits=3, eps=1e-3)
            }
          ##rand.table<-xtable(s$rand.table, align="lcccc", display=c("s","f","d","d","s"))
          if(class(t$model)!="lm")
            result$anova.table[,which(colnames(result$anova.table)=="Pr(>F)")]<-format.pval(result$anova.table[,which(colnames(result$anova.table)=="Pr(>F)")], digits=3, eps=1e-3)

          return(result)
        }
      resultFULL[[ind.resp]]<-fillresult(t)
    }


  detach(data1)
  names(resultFULL)<-response
  return(resultFULL)
}
