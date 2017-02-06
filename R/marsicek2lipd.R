library(readxl)
md = read_excel("~/Downloads/Posy_1905.xls",1)
cd = read_excel("~/Downloads/Posy_1905.xls",2,skip = 3)
pd = read_excel("~/Downloads/Posy_1905.xls",3)

#initialize a new lipd object
L = list()

#assign some default metadata
L$lipdVersion = 1.2
L$archiveType = "lake sediment"

#read in metadata

L$investigator = md[1,2]
L$lastUpdated = md[2,2]
L$dataContributor = md[3,2]

L$pub[[1]]$citation = md[5,2]

L$geo$location = md[10,2]

L$neotomaCoreID = as.numeric(md[12,2])
L$geo$latitude = as.numeric(md[14,2])
L$geo$longitude = as.numeric(md[15,2])
L$geo$elevation = as.numeric(md[17,2])

proxy = md[19,2] #for later use
calibration = list()
calibration$method = md[19,4] #for later use
taxaList = md[21,2] #for later use
pn=1;
for(p in 26:28){
  if(!is.na(md[p,2])){
    pn = pn+1
    L$pub[[pn]]$citation = md[p,2]
    
  }
}

L$geo$notes = md[29,2]






#build key value pairs
#remove data where all is NA
# allna = which(apply(is.na(md),1,all))
# mdg = md[-allna,]
# 
# #go through good and assign
# for