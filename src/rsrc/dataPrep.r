
#### prepare the input data (three datasets) from carrots data
# consumer liking data
#spl.data<-split(data, data$Consumer)
#consumer.liking<-NULL

#for(i in 1:length(spl.data))
#{
#  c1<-spl.data[[i]][8]
#  colnames(c1)<-paste(unique(spl.data[[i]]$Consumer))  
#  if(i==1)
#    consumer.liking<-c1
#  else
#    consumer.liking<-cbind(consumer.liking,c1)
#}

# design matrix
#design.matr<-unique(data[,c(9:11,14)])

# Consumer attributes data
#cons.attr<-unique(data[,c(1:7)])[,c(2:7)]
#rownames(cons.attr)<-colnames(consumer.liking)


# write three dataset into txt files
#write.table(file="C:/alku/projects/Conjoint MixMod/Conjoint versions/ConjointConsumerCheck_26_02_2012/data preparation/carrots data/consumAttr.txt", cons.attr, quote=FALSE)
#write.table(file="C:/alku/projects/Conjoint MixMod/Conjoint versions/ConjointConsumerCheck_26_02_2012/data preparation/carrots data/designMatr.txt", design.matr, quote=FALSE)
#write.table(file="C:/alku/projects/Conjoint MixMod/Conjoint versions/ConjointConsumerCheck_26_02_2012/data preparation/carrots data/consumLike.txt", consumer.liking, quote=FALSE)


# makes one dataset out of 3 datasets in order to run conjoint function
makeDataForConjoint<-function(design.matr, list.consum.liking, consum.attr=NULL)
{
    out.data.prev<-NULL
   for(ind.liking in 1:length(list.consum.liking$matr.liking))
    {
      # merge design matrix and all consumer liking matrices
      mm<-merge(design.matr, list.consum.liking$matr.liking[[ind.liking]], by="row.names")
      out.data<-mm[,2:(ncol(design.matr)+1)]
      #out.data$Consumer.Liking2<-mm[,(ncol(design.matr)+2)] 
      out.data[,list.consum.liking$names.liking[ind.liking]]<-mm[,(ncol(design.matr)+2)]
      out.data$Consumer<-rep(colnames(mm)[ncol(design.matr)+2],nrow(mm))
      for( i in (ncol(design.matr)+3):ncol(mm))
      {
        out.data1<-mm[,2:(ncol(design.matr)+1)]
        out.data1[,list.consum.liking$names.liking[ind.liking]]<-mm[,i]  
        out.data1$Consumer<-rep(colnames(mm)[i],nrow(mm))
        out.data<-rbind(out.data, out.data1)
      }
      if(!is.null(out.data.prev))
        out.data<-merge(out.data, out.data.prev, sort=FALSE)
          
      out.data.prev<-out.data      
    }
  
    if(!is.null(consum.attr))
      out.data<-merge(out.data, consum.attr, by.x="Consumer", by.y="row.names", all.x=TRUE)
    out.data$Consumer<-as.numeric(out.data$Consumer)
    return(out.data)
}

