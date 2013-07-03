#########################################################################
############## test Conjoint Analysis Program (conjoint.r) ##############
#########################################################################

# How to call this script from any R working directory
# source("path/testConjoint.r", chdir=TRUE)

#### Set paths
# orig_WD <- getwd()
# Working Directory
# WD <- file.path(orig_WD, "rsrc")
# setwd(WD)
# Where the testdata is to be found
# DD <- file.path(WD, "datasets", "HamData")
DD <- "/home/thomas/TGXnet/Prosjekter/2009-13-ConsumerCheck/Conjoint/Conjoint_18_03_2013/data"

#library(MixMod)
#library(lme4)
#library(MASS)
library(Hmisc)
library(lmerTest)
source("conjoint.r")

###########################################################################
# Analyse Barley Bready data from CZ
###########################################################################

#for bug2
bb <- read.csv(file=file.path(DD, "BB_ALL_noAge5.csv"), sep=";")
#ham <- read.csv(paste(getwd(),"/data/ham.csv",sep=""), sep = ";")
#for bug1
bb <- read.csv(file=file.path(DD, "BB_CZ.csv"), sep=";")
bb_CZ <- read.csv(file=file.path(DD, "BB_CZ.csv"), sep=";")
bb_CZ_noMissing <- read.csv(file=file.path(DD, "BB_CZ_noMissing.csv"), sep=";")
bb_E <- read.csv(file=file.path(DD, "BB_E.csv"), sep=";")
bb_N <- read.csv(file=file.path(DD, "BB_N.csv"), sep=";")
bb_SC <- read.csv(file=file.path(DD, "BB_SC.csv"), sep=";")
bb_SP <- read.csv(file=file.path(DD, "BB_SP.csv"), sep=";")


# for bug1
response <- c("Liking")
#fixed<-list(Product=c("Barley", "Salt"), Consumer="Sex")
fixed<-list(Product=c("Barley", "Salt"), Consumer=c("Sex", "Age"))
random<-c("Consumer")
facs<-c("Consumer","Barley","Salt","Sex", "Age")

res <- ConjointNoMerge(structure=2, bb_SP, response, fixed, random, facs)

randTab <- res[[1]][1]
anovaTab <- res[[1]][2]
lsmeansTab <- res[[1]][3]

### write.table(randTab, file="__conjRes_randomTable.txt", sep ="\t", eol="\n", row.names=TRUE, col.names=TRUE)
### write.table(anovaTab, file="__conjRes_anovaTable.txt", sep ="\t", eol="\n", row.names=TRUE, col.names=TRUE)
### write.table(lsmeansTab, file="__conjRes_lsmeansTable.txt", sep ="\t", eol="\n", row.names=TRUE, col.names=TRUE)


# for bug2
### response <- c("Liking")
#fixed<-list(Product=c("Barley", "Salt"), Consumer="Sex")
### fixed<-list(Product=c("Barley", "Salt"), Consumer=c("Country","Sex", "Age"))
### random<-c("Consumer")
### facs<-c("Consumer","Barley","Salt","Country","Sex","Age")

### res <- conjoint(structure=2, bb, response, fixed, random, facs)


# bug 3 wine
#ham<-read.csv(paste(getwd(),"/data/ham.csv",sep=""), sep = ";")
### consum.attr<-read.table(file="C:/Users/Romario/Desktop/Sasha Crap/Conjoint/Conjoint bug wine/consumers.txt",header=TRUE)
### design.matr<-read.table(file="C:/Users/Romario/Desktop/Sasha Crap/Conjoint/Conjoint bug wine/wines.txt",header=TRUE)
### consumer.liking<-read.table(file="C:/Users/Romario/Desktop/Sasha Crap/Conjoint/Conjoint bug wine/testfull.txt",header=TRUE, check.names=FALSE)
### list.consum.liking<-list(matr.liking=list(consumer.liking), names.liking=c("liking"))

### data <- makeDataForConjoint(design.matr, list.consum.liking, consum.attr)

### response <- c("liking")
### fixed<-list(Product=c("wine1", "wine2"), Consumer=c("gender"))
### random<-c("Consumer")
### facs<-c("Consumer","wine1","wine2","gender")

### res <- conjoint(structure=1, data, response, fixed, random, facs)


# test covariates with carrots data
### data(carrots)

### response<-c("Preference")
### fixed<-list(Product=c("sens2","sens1"),Consumer=c("Income","Homesize"))
### random<-c("Consumer")
### facs <- c("Consumer", "Income", "Homesize")

### res <- conjoint(structure=3, carrots, response, fixed, random, facs)
