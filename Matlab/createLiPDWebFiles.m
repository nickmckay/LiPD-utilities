%create lipd-web (google spreadsheet) files

L=readLiPD('/Users/nick/Dropbox/LiPD/library/Arc-HalletLake.McKay.2008.lpd');



%paleoData
% % % deal with authorization on google
%first create a new spreadsheet
load('google_tokens.mat');

%see how long since last refresh; update if more than an hour
if ((now-lastUpdated)*24*60)>60
    
    % to refresh the Docs access token (usually expires after 1 hr) you'd call
    aTokenDocs=refreshAccessToken(client_id,client_secret,rTokenDocs);
    
    % to refresh the Spreadsheet access token (usually expires after 1 hr) you'd call
    aTokenSpreadsheet=refreshAccessToken(client_id,client_secret,rTokenSpreadsheet);
    
    %reset when last updated
    lastUpdated=now;
    save -append google_tokens.mat lastUpdated aTokenDocs aTokenSpreadsheet
end

%this will create a new spreadsheet, with a useless first worksheet.
%We'll delete it later
spreadSheetNew=createSpreadsheet(L.dataSetName,aTokenDocs,'default.csv','text/csv');
L.googleSpreadSheetKey=spreadSheetNew.spreadsheetKey;

%now create a worksheet for each paleoDataTable
pdNames=fieldnames(L.paleoData);
for pd=1:length(L.paleoData)
    P=L.paleoData.(pdNames{pd});
    %get the names of the columns
    colNames=structFieldNames(P);
    nCol=length(colNames);
    nRow=length(P.(colNames{1}).values);
    %create a new spreadsheet, with two extra rows (for variable name
    %and TSID)
    newWS=createWorksheet(spreadSheetNew.spreadsheetKey,nRow+2,nCol,['paleoData-' pdNames{pd}],aTokenSpreadsheet);
    P.googWorkSheetKey=newWS.worksheetKey;
    
    %go through the columns and populate the cells
    for c=1:nCol
        %check for TSid
        if ~isfield(P.(colNames{c}),'TSid')
            %should probably create one - function that checks against
            %master list?
            %for now - temporary id
            P.(colNames{c}).TSid=['temp' num2str(rand*1e6,6)];
        end
        
        if ~iscell(P.(colNames{c}).values)
            colData=[P.(colNames{c}).variableName; P.(colNames{c}).TSid; cellstr(num2str(P.(colNames{c}).values))];
        else
            colData=[P.(colNames{c}).variableName; P.(colNames{c}).TSid; P.(colNames{c}).values];
        end
        %figure out what column to put it in
        if isfield(P.(colNames{c}),'number')
            colNum=P.(colNames{c}).number;
        else
            colNum=c;
        end
        editWorksheetColumn(spreadSheetNew.spreadsheetKey,newWS.worksheetKey,colNum,1:nRow,colData,aTokenSpreadsheet);
    end
    L.paleoData.(pdNames{pd})=P;
    
end

%chronData
%if there's chrondata, write that too.
if isfield(L,'chronData')
    %now create a worksheet for each chronDataTable
    pdNames=fieldnames(L.chronData);
    for pd=1:length(L.chronData)
        P=L.chronData.(pdNames{pd});
        %get the names of the columns
        colNames=structFieldNames(P);
        nCol=length(colNames);
        nRow=length(P.(colNames{1}).values);
        %create a new spreadsheet, with two extra rows (for variable name
        %and TSID)
        newWS=createWorksheet(spreadSheetNew.spreadsheetKey,nRow+2,nCol,['chronData-' pdNames{pd}],aTokenSpreadsheet);
        P.googWorkSheetKey=newWS.worksheetKey;
        
        
        %go through the columns and populate the cells
        for c=1:nCol
            %check for TSid
            if ~isfield(P.(colNames{c}),'TSid')
                %should probably create one - function that checks against
                %master list?
                %for now - temporary id
                P.(colNames{c}).TSid=['temp' num2str(rand*1e6,6)];
            end
            
            if ~iscell(P.(colNames{c}).values)
                colData=[P.(colNames{c}).variableName; P.(colNames{c}).TSid; cellstr(num2str(P.(colNames{c}).values))];
            else
                colData=[P.(colNames{c}).variableName; P.(colNames{c}).TSid; P.(colNames{c}).values];
            end
            %figure out what column to put it in
            if isfield(P.(colNames{c}),'number')
                colNum=P.(colNames{c}).number;
            else
                colNum=c;
            end
            editWorksheetColumn(spreadSheetNew.spreadsheetKey,newWS.worksheetKey,colNum,1:nRow,colData,aTokenSpreadsheet);
        end
        L.chronData.(pdNames{pd})=P;%write it back into the main structure
    end
end
%get the names of the worksheets
wsNames=getWorksheetList(spreadSheetNew.spreadsheetKey,aTokenSpreadsheet);


%metadata
%edit that first sheet to become the metadatasheet






%delete that stupid first worksheet
%deleteWorksheet(spreadSheetNew.spreadsheetKey,wsNames(1).worksheetKey,aTokenSpreadsheet);


%save updated LipD file?
