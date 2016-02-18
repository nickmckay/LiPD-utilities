function L=updateLiPDGoogleFile(L)
%updates the google version of LiPD file that already exists
% % % deal with authorization on google
checkGoogleTokens;


%check to see if L already has a google file
if ~isfield(L,'googleSpreadSheetKey')
    error([L.dataSetName ' does not already have a google spreadsheet, you should use createLiPDGoogleFile instead'])
end
rewrite=0; %by default, we're doing nothing to this spreadsheet
%check to see if the tagMD5's are the same
col1=getWorksheetColumn(L.googleSpreadSheetKey,L.googleMetadataWorksheet,1,aTokenSpreadsheet,0);
tr=find(strcmp('tagMD5',col1));

if isempty(tr)
    rewrite=2;%if there is no tag MD5
else
    googTagMD5=getWorksheetCell(L.googleSpreadSheetKey,L.googleMetadataWorksheet,tr,2,aTokenSpreadsheet);
    if ~strcmp(L.tagMD5,googTagMD5)
        rewrite=1;%or if it's not the same, rewrite
    end
end

if rewrite>0
    if rewrite==1
        display([L.dataSetName ': MD5 tags dont match - updating spreadsheet'])
    else
        display([L.dataSetName ': NO MD5 tag on google - updating spreadsheet'])
    end
    
    
    %what worksheets do we have
    wl=getWorksheetList(L.googleSpreadSheetKey,aTokenSpreadsheet);
    
    %how many do we need?
    nPD=length(fieldnames(L.paleoData));
    nCD=0;%start with 0
    if isfield(L,'chronData')
        nCD=length(fieldnames(L.chronData));
    end
    wNeeded=nPD+nCD+1;%an extra one formetadata
    
    rightNumberofSheets=0;
    if length(wl)==wNeeded
        rightNumberofSheets=1;
    end
    
    %If you have the right number of sheets, go into this process - if not,
    %recreate them all.
    
    if rightNumberofSheets
        %now update the worksheet for each paleoDataTable
        pdNames=fieldnames(L.paleoData);
        for pd=1:length(pdNames)
            P=L.paleoData.(pdNames{pd});
            
            %get the names of the columns
            colNames=structFieldNames(P);
            nCol=length(colNames);
            nRow=length(P.(colNames{1}).values)+2;
            
            
            %
            changeWorksheetNameAndSize(L.googleSpreadSheetKey,P.googWorkSheetKey,nRow,nCol,['paleoData-' pdNames{pd}],aTokenSpreadsheet);
            
            
            %go through the columns and populate the cells
            for c=1:nCol
                %check for TSid
                if ~isfield(P.(colNames{c}),'TSid')
                    %create one - check against master list
                    P.(colNames{c}).TSid=createTSID(P.(colNames{c}).variableName,L.dataSetName,L.googleSpreadSheetKey,P.googWorkSheetKey);
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
                editWorksheetColumn(L.googleSpreadSheetKey,P.googWorkSheetKey,colNum,1:nRow,colData,aTokenSpreadsheet);
            end
            L.paleoData.(pdNames{pd})=P;
            
        end
        
        
        %chronData
        %if there's chrondata, write that too.
        if isfield(L,'chronData')
            %now create a worksheet for each chronDataTable
            pdNames=fieldnames(L.chronData);
            for pd=1:length(pdNames)
                P=L.chronData.(pdNames{pd});
                %get the names of the columns
                colNames=structFieldNames(P);
                nCol=length(colNames);
                nRow=length(P.(colNames{1}).values)+2;
                
                
                %
                changeWorksheetNameAndSize(L.googleSpreadSheetKey,P.googWorkSheetKey,nRow,nCol,['chronData-' pdNames{pd}],aTokenSpreadsheet);
                
                
                %go through the columns and populate the cells
                for c=1:nCol
                    %check for TSid
                    if ~isfield(P.(colNames{c}),'TSid')
                        %create one - check against master list
                        P.(colNames{c}).TSid=createTSID(P.(colNames{c}).variableName,L.dataSetName,L.googleSpreadSheetKey,P.googWorkSheetKey);
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
                    editWorksheetColumn(L.googleSpreadSheetKey,P.googWorkSheetKey,colNum,1:nRow,colData,aTokenSpreadsheet);
                end
                L.chronData.(pdNames{pd})=P;%write it back into the main structure
            end
        end
        
        
    else %if there is not the right number of sheets...
        %just make new ones
        %first delete all but metadata
        for w=2:length(wl)
            deleteWorksheet(L.googleSpreadSheetKey,wl(w).worksheetKey,aTokenSpreadsheet);
        end
        
        %now create a worksheet for each paleoDataTable
        pdNames=fieldnames(L.paleoData);
        for pd=1:length(pdNames)
            P=L.paleoData.(pdNames{pd});
            %get the names of the columns
            colNames=structFieldNames(P);
            nCol=length(colNames);
            nRow=length(P.(colNames{1}).values)+2;
            %create a new spreadsheet, with two extra rows (for variable name
            %and TSID)
            display('creating new worksheet')
            newWS=createWorksheet(L.googleSpreadSheetKey,nRow,nCol,['paleoData-' pdNames{pd}],aTokenSpreadsheet);
            display(['created new worksheet ' newWS.worksheetKey])
            
            P.googWorkSheetKey=newWS.worksheetKey;
            
            %go through the columns and populate the cells
            for c=1:nCol
                %check for TSid
                if ~isfield(P.(colNames{c}),'TSid')
                    %create one - check against master list
                    P.(colNames{c}).TSid=createTSID(P.(colNames{c}).variableName,L.dataSetName,L.googleSpreadSheetKey,P.googWorkSheetKey);
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
                editWorksheetColumn(L.googleSpreadSheetKey,newWS.worksheetKey,colNum,1:nRow,colData,aTokenSpreadsheet);
            end
            L.paleoData.(pdNames{pd})=P;
            
        end
        
        ['L key-' L.paleoData.(pdNames{pd}).googWorkSheetKey]
        
        %chronData
        %if there's chrondata, write that too.
        if isfield(L,'chronData')
            %now create a worksheet for each chronDataTable
            pdNames=fieldnames(L.chronData);
            for pd=1:length(pdNames)
                P=L.chronData.(pdNames{pd});
                %get the names of the columns
                colNames=structFieldNames(P);
                nCol=length(colNames);
                nRow=length(P.(colNames{1}).values)+2;
                %create a new spreadsheet, with two extra rows (for variable name
                %and TSID)
                display('creating new worksheet')
                newWS=createWorksheet(L.googleSpreadSheetKey,nRow,nCol,['chronData-' pdNames{pd}],aTokenSpreadsheet);
                display(['created new worksheet ' newWS.worksheetKey])
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
                    editWorksheetColumn(L.googleSpreadSheetKey,newWS.worksheetKey,colNum,1:nRow,colData,aTokenSpreadsheet);
                end
                L.chronData.(pdNames{pd})=P;%write it back into the main structure
            end
        end
    end
    %Now metadata the same for all cases
    %metadata
    %edit that first sheet to become the metadatasheet
    
    %extract timeseries
    TS=structord(extractTimeseriesLiPD(L,1));
    
    %get rid of unnecessary metadata
    torem={'age','ageUnits','depth','depthUnits','year','yearUnits','geo_type','paleoData_values','pub1_abstract','pub2_abstract','paleoData_dataType','paleoData_missingValue'};
    f=fieldnames(TS);
    pid=f(find(~cellfun(@isempty,(strfind(f,'identifier')))&strncmpi('pub',f,3)));
    if ~isempty(pid)%remove any pub identifiers, if there are any
        TS=rmfield(TS,pid);
    end
    for i=1:length(torem)
        if isfield(TS,torem{i})
            TS=rmfield(TS,torem{i});
        end
    end
    f=fieldnames(TS);
    %make chunks.
    baseNames=f(find(cellfun(@isempty,(strfind(f,'_')))));
    geoNames=f(find(strncmpi('geo_',f,4)));
    pubNames=f(find(strncmpi('pub',f,3)));
    fundNames=f(find(strncmpi('fund',f,4)));
    paleoDataNames=f(find(strncmpi('paleoData_',f,10)));
    ciNames=f(find(strncmpi('climateInterpretation_',f,22)));
    calNames=f(find(strncmpi('calibration_',f,12)));
    paleoDatai=(find(strncmpi('paleoData_',f,10)));
    cii=(find(strncmpi('climateInterpretation_',f,22)));
    cali=(find(strncmpi('calibration_',f,12)));
    
    
    
    %create top chunk, includes, base, pub and geo metadata
    %how big to make it?
    tcr=max([length(geoNames) length(pubNames) length(baseNames) length(fundNames)]);
    
    if isempty(fundNames)%if no funding then
        %8columns (2 and an empty one for each
        topChunk=cell(tcr,8);
    else %include 3 more for funding
        topChunk=cell(tcr,11);
    end
    
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
    %save topChunk.mat topChunk %TROUBLESHOOTING
    %funding fourth
    if ~isempty(fundNames)%
        topChunk(1:length(fundNames),10)=fundNames;
        for n=1:length(fundNames)
            %         fN=TS(1).(fundNames{n}); %TROUBLESHOOTING
            %         save fn.mat fN ; %TROUBLESHOOTING
            topChunk{n,11}=TS(1).(fundNames{n});
        end
    end
    
    %make header
    if ~isempty(fundNames)%
        header={'Base Metadata', ' ',' ','Publication Metadata','','','Geographic metadata','','','Funding metadata',''};
    else
        header={'Base Metadata', ' ',' ','Publication Metadata','','','Geographic metadata',''};
    end
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
    
    %add in the headers
    h1=cell(1,size(botChunk,2));
    h1{1}='paleoData column metadata';
    botChunk=[h1; f(pdCi)';botChunk];
    
    %combine the two chunks
    nrow=size(topChunk,1)+size(botChunk,1)+1;
    
    ncol=max([size(topChunk,2),size(botChunk,2)]);
    
    %make final cell to be written to google
    metadataCell=cell(nrow,ncol);
    metadataCell(1:size(topChunk,1),1:size(topChunk,2))=topChunk;
    metadataCell((size(topChunk,1)+2):end,1:size(botChunk,2))=botChunk;
    
    %make all the cell entries strings
    %save dum.mat metadataCell %troubleshooting
    metadataCell4Goog=stringifyCells(metadataCell);
    
    %now write this into the first worksheet
    changeWorksheetNameAndSize(L.googleSpreadSheetKey,L.googleMetadataWorksheet,nrow,ncol,'metadata',aTokenSpreadsheet);
    
    for m=1:ncol
        editWorksheetColumn(L.googleSpreadSheetKey,L.googleMetadataWorksheet,m,1:nrow,metadataCell4Goog(:,m),aTokenSpreadsheet);
    end
    
    
    
    
    
    
    
    
else %don't rewrite
    display([L.dataSetName ': MD5 tags match - not updating spreadsheet'])
end    %save updated LipD file?
