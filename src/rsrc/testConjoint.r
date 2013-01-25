#########################################################################
############## test Conjoint Analysis Program (conjoint.r) ##############
#########################################################################


#### change here the path
# dir<-"C:/alku/projects/Conjoint MixMod/Conjoint versions/ConjointConsumerCheck_27_02_2012"
dir<-"C:/Users/PC/My Documents/CCDev/ConjointConsumerCheck_27_04_2012"
setwd(dir)


# install.packages(paste(getwd(),"/MixMod.zip", sep=""), repos = NULL)
library(MixMod)
library(lme4)
library(Hmisc)
source(paste(getwd(),"/rsrc/conjoint.r",sep=""))

###########################################################################
# example from the book: Ham data
###########################################################################


#ham<-read.csv(paste(getwd(),"/data/ham.csv",sep=""), sep = ";")
consum.attr<-read.table(file=paste(getwd(),"/data preparation/ham data/consumAttr.txt",sep=""),header=TRUE)
design.matr<-read.table(file=paste(getwd(),"/data preparation/ham data/designMatr.txt",sep=""),header=TRUE)
consumer.liking<-read.table(file=paste(getwd(),"/data preparation/ham data/consumLike.txt",sep=""),header=TRUE, check.names=FALSE)
list.consum.liking<-list(matr.liking=list(consumer.liking), names.liking=c("informed.liking"))

fixed<-list(Product=c("Product", "Information"), Consumer="Kjonn")
random<-c("Consumer")
response<-c("informed.liking")
facs<-c("Consumer","Product","Information","Kjonn")

res.ham<-conjoint(structure=3, consum.attr=consum.attr, design.matr=design.matr, list.consum.liking=list.consum.liking, response, fixed, random, facs)


###########################################################################
# example: gm data 
###########################################################################
# Load liking data (here we have three of them)
odfl.liking <- read.table(file=paste(getwd(),"/data preparation/gm data/odour-flavour_liking.txt", sep=""), header=TRUE, check.names=FALSE)
consistency.liking <- read.table(file=paste(getwd(),"/data preparation/gm data/consistency_liking.txt", sep=""), header=TRUE, check.names=FALSE)
overall.liking <- read.table(file=paste(getwd(),"/data preparation/gm data/overall_liking.txt", sep=""), header=TRUE, check.names=FALSE)

# Load consumer attributes
consum.attr <- read.table(file=paste(getwd(),"/data preparation/gm data/consumerAttributes.txt", sep=""), header=TRUE)

# Load design matrix
design.matr <- read.table(file=paste(getwd(),"/data preparation/gm data/design.txt", sep=""), header=TRUE)

list.consum.liking<-list(matr.liking=list(odfl.liking, consistency.liking, overall.liking), names.liking=c("odourflavour", "consistency", "overall"))

fixed<-list(Product=c("Flavour", "Sugarlevel"), Consumer="Sex")
random<-c("Consumer")
response<-c("odourflavour", "consistency", "overall")
facs<-c("Consumer","Flavour","Sugarlevel","Sex")
 
res.gm<-conjoint(structure=3, consum.attr=consum.attr, design.matr=design.matr, list.consum.liking=list.consum.liking, response, fixed, random, facs)

