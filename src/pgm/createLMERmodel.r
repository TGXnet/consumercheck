createLMERmodel<-function(structure, data, response, fixed, random, corr)
{
 
 source(paste(getwd(),"/pgm/createFormula.r",sep=""))
 source(paste(getwd(),"/pgm/checkNumberInteract.r",sep=""))
 source(paste(getwd(),"/pgm/createFormulaAllFixRand.r",sep=""))  

 #construct formula for lmer model 
 #fma<-createFormula(structure, data, response, fixed, random)
 mf.final<-createFormulaAllFixRand(structure, data, response, fixed, random, corr) 

 
 
 model<-eval(substitute(lmer( mf.final, data=data),list( mf.final= mf.final)))
 
 #model<-update(model, REML=TRUE)
 
 mf.final<-update.formula(formula(model),formula(model))
 model<-eval(substitute(lmer(mf.final, data=data),list(mf.final=mf.final)))
 #model<-update(model, data=data ,REML=TRUE)
 
 return(model)
}