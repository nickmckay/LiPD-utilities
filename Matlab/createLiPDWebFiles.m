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

%extract timeseries
TS=structord( extractTimeseriesLiPD(L,1));

%get rid of unnecessary metadata
torem={'age','ageUnits','depth','depthUnits','year','yearUnits','geo_type','paleoData_values'};
f=fieldnames(TS);
pid=f(find(~cellfun(@isempty,(strfind(f,'identifier')))&strncmpi('pub',f,3)));
if ~isempty(pid)%remove any pub identifiers, if there are any
    TS=rmfield(TS,pid);
end
TS=rmfield(TS,torem);
f=fieldnames(TS);
%make chunks. 
baseNames=f(find(cellfun(@isempty,(strfind(f,'_')))));
geoNames=f(find(strncmpi('geo_',f,4)));
pubNames=f(find(strncmpi('pub',f,3)));
paleoDataNames=f(find(strncmpi('paleoData_',f,10)));
ciNames=f(find(strncmpi('climateInterpretation_',f,22)));
calNames=f(find(strncmpi('calibration_',f,12)));
paleoDatai=(find(strncmpi('paleoData_',f,10)));
cii=(find(strncmpi('climateInterpretation_',f,22)));
cali=(find(strncmpi('calibration_',f,12)));

%need to add chron!


%create top chunk, includes, base, pub and geo metadata
%how big to make it?
tcr=max([length(geoNames) length(pubNames) length(baseNames)]);
%8columns (2 and an empty one for each
topChunk=cell(tcr,8); 

%base first
topChunk(1:length(baseNames),1)=baseNames;
for n=1:length(baseNames)
    topChunk{n,2}=TS(1).(baseNames{n});
end

%pub second
topChunk(1:length(pubNames),4)=pubNames;
for n=1:length(pubNames)
    topChunk{n,5}=TS(1).(pubNames{n});
end

%geo third
topChunk(1:length(geoNames),7)=geoNames;
for n=1:length(geoNames)
    topChunk{n,8}=TS(1).(geoNames{n});
end

%make header
header={'Base Metadata', ' ',' ','Publication Metadata','','','Geographic metadata',''};
%add in header
topChunk=[header ; topChunk];




%now make the paleoData chunks
%make TSid first
tsi=find(strcmp('paleoData_TSid',f));
%make variableName second
vni=find(strcmp('paleoData_variableName',f));
%make description third
di=find(strcmp('paleoData_description',f));
%make units fourth
ui=find(strcmp('paleoData_units',f));


pdCi=[tsi; vni; di; ui;  setdiff(paleoDatai,[tsi vni di ui]); cii; cali];
botChunk=cell(length(TS),length(pdCi)); 

for p=1:length(pdCi)
   botChunk(:,p)={TS.(f{pdCi(p)})}; 
end

%add in the header
botChunk=[f(pdCi)';botChunk];

%combine the two chunks
nrow=size(topChunk,1)+size(botChunk,1)+1;

ncol=max([size(topChunk,2),size(botChunk,2)]);

%make final cell to be written to google
metadataCell=cell(nrow,ncol);
metadataCell(1:size(topChunk,1),1:size(topChunk,2))=topChunk;
metadataCell((size(topChunk,1)+2):end,1:size(botChunk,2))=botChunk;

%make all the cell entries strings
metadataCell=stringifyCells(metadataCell);

%now write this into the first worksheet
changeWorksheetNameAndSize(spreadSheetNew.spreadsheetKey,wsNames(1).worksheetKey,nrow,ncol,'metadata',aTokenSpreadsheet);

for m=1:ncol
editWorksheetColumn(spreadSheetNew.spreadsheetKey,wsNames(1).worksheetKey,m,1:nrow,metadataCell(:,m),aTokenSpreadsheet);
end


%save updated LipD file?
