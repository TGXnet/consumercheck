createLMERmodel<-function(structure, data1, response, fixed, random, corr)
{
 
 source("createFormula.r")
 source("checkNumberInteract.r")
 source("checkComb.r")
 source("checkZeroCell.r")
 source("createFormulaAllFixRand.r")

 #construct formula for lmer model 
 #fma<-createFormula(structure, data, response, fixed, random)
 mf.final <- createFormulaAllFixRand(structure, data1, response, fixed, random, corr) 
 

 
 model<-eval(substitute(lme4::lmer( mf.final),list( mf.final= mf.final)))
 
 model<-as(model,"mer")
 model<-update(model)
 
 #mf.final<-update.formula(formula(model),formula(model))
 #model<-eval(substitute(lmer(mf.final, data=data),list(mf.final=mf.final)))
 #model<-update(model, data=data ,REML=TRUE)
 
 return(model)
}
