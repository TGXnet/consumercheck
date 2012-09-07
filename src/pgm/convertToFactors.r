convertToFactors<-function(data, facs)
{
 #convert matrix to dataframe
 data<-data.frame(data)
 facs.ind<-match(facs, names(data))
 
 #convert effects to factors
 for(i in facs.ind)
  data[,i]<-factor(data[,i])

 return(data)
}