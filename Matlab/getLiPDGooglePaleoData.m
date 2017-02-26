function GTS=getLiPDGooglePaleoData(GTS)
checkGoogleTokens;
for ts=1:length(GTS)
    TSid=GTS(ts).paleoData_TSid;
    
    TSids=getWorksheetRow(GTS(ts).googleSpreadSheetKey,GTS(ts).paleoData_googleWorkSheetKey,2,aTokenSpreadsheet);
    whichCol=find(strcmp(TSid,TSids));
    if isempty(whichCol)
        if exist('nObs')
            warning(['can''t match the tsid ' TSid '; filling the column with NaNs'])
            GTS(ts).paleoData_values=nan(nObs,1);
        else
            error('I cant do anything if I cant match the first TSid')
        end
    else
        colData=getWorksheetColumn(GTS(ts).googleSpreadSheetKey,GTS(ts).paleoData_googleWorkSheetKey,whichCol,aTokenSpreadsheet);
        v=convertCellStringToNumeric(colData(3:end));
        if ischar(v)
            v=cellstr(v);
        end
        GTS(ts).paleoData_values=v;
        nObs = length(v);
    end
end


