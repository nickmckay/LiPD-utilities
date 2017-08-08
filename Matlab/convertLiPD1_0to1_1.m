function L=convertLiPD1_0to1_1(L,forceConvert)

if nargin<2
    forceConvert = 0;
end
if ~isfield(L,'lipdVersion')
    
    L.lipdVersion = 1.0;
end

if ischar(L.lipdVersion)
    L.lipdVersion = str2num(L.lipdVersion);
end

if L.lipdVersion == 1.0 | forceConvert
    if isfield(L,'chronData')
    C=L.chronData;
    cnames = fieldnames(C);
    newC=cell(1,1);
    for i = 1:length(cnames);
        Cn=rmfieldsoft(C.(cnames{i}),{'chronDataTableName','chronTableName','chronMD5'});
        newC{i,1}.chronMeasurementTable = Cn;
    end
        L.chronData=newC;
    end
    L.lipdVersion = 1.1;
    
end

