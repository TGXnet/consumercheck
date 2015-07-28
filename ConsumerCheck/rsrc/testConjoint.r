#########################################################################
############## test Conjoint Analysis Program (conjoint.r) ##############
#########################################################################

# How to call this script from any R working directory
# source("path/testConjoint.r", chdir=TRUE)

#### Set paths
# Work Directory
WD <- getwd()
# Project Directory
PD <- dirname(dirname(WD))
# Data Directory
# Ham data
HDD <- file.path(PD, "TestData", "HamData")
# Barley bread data
BDD <- file.path(PD, "TestData", "BarleyBread")
# DD <- "/home/thomas/TGXnet/Prosjekter/2009-13-ConsumerCheck/Conjoint/Conjoint_18_03_2013/data"

library(Hmisc)
library(lmerTest)
source("conjoint.r")

###########################################################################
# Analyse Barley Bready data from Norway
###########################################################################

bb.N <- read.csv(file=file.path(BDD, "BB_N_noMissing.csv"), sep=";")


response <- c("Liking")
fixed <- list(Product=c("Barley", "Salt"), Consumer="Sex")
random <- c("Consumer")
facs<-c("Consumer", "Barley", "Salt", "Sex", "Age")

res <- conjoint(structure=3, bb.N, response, fixed, random, facs)

##check with the ham
# response <- c("Informed.liking")
# fixed <- list(Product=c("Product", "Information"), Consumer="Gender")
# random <- c("Consumer")
# facs <- c("Consumer", "Product", "Information", "Gender")
# 
# res.ham <- conjoint(structure=3, ham, response, fixed, random, facs)

randTab <- res[[1]][1]
anovaTab <- res[[1]][2]
lsmeansTab <- res[[1]][3]
diffLsTab <- res[[1]][4]
resid <- res[[1]][5]
resid.ind <- res[[1]][6]

print(res$Liking$anova.table)
print(randTab)

### write.table(randTab, file="__conjRes_randomTable.txt", sep ="\t", eol="\n", row.names=TRUE, col.names=TRUE)
