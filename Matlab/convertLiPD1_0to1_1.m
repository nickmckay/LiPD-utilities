function L=convertLiPD1_0to1_1(L)

C=L.chronData;
cnames = fieldnames(C);
newC=cell(1,1);
for i = 1:length(cnames);
    Cn=rmfieldsoft(C.(cnames{i}),{'chronDataTableName','chronTableName','chronMD5'});
    newC{i,1}.chronMeasurementTable = Cn;   
end
L.LiPDVersion = '1.1';
L.chronData=newC;