#########################################################################
############## test Conjoint Analysis Program (conjoint.r) ##############
#########################################################################

#### Set paths
orig_WD <- getwd()
# Working Directory
WD <- dirname(orig_WD)
setwd(WD)
# Where the testdata is to be found
# DD <- file.path(WD, "datasets", "HamData")
DD <- "/home/thomas/TGXnet/Prosjekter/2009-13-ConsumerCheck/Conjoint/ConjointConsumerCheck_2012-04-27/data preparation/ham data"

# Load libraries
# install.packages(paste(getwd(),"/MixMod.zip", sep=""), repos = NULL)
library(MixMod)
library(lme4)
library(Hmisc)
source(file.path(WD, "rsrc", "conjoint.r"))

###########################################################################
# example from the book: Ham data
###########################################################################

#ham<-read.csv(paste(getwd(),"/data/ham.csv",sep=""), sep = ";")
consum.attr<-read.table(file=file.path(DD, "consumAttr.txt"), header=TRUE)
design.matr<-read.table(file=file.path(DD, "designMatr.txt") ,header=TRUE)
consumer.liking<-read.table(file=file.path(DD, "consumLike.txt"), header=TRUE, check.names=FALSE)
list.consum.liking<-list(matr.liking=list(consumer.liking), names.liking=c("informed.liking"))

fixed<-list(Product=c("Product", "Information"), Consumer="Kjonn")
random<-c("Consumer")
response<-c("informed.liking")
facs<-c("Consumer","Product","Information","Kjonn")

res.ham<-ConjointMerge(structure=3, consum.attr=consum.attr, design.matr=design.matr, list.consum.liking=list.consum.liking, response, fixed, random, facs)


###########################################################################
# example: gm data 
###########################################################################
# Load liking data (here we have three of them)
#odfl.liking <- read.table(file=paste(getwd(),"/data preparation/gm data/odour-flavour_liking.txt", sep=""), header=TRUE, check.names=FALSE)
#consistency.liking <- read.table(file=paste(getwd(),"/data preparation/gm data/consistency_liking.txt", sep=""), header=TRUE, check.names=FALSE)
#overall.liking <- read.table(file=paste(getwd(),"/data preparation/gm data/overall_liking.txt", sep=""), header=TRUE, check.names=FALSE)

# Load consumer attributes
#consum.attr <- read.table(file=paste(getwd(),"/data preparation/gm data/consumerAttributes.txt", sep=""), header=TRUE)

# Load design matrix
#design.matr <- read.table(file=paste(getwd(),"/data preparation/gm data/design.txt", sep=""), header=TRUE)

#list.consum.liking<-list(matr.liking=list(odfl.liking, consistency.liking, overall.liking), names.liking=c("odourflavour", "consistency", "overall"))

#fixed<-list(Product=c("Flavour", "Sugarlevel"), Consumer="Sex")
#random<-c("Consumer")
#response<-c("odourflavour", "consistency", "overall")
#facs<-c("Consumer","Flavour","Sugarlevel","Sex")
 
#res.gm<-conjoint(structure=3, consum.attr=consum.attr, design.matr=design.matr, list.consum.liking=list.consum.liking, response, fixed, random, facs)
