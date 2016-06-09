function L=convertLiPD1_0to1_1(L)

if ~isfield(L,'LiPDVersion')
    
    L.LiPDVersion = 1.0;
end

if L.LiPDVersion == 1.0
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
    L.LiPDVersion = '1.1';
    
end

