D <- readLipd("~/Dropbox/HoloceneLiPDLibrary/masterDatabase/")
TS <- extractTs(D)
py <- geoChronR::pullTsVariable(TS,"pub1_pubYear")
y <- geoChronR::pullTsVariable(TS,"pub1_year")


nTS <- fix_pubYear(TS)
py2 <- geoChronR::pullTsVariable(nTS,"pub1_pubYear")
y2 <- geoChronR::pullTsVariable(nTS,"pub1_year")

nD <- collapseTs(nTS)
TS2 <- extractTs(nD)
py3 <- geoChronR::pullTsVariable(TS2,"pub1_pubYear")
y3 <- geoChronR::pullTsVariable(TS2,"pub1_year")


#smaller test
L <- readLipd("~/Downloads/2005-804.Ledu.2013.lpd")
ts <- extractTs(L)
ts <- geoChronR::pushTsVariable(ts,"paleoData_test",matrix("test",nrow = length(ts)),createNew = TRUE)
ts <- geoChronR::pushTsVariable(ts,"test",matrix("test",nrow = length(ts)),createNew = TRUE)
ts <- geoChronR::pushTsVariable(ts,"pub1_test",matrix("test",nrow = length(ts)),createNew = TRUE)

L2 <- collapseTs(ts)
names(L)
names(L2)

names(L$pub[[1]])
names(L2$pub[[1]])


names(L$paleoData[[1]]$measurementTable[[1]])
names(L2$paleoData[[1]]$measurementTable[[1]])

names(L$paleoData[[1]]$measurementTable[[1]]$Temp)
names(L2$paleoData[[1]]$measurementTable[[1]]$Temp)



L$pub[[1]]$year
L2$pub[[1]]$year


nts <- fix_pubYear(ts)
nts[[1]]
l <- collapseTs(nts)