##############################################################################
# performs  Conjoint Analysis for lmer object
##############################################################################
#conjoint<-function(structure=1, data, response, fixed, random, corr = FALSE, alpha.rand = 0.1, alpha.fix = 0.05, plot=FALSE)
conjoint<-function(structure=1, consum.attr, design.matr, list.consum.liking, response, fixed, random, facs, corr = FALSE, alpha.rand = 0.1, alpha.fix = 0.05, plot=FALSE) {
  #structure=1  (default structure) : Analysis of main effects, Random consumer effect AND interaction 
  #         between consumer and the main effects. 
  #        (Automized reduction in random part, NO reduction in fixed part).
  #structure=2 : Main effects AND all 2-factor interactions. 
  #         Random consumer effect AND interaction between consumer and 
  #         all fixed effects (both main and interaction ones). 
  #         (Automized reduction in random part, NO reduction in fixed part). 
  #structure=3 : Full factorial model with ALL possible fixed and random effects. 
  #         (Automized reduction in random part, AND automized reduction in fixed part).

  source(paste(getwd(), "/pgm/createLMERmodel.r", sep = ""))
  source(paste(getwd(), "/pgm/convertToFactors.r", sep = ""))
  source(paste(getwd(), "/pgm/dataPrep.r", sep = ""))

  resultFULL<-vector("list",length(response))  #the result that will be returned

  data<-makeDataForConjoint(design.matr, list.consum.liking, consum.attr)

  #source(paste(getwd(), "/pgm/convertToFactors.r", sep = ""))
  #data<-convertToFactors(data,c(fixed,random))

  #convert some of the variables specified by user to factors
  data<-convertToFactors(data, facs)

  for(ind.resp in 1:length(response)) {
    print(paste("Calculating ", response[ind.resp],"...", sep=" "))
    model<-createLMERmodel(structure, data, response[ind.resp], fixed, random, corr)

    #check if reduction of the fixed part is required
    if(structure==1 || structure==2)
      isFixReduce<-FALSE
    else
      isFixReduce<-TRUE
    isRandReduce<-TRUE
    isLsmeans<-TRUE

    #check if there are correlations between intercepts and slopes
    checkCorr<-function(model) {
      corr.intsl<-FALSE
      lnST<-length(model@ST)
      for(i in 1:lnST) {
        if(nrow(model@ST[[i]])>1)
          corr.intsl<-TRUE
      }
      return(corr.intsl)
    }

    if(checkCorr(model))
      isRandReduce<-FALSE

    #print(model)
    #print(data)
    #print(model)

    #t<-totalAnovaRandLsmeans(model, data,  alpha.rand = 0.05, alpha.fix = 0.05, isFixReduce = FALSE, isRandReduce = FALSE, isTotal=TRUE, isAnova=FALSE, isRand=FALSE, isLSMEANS=FALSE, test.effs=NULL, plot=FALSE)

    t<-totalAnalysis(model, data, isFixReduce=isFixReduce, isRandReduce=isRandReduce, isLsmeans=isLsmeans , plot=plot, alpha.rand=alpha.rand, alpha.fix=alpha.fix)

    getFormula<-function(model, withRand=TRUE) {
      fmodel<-formula(model)
      terms.fm<-attr(terms(fmodel),"term.labels")
      ind.rand.terms<-which(unlist(lapply(terms.fm,function(x) substring.location(x, "|")$first))!=0)
      terms.fm[ind.rand.terms]<-unlist(lapply(terms.fm[ind.rand.terms],function(x) paste("(",x,")",sep="")))
      fm<-paste(fmodel)
      if(withRand)
        fm[3]<-paste(terms.fm,collapse=" + ")
      else
        fm[3]<-paste(terms.fm[-ind.rand.terms],collapse=" + ")
      return(fm)
    }

    fillresult<-function(t) {
      result<-NULL
      result$rand.table<-t$rand.table
      result$anova.table<-t$anova.table
      result$lsmeans.table<-t$lsmeans.table
      result$diffs.lsmeans.table<-t$diffs.lsmeans.table
      fm<-getFormula(t$model, withRand=FALSE)
      if(fm[3]=="")
        res<-lm(as.formula(paste(fm[2],fm[1],1, sep="")), data=data)$residuals
      else
        res<-lm(as.formula(paste(fm[2],fm[1],fm[3], sep="")), data=data)$residuals
      result$residuals<-res
      return(result)
    }

    resultFULL[[ind.resp]]<-fillresult(t)
  }

  names(resultFULL)<-response
  return(resultFULL)
}
