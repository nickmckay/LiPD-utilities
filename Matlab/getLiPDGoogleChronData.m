function GTS=getLiPDGoogleChronData(GTS)
checkGoogleTokens;

for ts=1:length(GTS)
    noTSid=0;
    TSid=GTS(ts).chronData_TSid;
    if length(TSid)==0
        noTSid = 1;
        warning('This TSid field is empty. Shame on you.')
        TSid = createTSID(GTS(ts).chronData_variableName,GTS(ts).dataSetName,GTS(ts).googleSpreadSheetKey,GTS(ts).chronData_googleWorkSheetKey);
        warning(['Creating a new TSid... ' TSid ' - I hope we guess righton matching!'])
        GTS(ts).chronData_TSid=TSid;
    end
    
    TSids=getWorksheetRow(GTS(ts).googleSpreadSheetKey,GTS(ts).chronData_googleWorkSheetKey,2,aTokenSpreadsheet);
    if noTSid
        firstNoTSid = min(find(cellfun(@isempty,TSids)));
        editWorksheetCell(GTS(ts).googleSpreadSheetKey,GTS(ts).chronData_googleWorkSheetKey,2,firstNoTSid,TSid,aTokenSpreadsheet)
        warning('Guessed about TSid, assuming missing ones are in order. If theyre not, this wont work.')
    end
    whichCol=find(strcmp(TSid,TSids));
    
    if isempty(whichCol)
        if exist('nObs')
            warning(['can''t match the tsid ' TSid '; filling the column with NaNs'])
            GTS(ts).chronData_values=nan(nObs,1);
        else
            error('I cant do anything if I cant match the first TSid')
        end
    else
        colData=getWorksheetColumn(GTS(ts).googleSpreadSheetKey,GTS(ts).chronData_googleWorkSheetKey,whichCol,aTokenSpreadsheet);
        v=convertCellStringToNumeric(colData(3:end));
        if ischar(v)
            v=cellstr(v);
        end
        GTS(ts).chronData_values=v;
        nObs = length(v);
    end
end

