function GTS=getLiPDGoogleChronData(GTS)
checkGoogleTokens;
for ts=1:length(GTS)
    TSid=GTS(ts).chronData_TSid;
 
    TSids=getWorksheetRow(GTS(ts).googleSpreadSheetKey,GTS(ts).chronData_googleWorkSheetKey,2,aTokenSpreadsheet);
    whichCol=find(strcmp(TSid,TSids));
    if isempty(whichCol)
        error(['can''t match the tsid ' TSid])
    end
    colData=getWorksheetColumn(GTS(ts).googleSpreadSheetKey,GTS(ts).chronData_googleWorkSheetKey,whichCol,aTokenSpreadsheet);   
    v=convertCellStringToNumeric(colData(3:end));
    if ischar(v)
        v=cellstr(v);
    end
    GTS(ts).chronData_values=v;
end

