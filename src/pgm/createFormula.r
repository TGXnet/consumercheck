 ### create formula for lmer object ###############################################
 createFormula<-function(structure, data, response, fixed, random)
 {
   data.compl<-data[complete.cases(data),]
   nrow.compl<-nrow(data.compl)
   source(paste(getwd(),"/pgm/checkNumberInteract.r",sep=""))
   source(paste(getwd(),"/pgm/createFormulaAllFixRand.r",sep=""))
   
   f<-function(x){
     is.factor(data[,which(colnames(data)==x)])
   }

   if(structure==1 || structure==2)
   {
     formula1<-paste(response, "~", sep="")
     #add main effects and 2d order random interactions 
     for(i in 1:length(fixed))
     {     
       if(checkNumberInteract(data,fixed[i]))
          next()
       if(checkNumberInteract(data,c(fixed[i],random[1])))
       {   
          formula1<-paste(formula1,fixed[i],"+",sep="")
          next()
       }  
       if(is.factor(data[,which(colnames(data)==fixed[i])]))   
          formula1<-paste(formula1,fixed[i],"+","(1|",fixed[i],":",random[1],")","+",sep="")
       else
          formula1<-paste(formula1,fixed[i],"+","(1+",fixed[i],"|",random[1],")","+",sep="")
       
     }
     #add random Consumer effect
     formula1<-paste(formula1,"(1|",random[1],")",sep="")
   }
   if(structure==2)
   {
     #add second order interactions in fixed part and 3d order in random part
     inter<-combn(fixed,2,simplify = FALSE)
     for(i in 1:length(inter))
     {       
       if(checkNumberInteract(data,c(inter[[i]][1],inter[[i]][2])))
         next()       
       formula1<-paste(formula1,"+",inter[[i]][1],":",inter[[i]][2],sep="")
       
       if(checkNumberInteract(data,c(inter[[i]][1],inter[[i]][2],random[1])))
         next()
       ind.cov<-which(unlist(lapply(inter[[i]],f))!=TRUE)
       if(length(ind.cov)==0)       
          formula1<-paste(formula1,"+","(1|",inter[[i]][1],":",inter[[i]][2],":",random[1],")",sep="")
       else if(length(ind.cov)==1)
       {
          formula1<-paste(formula1,"+","(1+",inter[[i]][ind.cov],"|",inter[[i]][-ind.cov],":",random[1],")",sep="")
       }
       
     } 
   }
   if(structure==3)
   {
     
     return(createFormulaAllFixRand(structure,data,response,fixed,random))     
       
   } 
   return(as.formula(formula1))
  }


