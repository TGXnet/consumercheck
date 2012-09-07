

#create formula with all random and fixed effects and their interactions
createFormulaAllFixRand<-function(structure, data, response, fixed, random, corr)
{
   
   f1<-function(x){
     is.factor(data[,which(colnames(data)==x)])
   }
  
   formula1<-NULL
   is.cov.present<-FALSE
   covs<-fixed$Product[which(unlist(lapply(fixed$Product,f1))!=TRUE)]
   if(length(covs)>0)
     is.cov.present<-TRUE
   formula.covs<-paste(covs,collapse="+")
     
     
   
   for (j in 1:length(c(fixed$Product, fixed$Consumer)))
   {
         #create all combinations of j'th order of fixed effects
         if(structure==1 & j>1)
           break
         if(structure==2 & j>2)
           break
         inter.fix<-combn(c(fixed$Product, fixed$Consumer), j, simplify = FALSE)
         
         #put in formula all fixed factor combinations of j'th order
         for(k in 1:length(inter.fix))
         {
            eff.fix<-paste(inter.fix[[k]],collapse=":")
            if(checkNumberInteract(data,inter.fix[[k]]))
              next()
            if(is.null(formula1))
               formula1<-paste(response, "~", eff.fix, sep="")
            else 
               formula1<-paste(formula1,"+", eff.fix, sep="")
            
                      
            #create all combinations of i'th order of random effects (interactions with fixed)
            for(i in 1:length(random))
            {
              
               inter.rand<-combn(random,i,simplify = FALSE)
               #put in formula all random (interactions with fixed) factor combinations of i'th order
               for(l in 1:length(inter.rand))
               { 
                                  
                 if(checkNumberInteract(data,c(inter.rand[[l]],inter.fix[[k]])))
                   next()
                 # if the consumer attributes are present in a fixed part
                 if(!is.null(fixed$Consumer) && length(which(inter.rand[[l]] %in% "Consumer"==TRUE))!=0)
                   eff.rand<-paste(c(inter.rand[[l]],fixed$Consumer),collapse=":")
                 else
                   eff.rand<-paste(inter.rand[[l]],collapse=":")
                 ind.cov<-which(unlist(lapply(inter.fix[[k]],f1))!=TRUE)
                 #eff.fix.ind.fix<-paste(inter.fix[[k]][-ind.cov],collapse=":")
                 #if(length(ind.cov)>0)
                 #{
                #   is.cov.present<-TRUE
                #   #if(length(ind.cov)>1)
                #   #  next
                #   covs<-paste(inter.fix[[k]][ind.cov],collapse="+")                   
                #   if(eff.fix.ind.fix!="")
                #       formula1<-paste(formula1,"+", "(1+",covs,"|",eff.fix.ind.fix,":",eff.rand,")",sep="") 
                #   else
                #       formula1<-paste(formula1,"+", "(1+",covs,"|",eff.rand,")",sep="") 
                                    
                # }
                # else if(!is.cov.present)
                #   formula1<-paste(formula1,"+", "(1|",eff.fix,":",eff.rand,")",sep="") 
                 if(length(ind.cov)==0)
                 {
                   # if the attributes associated with Consumer are present then
                   # eliminate this attribute from eff.fix
                   eff.fix.rand<-if(!is.null(fixed$Consumer)) paste(inter.fix[[k]][!inter.fix[[k]] %in% fixed$Consumer], collapse=":") else eff.fix
                   if(eff.fix.rand=="")
                     next
                   if(is.cov.present)
                   {
                     if(corr)
                       formula1<-paste(formula1,"+", "(1+",formula.covs,"|",eff.fix.rand,":",eff.rand,")",sep="")
                     else
                       formula1<-paste(formula1,"+", paste(lapply(covs, function(x) paste("(0+",x,"|",eff.fix.rand,":",eff.rand,")",sep="")),collapse="+"))
                     
                   }                      
                   if(!is.cov.present || !corr)
                      formula1<-paste(formula1,"+", "(1|",eff.fix.rand,":",eff.rand,")",sep="")
                 }
                    
               }
             }
          }
     }
     
   
     #create all combinations of i'th order of random effects 
     for(i in 1:length(random))
     {
        inter.rand<-combn(random,i,simplify = FALSE)
        #put in formula all random factor combinations of i'th order
        for(l in 1:length(inter.rand))
        { 
              
          if(checkNumberInteract(data,inter.rand[[l]]))
             next()
          
          # if the consumer attributes are present in a fixed part
          if(!is.null(fixed$Consumer) && length(which(inter.rand[[l]] %in% "Consumer"==TRUE))!=0)
             eff.rand<-paste(c(inter.rand[[l]],fixed$Consumer),collapse=":")
          else
             eff.rand<-paste(inter.rand[[l]],collapse=":")
          
          if(is.cov.present)
          {
            if(corr)
              formula1<-paste(formula1,"+", "(1+",formula.covs,"|",eff.rand,")",sep="")
            else
              formula1<-paste(formula1,"+", paste(lapply(covs, function(x) paste("(0+",x,"|",eff.rand,")",sep="")),collapse="+"))
           }            
          if(!is.cov.present || !corr)
            formula1<-paste(formula1,"+", "(1|",eff.rand,")",sep="")
               
        }
     }     
 return(as.formula(formula1))
}



