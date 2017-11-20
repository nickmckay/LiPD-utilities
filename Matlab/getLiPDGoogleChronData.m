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
         elseif length(whichCol)>1
        error('Duplicate TSids in dataTable')
    else
        colData=getWorksheetColumn(GTS(ts).googleSpreadSheetKey,GTS(ts).chronData_googleWorkSheetKey,whichCol,aTokenSpreadsheet);
        v=convertCellStringToNumeric(colData(3:end));
        if ischar(v)
            v=cellstr(v);
        end
        
        
        %convert blanks to NaNs
        if iscell(v)
        v(cellfun(@isempty,v))={NaN};
        else
        v(isempty(v))=NaN; 
        end
        
        if ~exist('nObs')
            nObs = length(v);
        end
        
        
        %deal with records that are too short
        if length(v) < nObs
            if iscell(v)
                v = [v ; repmat({NaN},nObs-length(v),1)];
            else
               v = [v ; nan(nObs-length(v),1)] ;
            end
        end
               
        GTS(ts).chronData_values=v;

       
    end

end

